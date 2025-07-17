import os
import logging
import asyncio
import tempfile
import shutil
from io import BytesIO
from typing import Optional
from pathlib import Path

from telegram import Update, Document, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ChatAction
from pdf2image import convert_from_path
from PIL import Image, ImageOps
import img2pdf

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def cleanup(self):
        """Clean up temporary files"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    async def send_status_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, action: str = None):
        """Send status message and optionally set chat action"""
        if action:
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=action)
        
        # Send status message
        status_msg = await update.effective_message.reply_text(message)
        await asyncio.sleep(1)  # Brief pause for user to read
        return status_msg
    
    async def invert_pdf_colors(self, update: Update, context: ContextTypes.DEFAULT_TYPE, pdf_path: str) -> str:
        """Invert colors of a PDF file and return the path to the inverted PDF"""
        try:
            # Status: Starting conversion
            await self.send_status_message(update, context, "📄 Extracting pages from PDF...", ChatAction.TYPING)
            
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=150)
            
            # Status: Pages detected
            await self.send_status_message(update, context, f"🔢 Total pages detected: {len(images)}")
            
            # Status: Starting color inversion
            await self.send_status_message(update, context, "🎨 Inverting colors on each page...", ChatAction.TYPING)
            
            # Invert colors of each image
            inverted_images = []
            for i, image in enumerate(images):
                # Convert to RGB if not already
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Invert colors
                inverted_image = ImageOps.invert(image)
                inverted_images.append(inverted_image)
                
                # Update progress for large PDFs
                if len(images) > 5 and (i + 1) % 5 == 0:
                    await self.send_status_message(update, context, f"🎨 Processed {i + 1}/{len(images)} pages...")
            
            # Status: Image transformation
            await self.send_status_message(update, context, "🧪 Applying image transformation...", ChatAction.TYPING)
            
            # Save inverted images to temporary files
            temp_image_paths = []
            for i, img in enumerate(inverted_images):
                temp_img_path = os.path.join(self.temp_dir, f"inverted_page_{i}.png")
                img.save(temp_img_path, "PNG")
                temp_image_paths.append(temp_img_path)
            
            # Status: Reassembling PDF
            await self.send_status_message(update, context, "🧩 Reassembling pages into new PDF...", ChatAction.TYPING)
            
            # Convert images back to PDF
            output_pdf_path = os.path.join(self.temp_dir, "inverted_output.pdf")
            with open(output_pdf_path, "wb") as f:
                f.write(img2pdf.convert(temp_image_paths))
            
            return output_pdf_path
            
        except Exception as e:
            logger.error(f"Error inverting PDF colors: {e}")
            raise
    
    async def create_layout_pdf(self, update: Update, context: ContextTypes.DEFAULT_TYPE, pdf_path: str, layout_type: str, orientation: str = "portrait") -> str:
        """Create N-up layout PDF with specified orientation"""
        try:
            # Status: Starting conversion
            await self.send_status_message(update, context, "📄 Extracting pages from PDF...", ChatAction.TYPING)
            
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=150)
            
            # Status: Pages detected
            await self.send_status_message(update, context, f"🔢 Total pages detected: {len(images)}")
            
            # Define layout configurations
            layout_configs = {
                "2in1": {"pages": 2, "cols": 2, "rows": 1},
                "4in1": {"pages": 4, "cols": 2, "rows": 2},
                "6in1": {"pages": 6, "cols": 3, "rows": 2},
                "9in1": {"pages": 9, "cols": 3, "rows": 3},
                "12in1": {"pages": 12, "cols": 4, "rows": 3},
                "16in1": {"pages": 16, "cols": 4, "rows": 4}
            }
            
            if layout_type not in layout_configs:
                raise ValueError(f"Unsupported layout type: {layout_type}")
            
            config = layout_configs[layout_type]
            pages_per_sheet = config["pages"]
            
            # Determine grid based on orientation
            if orientation == "landscape":
                grid_cols, grid_rows = config["rows"], config["cols"]
                # A4 landscape dimensions
                a4_width, a4_height = 1754, 1240
            else:  # portrait
                grid_cols, grid_rows = config["cols"], config["rows"]
                # A4 portrait dimensions
                a4_width, a4_height = 1240, 1754
            
            # Status: Processing layout
            await self.send_status_message(update, context, f"📐 Creating {layout_type} layout in {orientation} orientation...", ChatAction.TYPING)
            
            # Calculate dimensions for each page on the sheet
            page_width = a4_width // grid_cols
            page_height = a4_height // grid_rows
            
            layout_images = []
            current_sheet = Image.new('RGB', (a4_width, a4_height), 'white')
            pages_on_current_sheet = 0
            
            for i, image in enumerate(images):
                # Resize image to fit in the allocated space
                image.thumbnail((page_width, page_height), Image.Resampling.LANCZOS)
                
                # Calculate position on the sheet
                col = pages_on_current_sheet % grid_cols
                row = pages_on_current_sheet // grid_cols
                
                x = col * page_width + (page_width - image.width) // 2
                y = row * page_height + (page_height - image.height) // 2
                
                # Paste the image onto the current sheet
                current_sheet.paste(image, (x, y))
                pages_on_current_sheet += 1
                
                # Update progress for large PDFs
                if len(images) > 10 and (i + 1) % 10 == 0:
                    await self.send_status_message(update, context, f"📐 Processed {i + 1}/{len(images)} pages...")
                
                # If sheet is full or it's the last page, save the sheet
                if pages_on_current_sheet == pages_per_sheet or i == len(images) - 1:
                    layout_images.append(current_sheet.copy())
                    current_sheet = Image.new('RGB', (a4_width, a4_height), 'white')
                    pages_on_current_sheet = 0
            
            # Status: Finalizing layout
            await self.send_status_message(update, context, "🧪 Applying layout transformation...", ChatAction.TYPING)
            
            # Save layout images to temporary files
            temp_image_paths = []
            for i, img in enumerate(layout_images):
                temp_img_path = os.path.join(self.temp_dir, f"layout_page_{i}.png")
                img.save(temp_img_path, "PNG")
                temp_image_paths.append(temp_img_path)
            
            # Status: Reassembling PDF
            await self.send_status_message(update, context, "🧩 Reassembling pages into new PDF...", ChatAction.TYPING)
            
            # Convert images back to PDF
            output_pdf_path = os.path.join(self.temp_dir, f"layout_{layout_type}_{orientation}_output.pdf")
            with open(output_pdf_path, "wb") as f:
                f.write(img2pdf.convert(temp_image_paths))
            
            return output_pdf_path
            
        except Exception as e:
            logger.error(f"Error creating layout PDF: {e}")
            raise

# Global processor instance
processor = PDFProcessor()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = """
🤖 **PDF Processing Bot**

