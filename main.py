import asyncio
import sqlite3
import os
from flask import Flask
from threading import Thread
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- НАСТРОЙКИ (ЗАМЕНИ НА СВОИ) ---
TOKEN = "8487544175:AAGU_2T8-PeYKXEuzh7PmKz8FHEEEohbw_k"
CHAT_ID = -100... # ТВОЙ_ID_ЧАТА_ТУТ

bot = Bot(token=TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
app = Flask('')

# --- БАЗА ДАННЫХ ---
db = sqlite3.connect("activity.db", check_same_thread=False)
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, msgs INTEGER DEFAULT 0)")
db.commit()

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
@app.route('/')
def home(): return "Бот запущен!"

def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# --- ЛОГИКА БОТА ---
async def send_greet(text):
    try: await bot.send_message(CHAT_ID, text)
    except: pass

@dp.message(Command("топ_акт"))
async def get_top(message: types.Message):
    cur.execute("SELECT name, msgs FROM users ORDER BY msgs DESC LIMIT 10")
    res = cur.fetchall()
    text = "🏆 **ТОП АКТИВИСТОВ:**\n\n"
    for i, row in enumerate(res, 1):
        text += f"{i}. {row[0]} — {row[1]} сообщ.\n"
    await message.answer(text, parse_mode="Markdown")

@dp.message()
async def count(message: types.Message):
    if not message.from_user: return
    cur.execute("INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)", 
                (message.from_user.id, message.from_user.full_name))
    cur.execute("UPDATE users SET msgs = msgs + 1 WHERE id = ?", (message.from_user.id,))
    db.commit()

async def main():
    Thread(target=run).start() # Запуск веб-сервера
    scheduler.add_job(send_greet, "cron", hour=8, args=["☀️ Доброе утро!"])
    scheduler.add_job(send_greet, "cron", hour=22, args=["🌙 Доброй ночи!"])
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
