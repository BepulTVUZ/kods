import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import pytz

# Bot token va admin ID lar
BOT_TOKEN = '8386033333:AAE_3l9yPxn8IHD-2IUWGdw3uKw-vwCY1V0'
ADMIN_IDS = [8406325971, 6246610843]  # Ikkita admin ID

# Bot va dispatcher yaratish
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Til tanlash tugmalari
language_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🇬🇧 English")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Tillar uchun matnlar
TEXTS = {
    'ru': {
        'start': "Выберите язык:",
        'after_lang': "Отправьте сообщение администратору. Мы постараемся ответить в течение 24-48 часов.",
        'message_sent': "Сообщение отправлено. Спасибо за вопрос!",
        'user_info': "📩 Новое сообщение от пользователя:\n\n",
        'admin_reply': "👨‍💻 Ответ администратора:\n",
        'command_for_admin': "Эта команда доступна только администраторам.",
        'admin_only': "Только для администраторов"
    },
    'en': {
        'start': "Choose language:",
        'after_lang': "Send a message to the admin. We will try to reply within 24-48 hours.",
        'message_sent': "Message sent. Thank you for your question!",
        'user_info': "📩 New message from user:\n\n",
        'admin_reply': "👨‍💻 Admin's reply:\n",
        'command_for_admin': "This command is for administrators only.",
        'admin_only': "For administrators only"
    }
}

# FSM holatlari
class UserState(StatesGroup):
    choosing_language = State()
    waiting_for_message = State()

# Foydalanuvchi ma'lumotlarini saqlash uchun
active_users = {}

# ADMIN FILTER
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# /start komandasi
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(UserState.choosing_language)
    await message.answer(
        "Выберите язык / Choose language:",
        reply_markup=language_keyboard
    )

# Til tanlash
@dp.message(UserState.choosing_language)
async def process_language(message: Message, state: FSMContext):
    lang = None
    if message.text == "🇷🇺 Русский":
        lang = 'ru'
    elif message.text == "🇬🇧 English":
        lang = 'en'
    
    if lang:
        await state.update_data(language=lang)
        await state.set_state(UserState.waiting_for_message)
        await message.answer(
            TEXTS[lang]['after_lang'],
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer("Пожалуйста, выберите язык из предложенных / Please choose a language from the options")

# Foydalanuvchi xabarini qabul qilish (admin buyruqlaridan boshqa hamma narsa)
@dp.message(UserState.waiting_for_message)
async def process_user_message(message: Message, state: FSMContext):
    # Agar admin bo'lsa va /send buyrug'i bo'lsa, uni alohida qayta ishlash
    if is_admin(message.from_user.id) and message.text and message.text.startswith('/send'):
        # Admin /send buyrug'ini ishlatmoqchi, lekin UserState da
        # Bu holatda state ni tozalaymiz va admin rejimiga o'tamiz
        await state.clear()
        await send_direct_message(message)
        return
    
    # Oddiy foydalanuvchi xabari
    user_data = await state.get_data()
    lang = user_data.get('language', 'en')
    
    # Foydalanuvchi ma'lumotlari
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else "Нет username / No username"
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()
    
    # Vaqtni UTC+5 da olish
    utc_plus_5 = pytz.timezone('Asia/Tashkent')  # UTC+5
    current_time = datetime.now(utc_plus_5).strftime("%Y-%m-%d %H:%M:%S")
    
    # Admin uchun xabar tayyorlash
    admin_message = (
        f"{TEXTS[lang]['user_info']}"
        f"👤 User ID: {user_id}\n"
        f"📛 Имя/Name: {full_name}\n"
        f"🔗 Username: {username}\n"
        f"🕐 Время отправки/Sent time (UTC+5): {current_time}\n"
        f"🌐 Язык/Language: {lang}\n"
        f"────────────────────\n"
        f"📝 Сообщение/Message:\n{message.text}"
    )
    
    # Foydalanuvchi ma'lumotlarini saqlash (admin javobi uchun)
    active_users[user_id] = lang
    
    # Barcha adminlarga xabar yuborish
    success_count = 0
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_message)
            success_count += 1
        except Exception as e:
            logging.error(f"Admin {admin_id} ga xabar yuborishda xatolik: {e}")
    
    # Foydalanuvchiga tasdiqlash
    if success_count > 0:
        await message.answer(TEXTS[lang]['message_sent'])
    else:
        error_text = "Xabar yuborishda xatolik yuz berdi" if lang == 'ru' else "Error sending message"
        await message.answer(error_text)

