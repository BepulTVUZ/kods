import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    LabeledPrice
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Bot token
BOT_TOKEN = "7488918446:AAGiaoinZJqtd_cVh46WD7YyEA36ap_PulE"

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)

# Bot va dispatcher
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# User data saqlash uchun dictionary
user_data = {}
bot_balance = 0

# Raqamlar ro'yxati
PHONE_NUMBERS = [
    "🇺🇸 USA: +1 (657) 4569699",
    "🇺🇸 USA: +1 (413) 4498280",
    "🇺🇸 USA: +1 (740) 4619427",
    "🇮🇪 IE: +353 89 9747266",
    "🇰🇿 KZ: +7(775) 3160336",
    "🇺🇿 UZ: +998(33) 5015246",
    "🇺🇿 UZ: +998(33) 3394470",
    "🇪🇸 ES: +34 608 223 970",
    "🇨🇾 CY: +357-96-799-648",
    "🇬🇧 GB: +44 7459 603196",
    "🇬🇧 GB: +44 7459 703200",
    "🇺🇸 USA: +1 (741) 4211310",
    "🇺🇸 USA: +1 (213) 5928471",
    "🇺🇸 USA: +1 (304) 7811953",
    "🇺🇸 USA: +1 (415) 9372648",
    "🇮🇪 IE: +353 89 9747266",
    "🇮🇪 IE: +353 89 6154832"
]

# Tillar ro'yxati
LANGUAGES = {
    "ru": "🇷🇺 Русский язык",
    "en": "🇬🇧 English",
    "tj": "🇹🇯 Тоҷикӣ (Tojik)",
    "kg": "🇰🇬 Кыргызча (Qirg'iz)",
    "kz": "🇰🇿 Қазақша (Qozoq)",
    "tk": "🇹🇲 Türkmençe (Turkman)",
    "ar": "🇸🇦 العربية (Arab)",
    "az": "🇦🇿 Azərbaycanca (Ozarbayjon)",
    "hy": "🇦🇲 Հայերեն (Arman)",
    "ro": "🇷🇴 Română (Rum)",
    "uz": "🇺🇿 O'zbekcha"
}

# FSM holatlari
class UserState(StatesGroup):
    choosing_language = State()
    main_menu = State()
    profile = State()
    online_users = State()
    faq = State()
    choosing_number = State()

# Til tanlash keyboard (4 ta qatorda)
def get_language_keyboard():
    buttons = []
    lang_list = list(LANGUAGES.values())
    
    # Har bir qatorda 2-3 ta button
    for i in range(0, len(lang_list), 3):
        row = lang_list[i:i+3]
        buttons.append([KeyboardButton(text=text) for text in row])
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

