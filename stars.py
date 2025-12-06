
import logging
import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton, Message
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

API_TOKEN = "8295313674:AAHpAN_PrRlI3U2VUzTqxZr0l1xad8b2Veo"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Foydalanuvchi ma'lumotlari saqlash uchun
user_data = {}
user_stars_balance = {}  # Foydalanuvchilarning stars balansi (simulyatsiya)

# Tillar lug'atlari
LANGUAGES = {
    "🇺🇿 UZ": {
        "name": "O'zbekcha",
        "buttons": {
            "start": "👇 Valyutani tanlang va almashtiring:",
            "choose_currency": "Iltimos nechta telegram yulduzcha almashtirmoqchisiz?\n"
                              "Eng kam almashtirish 130 ta telegram yulduzcha.\nMenga yozing...👇",
            "min_error": "❌ Eng kam almashtirish 130 ta telegram yulduzcha.\nQaytadan son kiriting...👇",
            "number_only": "❌ Iltimos faqat son kiriting...👇",
            "payment_success": "✅ To'lov qabul qilindi!\n\n💳 Iltimos karta raqamingizni yuboring (faqat raqamlar):",
            "card_request": "💳 Iltimos karta raqamingizni yuboring (faqat raqamlar):",
            "card_success": "✅ Ariza qabul qilindi! Sizning kartangizga 24 soat ichida hisobingizga tushadi.",
            "invalid_card": "❌ Noto'g'ri karta raqami. Faqat raqamlardan iborat bo'lishi kerak.",
            "insufficient_balance": "❌ Sizda yetarli yulduzcha mavjud emas. Hozirda sizda {} yulduzcha bor.",
            "your_balance": "💰 Sizning Telegram Stars balansingiz: {} ⭐",
            "currency_buttons": [
                "⭐️Stars ➡️ 🇷🇺 Rubl",
                "⭐️Stars ➡️ 🇰🇿 Tenge",
                "⭐️Stars ➡️ 🇺🇿 So'm",
                "⭐️Stars ➡️ 🇰🇬 Som",
                "⭐️Stars ➡️ 🇹🇯 Somoniy",
                "⭐️Stars ➡️ Visa card",
                "⭐️Stars ➡️ Master card"
            ]
        }
    },
    "🇷🇺 RU": {
        "name": "Русский",
        "buttons": {
            "start": "👇 Выберите валюту и обменяйте:",
            "choose_currency": "Пожалуйста, сколько телеграм звездочек вы хотите обменять?\n"
                              "Минимальный обмен - 130 телеграм звездочек.\nНапишите мне...👇",
            "min_error": "❌ Минимальный обмен - 130 телеграм звездочек.\nВведите число еще раз...👇",
            "number_only": "❌ Пожалуйста, вводите только цифры...👇",
            "payment_success": "✅ Платеж принят!\n\n💳 Пожалуйста, отправьте номер вашей карты (только цифры):",
            "card_request": "💳 Пожалуйста, отправьте номер вашей карты (только цифры):",
            "card_success": "✅ Заявка принята! На вашу карту средства поступят в течение 24 часов.",
            "invalid_card": "❌ Неправильный номер карты. Должен содержать только цифры.",
            "insufficient_balance": "❌ У вас недостаточно звездочек. В настоящее время у вас есть {} звездочек.",
            "your_balance": "💰 Ваш баланс Telegram Stars: {} ⭐",
            "currency_buttons": [
                "⭐️Stars ➡️ 🇷🇺 Рубль",
                "⭐️Stars ➡️ 🇰🇿 Тенге",
                "⭐️Stars ➡️ 🇺🇿 Сум",
                "⭐️Stars ➡️ 🇰🇬 Сом",
                "⭐️Stars ➡️ 🇹🇯 Сомони",
                "⭐️Stars ➡️ Visa card",
                "⭐️Stars ➡️ Master card"
            ]
        }
    },
    "🇺🇸 EN": {
        "name": "English",
        "buttons": {
            "start": "👇 Select currency and exchange:",
            "choose_currency": "Please how many telegram stars do you want to exchange?\n"
                              "Minimum exchange is 130 telegram stars.\nWrite to me...👇",
            "min_error": "❌ Minimum exchange is 130 telegram stars.\nEnter number again...👇",
            "number_only": "❌ Please enter numbers only...👇",
            "payment_success": "✅ Payment received!\n\n💳 Please send your card number (digits only):",
            "card_request": "💳 Please send your card number (digits only):",
            "card_success": "✅ Application accepted! Funds will be credited to your card within 24 hours.",
            "invalid_card": "❌ Invalid card number. Must contain only digits.",
            "insufficient_balance": "❌ You don't have enough stars. Currently you have {} stars.",
            "your_balance": "💰 Your Telegram Stars balance: {} ⭐",
            "currency_buttons": [
                "⭐️Stars ➡️ 🇷🇺 Ruble",
                "⭐️Stars ➡️ 🇰🇿 Tenge",
                "⭐️Stars ➡️ 🇺🇿 Sum",
                "⭐️Stars ➡️ 🇰🇬 Som",
                "⭐️Stars ➡️ 🇹🇯 Somoni",
                "⭐️Stars ➡️ Visa card",
                "⭐️Stars ➡️ Master card"
            ]
        }
    },
    "🇰🇬 KG": {
        "name": "Кыргызча",
        "buttons": {
            "start": "👇 Валютаны тандап, алмаштырыңыз:",
            "choose_currency": "Сураныч, канча телеграм жылдыз алмаштыргыңыз келет?\n"
                              "Эң аз алмаштыруу 130 телеграм жылдыз.\nМага жазыңыз...👇",
            "min_error": "❌ Эң аз алмаштыруу 130 телеграм жылдыз.\nКайрадан сан жазыңыз...👇",
            "number_only": "❌ Сураныч, гана сан жазыңыз...👇",
            "payment_success": "✅ Төлөм кабыл алынды!\n\n💳 Сураныч, карта номериңизди жөнөтүңүз (сандар гана):",
            "card_request": "💳 Сураныч, карта номериңизди жөнөтүңүз (сандар гана):",
            "card_success": "✅ Өтүнүч кабыл алынды! Картаңызга акча 24 саат ичинде түшөт.",
            "invalid_card": "❌ Туура эмес карта номери. Сандар гана болушу керек.",
            "insufficient_balance": "❌ Сизде жетиштүү жылдыз жок. Азыр сизде {} жылдыз бар.",
            "your_balance": "💰 Сиздин Telegram Stars балансыңыз: {} ⭐",
            "currency_buttons": [
                "⭐️Stars ➡️ 🇷🇺 Рубль",
                "⭐️Stars ➡️ 🇰🇿 Тенге",
                "⭐️Stars ➡️ 🇺🇿 Сум",
                "⭐️Stars ➡️ 🇰🇬 Сом",
                "⭐️Stars ➡️ 🇹🇯 Сомони",
                "⭐️Stars ➡️ Visa card",
                "⭐️Stars ➡️ Master card"
            ]
        }
    },
    "🇹🇯 TJ": {
        "name": "Тоҷикӣ",
        "buttons": {
            "start": "👇 Асъорро интихоб кунед ва иваз кунед:",
            "choose_currency": "Лутфан, чанд ситораи телеграм иваз мекунед?\n"
                              "Ҳадди ақал иваз 130 ситораи телеграм.\nБа ман нависед...👇",
            "min_error": "❌ Ҳадди ақал иваз 130 ситораи телеграм.\nБори дигар рақам нависед...👇",
            "number_only": "❌ Лутфан, фақат рақам нависед...👇",
            "payment_success": "✅ Пардохт қабул шуд!\n\n💳 Лутфан, рақами корти худро фиристед (танҳо рақамҳо):",
            "card_request": "💳 Лутфан, рақами корти худро фиристед (танҳо рақамҳо):",
            "card_success": "✅ Дархост қабул шуд! Ба корти шумо дар давоми 24 соат пуҳо хоҳад расид.",
            "invalid_card": "❌ Рақами корти нодуруст. Бояд танҳо рақамҳо дошта бошад.",
            "insufficient_balance": "❌ Шумо ситораҳои кофӣ надоред. Дар айни замон шумо {} ситора доред.",
            "your_balance": "💰 Баланси Telegram Stars-и шумо: {} ⭐",
            "currency_buttons": [
                "⭐️Stars ➡️ 🇷🇺 Рубл",
                "⭐️Stars ➡️ 🇰🇿 Тенге",
                "⭐️Stars ➡️ 🇺🇿 Сум",
                "⭐️Stars ➡️ 🇰🇬 Сом",
                "⭐️Stars ➡️ 🇹🇯 Сомонӣ",
                "⭐️Stars ➡️ Visa card",
                "⭐️Stars ➡️ Master card"
            ]
        }
    },
    "🇰🇿 KZ": {
        "name": "Қазақша",
        "buttons": {
            "start": "👇 Валютаны таңдап, алмастырыңыз:",
            "choose_currency": "Өтінеміз, қанша телеграм жұлдыз алмастырғыңыз келеді?\n"
                              "Ең аз алмастыру 130 телеграм жұлдыз.\nМаған жазыңыз...👇",
            "min_error": "❌ Ең аз алмастыру 130 телеграм жұлдыз.\nҚайтадан сан жазыңыз...👇",
            "number_only": "❌ Өтінеміз, тек сан жазыңыз...👇",
            "payment_success": "✅ Төлем қабылданды!\n\n💳 Өтінеміз, карта нөміріңізді жіберіңіз (тек сандар):",
            "card_request": "💳 Өтінеміз, карта нөміріңізді жіберіңіз (тек сандар):",
            "card_success": "✅ Өтініш қабылданды! Картаңызға 24 сағат ішінде ақша түседі.",
            "invalid_card": "❌ Қате карта нөмірі. Тек сандардан тұруы керек.",
            "insufficient_balance": "❌ Сізде жеткілікті жұлдыз жоқ. Қазір сізде {} жұлдыз бар.",
            "your_balance": "💰 Сіздің Telegram Stars балансыңыз: {} ⭐",
            "currency_buttons": [
                "⭐️Stars ➡️ 🇷🇺 Рубль",
                "⭐️Stars ➡️ 🇰🇿 Теңге",
                "⭐️Stars ➡️ 🇺🇿 Сум",
                "⭐️Stars ➡️ 🇰🇬 Сом",
                "⭐️Stars ➡️ 🇹🇯 Сомони",
                "⭐️Stars ➡️ Visa card",
                "⭐️Stars ➡️ Master card"
            ]
        }
    }
}

