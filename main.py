from telethon import TelegramClient, events
import os

# --- بياناتك الأساسية ---
API_ID = 9192208
API_HASH = 'b63a6ff44f1a7df70b0e04ae08374ff9'

# ID الحساب اللي هيستلم ويخزن (المخزن السري)
STORAGE_ID = 602487074 

# اسم ملف الجلسة (تأكد من رفع ملف acc1.session مع الكود)
client = TelegramClient('acc1', API_ID, API_HASH)

@client.on(events.NewMessage(incoming=True))
async def handler(event):
    # الكشف على أي ميديا (صورة أو فيديو) مؤقتة (View Once)
    is_view_once = False
    if event.media:
        # فحص خاصية التايمر (TTL)
        if hasattr(event.media, 'ttl_seconds') and event.media.ttl_seconds is not None:
            is_view_once = True
            
    if is_view_once:
        print(f"📸 اكتشاف وسائط مؤقتة من {event.chat_id}.. جاري المعالجة")
        try:
            # 1. تحميل الملف مؤقتاً على السيرفر
            path = await event.download_media()
            
            if path:
                # 2. جلب معلومات المرسل لتوثيقها في المخزن
                sender = await event.get_sender()
                name = f"{sender.first_name} {sender.last_name or ''}"
                user = f"@{sender.username}" if sender.username else "بدون يوزر"
                
                caption_text = (
                    f"🔓 **تم فك صورة مؤقتة بنجاح**\n\n"
                    f"👤 **المرسل:** {name}\n"
                    f"🆔 **اليوزر:** {user}\n"
                    f"🔗 **المصدر:** `{event.chat_id}`"
                )

                # 3. إرسال الملف للمخزن كصورة دائمة (ملف جديد تماماً)
                # ده الحل النهائي لمشكلة "منتهية الصلاحية"
                await client.send_file(STORAGE_ID, path, caption=caption_text)
                
                # 4. مسح الملف من السيرفر فوراً للأمان ولتوفير المساحة
                os.remove(path)
                print("✅ تمت العملية بنجاح وأرسلت للمخزن.")
                
        except Exception as e:
            print(f"❌ حدث خطأ تقني: {e}")

# تشغيل الكود
print("🚀 الكود يعمل الآن على السيرفر 24 ساعة...")
client.start()
client.run_until_disconnected()
