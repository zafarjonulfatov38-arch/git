import os
import requests
import telebot
from telebot import types

# 1. BOT TOKENI
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN muhit o‘zgaruvchisi sozlanmagan")

bot = telebot.TeleBot(TOKEN)

# 2. PAPKALAR
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KITOBLAR_DIR = os.path.join(BASE_DIR, "kitoblar")

# 3. ASOSIY MENYU
ASOSIY = [
    "📚 Dars jadvali",
    "🌐 Tarjimon",
    "📢 Maktab yangiliklari",
    "📖 Kutubxona",
    "👥 Koordinatorlar",
]

# 4. SINF JADVALLARI
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

# 5. KITOBLAR
KITOBLAR = {
    "Asrga tatigulik kun": "ASRGA TATIGULIK KUN voqealari.pdf",
    "Gulliverning sayohatlari":
        "Gulliverning sayohatlari [@jahonadabiyoti_uz].pdf",
    "Molxona": "MOLXONA asari voqealari.pdf",
    "Temir xotin": "TEMIR XOTIN voqealari.pdf",
    "Tushda kechgan umrlar": "Tushda kechgan umrlar.pdf",
    "Zarbulmasal": "ZARBULMASAL obrazlari va voqealari.pdf",
}

# 6. KOORDINATORLAR
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


# 7. TUGMALAR YASASH
def menyu_yasash(tugmalar):
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True,
        row_width=1
    )
    for nom in tugmalar:
        keyboard.add(types.KeyboardButton(nom))
    return keyboard


def asosiy_menyuni_yubor(chat_id):
    bot.send_message(
        chat_id,
        "🏫 Maktab botiga xush kelibsiz!\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=menyu_yasash(ASOSIY)
    )


def orqaga_tugmasi(tugmalar):
    return tugmalar + ["⬅️ Bosh menyu"]


# 8. START
@bot.message_handler(commands=["start"])
def start(message):
    TARJIMA_REJIMI.discard(message.from_user.id)
    asosiy_menyuni_yubor(message.chat.id)


# 9. BOSH MENYU
@bot.message_handler(func=lambda m: m.text == "⬅️ Bosh menyu")
def bosh_menyu(message):
    TARJIMA_REJIMI.discard(message.from_user.id)
    asosiy_menyuni_yubor(message.chat.id)


# 10. DARS JADVALI
@bot.message_handler(func=lambda m: m.text == "📚 Dars jadvali")
def sinflarni_korsat(message):
    tugmalar = [
        "10-A sinf",
        "11-A sinf",
        "11-B sinf",
        "⬅️ Bosh menyu",
    ]
    bot.send_message(
        message.chat.id,
        "🎓 Sinfingizni tanlang:",
        reply_markup=menyu_yasash(tugmalar)
    )


@bot.message_handler(
    func=lambda m: m.text in JADVALLAR
)
def sinf_jadvali(message):
    sinf = message.text
    kunlar = JADVALLAR[sinf]

    matn = f"📚 {sinf.upper()} DARS JADVALI\n\n"
    for kun, fanlar in kunlar.items():
        matn += f"📅 {kun}\n"
        for raqam, fan in enumerate(fanlar, start=1):
            matn += f"{raqam}. {fan}\n"
        matn += "\n"

    bot.send_message(
        message.chat.id,
        matn,
        reply_markup=menyu_yasash([
            "📚 Dars jadvali",
            "⬅️ Bosh menyu",
        ])
    )


# 11. KUTUBXONA
@bot.message_handler(func=lambda m: m.text == "📖 Kutubxona")
def kutubxona(message):
    bot.send_message(
        message.chat.id,
        "📖 Kutubxonaga xush kelibsiz!",
        reply_markup=menyu_yasash([
            "📖 Kitob o‘qish",
            "⬅️ Bosh menyu",
        ])
    )


@bot.message_handler(func=lambda m: m.text == "📖 Kitob o‘qish")
def kitoblar_royxati(message):
    bot.send_message(
        message.chat.id,
        "📚 Kerakli kitobni tanlang:",
        reply_markup=menyu_yasash(
            list(KITOBLAR.keys()) + ["⬅️ Bosh menyu"]
        )
    )


