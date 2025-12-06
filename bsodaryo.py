import os
import asyncio
from datetime import datetime
import re
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.tl.types import InputMediaUploadedPhoto
from PIL import Image, ImageDraw, ImageFont
import io

# Konfiguratsiya
API_ID = '36348223'  # my.telegram.org dan oling
API_HASH = '7c9f20953f077b408498280ca469186f'  # my.telegram.org dan oling
PHONE_NUMBER = '+998959708406'

# Kanallar
SOURCE_CHANNEL = '@Daryo'  # Manba kanal
TARGET_CHANNEL = '@BSONewsUz'   # Nisha kanal

# Telethon client yaratish
client = TelegramClient('session_name', API_ID, API_HASH)

def process_text(text):
    """Matnni qayta ishlash: turli elementlarni o'chirish va oxiriga qo'shimcha qo'shish"""
    if not text:
        return ""
    
    # 1. "Reklama" so'zini tekshirish (katta-kichik harflarga sezgir)
    reklama_patterns = ['реклама', 'reklama', 'реклaмa', 'rеklаmа']
    for pattern in reklama_patterns:
        if pattern in text.lower():
            return None
    
    # 2. "https" linklarini o'chirish
    # HTTP/HTTPS linklarini o'chirish
    text = re.sub(r'https?://\S+', '', text)
    
    # 3. Matnni qatorlarga ajratish
    lines = text.split('\n')
    processed_lines = []
    
    # 4. Birinchi paragraph (bo'sh qatorgacha) ni bitta qatorda birlashtirish
    first_paragraph_lines = []
    in_first_paragraph = True
    
    for line in lines:
        # Agar qator bo'sh bo'lsa, birinchi paragraph tugadi
        if not line.strip():
            in_first_paragraph = False
            if first_paragraph_lines:
                # Birinchi paragraphni bitta qatorda birlashtirish
                first_paragraph = ' '.join(line.strip() for line in first_paragraph_lines if line.strip())
                if first_paragraph:
                    processed_lines.append(first_paragraph)
                    first_paragraph_lines = []
            processed_lines.append('')  # Bo'sh qatorni saqlash
            continue
        
        # Agar hali birinchi paragraphda bo'lsak
        if in_first_paragraph:
            first_paragraph_lines.append(line)
        else:
            # Keyingi qatorlarni oddiy ishlash
            # "Batafsil —" ni o'chirish (turli formatlarda)
            batafsil_patterns = [
                r'^Batafsil\s*[—\-:].*',
                r'^batafsil\s*[—\-:].*',
                r'.*Batafsil\s*[—\-:].*',
                r'.*batafsil\s*[—\-:].*',
            ]
            
            line_clean = line
            for pattern in batafsil_patterns:
                line_clean = re.sub(pattern, '', line_clean)
            
            # Agar qator faqat "Batafsil —" dan iborat bo'lsa, butun qatorni o'chiramiz
            if re.search(r'^Batafsil\s*[—\-:]', line, re.IGNORECASE):
                continue
            
            # "👉 Obuna bo'ling — @daryo" va uning variantlarini o'chirish
            daryo_patterns = [
                r'👉 Obuna bo‘ling — @daryo.*',
                r'👉 Obuna bo\'ling — @daryo.*',
                r'👉 Obuna bo\'ling - @daryo.*',
                r'👉 Obuna bo‘ling - @daryo.*',
                r'👉 Obuna bo\'ling—@daryo.*',
                r'👉 Obuna bo‘ling—@daryo.*',
                r'Obuna bo‘ling — @daryo.*',
                r'Obuna bo\'ling — @daryo.*',
                r'^@daryo.*',
                r'^👉 @daryo.*',
                r'^— @daryo.*',
                r'^- @daryo.*',
            ]
            
            for pattern in daryo_patterns:
                line_clean = re.sub(pattern, '', line_clean, flags=re.IGNORECASE)
            
            # Agar qator faqat bu patternlardan iborat bo'lsa, butun qatorni o'chiramiz
            if re.search(r'^(👉 )?Obuna bo\'?ling\s*[—\-]?\s*@daryo', line, re.IGNORECASE):
                continue
            
            # Agar qator bo'sh bo'lmasa, saqlaymiz
            if line_clean.strip():
                processed_lines.append(line_clean)
    
    # Agar birinchi paragraph hali saqlanmagan bo'lsa (agar oxirida bo'sh qator bo'lmasa)
    if first_paragraph_lines:
        first_paragraph = ' '.join(line.strip() for line in first_paragraph_lines if line.strip())
        if first_paragraph:
            processed_lines.append(first_paragraph)
    
    # Qatorlarni birlashtirish
    text = '\n'.join(processed_lines)
    
    # 5. @ bilan boshlanadigan so'zlarni o'chirish (lekin maxsus @ belgilarni saqlash)
    # Avval maxsus @ belgilarni saqlash
    special_mentions = ['@BSONewsUz', '@BSOnewsUZ', '@BSONews', '@BSOnews']
    for mention in special_mentions:
        text = text.replace(mention, 'SPECIAL_MENTION_PLACEHOLDER')
    
    # Boshqa @ bilan boshlanadigan so'zlarni o'chirish
    pattern = r'@\w+'
    text = re.sub(pattern, '', text)
    
    # Maxsus @ belgilarni qaytarish
    for mention in special_mentions:
        text = text.replace('SPECIAL_MENTION_PLACEHOLDER', mention)
    
    # 6. Qo'shimcha bo'shliqlarni tozalash
    # Har bir qatordagi ortiqcha bo'shliqlarni tozalash
    lines = text.split('\n')
    cleaned_lines = []
    for i, line in enumerate(lines):
        # Qatordagi ortiqcha bo'shliqlarni tozalash
        line_clean = re.sub(r'\s+', ' ', line).strip()
        if line_clean:
            cleaned_lines.append(line_clean)
        elif i > 0 and i < len(lines) - 1:  # O'rtadagi bo'sh qatorlarni saqlash
            cleaned_lines.append('')
    
    text = '\n'.join(cleaned_lines)
    
    # 7. Ortiqcha bo'sh qatorlarni tozalash (lekin matn formatini saqlab)
    # Bir nechta ketma-ket bo'sh qatorlarni 2 taga qisqartirish
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
    
    # 8. Agar matn faqat bo'shliq yoki belgilardan iborat bo'lsa
    if not text or text.isspace():
        return ""
    
    # 9. Matnni to'g'ri formatda qaytarish
    # Avval tekshirish, oxirida "👉 @BSOnewsUZ" bormi?
    if not text.strip().endswith("👉 @BSOnewsUZ"):
        # Agar oxirida @BSOnewsUZ bo'lmasa, qo'shamiz
        # Oxiridagi ortiqcha bo'shliqlarni tozalash
        text = text.rstrip()
        # Agar oxiri bo'sh qator bilan tugasa, undan xalos bo'lamiz
        if text.endswith('\n'):
            text = text.rstrip('\n')
        
        # Matnni 2 bo'sh qator bilan ajratib, keyin qo'shimcha matn qo'shamiz
        result = f"{text}\n\n👉 @BSOnewsUZ"
    else:
        # Agar allaqachon bo'lsa, o'zgartirmaymiz
        result = text
    
    return result