# Admin javobini foydalanuvchiga yuborish (REPLY usuli)
@dp.message(F.from_user.id.in_(ADMIN_IDS), F.reply_to_message)
async def admin_reply(message: Message):
    try:
        # Admin xabaridan foydalanuvchi ID sini ajratib olish
        original_text = message.reply_to_message.text
        lines = original_text.split('\n')
        user_id = None
        
        # User ID ni qidirish
        for line in lines:
            if "User ID:" in line:
                user_id = int(line.split(":")[1].strip())
                break
        
        if user_id:
            # Tilni aniqlash
            lang = active_users.get(user_id, 'en')
            if lang not in ['ru', 'en']:
                # Xabardan tilni aniqlash
                for line in lines:
                    if "Язык/Language:" in line:
                        lang_part = line.split(":")[1].strip()
                        if 'ru' in lang_part.lower():
                            lang = 'ru'
                        else:
                            lang = 'en'
                        break
            
            # Foydalanuvchiga javob yuborish
            await bot.send_message(user_id, f"{TEXTS[lang]['admin_reply']}{message.text}")
            
            # Admin ga tasdiqlash
            await message.answer("✅ Ответ отправлен пользователю.")
            
            # O'chirish kerak bo'lsa active_users dan
            if user_id in active_users:
                del active_users[user_id]
                
        else:
            await message.answer("❌ ID пользователя не найден.")
    
    except Exception as e:
        logging.error(f"Ответ администратора (reply): {e}")
        await message.answer("❌ Ошибка при отправке ответа.")

# Admin to'g'ridan-to'g'ri foydalanuvchiga yuborishi uchun
@dp.message(Command("send"))
async def send_direct_command(message: Message):
    """To'g'ridan-to'g'ri foydalanuvchiga xabar yuborish (/send buyrug'i)"""
    
    # Faqat adminlar uchun
    if not is_admin(message.from_user.id):
        # Foydalanuvchi uchun tilni aniqlash
        lang = 'en'
        if message.from_user.language_code and 'ru' in message.from_user.language_code:
            lang = 'ru'
        await message.answer(TEXTS[lang]['command_for_admin'])
        return
    
    try:
        # Format: /send <user_id> <xabar>
        parts = message.text.split(' ', 2)
        if len(parts) < 3:
            await message.answer("❌ Формат: /send <user_id> <сообщение>")
            return
        
        user_id = int(parts[1])
        text_message = parts[2]
        
        # Tilni aniqlash (default rus)
        lang = 'ru'
        
        await bot.send_message(user_id, f"{TEXTS[lang]['admin_reply']}{text_message}")
        await message.answer(f"✅ Сообщение отправлено пользователю {user_id}")
    
    except ValueError:
        await message.answer("❌ Неверный ID пользователя")
    except Exception as e:
        logging.error(f"Прямое сообщение: {e}")
        await message.answer("❌ Ошибка при отправке сообщения")

# Adminlar uchun maxsus handler
@dp.message(F.from_user.id.in_(ADMIN_IDS))
async def handle_admin_direct(message: Message):
    """Adminning to'g'ridan-to'g'ri xabarlari"""
    
    # Agar bu reply bo'lsa, reply funksiyasi ishlaydi
    if message.reply_to_message:
        return
    
    # Agar bu /send buyrug'i bo'lsa
    if message.text and message.text.startswith('/send'):
        await send_direct_command(message)
        return
    
    # Boshqa buyruqlar
    if message.text == "/help":
        await admin_help(message)
    elif message.text == "/stats":
        await show_stats(message)
    else:
        # Admin oddiy xabar yuborgan
        await message.answer(
            "ℹ️ Доступные команды:\n"
            "/help - помощь\n"
            "/stats - статистика\n"
            "/send <id> <msg> - отправить сообщение\n\n"
            "Чтобы ответить пользователю, используйте Reply на его сообщение."
        )

# Adminlarga yordamchi buyruq
async def admin_help(message: Message):
    help_text = (
        "📋 Доступные команды для администратора:\n\n"
        "**1. Ответить пользователю:**\n"
        "   • Нажмите **Reply** на сообщение от бота\n"
        "   • Напишите ответ\n"
        "   • Отправьте - ответ автоматически пойдет пользователю\n\n"
        "**2. Прямая отправка:**\n"
        "   • /send <user_id> <сообщение>\n"
        "   • Пример: /send 12345678 Привет! Как дела?\n\n"
        "**3. Другие команды:**\n"
        "   • /help - эта справка\n"
        "   • /stats - статистика\n\n"
        "**Важно:** Ответ отправляется на языке, который выбрал пользователь."
    )
    await message.answer(help_text)

# Adminlarga statistikani ko'rsatish
async def show_stats(message: Message):
    stats_text = (
        f"📊 Статистика:\n"
        f"• Активные пользователи: {len(active_users)}\n"
        f"• Администраторов: {len(ADMIN_IDS)}\n"
        f"• Поддерживаемые языки: 2 (ru, en)"
    )
    await message.answer(stats_text)

# Asosiy funksiya
async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logging.info("🚀 Бот запущен!")
    logging.info(f"👥 Администраторы: {ADMIN_IDS}")
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())