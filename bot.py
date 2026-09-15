import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import google.generativeai as genai

# ---- SOZLAMALAR (bularni Railway'da "Environment Variables" orqali kiritasiz) ----
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

logging.basicConfig(level=logging.INFO)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-flash-latest")

PROMPT_TEMPLATE = """Sen film tavsiya qiluvchi yordamchisan. Foydalanuvchi o'z kayfiyati va bo'sh vaqti haqida yozadi (masalan: "hafaman, 35 daqiqam bor").

Vazifang:
1. Foydalanuvchi matnidan KAYFIYAT (masalan: xafa, charchagan, quvnoq, zerikkan, motivatsiya kerak) va VAQT (necha daqiqa) ni aniqla.
2. Shu kayfiyat va vaqtga mos film yoki serial qismini tavsiya qil.
3. Vaqt chegarasiga qat'iy amal qil — foydalanuvchi aytgan daqiqadan uzun bo'lmasin.
4. Javobni FAQAT quyidagi formatda ber, boshqa hech narsa yozma:

🎬 Film: [nom]
⏱ Davomiyligi: [necha daqiqa]
💬 Nega mos: [1 gapda, nima uchun hozirgi kayfiyatga mos ekanini tushuntir]

Agar foydalanuvchi matnida kayfiyat yoki vaqt aniq bo'lmasa, taxmin qilib eng mos variantni tanla (savol berma, doim javob qaytar).

Foydalanuvchi matni: {user_message}
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Salom! 🎬\nQanday kayfiyatdasiz va necha daqiqalik film ko'rmoqchisiz?\n\n"
        "Masalan: \"Hafaman, 35 daqiqam bor\" deb yozing."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await update.message.chat.send_action("typing")

    try:
        prompt = PROMPT_TEMPLATE.format(user_message=user_text)
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await update.message.reply_text(
            "Kechirasiz, xatolik yuz berdi. Birozdan keyin qayta urinib ko'ring."
        )


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()
