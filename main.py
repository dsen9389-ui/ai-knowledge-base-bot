import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import aiosqlite
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN", "")
DB_PATH = "knowledge_base.db"

router = Router()

class NoteState(StatesGroup):
    waiting_for_note = State()

def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Add Note"), KeyboardButton(text="My Notes")],
            [KeyboardButton(text="Statistics"), KeyboardButton(text="Help")]
        ],
        resize_keyboard=True
    )

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        await db.commit()

@router.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = (
        "Welcome to AI Knowledge Base Bot!\
\
"
        "Organize your raw notes into structured markdown effortlessly."
    )
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@router.message(Command("help"))
@router.message(F.text == "Help")
async def cmd_help(message: Message):
    help_text = (
        "Commands available:\
"
        "/start - Start the bot\
"
        "/help - Show this help message\
"
        "/status - Check system health\
\
"
        "Use the keyboard buttons below to manage your personal notes."
    )
    await message.answer(help_text, reply_markup=get_main_keyboard())

@router.message(Command("status"))
async def cmd_status(message: Message):
    await message.answer("System status: Online and operational. Database is connected.")

@router.message(F.text == "Add Note")
async def note_start(message: Message, state: FSMContext):
    await state.set_state(NoteState.waiting_for_note)
    await message.answer("Send me your raw notes or text snippet. I will format it into markdown.")

@router.message(NoteState.waiting_for_note)
async def note_receive(message: Message, state: FSMContext):
    user_id = message.from_user.id
    raw_text = message.text
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO notes (user_id, content) VALUES (?, ?)",
            (user_id, raw_text)
        )
        await db.commit()
        
    await state.clear()
    
    markdown_output = (
        "### Structured Markdown Article\
\
"
        f"{raw_text}\
\
"
        "---\
"
        "*Tags: #notes #knowledgebase*"
    )
    
    await message.answer(
        f"Note saved successfully!\
\
{markdown_output}",
        reply_markup=get_main_keyboard()
    )

@router.message(F.text == "My Notes")
async def list_notes(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT content FROM notes WHERE user_id = ? ORDER BY id DESC LIMIT 5",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            
    if not rows:
        await message.answer("You do not have any saved notes yet. Click Add Note to begin.", reply_markup=get_main_keyboard())
        return
        
    response = "Your recent notes:\
\
"
    for i, row in enumerate(rows, 1):
        snippet = row[0][:50] + "..." if len(row[0]) > 50 else row[0]
        response += f"{i}. {snippet}\
"
        
    await message.answer(response, reply_markup=get_main_keyboard())

@router.message(F.text == "Statistics")
async def show_stats(message: Message):
    user_id = message.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT COUNT(*) FROM notes WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            count = row[0] if row else 0
            
    await message.answer(f"Your Knowledge Base Statistics:\
\
Total Notes Saved: {count}", reply_markup=get_main_keyboard())

async def main():
    logging.basicConfig(level=logging.INFO)
    if not TOKEN:
        logging.error("BOT_TOKEN is missing from environment variables!")
        return
        
    await init_db()
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    logging.info("Starting bot polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())