# Matnlar har bir til uchun - to'liq versiya
TEXTS = {
    "ru": {
        "main_menu": {
            "sim_menu": "📋 Меню SIM-карт для приёма SMS-кодов",
            "balance": "💳 Мой баланс",
            "profile": "👤 Мой профиль",
            "faq": "❓ F.A.Q и Поддержка",
            "online": "👥 Сейчас онлайн",
            "language": "🌐 Язык / Language"
        },
        "main_text": "🌍 VIRTUAL GRAM - №1 — Аренда дешевых номеров. Получение SMS.\nВаш текущий баланс: 0 Telegram Stars",
        "back_button": "⬅️ Назад в меню",
        "profile_text": "👤 Мой профиль\n\nВаш ID: {user_id}\nБаланс: 0 Telegram stars\nПокупок виртуалных сим картов: 0",
        "online_text": "Количество людей, использующих бота по всему миру сейчас: 🟢 {count}",
        "faq_text": """❓ Часто задаваемые вопросы (F.A.Q.)

1. Что такое виртуальная SIM-карта?
Это цифровой номер для приёма SMS без физической SIM-карты. Идеально подходит для регистрации в сервисах и приложениях.

2. Какие преимущества виртуальной SIM?
• Быстрое подключение — никаких походов в магазины.
• Использование в разных странах.
• Несколько номеров на одном устройстве.
• Основной номер остаётся конфиденциальным.

3. В каких странах работает?
Мы предлагаем номера для популярных стран: Европа, Азия, США, Латинская Америка и др.

4. Как получить виртуальный номер?
После покупки вы получите номер, который можно сразу использовать для приёма SMS.

5. Можно ли звонить или отправлять SMS?
Виртуальные номера предназначены только для приёма SMS. Для звонков используйте обычный номер или мессенджеры (WhatsApp, Telegram и др.).

6. Можно ли вернуть деньги?
После выдачи номера возврат средств невозможен, так как номер считается использованным.""",
        "sim_menu_text": "📋 SIM-карты меню (здесь будет функционал SIM-карт)",
        "balance_text": "💳 Ваш баланс: 0 Telegram Stars",
        "use_buttons": "⚠️ Пожалуйста, используйте кнопки меню для навигации.",
        "welcome": "🇷🇺 Здравствуйте, пожалуйста, выберите язык!\n🇬🇧 Hello, please choose a language!",
        "lang_selected": "✅ Язык выбран: Русский",
        "choose_lang": "🇷🇺 Пожалуйста, выберите язык!\n🇬🇧 Please choose a language!",
        "available_numbers": "📋 Доступные номера:",
        "payment_text": "💰 Для покупки этого номера на 2 недели необходимо 45 Telegram Stars:",
        "payment_success": "✅ Платеж успешно принят!",
        "show_balance": "📊 Баланс бота: {balance} Stars",
        "payment_title": "Аренда виртуального номера",
        "payment_description": "Аренда номера на 2 недели: {number}",
        "payment_label": "2 недели аренды номера",
        "start_command": "ℹ️ Botdan foydalanish uchun /start komandasini yuboring.\nℹ️ To use the bot, send the /start command."
    },
    "en": {
        "main_menu": {
            "sim_menu": "📋 SMS Code Reception SIM Cards Menu",
            "balance": "💳 My Balance",
            "profile": "👤 My Profile",
            "faq": "❓ F.A.Q and Support",
            "online": "👥 Now Online",
            "language": "🌐 Language / Язык"
        },
        "main_text": "🌍 VIRTUAL GRAM - №1 — Cheap number rental. SMS reception.\nYour current balance: 0 Telegram Stars",
        "back_button": "⬅️ Back to menu",
        "profile_text": "👤 My Profile\n\nYour ID: {user_id}\nBalance: 0 Telegram stars\nVirtual SIM card purchases: 0",
        "online_text": "Number of people using the bot worldwide now: 🟢 {count}",
        "faq_text": """❓ Frequently Asked Questions (F.A.Q.)

1. What is a virtual SIM card?
This is a digital number for receiving SMS without a physical SIM card. Perfect for registration in services and applications.

2. What are the advantages of virtual SIM?
• Quick connection — no trips to stores.
• Use in different countries.
• Multiple numbers on one device.
• Your main number remains confidential.

3. In which countries does it work?
We offer numbers for popular countries: Europe, Asia, USA, Latin America, etc.

4. How to get a virtual number?
After purchase, you will receive a number that can be immediately used for receiving SMS.

5. Can I make calls or send SMS?
Virtual numbers are for receiving SMS only. For calls, use a regular number or messengers (WhatsApp, Telegram, etc.).

6. Can I get a refund?
After issuing the number, a refund is not possible, as the number is considered used.""",
        "sim_menu_text": "📋 SIM Cards Menu (SIM cards functionality will be here)",
        "balance_text": "💳 Your balance: 0 Telegram Stars",
        "use_buttons": "⚠️ Please use menu buttons for navigation.",
        "welcome": "🇷🇺 Здравствуйте, пожалуйста, выберите язык!\n🇬🇧 Hello, please choose a language!",
        "lang_selected": "✅ Language selected: English",
        "choose_lang": "🇷🇺 Пожалуйста, выберите язык!\n🇬🇧 Please choose a language!",
        "available_numbers": "📋 Available numbers:",
        "payment_text": "💰 To purchase this number for 2 weeks you need 45 Telegram Stars:",
        "payment_success": "✅ Payment successful!",
        "show_balance": "📊 Bot balance: {balance} Stars",
        "payment_title": "Virtual Number Rental",
        "payment_description": "Number rental for 2 weeks: {number}",
        "payment_label": "2 weeks number rental",
        "start_command": "ℹ️ To use the bot, send the /start command."
    },
    "tj": {
        "main_menu": {
            "sim_menu": "📋 Менюи SIM-картаҳо барои қабули рамзҳои SMS",
            "balance": "💳 Баланси ман",
            "profile": "👤 Профили ман",
            "faq": "❓ Саволҳои зуд-зуд такроршаванда ва Дастгирӣ",
            "online": "👥 Ҳозир онлайн",
            "language": "🌐 Забон / Language"
        },
        "main_text": "🌍 VIRTUAL GRAM - №1 — Иҷораи рақамҳои арзон. Қабули SMS.\nБаланси ҷории шумо: 0 Telegram Stars",
        "back_button": "⬅️ Бозгашт ба меню",
        "profile_text": "👤 Профили ман\n\nID-и шумо: {user_id}\nБаланс: 0 Telegram stars\nХариди сим-картаҳои виртуалӣ: 0",
        "online_text": "Шумораи одамони истифодабарандаи бот дар саросари ҷаҳон ҳоло: 🟢 {count}",
        "faq_text": """❓ Саволҳои зуд-зуд такроршаванда (F.A.Q.)

1. SIM-картаи виртуалӣ чист?
Ин рақами рақамӣ барои қабули SMS бе SIM-картаи физикӣ мебошад. Барои сабтином дар хидматҳо ва барномаҳо мунтазам аст.

2. Кадом имтиёзҳои SIM-и виртуалӣ?
• Пайвастшавӣ зуд — бе рафтан ба мағозаҳо.
• Истифода дар кишварҳои гуногун.
• Чанд рақам дар як дастгоҳ.
• Рақами асосии шумо махфӣ мемонад.

3. Дар кадом кишварҳо кор мекунад?
Мо рақамҳоро барои кишварҳои машҳур пешниҳод мекунем: Аврупо, Осиё, ИМА, Амрикои Лотинӣ ва ғ.

4. Чӣ тавр рақами виртуалӣ гирифтан мумкин аст?
Пас аз харид, шумо рақамро мегиред, ки фавран барои қабули SMS истифода бурдан мумкин аст.

5. Оё метавон занг зада ё SMS фиристод?
Рақамҳои виртуалӣ танҳо барои қабули SMS мебошанд. Барои зангҳо, рақами оддӣ ё паёмрасонҳоро (WhatsApp, Telegram ва ғ.) истифода баред.

6. Оё пуҳоро бозгардонидан мумкин аст?
Пас аз додани рақам, бозгардонидани пу имконнопазир аст, зеро рақам истифодашуда ҳисобида мешавад.""",
        "sim_menu_text": "📋 Менюи SIM-картаҳо (дар ин ҷо функсионалии SIM-картаҳо хоҳад буд)",
        "balance_text": "💳 Баланси шумо: 0 Telegram Stars",
        "use_buttons": "⚠️ Лутфан барои навигатсия тугмаҳои менюро истифода баред.",
        "welcome": "Салом, лутфан забони худро интихоб кунед!",
        "lang_selected": "✅ Забон интихоб шуд: Тоҷикӣ",
        "choose_lang": "Лутфан забони худро интихоб кунед!",
        "available_numbers": "📋 Рақамҳои дастрас:",
        "payment_text": "💰 Барои хариди ин рақам барои 2 ҳафта ба шумо 45 Telegram Stars лозим аст:",
        "payment_success": "✅ Пардохт қабул шуд!",
        "show_balance": "📊 Баланси бот: {balance} Stars",
        "payment_title": "Иҷораи рақами виртуалӣ",
        "payment_description": "Иҷораи рақам барои 2 ҳафта: {number}",
        "payment_label": "2 ҳафта иҷораи рақам",
        "start_command": "ℹ️ Барои истифодаи бот, фармони /start-ро ирсол кунед."
    },
    "kg": {
        "main_menu": {
            "sim_menu": "📋 SMS коддорун кабыл алуу үчүн SIM-карталар менюсу",
            "balance": "💳 Менин балансым",
            "profile": "👤 Менин профилим",
            "faq": "❓ Көп берилүүчү суроолор жана Колдоо",
            "online": "👥 Азыр онлайн",
            "language": "🌐 Тил / Language"
        },
        "main_text": "🌍 VIRTUAL GRAM - №1 — Арзан номерлердин ижарасы. SMS кабыл алуу.\nУчурдагы балансыңыз: 0 Telegram Stars",
        "back_button": "⬅️ Менюго кайтуу",
        "profile_text": "👤 Менин профилим\n\nСиздин ID: {user_id}\nБаланс: 0 Telegram stars\nВиртуалдык SIM-карталарды сатып алуулар: 0",
        "online_text": "Ботту бүткүл дүйнө жүзүндө азыр колдонуп жаткан адамдардын саны: 🟢 {count}",
        "faq_text": """❓ Көп берилүүчү суроолор (F.A.Q.)

1. Виртуалдык SIM-карта деген эмне?
Бул физикалык SIM-картасыз SMS кабыл алуу үчүн сандык номер. Сервистерге жана колдонмолорго катталуу үчүн жакшы.

2. Виртуалдык SIMдин артыкчылыктары кандай?
• Тезирээк туташуу — дүкөнгө баруунун кажети жок.
• Ар түрдүү өлкөлөрдө колдонуу.
• Бир түзмөктө бир нече номер.
• Негизги номериңиз жашыруун калат.

3. Кайсы өлкөлөрдө иштейт?
Биз популярдуу өлкөлөр үчүн номерлерди сунуштайбыз: Европа, Азия, АКШ, Латын Америкасы ж.б.

4. Виртуалдык номерди кантип алууга болот?
Сатып алгандан кийин, сиз SMS кабыл алуу үчүн дароо колдонсо боло турган номерди аласыз.

5. Зенг жасасам же SMS жөнөтсөм болобу?
Виртуалдык номерлер SMS гана кабыл алуу үчүн. Зенгдер үчүн, кадимки номерди же мессенжерлерди (WhatsApp, Telegram ж.б.) колдонуңуз.

6. Акчаны кайтарып алууга болобу?
Номерди бергенден кийин, акчаны кайтаруу мүмкүн эмес, себеби номер колдонулган деп эсептелет.""",
        "sim_menu_text": "📋 SIM-карталар менюсу (бул жерде SIM-карталардын функционалдыгы болот)",
        "balance_text": "💳 Сиздин балансыңыз: 0 Telegram Stars",
        "use_buttons": "⚠️ Навигация үчүн меню баскычтарын колдонуңуз.",
        "welcome": "Саламатсызбы, тилиңизди тандаңыз!",
        "lang_selected": "✅ Тил танданды: Кыргызча",
        "choose_lang": "Тилиңизди тандаңыз!",
        "available_numbers": "📋 Бар номерилер:",
        "payment_text": "💰 Бул номерди 2 жумага сатып алуу үчүн 45 Telegram Stars керек:",
        "payment_success": "✅ Төлөм кабыл алынды!",
        "show_balance": "📊 Бот балансы: {balance} Stars",
        "payment_title": "Виртуалдык номер ижарасы",
        "payment_description": "2 жумага номер ижарасы: {number}",
        "payment_label": "2 жума номер ижарасы",
        "start_command": "ℹ️ Ботту колдонуу үчүн /start буйругуну жөнөтүңүз."
    },
    "kz": {
        "main_menu": {
            "sim_menu": "📋 SMS кодтарын қабылдау үшін SIM-карталар мәзірі",
            "balance": "💳 Менің балансым",
            "profile": "👤 Менің профилім",
            "faq": "❓ Жиі қойылатын сұрақтар және Қолдау",
            "online": "👥 Қазір онлайн",
            "language": "🌐 Тіл / Language"
        },
        "main_text": "🌍 VIRTUAL GRAM - №1 — Арзан нөмірлерді жалға алу. SMS қабылдау.\nАғымдағы балансыңыз: 0 Telegram Stars",
        "back_button": "⬅️ Мәзірге оралу",
        "profile_text": "👤 Менің профилім\n\nСіздің ID: {user_id}\nБаланс: 0 Telegram stars\nВиртуалды SIM-карталарды сатып алу: 0",
        "online_text": "Ботты бүкіл әлем бойынша қазір қолданып жатқан адамдар саны: 🟢 {count}",
        "faq_text": """❓ Жиі қойылатын сұрақтар (F.A.Q.)

1. Виртуалды SIM-карта деген не?
Бұл физикалық SIM-картасыз SMS қабылдау үшін сандық нөмір. Сервистерге және қосымшаларға тіркелу үшін өте қолайлы.

2. Виртуалды SIM-нің артықшылықтары қандай?
• Жылдам қосылу — дүкендерге барудың қажеті жоқ.
• Әр түрлі елдерде қолдану.
• Бір құрылғыда бірнеше нөмір.
• Негізгі нөміріңіз құпия қалады.

3. Қай елдерде жұмыс істейді?
Біз танымал елдер үшін нөмірлерді ұсынамыз: Еуропа, Азия, АҚШ, Латын Америкасы және т.б.

4. Виртуалды нөмірді қалай алуға болады?
Сатып алғаннан кейін, сіз SMS қабылдау үшін бірден пайдалануға болатын нөмірді аласыз.

5. Қоңырау шалуға немесе SMS жіберуге бола ма?
Виртуалды нөмірлер тек SMS қабылдау үшін. Қоңыраулар үшін, қарапайым нөмірді немесе мессенджерлерді (WhatsApp, Telegram және т.б.) пайдаланыңыз.

6. Ақшаны қайтаруға бола ма?
Нөмірді бергеннен кейін, ақшаны қайтару мүмкін емес, өйткені нөмір пайдаланылған деп есептеледі.""",
        "sim_menu_text": "📋 SIM-карталар мәзірі (мұнда SIM-карталар функционалы болады)",
        "balance_text": "💳 Сіздің балансыңыз: 0 Telegram Stars",
        "use_buttons": "⚠️ Навигация үшін мәзір түймелерін пайдаланыңыз.",
        "welcome": "Сәлеметсіз бе, тіліңізді таңдаңыз!",
        "lang_selected": "✅ Тіл таңдалды: Қазақша",
        "choose_lang": "Тіліңізді таңдаңыз!",
        "available_numbers": "📋 Қолжетімді нөмірлер:",
        "payment_text": "💰 Бұл нөмірді 2 аптаға сатып алу үшін 45 Telegram Stars қажет:",
        "payment_success": "✅ Төлем қабылданды!",
        "show_balance": "📊 Бот балансы: {balance} Stars",
        "payment_title": "Виртуалды нөмір жалдау",
        "payment_description": "2 аптаға нөмір жалдау: {number}",
        "payment_label": "2 апта нөмір жалдау",
        "start_command": "ℹ️ Ботты пайдалану үшін /start пәрменін жіберіңіз."
    },
    "tk": {
        "main_menu": {
            "sim_menu": "📋 SMS kodlaryny kabul etmek üçin SIM-kartlar menýasy",
            "balance": "💳 Balansym",
            "profile": "👤 Profilim",
            "faq": "❓ Köp soraglar we Goldaw",
            "online": "👥 Häzir onlaýn",
            "language": "🌐 Dil / Language"
        },
        "main_text": "🌍 VIRTUAL GRAM - №1 — Arzan nomerleri ijaralamak. SMS kabul etmek.\nHäzirki balansyňyz: 0 Telegram Stars",
        "back_button": "⬅️ Menýa gaýtmak",
        "profile_text": "👤 Profilim\n\nSiziň ID: {user_id}\nBalans: 0 Telegram stars\nWirtual SIM-kartlary satyn alyşlar: 0",
        "online_text": "Boty dünýä boýunça häzir ulanýan adamlar sany: 🟢 {count}",
        "faq_text": """❓ Köp soraglar (F.A.Q.)

1. Wirtual SIM-karta näme?
Bu fiziki SIM-kartasyz SMS kabul etmek üçin sanly nomer. Hyzmatlara we programmalara registrasiýa üçin gowy.

2. Wirtual SIM-iň üstünlikleri nämä?
• Çalt birikmek — dükanlara gitmek gerek däl.
• Türli ýurtlarda ulanmak.
• Bir enjamynda birnäçe nomer.
• Esasy nomeriňiz gizlin galýar.

3. Haýsy ýurtlarda işleýär?
Biz meşhur ýurtlar üçin nomerleri hödürleýäris: Ýewropa, Aziýa, ABŞ, Latyn Amerikasy we ş.m.

4. Wirtual nomeri nädip almaly?
Satyn alandan soň, SMS kabul etmek üçin derrew ulanyp bilersiňiz.

5. Zeng edip ýa-da SMS iberip bolarmy?
Wirtual nomerler diňe SMS kabul etmek üçin. Zengler üçin, adaty nomeri ýa-da messenjerleri (WhatsApp, Telegram we ş.m.) ulanyň.

6. Pul yzyna gaytaryp almak bolarmy?
Nomeri berenden soň, pul yzyna gaytarmak mümkin däl, sebäbi nomer ulanyldy hasaplanýar.""",
        "sim_menu_text": "📋 SIM-kartlar menýasy (barda SIM-kartlaryň funksionalygy bolar)",
        "balance_text": "💳 Siziň balansyňyz: 0 Telegram Stars",
        "use_buttons": "⚠️ Nawigasiýa üçin menýu düwmelerini ulanyň.",
        "welcome": "Salam, dilizi saýlaň!",
        "lang_selected": "✅ Dil saýlandy: Türkmençe",
        "choose_lang": "Diliňizi saýlaň!",
        "available_numbers": "📋 Elýeterli nomerler:",
        "payment_text": "💰 Bu nomeri 2 hepde satyn almak üçin 45 Telegram Stars gerek:",
        "payment_success": "✅ Töleg kabul edildi!",
        "show_balance": "📊 Bot balansy: {balance} Stars",
        "payment_title": "Wirtual nomer ijarasy",
        "payment_description": "2 hepde nomer ijarasy: {number}",
        "payment_label": "2 hepde nomer ijarasy",
        "start_command": "ℹ️ Boty ulanyş üçin /start buýrugy iberiň."
    },
    "ar": {
        "main_menu": {
            "sim_menu": "📋 قائمة بطاقات SIM لاستقبال رموز SMS",
            "balance": "💳 رصيدي",
            "profile": "👤 ملفي الشخصي",
            "faq": "❓ الأسئلة الشائعة والدعم",
            "online": "👥 متصل الآن",
            "language": "🌐 اللغة / Language"
        },
        "main_text": "🌍 VIRTUAL GRAM - №1 — تأجير أرقام رخيصة. استقبال الرسائل النصية.\nرصيدك الحالي: 0 Telegram Stars",
        "back_button": "⬅️ العودة إلى القائمة",
        "profile_text": "👤 ملفي الشخصي\n\nمعرفك: {user_id}\nالرصيد: 0 نجوم تليجرام\nمشتريات بطاقات SIM الافتراضية: 0",
        "online_text": "عدد الأشخاص الذين يستخدمون البوت حول العالم الآن: 🟢 {count}",
        "faq_text": """❓ الأسئلة الشائعة (F.A.Q.)

1. ما هي بطاقة SIM الافتراضية؟
هذا رقم رقمي لاستقبال الرسائل النصية القصيرة بدون بطاقة SIM مادية. مثالي للتسجيل في الخدمات والتطبيقات.

2. ما هي مزايا بطاقة SIM الافتراضية؟
• اتصال سريع - لا حاجة للذهاب إلى المتاجر.
• الاستخدام في مختلف البلدان.
• أرقام متعددة على جهاز واحد.
• رقمك الرئيسي يبقى سريًا.

3. في أي البلدان تعمل؟
نحن نقدم أرقامًا للبلدان الشهيرة: أوروبا، آسيا، الولايات المتحدة، أمريكا اللاتينية، إلخ.

4. كيف يمكن الحصول على رقم افتراضي؟
بعد الشراء، ستحصل على رقم يمكن استخدامه على الفور لاستقبال الرسائل النصية القصيرة.

5. هل يمكن الاتصال أو إرسال رسائل نصية؟
الأرقام الافتراضية مخصصة لاستقبال الرسائل النصية القصيرة فقط. للمكالمات، استخدم رقمًا عاديًا أو المراسلات (WhatsApp، Telegram، إلخ.).

6. هل يمكن استرداد الأموال؟
بعد إصدار الرقم، لا يمكن استرداد الأموال، حيث يعتبر الرقم مستخدمًا.""",
        "sim_menu_text": "📋 قائمة بطاقات SIM (ستكون وظائف بطاقات SIM هنا)",
        "balance_text": "💳 رصيدك: 0 نجوم تليجرام",
        "use_buttons": "⚠️ يرجى استخدام أزرار القائمة للتنقل.",
        "welcome": "مرحبًا، يرجى اختيار لغتك!",
        "lang_selected": "✅ تم اختيار اللغة: العربية",
        "choose_lang": "يرجى اختيار لغتك!",
        "available_numbers": "📋 الأرقام المتاحة:",
        "payment_text": "💰 لشراء هذا الرقم لمدة أسبوعين تحتاج إلى 45 نجوم تليجرام:",
        "payment_success": "✅ تم قبول الدفعة!",
        "show_balance": "📊 رصيد البوت: {balance} Stars",
        "payment_title": "تأجير رقم افتراضي",
        "payment_description": "تأجير رقم لمدة أسبوعين: {number}",
        "payment_label": "2 أسبوع تأجير رقم",
        "start_command": "ℹ️ لاستخدام البوت، أرسل الأمر /start."
    },
    "az": {
        "main_menu": {
            "sim_menu": "📋 SMS kodlarını qəbul etmək üçin SIM-kartlar menyusu",
            "balance": "💳 Balansım",
            "profile": "👤 Profilim",
            "faq": "❓ Tez-tez verilən suallar və Dəstək",
            "online": "👥 İndi onlayn",
            "language": "🌐 Dil / Language"
        },
        "main_text": "🌍 VIRTUAL GRAM - №1 — Ucuz nömrələrin icarəsi. SMS qəbulu.\nCari balansınız: 0 Telegram Stars",
        "back_button": "⬅️ Menyaya qayıt",
        "profile_text": "👤 Profilim\n\nSizin ID: {user_id}\nBalans: 0 Telegram ulduzu\nVirtual SIM-kart alışları: 0",
        "online_text": "Botu dünya üzrə indi istifadə edən insanların sayı: 🟢 {count}",
        "faq_text": """❓ Tez-tez verilən suallar (F.A.Q.)

1. Virtual SIM-kart nədir?
Bu fiziki SIM-kart olmadan SMS qəbul etmək üçin rəqəmsal nömrədir. Xidmətlərə və tətbiqlərə qeydiyyat üçin ideal.

2. Virtual SIM-in üstünlükləri nələrdir?
• Sürətli qoşulma - mağazalara getmək lazım deyil.
• Müxtəlif ölkələrdə istifadə.
• Bir cihazda bir neçə nömrə.
• Əsas nömrəniz gizli qalır.

3. Hansı ölkələrdə işləyir?
Biz məşhur ölkələr üçin nömrələr təklif edirik: Avropa, Asiya, ABŞ, Latın Amerikası və s.

4. Virtual nömrəni necə əldə etmək olar?
Satın aldıqdan sonra, SMS qəbul etmək üçün dərhal istifadə edə biləcəyiniz nömrəni alacaqsınız.

5. Zəng etmək və ya SMS göndərmək olarmı?
Virtual nömrələr yalnız SMS qəbul etmək üçündür. Zənglər üçün, adi nömrə və ya mesenjerlərdən (WhatsApp, Telegram və s.) istifadə edin.

6. Pulu geri almaq olarmı?
Nömrə verildikdən sonra, pulun geri qaytarılması mümkün deyil, çünki nömrə istifadə edilmiş sayılır.""",
        "sim_menu_text": "📋 SIM-kartlar menyusu (burada SIM-kartların funksionallığı olacaq)",
        "balance_text": "💳 Balansınız: 0 Telegram Stars",
        "use_buttons": "⚠️ Naviqasiya üçin menyu düymələrindən istifadə edin.",
        "welcome": "Salam, dilinizi seçin!",
        "lang_selected": "✅ Dil seçildi: Azərbaycanca",
        "choose_lang": "Dilinizi seçin!",
        "available_numbers": "📋 Mövcud nömrələr:",
        "payment_text": "💰 Bu nömrəni 2 həftəyə satın almaq üçün 45 Telegram Stars lazımdır:",
        "payment_success": "✅ Ödəniş qəbul edildi!",
        "show_balance": "📊 Bot balansı: {balance} Stars",
        "payment_title": "Virtual nömrə icarəsi",
        "payment_description": "2 həftə nömrə icarəsi: {number}",
        "payment_label": "2 həftə nömrə icarəsi",
        "start_command": "ℹ️ Botu istifadə etmək üçün /start əmrini göndərin."
    },
    "hy": {
        "main_menu": {
            "sim_menu": "📋 SMS կոդերի ընդունման SIM քարտերի մենյու",
            "balance": "💳 Իմ հաշվեկշիռը",
            "profile": "👤 Իմ պրոֆիլը",
            "faq": "❓ Հաճախ տրվող հարցեր և Աջակցություն",
            "online": "👥 Այժմ առցանց",
            "language": "🌐 Լեզու / Language"
        },
        "main_text": "🌍 VIRTUAL GRAM - №1 — Էժան համարների վարձակալություն: SMS ընդունում:\nՁեր ընթացիկ հաշվեկշիռը: 0 Telegram Stars",
        "back_button": "⬅️ Վերադառնալ մենյու",
        "profile_text": "👤 Իմ պրոֆիլը\n\nՁեր ID: {user_id}\nՀաշվեկշիռ: 0 Telegram աստղ\nՎիրտուալ SIM քարտերի գնումներ: 0",
        "online_text": "Աշխարհում այժմ բոտ օգտագործող մարդկանց թիվը: 🟢 {count}",
        "faq_text": """❓ Հաճախ տրվող հարցեր (F.A.Q.)

1. Ի՞նչ է վիրտուալ SIM քարտը:
Սա ֆիզիկական SIM քարտի բացակայությամբ SMS ստանալու թվային համար է: Իդեալական է ծառայություններում և հավելվածներում գրանցվելու համար:

2. Որո՞նք են վիրտուալ SIM-ի առավելությունները:
• Արագ միացում - խանութներ գնալու կարիք չկա:
• Օգտագործում տարբեր երկրներում:
• Մի քանի համար մեկ սարքում:
• Ձեր հիմնական համարը մնում է գաղտնի:

3. Ո՞ր երկրներում է այն աշխատում:
Մենք առաջարկում ենք համարներ հայտնի երկրների համար: Եվրոպա, Ասիա, ԱՄՆ, Լատինական Ամերիկա և այլն:

4. Ինչպե՞ս ստանալ վիրտուալ համար:
Գնումից հետո դուք կստանաք համար, որը կարող եք անմիջապես օգտագործել SMS ստանալու համար:

5. Կարո՞ղ եմ զանգել կամ SMS ուղարկել:
Վիրտուալ համարները նախատեսված են միայն SMS ստանալու համար: Զանգերի համար օգտագործեք սովորական համար կամ մեսենջերներ (WhatsApp, Telegram և այլն):

6. Կարո՞ղ եմ փոխհատուցում ստանալ:
Համարը տրամադրելուց հետո փոխհատուցումը հնարավոր չէ, քանի որ համարը համարվում է օգտագործված:""",
        "sim_menu_text": "📋 SIM քարտերի մենյու (այստեղ կլինի SIM քարտերի ֆունկցիոնալությունը)",
        "balance_text": "💳 Ձեր հաշվեկշիռը: 0 Telegram Stars",
        "use_buttons": "⚠️ Խնդրում ենք օգտագործել մենյուի կոճակները նավարկության համար:",
        "welcome": "Բարև, ընտրեք ձեր լեզուն:",
        "lang_selected": "✅ Լեզուն ընտրվել է: Հայերեն",
        "choose_lang": "Ընտրեք ձեր լեզուն:",
        "available_numbers": "📋 Հասանելի համարներ:",
        "payment_text": "💰 Այս համարը 2 շաբաթով գնելու համար անհրաժեշտ է 45 Telegram Stars:",
        "payment_success": "✅ Վճարումն ընդունված է!",
        "show_balance": "📊 Բոտի հաշվեկշիռ: {balance} Stars",
        "payment_title": "Վիրտուալ համարի վարձակալություն",
        "payment_description": "2 շաբաթ համարի վարձակալություն: {number}",
        "payment_label": "2 շաբաթ համարի վարձակալություն",
        "start_command": "ℹ️ Բոտն օգտագործելու համար ուղարկեք /start հրամանը:"
    },
    "ro": {
        "main_menu": {
            "sim_menu": "📋 Meniu carduri SIM pentru primirea codurilor SMS",
            "balance": "💳 Balanța mea",
            "profile": "👤 Profilul meu",
            "faq": "❓ Întrebări frecvente și Suport",
            "online": "👥 Acum online",
            "language": "🌐 Limbă / Language"
        },
        "main_text": "🌍 VIRTUAL GRAM - №1 — Închiriere numere ieftine. Primire SMS.\nBalanța curentă: 0 Telegram Stars",
        "back_button": "⬅️ Înapoi la meniu",
        "profile_text": "👤 Profilul meu\n\nID-ul dvs: {user_id}\nBalanță: 0 stele Telegram\nAchiziții carduri SIM virtuale: 0",
        "online_text": "Numărul de persoane care utilizează botul în întreaga lume acum: 🟢 {count}",
        "faq_text": """❓ Întrebări frecvente (F.A.Q.)

1. Ce este un card SIM virtual?
Acesta este un număr digital pentru primirea SMS fără un card SIM fizic. Ideal pentru înregistrarea în servicii și aplicații.

2. Care sunt avantajele SIM-ului virtual?
• Conexiune rapidă - nu este nevoie să mergi la magazine.
• Utilizare în diferite țări.
• Mai multe numere pe un singur dispozitiv.
• Numărul dvs principal rămâne confidențial.

3. În ce țări funcționează?
Oferim numere pentru țări populare: Europa, Asia, SUA, America Latină etc.

4. Cum pot obține un număr virtual?
După achiziție, veți primi un număr который poate fi utilizat imediat pentru primirea SMS.

5. Pot să sun sau să trimit SMS?
Numerele virtuale sunt doar pentru primirea SMS. Pentru apeluri, utilizați un număr obișnuit sau messenger-e (WhatsApp, Telegram etc.).

6. Pot primi o rambursare?
După emiterea numărului, rambursarea nu este posibilă, deoarece numărul este considerat utilizat.""",
        "sim_menu_text": "📋 Meniu carduri SIM (aici va fi funcționalitatea cardurilor SIM)",
        "balance_text": "💳 Balanța dvs: 0 Telegram Stars",
        "use_buttons": "⚠️ Vă rugăm să utilizați butoanele meniu pentru navigare.",
        "welcome": "Bună ziua, vă rugăm să alegeți limba!",
        "lang_selected": "✅ Limba selectată: Română",
        "choose_lang": "Vă rugăm să alegeți limba!",
        "available_numbers": "📋 Numere disponibile:",
        "payment_text": "💰 Pentru a cumpăra acest număr pentru 2 săptămâni aveți nevoie de 45 Telegram Stars:",
        "payment_success": "✅ Plată acceptată!",
        "show_balance": "📊 Balanța botului: {balance} Stars",
        "payment_title": "Închiriere număr virtual",
        "payment_description": "Închiriere număr pentru 2 săptămâni: {number}",
        "payment_label": "2 săptămâni închiriere număr",
        "start_command": "ℹ️ Pentru a utiliza botul, trimiteți comanda /start."
    },
    "uz": {
        "main_menu": {
            "sim_menu": "📋 SMS kodlarini qabul qilish uchun SIM-kartalar menyusi",
            "balance": "💳 Mening balansim",
            "profile": "👤 Mening profilim",
            "faq": "❓ Tez-tez beriladigan savollar va Qo'llab-quvvatlash",
            "online": "👥 Hozir onlayn",
            "language": "🌐 Til / Language"
        },
        "main_text": "🌍 VIRTUAL GRAM - №1 — Arzon raqamlarni ijaralash. SMS qabul qilish.\nJoriy balansingiz: 0 Telegram Stars",
        "back_button": "⬅️ Menyuga qaytish",
        "profile_text": "👤 Mening profilim\n\nSizning ID: {user_id}\nBalans: 0 Telegram yulduzi\nVirtual SIM-karta xaridlari: 0",
        "online_text": "Botdan butun dunyo bo'yicha hozir foydalanayotgan odamlar soni: 🟢 {count}",
        "faq_text": """❓ Tez-tez beriladigan savollar (F.A.Q.)

1. Virtual SIM-karta nima?
Bu jismoniy SIM-kartasiz SMS qabul qilish uchun raqamli raqam. Xizmatlar va ilovalarga ro'yxatdan o'tish uchun juda qulay.

2. Virtual SIMning afzalliklari qanday?
• Tez ulanish - do'konlarga borishning hojati yo'q.
• Turli mamlakatlarda foydalanish.
• Bir qurilmada bir nechta raqam.
• Asosiy raqamingiz maxfiy qoladi.

3. Qaysi mamlakatlarda ishlaydi?
Biz mashhur mamlakatlar uchun raqamlarni taklif qilamiz: Yevropa, Osiyo, AQSh, Lotin Amerikasi va boshqalar.

4. Virtual raqamni qanday olish mumkin?
Xarid qilgandan so'ng, siz SMS qabul qilish uchun darhol foydalanish mumkin bo'lgan raqamni olasiz.

5. Qo'ng'iroq qilish yoki SMS yuborish mumkinmi?
Virtual raqamlar faqat SMS qabul qilish uchun. Qo'ng'iroqlar uchun, oddiy raqam yoki messenjerlardan (WhatsApp, Telegram va boshqalar) foydalaning.

6. Pulni qaytarib olish mumkinmi?
Raqam berilgandan so'ng, pulni qaytarish mumkin emas, chunki raqam foydalanilgan hisoblanadi.""",
        "sim_menu_text": "📋 SIM-kartalar menyusi (bu yerda SIM-kartalarning funksionalligi bo'ladi)",
        "balance_text": "💳 Sizning balansingiz: 0 Telegram Stars",
        "use_buttons": "⚠️ Navigatsiya uchun menyu tugmalaridan foydalaning.",
        "welcome": "Salom, tilni tanlang!",
        "lang_selected": "✅ Til tanlandi: O'zbekcha",
        "choose_lang": "Tilni tanlang!",
        "available_numbers": "📋 Mavjud raqamlar:",
        "payment_text": "💰 Ushbu raqamni 2 haftaga sotib olish uchun 45 Telegram Stars to'lashingiz zarur:",
        "payment_success": "✅ To'lov qabul qilindi!",
        "show_balance": "📊 Bot balansi: {balance} Stars",
        "payment_title": "Virtual raqam ijarasi",
        "payment_description": "2 haftaga raqam ijarasi: {number}",
        "payment_label": "2 hafta raqam ijarasi",
        "start_command": "ℹ️ Botdan foydalanish uchun /start buyrug'ini yuboring."
    }
}

