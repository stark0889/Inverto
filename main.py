import os
import logging
import asyncio
import tempfile
import shutil
from io import BytesIO
from typing import Optional
from pathlib import Path

from telegram import Update, Document
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
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
    
    def invert_pdf_colors(self, pdf_path: str) -> str:
        """Invert colors of a PDF file and return the path to the inverted PDF"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=150)
            
            # Invert colors of each image
            inverted_images = []
            for i, image in enumerate(images):
                # Convert to RGB if not already
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Invert colors
                inverted_image = ImageOps.invert(image)
                inverted_images.append(inverted_image)
            
            # Save inverted images to temporary files
            temp_image_paths = []
            for i, img in enumerate(inverted_images):
                temp_img_path = os.path.join(self.temp_dir, f"inverted_page_{i}.png")
                img.save(temp_img_path, "PNG")
                temp_image_paths.append(temp_img_path)
            
            # Convert images back to PDF
            output_pdf_path = os.path.join(self.temp_dir, "inverted_output.pdf")
            with open(output_pdf_path, "wb") as f:
                f.write(img2pdf.convert(temp_image_paths))
            
            return output_pdf_path
            
        except Exception as e:
            logger.error(f"Error inverting PDF colors: {e}")
            raise
    
    def create_layout_pdf(self, pdf_path: str, layout_type: str) -> str:
        """Create N-up layout PDF (2-in-1 or 4-in-1)"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=150)
            
            # A4 size in pixels at 150 DPI (approximately)
            a4_width, a4_height = 1240, 1754
            
            if layout_type == "2in1":
                pages_per_sheet = 2
                grid_cols, grid_rows = 2, 1
            elif layout_type == "4in1":
                pages_per_sheet = 4
                grid_cols, grid_rows = 2, 2
            else:
                raise ValueError(f"Unsupported layout type: {layout_type}")
            
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
                
                # If sheet is full or it's the last page, save the sheet
                if pages_on_current_sheet == pages_per_sheet or i == len(images) - 1:
                    layout_images.append(current_sheet.copy())
                    current_sheet = Image.new('RGB', (a4_width, a4_height), 'white')
                    pages_on_current_sheet = 0
            
            # Save layout images to temporary files
            temp_image_paths = []
            for i, img in enumerate(layout_images):
                temp_img_path = os.path.join(self.temp_dir, f"layout_page_{i}.png")
                img.save(temp_img_path, "PNG")
                temp_image_paths.append(temp_img_path)
            
            # Convert images back to PDF
            output_pdf_path = os.path.join(self.temp_dir, f"layout_{layout_type}_output.pdf")
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
• `/help` - Show this help message

📋 **How to use:**
1. Send me a PDF file
2. Use one of the commands above to process it
3. I'll send you back the processed PDF

⚠️ **Note:** Please send PDF files only (max 20MB recommended)
    """
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message."""
    await start(update, context)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document uploads."""
    document: Document = update.message.document
    
    if not document.file_name.lower().endswith('.pdf'):
        await update.message.reply_text("❌ Please send a PDF file only.")
        return
    
    # Store the file info in context for later processing
    context.user_data['pdf_file_id'] = document.file_id
    context.user_data['pdf_file_name'] = document.file_name
    
    await update.message.reply_text(
        f"📄 PDF received: {document.file_name}\n\n"
        "Now use one of these commands to process it:\n"
        "• `/invert` - Invert colors\n"
        "• `/layout_2in1` - 2-pages-per-sheet\n"
        "• `/layout_4in1` - 4-pages-per-sheet"
    )

async def process_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE, operation: str) -> None:
    """Process PDF with the specified operation."""
    if 'pdf_file_id' not in context.user_data:
        await update.message.reply_text("❌ Please send a PDF file first.")
        return
    
    try:
        # Send processing message
        processing_msg = await update.message.reply_text("🔄 Processing your PDF... Please wait.")
        
        # Download the file
        file = await context.bot.get_file(context.user_data['pdf_file_id'])
        
        # Create temporary file for input PDF
        input_pdf_path = os.path.join(processor.temp_dir, "input.pdf")
        await file.download_to_drive(input_pdf_path)
        
        # Process based on operation
        if operation == "invert":
            output_pdf_path = processor.invert_pdf_colors(input_pdf_path)
            operation_text = "inverted"
        elif operation in ["2in1", "4in1"]:
            output_pdf_path = processor.create_layout_pdf(input_pdf_path, operation)
            operation_text = f"{operation} layout"
        else:
            await update.message.reply_text("❌ Unknown operation.")
            return
        
        # Send the processed PDF back
        original_name = context.user_data['pdf_file_name']
        output_name = f"{operation}_{original_name}"
        
        with open(output_pdf_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=output_name,
                caption=f"✅ Your {operation_text} PDF is ready!"
            )
        
        # Delete processing message
        await processing_msg.delete()
        
        # Clean up temporary files
        if os.path.exists(input_pdf_path):
            os.remove(input_pdf_path)
        if os.path.exists(output_pdf_path):
            os.remove(output_pdf_path)
            
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

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors and notify user."""
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ An error occurred. Please try again.")

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
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    
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