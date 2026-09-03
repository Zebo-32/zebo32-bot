import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Logging sozlamalari
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Boshlang'ich ombor ma'lumotlari (Excel jadvalingiz asosida)
inventory = {
    "Холодильник": {"umumiy": 38, "kirim": 0, "sotilgan": 0},
    "Газ плита": {"umumiy": 27, "kirim": 0, "sotilgan": 0},
    "Пол автомат": {"umumiy": 4, "kirim": 0, "sotilgan": 0},
    "Кондиционер": {"umumiy": 22, "kirim": 0, "sotilgan": 0},
    "Пылесос": {"umumiy": 17, "kirim": 0, "sotilgan": 0},
    "ТВ": {"umumiy": 34, "kirim": 0, "sotilgan": 0},
    "Дымоход": {"umumiy": 7, "kirim": 0, "sotilgan": 0},
    "Микроволновка": {"umumiy": 10, "kirim": 0, "sotilgan": 0},
    "Коллер": {"umumiy": 13, "kirim": 0, "sotilgan": 0},
    "Автомат": {"umumiy": 22, "kirim": 0, "sotilgan": 0},
    "Радиатор": {"umumiy": 2, "kirim": 0, "sotilgan": 0},
    "Морозильник": {"umumiy": 2, "kirim": 0, "sotilgan": 0},
    "Воздух очиститель": {"umumiy": 2, "kirim": 0, "sotilgan": 0},
    "Посуда мойка": {"umumiy": 1, "kirim": 0, "sotilgan": 0},
    "Утюг": {"umumiy": 0, "kirim": 0, "sotilgan": 0},
    "Аэрогриль": {"umumiy": 1, "kirim": 0, "sotilgan": 0},
    "Тостер": {"umumiy": 1, "kirim": 0, "sotilgan": 0},
    "Мясорубка": {"umumiy": 2, "kirim": 0, "sotilgan": 0},
}

# Conversation bosqichlari
SELECT_PRODUCT_ADD, AMOUNT_ADD, SELECT_PRODUCT_SUB, AMOUNT_SUB = range(4)

# Menyu tugmalari
MAIN_KEYBOARD = [
    ["📊 To'liq Hisobot", "🔴 Kam Qolganlar"],
    ["➕ Кирим (Qo'shish)", "➖ Сотилган (Airish)"],
    ["ℹ️ Bot Haqida"]
]
reply_markup = ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)

# /start buyrug'i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Xush kelibsiz! Omborni boshqarish uchun quyidagi tugmalardan birini tanlang:", reply_markup=reply_markup)

# To'liq Excel hisoboti ko'rinishidagi ma'lumot
async def full_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📋 **OMBOR HISOBOTI**\n\n"
    text += "Категория | Кирим | Сотилган | Қолдиқ | Ҳолати\n"
    text += "--------------------------------------------------\n"
    
    total_qoldiq = 0
    total_kirim = 0
    total_sotilgan = 0

    for item, data in inventory.items():
        qoldiq = data["umumiy"] + data["kirim"] - data["sotilgan"]
        holat = "🟢 Етарли" if qoldiq >= 3 else "🔴 Кам қолди"
        text += f"• **{item}**: Kirim: {data['kirim']} | Sotilgan: {data['sotilgan']} | **Qoldiq: {qoldiq} ta** ({holat})\n"
        
        total_qoldiq += qoldiq
        total_kirim += data["kirim"]
        total_sotilgan += data["sotilgan"]

    text += f"\n--------------------------------------------------\n"
    text += f"**ЖАМИ / УМУМИЙ:**\n"
    text += f"➕ Кирим: {total_kirim} | ➖ Сотилган: {total_sotilgan} | 📦 **Қолдиқ: {total_qoldiq} ta**"
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

# Kam qolgan mahsulotlar
async def low_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "🔴 **KAMLAGAN MAHSULOTLAR (3 tadan kam):**\n\n"
    found = False
    for item, data in inventory.items():
        qoldiq = data["umumiy"] + data["kirim"] - data["sotilgan"]
        if qoldiq < 3:
            text += f"• **{item}**: {qoldiq} ta qoldi\n"
            found = True
    if not found:
        text = "✅ Barcha mahsulotlar yetarli miqdorda!"
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

