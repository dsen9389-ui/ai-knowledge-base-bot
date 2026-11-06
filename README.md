# AI Knowledge Base Bot

Turn messy notes into structured personal knowledge bases instantly using Python and aiogram.

## Features

- Capture raw text via chat messages
- Generate structured markdown articles automatically
- Track storage and note counts per user

## Local Setup

1. Clone the repository.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy .env.example to .env and add your Telegram bot token:
   ```bash
   cp .env.example .env
   ```
4. Run the bot:
   ```bash
   python main.py
   ```

## Deployment Guide for Render or Koyeb

1. Push your code to a GitHub repository.
2. Create a new Web Service or Background Worker on Render/Koyeb.
3. Connect your GitHub repository.
4. Set the Build Command to: `pip install -r requirements.txt`
5. Set the Start Command to: `python main.py`
6. Add an environment variable named `BOT_TOKEN` with your Telegram token.
7. Deploy and enjoy your running bot.