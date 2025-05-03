import os
from fastapi import FastAPI, Request
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import logging

# Загрузка переменных окружения
load_dotenv()  # Это нужно только для локальной разработки. На Railway переменные загружаются автоматически.

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Загружаем из переменной окружения на Railway
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Загружаем из переменной окружения на Railway

# Логи
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Проверка переменных окружения
if not BOT_TOKEN or not WEBHOOK_URL:
    logger.error("Переменные окружения не найдены!")
    raise ValueError("BOT_TOKEN или WEBHOOK_URL не заданы!")

# FastAPI
app = FastAPI()

# Telegram Application
telegram_app = Application.builder().token(BOT_TOKEN).build()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton(text="Открыть Квиз", web_app=WebAppInfo(url="https://kvizapp.vercel.app"))]
    ]
    await update.message.reply_text(
        "Нажми кнопку чтобы открыть квиз!",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# Обработка данных из WebApp
async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.message.web_app_data.data
    await update.message.reply_text(f"Ты отправил: {data}")

# Инициализация обработчиков
@app.on_event("startup")
async def startup():
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    
    # Установка Webhook
    webhook_url = WEBHOOK_URL + "/webhook"
    await telegram_app.bot.set_webhook(webhook_url)
    logger.info(f"Webhook установлен на {webhook_url}!")

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