# Bot haqida
async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ Usbu bot ombordagi mahsulotlar kiritmasi (Кирим) va sotuvlarini (Сотилган) hisoblab borish uchun mo'ljallangan.", reply_markup=reply_markup)

# --- KIRIM QILISH (KIRIM) ---
async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = list(inventory.keys())
    keyboard = [[p] for p in products]
    keyboard.append(["Bekor qilish"])
    await update.message.reply_text("➕ Qaysi mahsulotga **Кирим** kiritmoqchisiz?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return SELECT_PRODUCT_ADD

async def select_product_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Bekor qilish":
        await update.message.reply_text("Bekor qilindi.", reply_markup=reply_markup)
        return ConversationHandler.END
    if text not in inventory:
        await update.message.reply_text("Iltimos, ro'yxatdagi mahsulotlardan birini tanlang.")
        return SELECT_PRODUCT_ADD
    
    context.user_data["selected_product"] = text
    await update.message.reply_text(f"Nechta **{text}** kirim qilindi? (Faqat son kiriting):")
    return AMOUNT_ADD

async def process_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(update.message.text)
        product = context.user_data["selected_product"]
        inventory[product]["kirim"] += amount
        
        qoldiq = inventory[product]["umumiy"] + inventory[product]["kirim"] - inventory[product]["sotilgan"]
        await update.message.reply_text(f"✅ **{product}** ga {amount} ta kirim qo'shildi!\nYangi qoldiq: **{qoldiq} ta**", reply_markup=reply_markup)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Iltimos, faqat musbat son kiriting!")
        return AMOUNT_ADD

# --- SOTILGAN (SOTUV) ---
async def start_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = list(inventory.keys())
    keyboard = [[p] for p in products]
    keyboard.append(["Bekor qilish"])
    await update.message.reply_text("➖ Qaysi mahsulot **Сотилган** (chiqim)?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return SELECT_PRODUCT_SUB

async def select_product_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Bekor qilish":
        await update.message.reply_text("Bekor qilindi.", reply_markup=reply_markup)
        return ConversationHandler.END
    if text not in inventory:
        await update.message.reply_text("Iltimos, ro'yxatdagi mahsulotlardan birini tanlang.")
        return SELECT_PRODUCT_SUB
    
    context.user_data["selected_product"] = text
    await update.message.reply_text(f"Nechta **{text}** sotildi? (Faqat son kiriting):")
    return AMOUNT_SUB

async def process_sub(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = int(update.message.text)
        product = context.user_data["selected_product"]
        inventory[product]["sotilgan"] += amount
        
        qoldiq = inventory[product]["umumiy"] + inventory[product]["kirim"] - inventory[product]["sotilgan"]
        await update.message.reply_text(f"✅ **{product}** dan {amount} ta sotuv yozildi!\nYangi qoldiq: **{qoldiq} ta**", reply_markup=reply_markup)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Iltimos, faqat musbat son kiriting!")
        return AMOUNT_SUB

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Amal bekor qilindi.", reply_markup=reply_markup)
    return ConversationHandler.END

# Asosiy dasturni ishga tushirish
if __name__ == '__main__':
    # O'zingizning Bot Tokeningizni shu yerga kiriting
    TOKEN = "8395782092:AAGIQQnpSUZOYx1karo0okCTptDDw2Qbo_I" 
    
    app = ApplicationBuilder().token(TOKEN).build()

    # Kirim conversation handler
    add_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r"^➕ Кирим \(Qo'shish\)$"), start_add)]
        states={
            SELECT_PRODUCT_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_product_add)],
            AMOUNT_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_add)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    # Sotuv conversation handler
    sub_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r"^➖ Сотилган \(Airish\)$"), start_sub)],
        states={
            SELECT_PRODUCT_SUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_product_sub)],
            AMOUNT_SUB: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_sub)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^📊 To'liq Hisobot$"), full_report))
    app.add_handler(MessageHandler(filters.Regex("^🔴 Kam Qolganlar$"), low_stock))
    app.add_handler(MessageHandler(filters.Regex("^ℹ️ Bot Haqida$"), about))
    app.add_handler(add_handler)
    app.add_handler(sub_handler)

    print("Bot ishga tushdi...")
    app.run_polling()