@bot.message_handler(func=lambda m: m.text in KITOBLAR)
def kitob_yuborish(message):
    nom = message.text
    kerakli_fayl = KITOBLAR[nom]

    if not os.path.isdir(KITOBLAR_DIR):
        bot.send_message(
            message.chat.id,
            "❌ kitoblar papkasi topilmadi.\n"
            "Uni main.py bilan bir papkada saqlang."
        )
        return

    # Fayl nomini katta-kichik harflarni hisobga olmasdan qidirish
    mavjud_fayllar = os.listdir(KITOBLAR_DIR)
    mos_fayl = next(
        (
            f for f in mavjud_fayllar
            if f.casefold() == kerakli_fayl.casefold()
        ),
        None
    )

    if not mos_fayl:
        bot.send_message(
            message.chat.id,
            f"❌ «{kerakli_fayl}» fayli topilmadi.\n"
            "Fayl nomini va kitoblar papkasini tekshiring."
        )
        return

    fayl_yoli = os.path.join(KITOBLAR_DIR, mos_fayl)

    try:
        with open(fayl_yoli, "rb") as fayl:
            bot.send_document(
                message.chat.id,
                fayl,
                caption=f"📖 {nom}"
            )
    except Exception as xato:
        print("PDF yuborish xatosi:", repr(xato))
        bot.send_message(
            message.chat.id,
            "❌ Kitobni yuborishda xato yuz berdi."
        )


# 12. TARJIMON
@bot.message_handler(func=lambda m: m.text == "🌐 Tarjimon")
def tarjimon(message):
    TARJIMA_REJIMI.add(message.from_user.id)
    bot.send_message(
        message.chat.id,
        "🌐 Inglizcha matn yuboring, men uni o‘zbekchaga tarjima qilaman.\n\n"
        "Bosh menyuga qaytish uchun «⬅️ Bosh menyu» tugmasini bosing."
    )


def tarjima_qilish(matn):
    url = "https://api.mymemory.translated.net/get"
    javob = requests.get(
        url,
        params={
            "q": matn,
            "langpair": "en|uz",
        },
        timeout=20
    )
    javob.raise_for_status()
    malumot = javob.json()

    if malumot.get("responseStatus") != 200:
        raise ValueError("Tarjima xizmati javob bermadi")

    tarjima = malumot.get("responseData", {}).get(
        "translatedText", ""
    )
    if not tarjima:
        raise ValueError("Tarjima bo‘sh qaytdi")

    return tarjima


# 13. MAKTAB YANGILIKLARI
@bot.message_handler(
    func=lambda m: m.text == "📢 Maktab yangiliklari"
)
def yangiliklar(message):
    bot.send_message(
        message.chat.id,
        "📢 Maktab yangiliklari bo‘limi.\n\n"
        "Hozircha yangiliklar kiritilmagan.",
        reply_markup=menyu_yasash([
            "⬅️ Bosh menyu"
        ])
    )


# 14. KOORDINATORLAR
@bot.message_handler(
    func=lambda m: m.text == "👥 Koordinatorlar"
)
def koordinatorlar(message):
    bot.send_message(
        message.chat.id,
        KOORDINATORLAR,
        reply_markup=menyu_yasash([
            "⬅️ Bosh menyu"
        ])
    )


# 15. BOSHQA MATNLAR
@bot.message_handler(content_types=["text"])
def boshqa_matn(message):
    if message.from_user.id in TARJIMA_REJIMI:
        try:
            natija = tarjima_qilish(message.text)
            bot.send_message(
                message.chat.id,
                "🇺🇿 Tarjima:\n\n" + natija
            )
        except Exception as xato:
            print("Tarjima xatosi:", repr(xato))
            bot.send_message(
                message.chat.id,
                "❌ Tarjima amalga oshmadi. "
                "Birozdan keyin qayta urinib ko‘ring."
            )
    else:
        bot.send_message(
            message.chat.id,
            "Iltimos, menyudagi tugmalardan birini tanlang."
        )


# 16. BOTNI ISHGA TUSHIRISH

def run_web_server():
    import http.server
    import socketserver

    port = int(os.environ.get("PORT", 8000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    from threading import Thread

    Thread(target=run_web_server, daemon=True).start()
    print("Maktab boti ishga tushmoqda...")
    bot.infinity_polling()
