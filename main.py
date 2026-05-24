import os
import telebot
import random
import re
from flask import Flask, request

TOKEN = "8575847456:AAE0K2YUmc5Ri77kFwrl14IIMV999ewfpeU"
# الرابط الخاص بمشروعك على Railway
WEBHOOK_URL = "https://web-production-aa4e6.up.railway.app/" 

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__) # تغيير الاسم ليكون متوافقاً تلقائياً مع السيرفر

# --- 1. البيانات ---
GREETING_PARTS_1 = ["يا هلا", "أهلاً", "مرحباً", "نورتنا", "يسعد هالمسا", "تحياتي", "يا مية هلا", "منور"]
GREETING_PARTS_2 = ["يا غالي", "يا بطل", "يا طيب", "يا مبدع", "يا صديقي", "يا ورد", "بطلنا", "يا عيوني"]
KIND_WELCOME = ["يا مرحباً بـ {name}، أشرقت الأنوار بوجودك! 🌟", "أهلاً بـ {name}، نورتنا بوجودك اللطيف! ✨", "بكل ود ومحبة، نرحب بـ {name} معنا. 🌸"]
FLIRT = ["عيونك أجمل من أي كلام.", "أنت شخص مميز جداً.", "وجودك يخلي اليوم أحلى.", "كلامك مثل العسل."]
JOKES = ["محشش سأل أخوه: إيش الفرق بين الأسبوع والصحراء؟ 😂", "بخيل طاح في البير قال أهم شيء ما تشربون الموية! 💸", "غبي دخل الامتحان قال: هو اسم دلع لواحد اسمه وفاء! 😂"] * 67
QUOTES = ["النجاح ليس النهاية. 🚀", "كن أنت التغيير. ✨", "الحياة تجربة شجاعة. 💪", "العلم نور. 💡"] * 33
GAMES = ["حجر ورقة مقص 🪨", "رمي النرد 🎲", "تخمين الرقم 🔢", "لعبة الألغاز 🧠"]
BAD_WORDS = ["سكس", "اباحي", "عري", "نيك", "قذر", "شرموطة"]

# --- 2. التحقق من المشرفين ---
def is_user_admin(message):
    try:
        admins = bot.get_chat_administrators(message.chat.id)
        for admin in admins:
            if admin.user.id == message.from_user.id:
                return True
        return False
    except: return False

# --- 3. الترحيب ---
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new(message):
    for new_user in message.new_chat_members:
        bot.reply_to(message, random.choice(KIND_WELCOME).replace("{name}", new_user.first_name))

# --- 4. المعالج الرئيسي ---
@bot.message_handler(func=lambda m: True)
def handle_all(message):
    text = message.text.lower() if message.text else ""
    chat_id = message.chat.id
    
    # نظام الحماية
    if not is_user_admin(message):
        if re.search(r'http[s]?://|t\.me/|www\.|@', text) or any(word in text for word in BAD_WORDS):
            try:
                bot.delete_message(chat_id, message.message_id)
                return
            except: pass

    # أوامر الإدارة
    if message.reply_to_message and any(cmd in text for cmd in ["طرد", "كتم", "فك كتم", "حظر"]):
        if not is_user_admin(message):
            bot.reply_to(message, "⚠️ عذراً، هذه الأوامر للمشرفين فقط!")
            return
        
        target_id = message.reply_to_message.from_user.id
        if "طرد" in text: bot.kick_chat_member(chat_id, target_id); bot.reply_to(message, "✅ تم الطرد.")
        elif "كتم" in text: bot.restrict_chat_member(chat_id, target_id, can_send_messages=False); bot.reply_to(message, "🔇 تم الكتم.")
        elif "فك كتم" in text: bot.restrict_chat_member(chat_id, target_id, can_send_messages=True); bot.reply_to(message, "✅ تم فك الكتم.")
        elif "حظر" in text: bot.ban_chat_member(chat_id, target_id); bot.reply_to(message, "🚫 تم الحظر.")
        return

    # أوامر عامة
    if text == "لارا":
        bot.reply_to(message, "👩‍💻 **أنا لارا، مساعدتك الذكية!**\nاكتب: نكتة، اقتباس، لعبة، غزلني، أو رحب بي.\n⚙️ **إدارة:** (طرد، كتم، فك كتم، حظر) بالرد على الرسالة.")
    elif any(word in text for word in ["سلام عليكم", "شلونكم", "هلا", "مرحبا", "باي"]):
        bot.reply_to(message, f"{random.choice(GREETING_PARTS_1)} {random.choice(GREETING_PARTS_2)}!")
    elif "غزلني" in text: bot.reply_to(message, random.choice(FLIRT))
    elif "نكتة" in text: bot.reply_to(message, random.choice(JOKES))
    elif "اقتباس" in text: bot.reply_to(message, random.choice(QUOTES))
    elif "لعبة" in text: bot.reply_to(message, f"🎮 أنا اخترت لك: {random.choice(GAMES)}")

# استقبال تحديثات تليجرام
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.stream.read().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# الصفحة الرئيسية لتفعيل الـ Webhook تلقائياً عند زيارتها أو تشغيل السيرفر
@app.route('/')
def webhook_setup():
    bot.remove_webhook()
    status = bot.set_webhook(url=WEBHOOK_URL + TOKEN)
    if status:
        return "تم تفعيل وتحديث البوت بنجاح عبر الـ Webhook! 🚀", 200
    else:
        return "فشل تفعيل الـ Webhook، تحقق من الإعدادات.", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
