import os
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import requests
import telebot
from telebot import types

# Logging is visible in Render's service logs.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure TELEGRAM_BOT_TOKEN in Render → Environment.
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment variable is not set")

bot = telebot.TeleBot(TOKEN)

# Folders
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KITOBLAR_DIR = os.path.join(BASE_DIR, "kitoblar")

# Main menu
ASOSIY = [
    "📚 Dars jadvali",
    "🌐 Tarjimon",
    "📢 Maktab yangiliklari",
    "📖 Kutubxona",
    "👥 Koordinatorlar",
]

# Class schedules
JADVALLAR = {
    "10-A sinf": {
        "Dushanba": [
            "Kelajak soati", "Ona tili", "Ona tili",
            "Algebra", "Adabiyot", "Informatika"
        ],
        "Seshanba": [
            "O‘zbek tarixi", "Informatika", "Algebra",
            "Ingliz tili", "CHQBT", "Jismoniy tarbiya"
        ],
        "Chorshanba": [
            "Ona tili", "Ingliz tili", "Algebra",
            "Rus tili", "Ona tili"
        ],
        "Payshanba": [
            "CHQBT", "Jahon tarixi", "Jismoniy tarbiya",
            "Tarbiya", "Rus tili"
        ],
        "Juma": [
            "Algebra", "Ona tili", "Algebra",
            "Adabiyot", "Algebra"
        ],
        "Shanba": [
            "Ona tili", "Adabiyot", "Geometriya",
            "Geometriya", "Geometriya"
        ],
    },
    "11-A sinf": {
        "Dushanba": [
            "Kelajak soati", "Algebra", "Algebra",
            "Ingliz tili", "Rus tili", "Adabiyot"
        ],
        "Seshanba": [
            "Algebra", "Jistar", "O‘zbekiston tarixi",
            "Algebra", "Informatika", "Algebra"
        ],
        "Chorshanba": [
            "Ingliz tili", "Jahon tarixi", "Algebra",
            "Ingliz tili", "CHQBT"
        ],
        "Payshanba": [
            "Ingliz tili", "CHQBT", "Ona tili",
            "Tarbiya", "Jistar"
        ],
        "Juma": [
            "Geometriya", "Informatika", "Algebra",
            "Geometriya", "Ona tili"
        ],
        "Shanba": [
            "Ingliz tili", "Geometriya", "Geometriya",
            "Adabiyot", "Rus tili"
        ],
    },
    "11-B sinf": {
        "Dushanba": [
            "Kelajak soati", "Rus tili", "Astronomiya",
            "Fizika", "Fransuz tili", "Algebra"
        ],
        "Seshanba": [
            "CHQBT", "DHA", "Fizika",
            "O‘zbekiston tarixi", "Algebra", "Ingliz tili"
        ],
        "Chorshanba": [
            "Adabiyot", "Fransuz tili", "Ingliz tili",
            "Jahon tarixi", "Algebra"
        ],
        "Payshanba": [
            "Fransuz tili", "Kimyo", "Adabiyot",
            "CHQBT", "Ona tili"
        ],
        "Juma": [
            "Biologiya", "Kimyo", "Ona tili",
            "Tadbirkorlik", "Geometriya"
        ],
    },
}

# PDF filenames in the kitoblar folder
KITOBLAR = {
    "Asrga tatigulik kun": "ASRGA TATIGULIK KUN voqealari.pdf",
    "Gulliverning sayohatlari":
        "Gulliverning sayohatlari [@jahonadabiyoti_uz].pdf",
    "Molxona": "MOLXONA asari voqealari.pdf",
    "Temir xotin": "TEMIR XOTIN voqealari.pdf",
    "Tushda kechgan umrlar": "Tushda kechgan umrlar.pdf",
    "Zarbulmasal": "ZARBULMASAL obrazlari va voqealari.pdf",
}

KOORDINATORLAR = (
    "👥 MAKTAB KOORDINATORLARI\n\n"
    "🌿 Ekologiya — Muysinova Zilola\n"
    "🎬 Media — Abdusoliyev Sardor\n"
    "⚽ Sport — Shokirov Shohruh\n"
    "📚 Ta’lim — Abduhakimova Lobar\n"
    "💻 IT — Nematov Lochinbek\n"
    "🎭 Madaniyat — ma’lumot kiritilmagan\n"
    "⚖️ Ombudsman — Najomova Madina"
)

TARJIMA_REJIMI = set()


def menyu_yasash(tugmalar):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    for nom in tugmalar:
        keyboard.add(types.KeyboardButton(nom))
    return keyboard


def asosiy_menyuni_yubor(chat_id):
    bot.send_message(
        chat_id,
        "🏫 Maktab botiga xush kelibsiz!\n\nKerakli bo‘limni tanlang:",
        reply_markup=menyu_yasash(ASOSIY),
    )


@bot.message_handler(commands=["start"])
def start(message):
    TARJIMA_REJIMI.discard(message.from_user.id)
    asosiy_menyuni_yubor(message.chat.id)


@bot.message_handler(func=lambda m: m.text == "⬅️ Bosh menyu")
def bosh_menyu(message):
    TARJIMA_REJIMI.discard(message.from_user.id)
    asosiy_menyuni_yubor(message.chat.id)