# Til tanlash tugmasi yaratish
def language_keyboard():
    builder = ReplyKeyboardBuilder()
    for lang_code in LANGUAGES.keys():
        builder.add(KeyboardButton(text=lang_code))
    builder.adjust(3, 3)  # 3 ta qator, har birida 3 ta tugma
    return builder.as_markup(resize_keyboard=True)

# Valyuta tugmalarini yaratish
def currency_keyboard(language):
    builder = ReplyKeyboardBuilder()
    for button_text in LANGUAGES[language]["buttons"]["currency_buttons"]:
        builder.add(KeyboardButton(text=button_text))
    builder.adjust(1)  # Har bir tugma alohida qatorda
    return builder.as_markup(resize_keyboard=True)

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Tilni tanlang / Выберите язык / Select language:", 
                         reply_markup=language_keyboard())

@dp.message(F.text.in_(LANGUAGES.keys()))
async def set_language(message: types.Message):
    user_id = message.from_user.id
    selected_language = message.text
    
    # Foydalanuvchi tilini saqlash
    user_data[user_id] = {
        "language": selected_language,
        "step": "currency"
    }
    
    # Boshlang'ich balansni o'rnatish (simulyatsiya)
    if user_id not in user_stars_balance:
        user_stars_balance[user_id] = random.randint(100, 5000)
    
    lang_text = LANGUAGES[selected_language]["buttons"]["start"]
    await message.answer(lang_text, reply_markup=currency_keyboard(selected_language))