Welcome! I can help you process PDF files with the following features:

📄 **Commands:**
• `/invert` - Invert colors of your PDF
• `/layout_2in1` - Convert to 2-pages-per-sheet layout
• `/layout_4in1` - Convert to 4-pages-per-sheet layout
• `/layout_6in1` - Convert to 6-pages-per-sheet layout
• `/layout_9in1` - Convert to 9-pages-per-sheet layout
• `/layout_12in1` - Convert to 12-pages-per-sheet layout
• `/layout_16in1` - Convert to 16-pages-per-sheet layout
• `/help` - Show this help message

📋 **How to use:**
1. Send me a PDF file
2. Use one of the commands above to process it
3. Choose orientation (portrait/landscape) for layout options
4. I'll send you back the processed PDF with real-time updates

⚠️ **Note:** Please send PDF files only (max 20MB recommended)
    """
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message."""
    await start(update, context)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document uploads."""
    document: Document = update.message.document
    
    # Status: File received
    await processor.send_status_message(update, context, "📥 PDF received. Validating file...", ChatAction.TYPING)
    
    # Status: Checking file type
    await processor.send_status_message(update, context, "🔍 Checking file type...")
    
    if not document.file_name.lower().endswith('.pdf'):
        await update.message.reply_text("❌ Please send a PDF file only.")
        return
    
    # Store the file info in context for later processing
    context.user_data['pdf_file_id'] = document.file_id
    context.user_data['pdf_file_name'] = document.file_name
    
    await update.message.reply_text(
        f"✅ PDF validated: {document.file_name}\n\n"
        "Now use one of these commands to process it:\n"
        "• `/invert` - Invert colors\n"
        "• `/layout_2in1` - 2-pages-per-sheet\n"
        "• `/layout_4in1` - 4-pages-per-sheet\n"
        "• `/layout_6in1` - 6-pages-per-sheet\n"
        "• `/layout_9in1` - 9-pages-per-sheet\n"
        "• `/layout_12in1` - 12-pages-per-sheet\n"
        "• `/layout_16in1` - 16-pages-per-sheet"
    )

async def create_orientation_keyboard(layout_type: str):
    """Create inline keyboard for orientation selection"""
    keyboard = [
        [
            InlineKeyboardButton("📱 Portrait", callback_data=f"orient_{layout_type}_portrait"),
            InlineKeyboardButton("📄 Landscape", callback_data=f"orient_{layout_type}_landscape")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def handle_orientation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle orientation selection callback"""
    query = update.callback_query
    await query.answer()
    
    # Parse callback data
    _, layout_type, orientation = query.data.split('_')
    
    # Delete the orientation selection message
    await query.delete_message()
    
    # Process the PDF with selected orientation
    await process_pdf_with_orientation(query, context, layout_type, orientation)