# Asosiy menu yaratish
def get_main_menu(language):
    texts = TEXTS[language]["main_menu"]
    
    if language in ["ar", "hy"]:  # Arab va Arman tillari uchun alohida tartib
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=texts["sim_menu"])],
                [
                    KeyboardButton(text=texts["balance"]),
                    KeyboardButton(text=texts["profile"])
                ],
                [
                    KeyboardButton(text=texts["faq"]),
                    KeyboardButton(text=texts["online"])
                ],
                [KeyboardButton(text=texts["language"])]
            ],
            resize_keyboard=True
        )
    else:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=texts["sim_menu"])],
                [
                    KeyboardButton(text=texts["balance"]),
                    KeyboardButton(text=texts["profile"])
                ],
                [
                    KeyboardButton(text=texts["faq"]),
                    KeyboardButton(text=texts["online"])
                ],
                [KeyboardButton(text=texts["language"])]
            ],
            resize_keyboard=True
        )
    
    return keyboard

# Ortga qaytish buttoni
def get_back_button(language):
    text = TEXTS[language]["back_button"]
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data="back_to_main")]
        ]
    )
    return keyboard

# Raqamlar uchun inline keyboard yaratish
def get_numbers_keyboard():
    buttons = []
    for i, number in enumerate(PHONE_NUMBERS):
        buttons.append([InlineKeyboardButton(text=number, callback_data=f"number_{i}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Til kodini topish
def get_language_code(text):
    for code, lang_text in LANGUAGES.items():
        if lang_text == text:
            return code
    return "en"  # Standart til

# Foydalanuvchi tilini olish
def get_user_language(user_id):
    return user_data.get(user_id, {}).get('language', 'uz')

# Foydalanuvchi ma'lumotlarini saqlash
def save_user_data(user_id, data):
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id].update(data)

# /start komandasi
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    # Foydalanuvchi tilini aniqlash
    user_lang_code = message.from_user.language_code
    if user_lang_code in LANGUAGES:
        default_lang = user_lang_code
    else:
        default_lang = "uz"
    
    # Foydalanuvchi ma'lumotlarini saqlash
    save_user_data(user_id, {
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
        'language': default_lang
    })
    
    welcome_text = TEXTS[default_lang]["welcome"]
    
    await message.answer(
        text=welcome_text,
        reply_markup=get_language_keyboard()
    )
    
    await state.set_state(UserState.choosing_language)

# Til tanlash
@dp.message(UserState.choosing_language)
async def choose_language(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    
    selected_lang = message.text
    lang_code = get_language_code(selected_lang)
    
    if lang_code in LANGUAGES:
        save_user_data(user_id, {'language': lang_code})
        
        greeting = TEXTS[lang_code]["lang_selected"]
        
        await message.answer(
            text=greeting,
            reply_markup=ReplyKeyboardRemove()
        )
        
        await asyncio.sleep(0.5)
        await show_main_menu(message, state, lang_code)
    else:
        error_text = TEXTS["ru"]["choose_lang"]
        await message.answer(
            text=error_text,
            reply_markup=get_language_keyboard()
        )

# Asosiy menuni ko'rsatish
async def show_main_menu(message: types.Message, state: FSMContext, language=None):
    user_id = message.from_user.id
    if not language:
        language = get_user_language(user_id)
    
    await state.set_state(UserState.main_menu)
    
    main_text = TEXTS[language]["main_text"]
    
    await message.answer(
        text=main_text,
        reply_markup=get_main_menu(language)
    )

# Profilni ko'rsatish
@dp.message(F.text.in_([TEXTS[lang]["main_menu"]["profile"] for lang in LANGUAGES if "main_menu" in TEXTS[lang]]))
async def show_profile(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    language = get_user_language(user_id)
    
    await state.set_state(UserState.profile)
    profile_text = TEXTS[language]["profile_text"].format(user_id=user_id)
    await message.answer(
        text=profile_text,
        reply_markup=get_back_button(language)
    )

# Online foydalanuvchilarni ko'rsatish
@dp.message(F.text.in_([TEXTS[lang]["main_menu"]["online"] for lang in LANGUAGES if "main_menu" in TEXTS[lang]]))
async def show_online_users(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    language = get_user_language(user_id)
    
    await state.set_state(UserState.online_users)
    online_count = random.randint(1000, 2000)
    online_text = TEXTS[language]["online_text"].format(count=online_count)
    await message.answer(
        text=online_text,
        reply_markup=get_back_button(language)
    )

# FAQ ko'rsatish
@dp.message(F.text.in_([TEXTS[lang]["main_menu"]["faq"] for lang in LANGUAGES if "main_menu" in TEXTS[lang]]))
async def show_faq(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    language = get_user_language(user_id)
    
    await state.set_state(UserState.faq)
    faq_text = TEXTS[language]["faq_text"]
    await message.answer(
        text=faq_text,
        reply_markup=get_back_button(language)
    )

# Balansni ko'rsatish
@dp.message(F.text.in_([TEXTS[lang]["main_menu"]["balance"] for lang in LANGUAGES if "main_menu" in TEXTS[lang]]))
async def show_balance(message: types.Message):
    user_id = message.from_user.id
    language = get_user_language(user_id)
    
    balance_text = TEXTS[language]["balance_text"]
    await message.answer(
        text=balance_text,
        reply_markup=get_back_button(language)
    )

# SIM karta menyusini ko'rsatish
@dp.message(F.text.in_([TEXTS[lang]["main_menu"]["sim_menu"] for lang in LANGUAGES if "main_menu" in TEXTS[lang]]))
async def show_sim_menu(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    language = get_user_language(user_id)
    
    await state.set_state(UserState.choosing_number)
    
    # Raqamlar ro'yxatini yuborish
    await message.answer(
        text=TEXTS[language]["available_numbers"],
        reply_markup=get_numbers_keyboard()
    )

# Tilni o'zgartirish
@dp.message(F.text.in_([TEXTS[lang]["main_menu"]["language"] for lang in LANGUAGES if "main_menu" in TEXTS[lang]]))
async def change_language(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    language = get_user_language(user_id)
    
    welcome_text = TEXTS[language]["choose_lang"]
    
    await message.answer(
        text=welcome_text,
        reply_markup=get_language_keyboard()
    )
    
    await state.set_state(UserState.choosing_language)

# Raqamni tanlash
@dp.callback_query(F.data.startswith("number_"))
async def choose_number(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = get_user_language(user_id)
    
    number_index = int(callback.data.split("_")[1])
    selected_number = PHONE_NUMBERS[number_index]
    
    # To'lov haqida xabar
    payment_text = f"{TEXTS[language]['payment_text']}\n\n{selected_number}"
    
    # Xabarni yuborish
    await callback.message.answer(payment_text)
    
    # To'lovni boshlash
    await send_invoice(callback, language, selected_number)
    await callback.answer()

# To'lov invoice yuborish
async def send_invoice(callback: types.CallbackQuery, language: str, number: str):
    prices = [LabeledPrice(label=TEXTS[language]["payment_label"], amount=45)]  
    
    try:
        await callback.bot.send_invoice(
            chat_id=callback.from_user.id,
            title=TEXTS[language]["payment_title"],
            description=TEXTS[language]["payment_description"].format(number=number),
            payload=f"number_payment_{number}",
            provider_token="",  # Bu yerga to'lov provayder tokenini qo'yishingiz kerak
            currency="XTR",
            prices=prices,
            start_parameter="number-payment"
        )
    except Exception as e:
        print(f"Invoice yuborishda xatolik: {e}")
        await callback.message.answer("⚠️ To'lov tizimida muammo yuzaga keldi. Iltimos, keyinroq urinib ko'ring.")

# To'lovni qabul qilish
@dp.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# Muvaffaqiyatli to'lov
@dp.message(F.successful_payment)
async def successful_payment(message: types.Message, state: FSMContext):
    global bot_balance
    bot_balance += message.successful_payment.total_amount
    
    user_id = message.from_user.id
    language = get_user_language(user_id)
    
    await message.answer(TEXTS[language]["payment_success"])
    
    # Asosiy menyuga qaytish
    await show_main_menu(message, state, language)

# Callback query handler (ortga qaytish)
@dp.callback_query(F.data == "back_to_main")
async def back_to_main(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    language = get_user_language(user_id)
    
    await callback.message.delete()
    
    await state.set_state(UserState.main_menu)
    await show_main_menu(callback.message, state, language)
    
    await callback.answer()

# Boshqa xabarlar uchun handler
@dp.message()
async def handle_other_messages(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == UserState.main_menu:
        user_id = message.from_user.id
        language = get_user_language(user_id)
        
        if not language or language not in TEXTS:
            language = "uz"
        
        use_buttons = TEXTS[language]["use_buttons"]
        await message.answer(use_buttons)
    elif current_state is None:
        user_id = message.from_user.id
        language = get_user_language(user_id)
        
        if not language or language not in TEXTS:
            language = "uz"
        
        await message.answer(TEXTS[language]["start_command"])

# Asosiy ishga tushirish
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())