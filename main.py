import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

TOKEN = os.environ.get("BOT_TOKEN")

stock_data = {
    "Холодильник": 38, "Газ плита": 27, "Пол автомат": 4,
    "Кондиционер": 22, "Пылесос": 17, "ТВ": 34,
    "Дымоход": 7, "Микроволновка": 10, "Коллер": 13,
    "Автомат": 22, "Радиатор": 2, "Морозильник": 2,
    "Воздух очиститель": 2, "Посуда мойка": 1, "Утюг": 0,
    "Аэрогриль": 1, "Тостер": 1, "Мясорубка": 2
}

keyboard = [
    ["📊 Umumiy Qoldiq", "🔴 Kam Qolganlar"],
    ["ℹ️ Bot Haqida"]
]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Ombordagi mahsulotlar hisobini yurituvchi botga xush kelibsiz.",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "📊 Umumiy Qoldiq":
        report = "📦 **OMBORDA MAVJUD MAHSULOTLAR:**\n\n"
        for item, qty in stock_data.items():
            status = "🔴 (Kam қолди)" if qty <= 2 else "🟢 (Етарли)"
            report += f"• **{item}**: {qty} ta {status}\n"
        await update.message.reply_text(report, parse_mode="Markdown")

    elif text == "🔴 Kam Qolganlar":
        report = "🚨 **ZAXIRASI KAM QOLGAN MAHSULOTLAR (≤2):**\n\n"
        low_stock = {k: v for k, v in stock_data.items() if v <= 2}
        if not low_stock:
            report += "Barcha mahsulotlar yetarli miqdorda mavjud."
        else:
            for item, qty in low_stock.items():
                report += f"❌ **{item}**: {qty} ta qoldi\n"
        await update.message.reply_text(report, parse_mode="Markdown")

    elif text == "ℹ️ Bot Haqida":
        await update.message.reply_text("Ushbu bot ombordagi tovarlar qoldig'ini nazorat qilish uchun mo'ljallangan.")

def main():
    if not TOKEN:
        print("BOT_TOKEN topilmadi!")
        return
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