async def process_pdf_with_orientation(update: Update, context: ContextTypes.DEFAULT_TYPE, layout_type: str, orientation: str) -> None:
    """Process PDF with specified layout and orientation"""
    if 'pdf_file_id' not in context.user_data:
        await update.effective_message.reply_text("❌ Please send a PDF file first.")
        return
    
    try:
        # Status: Starting processing
        await processor.send_status_message(update, context, f"🔄 Processing your PDF with {layout_type} {orientation} layout...", ChatAction.TYPING)
        
        # Download the file
        file = await context.bot.get_file(context.user_data['pdf_file_id'])
        
        # Create temporary file for input PDF
        input_pdf_path = os.path.join(processor.temp_dir, "input.pdf")
        await file.download_to_drive(input_pdf_path)
        
        # Process the PDF
        output_pdf_path = await processor.create_layout_pdf(update, context, input_pdf_path, layout_type, orientation)
        operation_text = f"{layout_type} {orientation} layout"
        
        # Status: Uploading
        await processor.send_status_message(update, context, "📤 Uploading your new PDF...", ChatAction.UPLOAD_DOCUMENT)
        
        # Send the processed PDF back
        original_name = context.user_data['pdf_file_name']
        output_name = f"{layout_type}_{orientation}_{original_name}"
        
        with open(output_pdf_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=output_name,
                caption=f"✅ Done! Your {operation_text} PDF is ready."
            )
        
        # Clean up temporary files
        if os.path.exists(input_pdf_path):
            os.remove(input_pdf_path)
        if os.path.exists(output_pdf_path):
            os.remove(output_pdf_path)
            
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        await update.effective_message.reply_text(f"❌ Error processing PDF: {str(e)}")

async def process_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE, operation: str) -> None:
    """Process PDF with the specified operation."""
    if 'pdf_file_id' not in context.user_data:
        await update.message.reply_text("❌ Please send a PDF file first.")
        return
    
    try:
        if operation == "invert":
            # Status: Starting processing
            await processor.send_status_message(update, context, "🔄 Processing your PDF for color inversion...", ChatAction.TYPING)
            
            # Download the file
            file = await context.bot.get_file(context.user_data['pdf_file_id'])
            
            # Create temporary file for input PDF
            input_pdf_path = os.path.join(processor.temp_dir, "input.pdf")
            await file.download_to_drive(input_pdf_path)
            
            # Process the PDF
            output_pdf_path = await processor.invert_pdf_colors(update, context, input_pdf_path)
            operation_text = "inverted"
            
            # Status: Uploading
            await processor.send_status_message(update, context, "📤 Uploading your new PDF...", ChatAction.UPLOAD_DOCUMENT)
            
            # Send the processed PDF back
            original_name = context.user_data['pdf_file_name']
            output_name = f"inverted_{original_name}"
            
            with open(output_pdf_path, 'rb') as f:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=f,
                    filename=output_name,
                    caption=f"✅ Done! Your {operation_text} PDF is ready."
                )
            
            # Clean up temporary files
            if os.path.exists(input_pdf_path):
                os.remove(input_pdf_path)
            if os.path.exists(output_pdf_path):
                os.remove(output_pdf_path)
                
        elif operation in ["2in1", "4in1", "6in1", "9in1", "12in1", "16in1"]:
            # Show orientation selection for layout operations
            keyboard = await create_orientation_keyboard(operation)
            await update.message.reply_text(
                f"📐 Choose orientation for {operation} layout:",
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text("❌ Unknown operation.")
            return
            
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        await update.message.reply_text(f"❌ Error processing PDF: {str(e)}")

async def invert_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /invert command."""
    await process_pdf(update, context, "invert")

async def layout_2in1_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /layout_2in1 command."""
    await process_pdf(update, context, "2in1")

async def layout_4in1_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /layout_4in1 command."""
    await process_pdf(update, context, "4in1")

async def layout_6in1_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /layout_6in1 command."""
    await process_pdf(update, context, "6in1")

async def layout_9in1_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /layout_9in1 command."""
    await process_pdf(update, context, "9in1")

async def layout_12in1_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /layout_12in1 command."""
    await process_pdf(update, context, "12in1")

async def layout_16in1_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /layout_16in1 command."""
    await process_pdf(update, context, "16in1")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and notify user."""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ An error occurred. Please try again.")

def main() -> None:
    """Start the bot."""
    # Get bot token from environment variable
    token = os.environ.get("BOT_TOKEN")
    if not token:
        logger.error("BOT_TOKEN environment variable not set!")
        return
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("invert", invert_command))
    application.add_handler(CommandHandler("layout_2in1", layout_2in1_command))
    application.add_handler(CommandHandler("layout_4in1", layout_4in1_command))
    application.add_handler(CommandHandler("layout_6in1", layout_6in1_command))
    application.add_handler(CommandHandler("layout_9in1", layout_9in1_command))
    application.add_handler(CommandHandler("layout_12in1", layout_12in1_command))
    application.add_handler(CommandHandler("layout_16in1", layout_16in1_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(CallbackQueryHandler(handle_orientation_callback, pattern="^orient_"))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Starting PDF Processing Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    try:
        main()
    finally:
        # Clean up on exit
        processor.cleanup()