def is_video_message(message):
    """Video yoki GIF ekanligini tekshirish"""
    if message.media and isinstance(message.media, MessageMediaDocument):
        document = message.media.document
        if document:
            mime_type = document.mime_type or ''
            
            # Video formatlarini aniqlash
            video_attributes = [attr for attr in document.attributes 
                              if hasattr(attr, 'video') or 'video' in str(attr).lower()]
            
            # GIF formatini aniqlash
            gif_attributes = [attr for attr in document.attributes 
                            if hasattr(attr, 'animated') or 'gif' in str(attr).lower()]
            
            # Video yoki GIF bo'lsa
            if 'video' in mime_type.lower() or video_attributes or gif_attributes:
                return True
    
    return False

async def add_text_to_image(image_bytes, file_name="processed_image.jpg"):
    """Rasmga @BSONewsUz matnini chizish"""
    try:
        # Bytes ni ochib olish
        image = Image.open(io.BytesIO(image_bytes))
        
        # Rasm formatini tekshirish va konvert qilish
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Rasm o'lchamlarini olish
        width, height = image.size
        
        # Draw object yaratish
        draw = ImageDraw.Draw(image)
        
        # Matn
        text = "@BSONewsUz"
        
        # Fontni aniqlash
        font = None
        font_size = min(width, height) // 15
        
        try:
            # Tizimdagi fontlarni sinab ko'rish
            font_paths = [
                "arial.ttf",  # Windows
                "Arial.ttf",  # Windows
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux Debian
                "C:/Windows/Fonts/arial.ttf",  # Windows full path
            ]
            
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    print(f"✅ Font topildi: {font_path}")
                    break
                except:
                    continue
            
        except Exception as e:
            print(f"❌ Font xatosi: {e}")
        
        # Agar font topilmasa, default font yaratish
        if font is None:
            print("⚠️ Font topilmadi, default font ishlatilmoqda...")
            try:
                font = ImageFont.load_default()
                text_width = len(text) * font_size // 2
                text_height = font_size
            except:
                print("⚠️ Default font ham ishlamadi, oddiy chizish...")
                text_width = len(text) * font_size // 2
                text_height = font_size
        
        # Matn o'lchamini hisoblash
        try:
            if font:
                text_bbox = draw.textbbox((0, 0), text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
            else:
                text_width = len(text) * font_size // 2
                text_height = font_size
        except:
            text_width = len(text) * font_size // 2
            text_height = font_size
        
        # Matn joylashuvi (o'ng pastki burchak)
        margin = 20
        x = width - text_width - margin
        y = height - text_height - margin
        
        # Agar koordinatalar manfiy bo'lsa, to'g'irlash
        x = max(10, x)
        y = max(10, y)
        
        # Matn atrofida fon qo'shish
        padding = 5
        draw.rectangle(
            [x - padding, y - padding, x + text_width + padding, y + text_height + padding],
            fill=(0, 0, 0, 150)
        )
        
        # Matn rangi (oq)
        text_color = (255, 255, 255, 255)
        
        # Matnni chizish
        if font:
            draw.text((x, y), text, font=font, fill=text_color)
        else:
            draw.text((x, y), text, fill=text_color)
        
        # Rasmni RGB formatiga o'tkazish
        result_image = image.convert('RGB')
        
        # Vaqtincha faylga saqlash
        temp_file = f"temp_{file_name}"
        result_image.save(temp_file, format='JPEG', quality=95)
        
        return temp_file
        
    except Exception as e:
        print(f"❌ Rasmga matn chizishda xatolik: {str(e)}")
        return None

async def process_single_photo(message, caption, target_entity):
    """Bitta rasmni qayta ishlash va yuborish"""
    try:
        # Vaqtincha fayl nomi
        temp_file = f"temp_photo_{message.id}.jpg"
        
        # Rasmni yuklab olish
        await message.download_media(file=temp_file)
        
        # Faylni o'qish
        with open(temp_file, 'rb') as f:
            image_bytes = f.read()
        
        # Rasmga matn chizish
        processed_file = await add_text_to_image(image_bytes, f"processed_{message.id}.jpg")
        
        if processed_file and os.path.exists(processed_file):
            # Qayta ishlangan rasmni yuborish
            await client.send_file(
                target_entity,
                processed_file,
                caption=caption if caption and caption.strip() else None,
                parse_mode='html'
            )
            
            # Vaqtincha fayllarni o'chirish
            if os.path.exists(temp_file):
                os.remove(temp_file)
            if os.path.exists(processed_file):
                os.remove(processed_file)
                
            return True
        else:
            # Agar rasmga matn chizish ishlamasa, oddiy yuborish
            print("⚠️ Rasmga matn chizish ishlamadi, oddiy rasm yuborilmoqda...")
            await client.send_file(
                target_entity,
                temp_file,
                caption=caption if caption and caption.strip() else None,
                parse_mode='html'
            )
            
            # Vaqtincha faylni o'chirish
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
            return True
            
    except Exception as e:
        print(f"❌ Bitta rasmni qayta ishlashda xatolik: {str(e)}")
        # Fayllarni tozalash
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False

async def process_album_photos(all_messages, caption, target_entity):
    """Albom rasmlarini qayta ishlash va yuborish"""
    try:
        processed_files = []
        temp_files = []
        
        for i, msg in enumerate(all_messages):
            if msg.media and isinstance(msg.media, MessageMediaPhoto):
                try:
                    # Vaqtincha fayl nomi
                    temp_file = f"temp_album_{msg.id}_{i}.jpg"
                    
                    # Rasmni yuklab olish
                    await msg.download_media(file=temp_file)
                    temp_files.append(temp_file)
                    
                    # Faylni o'qish
                    with open(temp_file, 'rb') as f:
                        image_bytes = f.read()
                    
                    # Rasmga matn chizish
                    processed_file = await add_text_to_image(image_bytes, f"processed_album_{msg.id}_{i}.jpg")
                    
                    if processed_file and os.path.exists(processed_file):
                        processed_files.append(processed_file)
                        print(f"📷 Rasm {i+1} qayta ishlandi")
                    else:
                        # Agar ishlamasa, oddiy rasmni qo'shamiz
                        if os.path.exists(temp_file):
                            processed_files.append(temp_file)
                            print(f"📷 Rasm {i+1} oddiy saqlandi")
                        
                except Exception as e:
                    print(f"⚠️ Rasm {i} qayta ishlashda xatolik: {str(e)}")
        
        # Agar kamida bitta rasm bo'lsa
        if processed_files:
            # Barcha rasmlarni yuborish
            await client.send_file(
                target_entity,
                processed_files,
                caption=caption if caption and caption.strip() else None,
                parse_mode='html'
            )
            
            # Vaqtincha fayllarni o'chirish
            for file in temp_files:
                if os.path.exists(file) and file not in processed_files:
                    os.remove(file)
            
            for file in processed_files:
                if os.path.exists(file):
                    os.remove(file)
                    
            return True
        else:
            return False
            
    except Exception as e:
        print(f"❌ Albom rasmlarini qayta ishlashda xatolik: {str(e)}")
        # Fayllarni tozalash
        for file in temp_files:
            if os.path.exists(file):
                os.remove(file)
        for file in processed_files:
            if os.path.exists(file):
                os.remove(file)
        return False

async def main():
    # Clientni ishga tushirish
    await client.start(PHONE_NUMBER)
    print(f"✅ Client ishga tushdi. {PHONE_NUMBER} raqami bilan bog'landi")
    print(f"📥 Manba kanal: {SOURCE_CHANNEL}")
    print(f"📤 Nisha kanal: {TARGET_CHANNEL}")
    print("⏳ Yangi postlar kutilmoqda...")
    print("=" * 50)
    print("MATN QAYTA ISHLASH QOIDALARI:")
    print("1. ❌ 'Reklama' so'zi - POST O'TKAZILMAYDI")
    print("2. ❌ 'https' linklari - O'CHIRILADI")
    print("3. ❌ 'Batafsil —' va variantlari - O'CHIRILADI")
    print("4. ❌ '@daryo' va obuna bo'ling matnlari - O'CHIRILADI")
    print("5. ❌ @ bilan boshlanadigan so'zlar - O'CHIRILADI")
    print("6. ✅ @BSONewsUz, @BSOnewsUZ - SAQLANADI")
    print("7. ✅ Oxiriga '👉 @BSOnewsUZ' - QO'SHILADI")
    print("8. 🖼️ Rasmlarga @BSONewsUz matni - CHIZILADI")
    print("9. ✅ Birinchi paragraph bir qatorda (jirniy) bo'ladi")
    print("=" * 50)

    # Manba kanaldan yangi postlarni kuzatish
    @client.on(events.NewMessage(chats=SOURCE_CHANNEL))
    async def handler(event):
        try:
            message = event.message
            
            # 1. Video/GIF postlarini tekshirish
            if is_video_message(message):
                print(f"❌ Video/GIF posti tashlandi - {datetime.now().strftime('%H:%M:%S')}")
                return
            
            # 2. Asl matnni olish (to'liq matnni log qilish)
            original_text = message.message or ""
            print("📝" + "="*50)
            print("ASL MATN:")
            print(original_text)
            print("="*50)
            
            # 3. Matnni qayta ishlash
            processed_text = process_text(original_text)
            
            # Agar process_text() None qaytarsa, bu "Reklama" so'zi borligini bildiradi
            if processed_text is None:
                print(f"❌ 'Reklama' so'zi tashlandi - {datetime.now().strftime('%H:%M:%S')}")
                return
            
            # 4. Rasm(lar)ni tekshirish
            has_photo = message.media and isinstance(message.media, MessageMediaPhoto)
            
            # Agar hech qanday media bo'lmasa va matn bo'sh bo'lsa, o'tkazish
            if not message.media and not processed_text:
                print(f"⚠️ Bo'sh post - {datetime.now().strftime('%H:%M:%S')}")
                return
            
            print(f"✅ Yangi post qabul qilindi - {datetime.now().strftime('%H:%M:%S')}")
            
            # 5. Qo'shimcha: @burgutuzb ni @BSONewsUz ga almashtirish
            if processed_text:
                processed_text = processed_text.replace('@Daryo', '@BSONewsUz')
                print("📝" + "="*50)
                print("QAYTA ISHLANGAN MATN:")
                print(processed_text)
                print("="*50)
            
            # 6. Nisha kanalni olish
            target_entity = await client.get_entity(TARGET_CHANNEL)
            
            # 7. Postni yuborish
            if has_photo:
                # Agar bu guruhli post bo'lsa (albom)
                if hasattr(message, 'grouped_id') and message.grouped_id:
                    print(f"📸 Albom posti aniqlandi ({message.grouped_id})")
                    
                    # Barcha guruh postlarini topish
                    all_messages = []
                    async for msg in client.iter_messages(message.peer_id, limit=20):
                        if hasattr(msg, 'grouped_id') and msg.grouped_id == message.grouped_id:
                            all_messages.append(msg)
                            if len(all_messages) >= 10:
                                break
                    
                    # Albomni faqat bir marta qayta ishlash - birinchi postni tekshirish
                    if len(all_messages) > 0:
                        # Birinchi postni topish
                        first_post = min(all_messages, key=lambda x: x.id)
                        if message.id != first_post.id:
                            print(f"⚠️ Albom posti allaqachon qayta ishlanmoqda, o'tkazildi")
                            return
                        
                        # Albomdagi barcha postlardan matnni yig'ish
                        album_caption = ""
                        for msg in all_messages:
                            if msg.message:
                                if album_caption:
                                    album_caption += "\n\n" + msg.message
                                else:
                                    album_caption = msg.message
                        
                        # Agar albom caption bo'sh bo'lsa, asosiy caption ishlatiladi
                        if not album_caption.strip():
                            album_caption = processed_text
                        else:
                            # Albom matnini qayta ishlash
                            processed_album_text = process_text(album_caption)
                            if processed_album_text and processed_album_text != "":
                                processed_album_text = processed_album_text.replace('@burgutuzb', '@BSONewsUz')
                                album_caption = processed_album_text
                            else:
                                album_caption = processed_text
                        
                        final_caption = album_caption if album_caption and album_caption.strip() else processed_text
                    else:
                        final_caption = processed_text
                    
                    print(f"📊 Albomdagi rasmlar soni: {len(all_messages)}")
                    
                    # Albom rasmlarini qayta ishlash va yuborish
                    success = await process_album_photos(all_messages, final_caption, target_entity)
                    
                    if success:
                        print(f"✅ Albom posti ({len(all_messages)} rasm) yuborildi - {datetime.now().strftime('%H:%M:%S')}")
                        if final_caption:
                            print(f"📝 Matn uzunligi: {len(final_caption)} belgi")
                    
                else:
                    # Oddiy bitta rasm posti
                    print("📸 Bitta rasm posti")
                    
                    # Rasmni qayta ishlash va yuborish
                    success = await process_single_photo(message, processed_text, target_entity)
                    
                    if success:
                        print(f"✅ Rasm+matn posti yuborildi - {datetime.now().strftime('%H:%M:%S')}")
                        if processed_text:
                            print(f"📝 Matn uzunligi: {len(processed_text)} belgi")
                            
            else:
                # Faqat matn postini yuborish
                if processed_text and processed_text.strip():
                    await client.send_message(target_entity, processed_text, parse_mode='html')
                    print(f"✅ Matn posti yuborildi - {datetime.now().strftime('%H:%M:%S')}")
                    print(f"📝 Matn uzunligi: {len(processed_text)} belgi")
                else:
                    print("⚠️ Bo'sh matn posti, yuborilmadi")
                
        except Exception as e:
            print(f"❌ Xatolik: {str(e)}")

    # Clientni ishga tushirish
    await client.run_until_disconnected()

if __name__ == '__main__':
    # API ma'lumotlarini so'rash
    print("=" * 50)
    print("Telegram Post Ko'chiruvchi Bot")
    print("=" * 50)
    
    # Agar API_ID va API_HASH kiritilmagan bo'lsa
    if API_ID == 'YOUR_API_ID':
        API_ID = input("Telegram API ID ni kiriting (my.telegram.org): ").strip()
        API_HASH = input("Telegram API HASH ni kiriting (my.telegram.org): ").strip()
    
    # Dasturni ishga tushirish
    with client:
        client.loop.run_until_complete(main())