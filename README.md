# PDF Processing Telegram Bot

A powerful Telegram bot that processes PDF files with color inversion and layout optimization features.

## Features

### 🎨 Color Inversion
- Converts PDF pages to images
- Inverts colors using Pillow (white becomes black, black becomes white)
- Recompiles into a single PDF with inverted colors

### 📄 Layout Options
- **2-in-1 Layout**: Combines 2 pages per sheet in a 2x1 format
- **4-in-1 Layout**: Combines 4 pages per sheet in a 2x2 format
- Maintains A4 paper size for optimal printing
- Memory-efficient processing for large files

### 🤖 Telegram Commands
- `/start` - Welcome message and instructions
- `/help` - Show help information
- `/invert` - Invert colors of the uploaded PDF
- `/layout_2in1` - Convert to 2-pages-per-sheet layout
- `/layout_4in1` - Convert to 4-pages-per-sheet layout

## Setup Instructions

### 1. Prerequisites
- Python 3.8 or higher
- A Telegram Bot Token (get from [@BotFather](https://t.me/BotFather))

### 2. Installation

#### Local Setup
```bash
# Clone or create the project
git clone <your-repo-url>
cd pdf-telegram-bot

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export BOT_TOKEN="your_bot_token_here"

# Run the bot
python main.py
```

#### Replit Setup
1. Create a new Replit project
2. Upload all files to the project
3. Add `BOT_TOKEN` to Secrets (Environment Variables)
4. Run the project

#### Render Setup
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Environment Variables**: Add `BOT_TOKEN` with your bot token

### 3. Getting a Bot Token
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy the bot token and set it as an environment variable

## Usage

1. Start a chat with your bot
2. Send `/start` to see the welcome message
3. Upload a PDF file
4. Use one of the processing commands:
   - `/invert` - for color inversion
   - `/layout_2in1` - for 2-pages-per-sheet
   - `/layout_4in1` - for 4-pages-per-sheet
5. Wait for processing and download the result

## Technical Details

### Dependencies
- `python-telegram-bot==20.7` - Telegram Bot API wrapper
- `pdf2image==1.17.0` - PDF to image conversion
- `Pillow==10.1.0` - Image processing
- `img2pdf==0.5.1` - Image to PDF conversion

### Memory Management
- Uses temporary files for processing
- Automatic cleanup of temporary files
- Efficient image processing with appropriate DPI settings
- Memory-conscious handling of large PDFs

### Error Handling
- Validates PDF file format
- Comprehensive error logging
- User-friendly error messages
- Graceful handling of processing failures

## File Structure
```
pdf-telegram-bot/
├── main.py              # Main bot application
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Deployment Considerations

### Environment Variables
- `BOT_TOKEN` - Your Telegram bot token (required)

### System Requirements
- Sufficient disk space for temporary file processing
- Memory for image processing (recommended: 512MB+)
- Network connectivity for Telegram API

### Limitations
- Maximum file size depends on Telegram limits (20MB for bots)
- Processing time depends on PDF size and complexity
- Temporary files are cleaned up automatically

## Troubleshooting

### Common Issues
1. **Bot not responding**: Check if `BOT_TOKEN` is set correctly
2. **Processing fails**: Ensure PDF is not corrupted or password-protected
3. **Memory errors**: Reduce PDF size or increase system memory
4. **Slow processing**: Large PDFs take more time to process

### Logs
The bot logs important events and errors. Check the console output for debugging information.

## License
This project is open source and available under the MIT License.

## Contributing
Feel free to submit issues and pull requests to improve the bot!