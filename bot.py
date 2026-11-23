import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
BASE_URL = os.environ["RENDER_EXTERNAL_URL"]

bot = Application.builder().token(TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! به سامانه IRAN LEGAL ENGINE خوش آمدید.\n\n"
        "سامانه در مرحله راه‌اندازی اولیه است."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - شروع\n"
        "/help - راهنما\n\n"
        "امکانات حقوقی هنوز فعال نشده‌اند."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "پیام شما دریافت شد.\nسامانه در حال راه‌اندازی است."
    )


bot.add_handler(CommandHandler("start", start))
bot.add_handler(CommandHandler("help", help_command))
bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.initialize()
    await bot.start()

    await bot.bot.set_webhook(
        url=f"{BASE_URL}/telegram/webhook",
        secret_token=WEBHOOK_SECRET,
    )

    yield

    await bot.bot.delete_webhook()
    await bot.stop()
    await bot.shutdown()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def home():
    return {"status": "IRAN LEGAL ENGINE is running"}


@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")

    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    data = await request.json()
    update = Update.de_json(data, bot.bot)
    await bot.process_update(update)

    return {"ok": True}