# Valyuta tanlash
@dp.message(F.text.startswith("⭐️Stars"))
async def choose_currency(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in user_data:
        await message.answer("Iltimos, avval tilni tanlang / Пожалуйста, сначала выберите язык / Please select language first:", 
                           reply_markup=language_keyboard())
        return
    
    user_data[user_id]["step"] = "amount"
    selected_language = user_data[user_id]["language"]
    lang_text = LANGUAGES[selected_language]["buttons"]["choose_currency"]
    await message.answer(lang_text)

# --- Agar foydalanuvchi son kiritsa ---
@dp.message(F.text.regexp(r"^\d+$"))
async def process_amount(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in user_data:
        await message.answer("Iltimos, avval tilni tanlang / Пожалуйста, сначала выберите язык / Please select language first:", 
                           reply_markup=language_keyboard())
        return
    
    # To'lov qilinganidan keyin karta raqami so'rash uchun tekshirish
    if user_data[user_id].get("step") == "card_number":
        # Karta raqamini tekshirish
        card_number = message.text
        
        # Karta raqami tekshiruvi (faqat raqamlar va minimal uzunlik)
        if not card_number.isdigit() or len(card_number) < 12 or len(card_number) > 19:
            selected_language = user_data[user_id]["language"]
            error_text = LANGUAGES[selected_language]["buttons"]["invalid_card"]
            await message.answer(error_text)
            return
        
        # Karta raqami qabul qilindi
        selected_language = user_data[user_id]["language"]
        success_text = LANGUAGES[selected_language]["buttons"]["card_success"]
        
        # Karta raqamini saqlash (agar kerak bo'lsa)
        user_data[user_id]["card_number"] = card_number
        
        # Foydalanuvchi bosqichini "currency" ga o'zgartirish
        user_data[user_id]["step"] = "currency"
        
        # Valyuta tugmalarini qayta ko'rsatish
        await message.answer(success_text, reply_markup=currency_keyboard(selected_language))
        return
    
    # Agar bosqich "amount" bo'lsa (yulduzcha miqdorini kiritish)
    if user_data[user_id].get("step") == "amount":
        selected_language = user_data[user_id]["language"]
        amount = int(message.text)
        
        # Foydalanuvchining balansini tekshirish (simulyatsiya)
        user_balance = user_stars_balance.get(user_id, 0)
        
        if amount < 130:
            error_text = LANGUAGES[selected_language]["buttons"]["min_error"]
            await message.answer(error_text)
        elif amount > user_balance:
            # Agar foydalanuvchi balansidan ko'p yulduzcha kiritib yuborsa
            insufficient_text = LANGUAGES[selected_language]["buttons"]["insufficient_balance"].format(user_balance)
            balance_text = LANGUAGES[selected_language]["buttons"]["your_balance"].format(user_balance)
            
            await message.answer(insufficient_text)
            await message.answer(balance_text)
            
            # Valyuta tugmalarini qayta ko'rsatish
            await message.answer(LANGUAGES[selected_language]["buttons"]["start"], 
                                reply_markup=currency_keyboard(selected_language))
            user_data[user_id]["step"] = "currency"
        else:
            # Invoice yaratish
            prices = [LabeledPrice(label="Telegram Stars to'lov", amount=amount)]
            
            try:
                await bot.send_invoice(
                    chat_id=message.chat.id,
                    title="Telegram Stars to'lov",
                    description=f"{amount} ta yulduzcha to'lov",
                    payload="stars_payment",
                    provider_token="",  # bu yerga to'lov provider token qo'yiladi
                    currency="XTR",     # Telegram Stars valyutasi
                    prices=prices,
                    start_parameter="stars-payment"
                )
            except Exception as e:
                logging.error(f"Invoice yaratishda xato: {e}")
                await message.answer("❌ To'lov tizimida xatolik. Iltimos, keyinroq urinib ko'ring.")
                
                # Valyuta tugmalarini qayta ko'rsatish
                await message.answer(LANGUAGES[selected_language]["buttons"]["start"], 
                                    reply_markup=currency_keyboard(selected_language))
                user_data[user_id]["step"] = "currency"

# --- Agar foydalanuvchi son emas ma'lumot kiritsa ---
@dp.message()
async def invalid_input(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in user_data:
        await message.answer("Iltimos, avval tilni tanlang / Пожалуйста, сначала выберите язык / Please select language first:", 
                           reply_markup=language_keyboard())
        return
    
    selected_language = user_data[user_id].get("language")
    
    # Karta raqami kiritish bosqichida noto'g'ri ma'lumot kiritilgan
    if user_data[user_id].get("step") == "card_number":
        error_text = LANGUAGES[selected_language]["buttons"]["invalid_card"]
        await message.answer(error_text)
        return
    
    # Miqdor kiritish bosqichida noto'g'ri ma'lumot kiritilgan
    if user_data[user_id].get("step") == "amount":
        error_text = LANGUAGES[selected_language]["buttons"]["number_only"]
        await message.answer(error_text)

# --- Pre-checkout ---
@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# --- To'lov muvaffaqiyatli bo'lsa ---
@dp.message(F.successful_payment)
async def successful_payment(message: Message):
    user_id = message.from_user.id
    
    if user_id in user_data:
        selected_language = user_data[user_id]["language"]
        success_text = LANGUAGES[selected_language]["buttons"]["payment_success"]
        
        # Foydalanuvchi balansini yangilash (simulyatsiya)
        payment_amount = message.successful_payment.total_amount
        if user_id in user_stars_balance:
            user_stars_balance[user_id] -= payment_amount
            if user_stars_balance[user_id] < 0:
                user_stars_balance[user_id] = 0
        
        # Foydalanuvchi bosqichini "card_number" ga o'zgartirish
        user_data[user_id]["step"] = "card_number"
        
        await message.answer(success_text)
    else:
        await message.answer("✅ To'lov qabul qilindi!\n\nIltimos, karta raqamingizni yuboring:")

# --- Run ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())