@bot.message_handler(func=lambda m: m.text == "📚 Dars jadvali")
def sinflarni_korsat(message):
    bot.send_message(
        message.chat.id,
        "🎓 Sinfingizni tanlang:",
        reply_markup=menyu_yasash([
            "10-A sinf", "11-A sinf", "11-B sinf", "⬅️ Bosh menyu"
        ]),
    )


@bot.message_handler(func=lambda m: m.text in JADVALLAR)
def sinf_jadvali(message):
    sinf = message.text
    matn = f"📚 {sinf.upper()} DARS JADVALI\n\n"
    for kun, fanlar in JADVALLAR[sinf].items():
        matn += f"📅 {kun}\n"
        for raqam, fan in enumerate(fanlar, start=1):
            matn += f"{raqam}. {fan}\n"
        matn += "\n"
    bot.send_message(
        message.chat.id,
        matn,
        reply_markup=menyu_yasash(["📚 Dars jadvali", "⬅️ Bosh menyu"]),
    )


@bot.message_handler(func=lambda m: m.text == "📖 Kutubxona")
def kutubxona(message):
    bot.send_message(
        message.chat.id,
        "📖 Kutubxonaga xush kelibsiz!",
        reply_markup=menyu_yasash(["📖 Kitob o‘qish", "⬅️ Bosh menyu"]),
    )


@bot.message_handler(func=lambda m: m.text == "📖 Kitob o‘qish")
def kitoblar_royxati(message):
    bot.send_message(
        message.chat.id,
        "📚 Kerakli kitobni tanlang:",
        reply_markup=menyu_yasash(list(KITOBLAR) + ["⬅️ Bosh menyu"]),
    )


@bot.message_handler(func=lambda m: m.text in KITOBLAR)
def kitob_yuborish(message):
    nom = message.text
    kerakli_fayl = KITOBLAR[nom]

    if not os.path.isdir(KITOBLAR_DIR):
        bot.send_message(message.chat.id, "❌ kitoblar papkasi topilmadi.")
        return

    mos_fayl = next(
        (f for f in os.listdir(KITOBLAR_DIR)
         if f.casefold() == kerakli_fayl.casefold()),
        None,
    )
    if not mos_fayl:
        bot.send_message(message.chat.id, f"❌ «{kerakli_fayl}» fayli topilmadi.")
        return

    try:
        with open(os.path.join(KITOBLAR_DIR, mos_fayl), "rb") as fayl:
            bot.send_document(message.chat.id, fayl, caption=f"📖 {nom}")
    except (OSError, telebot.apihelper.ApiTelegramException) as error:
        logger.exception("PDF yuborishda xato")
        bot.send_message(message.chat.id, "❌ Kitobni yuborishda xato yuz berdi.")


@bot.message_handler(func=lambda m: m.text == "🌐 Tarjimon")
def tarjimon(message):
    TARJIMA_REJIMI.add(message.from_user.id)
    bot.send_message(
        message.chat.id,
        "🌐 Inglizcha matn yuboring, men uni o‘zbekchaga tarjima qilaman.\n\n"
        "Bosh menyuga qaytish uchun «⬅️ Bosh menyu» tugmasini bosing.",
    )


def tarjima_qilish(matn):
    javob = requests.get(
        "https://api.mymemory.translated.net/get",
        params={"q": matn, "langpair": "en|uz"},
        timeout=20,
    )
    javob.raise_for_status()
    malumot = javob.json()
    if malumot.get("responseStatus") != 200:
        raise ValueError("Tarjima xizmati javob bermadi")
    tarjima = malumot.get("responseData", {}).get("translatedText", "")
    if not tarjima:
        raise ValueError("Tarjima bo‘sh qaytdi")
    return tarjima


@bot.message_handler(func=lambda m: m.text == "📢 Maktab yangiliklari")
def yangiliklar(message):
    bot.send_message(
        message.chat.id,
        "📢 Maktab yangiliklari bo‘limi.\n\nHozircha yangiliklar kiritilmagan.",
        reply_markup=menyu_yasash(["⬅️ Bosh menyu"]),
    )


@bot.message_handler(func=lambda m: m.text == "👥 Koordinatorlar")
def koordinatorlar(message):
    bot.send_message(
        message.chat.id,
        KOORDINATORLAR,
        reply_markup=menyu_yasash(["⬅️ Bosh menyu"]),
    )


@bot.message_handler(content_types=["text"])
def boshqa_matn(message):
    if message.from_user.id in TARJIMA_REJIMI:
        try:
            natija = tarjima_qilish(message.text)
            bot.send_message(message.chat.id, "🇺🇿 Tarjima:\n\n" + natija)
        except (requests.RequestException, ValueError, KeyError) as error:
            logger.exception("Tarjima xatosi")
            bot.send_message(
                message.chat.id,
                "❌ Tarjima amalga oshmadi. Birozdan keyin qayta urinib ko‘ring.",
            )
    else:
        bot.send_message(
            message.chat.id,
            "Iltimos, menyudagi tugmalardan birini tanlang.",
        )


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/health"):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, format, *args):
        logger.info("HTTP: " + format, *args)


def run_web_server():
    port = int(os.environ.get("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthCheckHandler)
    logger.info("Health-check server listening on port %s", port)
    server.serve_forever()


if __name__ == "__main__":
    Thread(target=run_web_server, daemon=True).start()
    logger.info("Maktab boti ishga tushmoqda...")
    bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=30)
