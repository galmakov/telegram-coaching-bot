import logging
import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application
from telegram.constants import ParseMode
import json

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфігурація
BOT_TOKEN = os.getenv("BOT_TOKEN", "8281150360:AAEHkDvp9XCWtE9XTNRZfJUE7LA4wILBz2o")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://worker-production-1934.up.railway.app")
GROUP_CHAT_ID = -1002798600170
PORT = int(os.getenv("PORT", 8000))

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

class CoachingBot:
    """Коучинг бот з турботливої дисципліни"""
    
    def __init__(self):
        self.help_keywords = {
            "питання": ["як", "що", "чому", "якщо", "чи", "де", "котра", "який"],
            "проблема": ["не вдається", "не можу", "затруднення", "застряг", "не виходить", "складність", "проблема"],
            "запит": ["допоможи", "порадь", "посоветуй", "підскажи", "зроби"],
            "мета": ["хочу", "мета", "план", "цель", "мечта", "прагну", "мрія"]
        }
    
    def is_coaching_request(self, text):
        """Перевірка чи це запит на коучинг"""
        text_lower = text.lower()
        
        # Перевіряємо хештег
        if "#коуч" in text:
            return True
        
        # Перевіряємо ключові слова
        for keywords in self.help_keywords.values():
            if any(kw in text_lower for kw in keywords):
                return True
        
        return False
    
    def generate_response(self, text, username):
        """Генерація коучингової відповіді"""
        text_lower = text.lower()
        
        # Для питань
        if any(kw in text_lower for kw in self.help_keywords['питання']):
            return f"{username}, хороше питання! 🎯\n\nБагато залежить від контексту. Розповідь мені більше:\n• Що саме тебе цікавить?\n• Яка твоя поточна ситуація?\n• Що ти вже спробував?\n\nЗ цими деталями я зможу дати конкретну пораду. 💡"
        
        # Для проблем
        if any(kw in text_lower for kw in self.help_keywords['проблема']):
            return f"{username}, розумію. 💪\n\nНо це - можливість для росту! Давай розібратись:\n• Що саме не вдається?\n• Коли це почалось?\n• Що ти вже спробував?\n\nЗ цією інформацією ми знайдемо рішення. 🔍"
        
        # Для цілей
        if any(kw in text_lower for kw in self.help_keywords['мета']):
            return f"{username}, чудово! 🎯\n\nЦе перший крок. Тепер нам потрібен план:\n• Яка точно твоя мета?\n• Коли ти хочеш це досягти?\n• Які перші 3 кроки?\n\nДавай визначимось! 🚀"
        
        # За замовчуванням
        return f"{username}, я бачу, що у тебе є питання. 👂\n\nРозповідь мені більше - я готовий допомогти. Яка саме твоя проблема? 🤔"

# Ініціалізуємо бота
coaching_bot = CoachingBot()

@app.route('/', methods=['GET'])
def health():
    """Health check"""
    return {"status": "ok", "message": "🤖 Bot is running!"}, 200

@app.route(f'/webhook', methods=['POST'])
def webhook():
    """Webhook для Telegram"""
    try:
        data = request.get_json()
        logger.info(f"📨 Webhook отримано: {json.dumps(data, ensure_ascii=False)[:200]}")
        
        update = Update.de_json(data, bot)
        
        if not update.message or not update.message.text:
            logger.info("❌ Повідомлення без тексту, ігноруємо")
            return {"ok": True}, 200
        
        # Ігноруємо повідомлення від самого бота
        if update.message.from_user.is_bot:
            logger.info("⚠️  Повідомлення від бота, ігноруємо")
            return {"ok": True}, 200
        
        text = update.message.text
        username = update.message.from_user.first_name or "Друже"
        chat_id = update.message.chat_id
        message_id = update.message.message_id
        
        logger.info(f"📨 Нове повідомлення від {username} (chat_id: {chat_id}): {text[:100]}")
        
        # Перевіряємо чи це групова повідомлення
        if chat_id != GROUP_CHAT_ID:
            logger.info(f"❌ Повідомлення з іншого чату (ID: {chat_id}), ігноруємо")
            return {"ok": True}, 200
        
        logger.info(f"✅ Повідомлення з групи! Перевіряємо...")
        
        # Перевіряємо чи це коучинг запит
        if coaching_bot.is_coaching_request(text):
            logger.info(f"🎯 Коучинг запит виявлено!")
            
            # Генеруємо коучингову відповідь
            response = coaching_bot.generate_response(text, username)
            
            logger.info(f"💬 Генеруємо відповідь...")
            
            # Відправляємо відповідь
            bot.send_message(
                chat_id=chat_id,
                text=response,
                reply_to_message_id=message_id,
                parse_mode=ParseMode.HTML
            )
            logger.info("✅ Відповідь надіслана!")
        else:
            logger.info("⏭️  Не коучинг запит, ігноруємо")
        
        return {"ok": True}, 200
    
    except Exception as e:
        logger.error(f"❌ Помилка в webhook: {e}", exc_info=True)
        return {"ok": False, "error": str(e)}, 500

def setup_webhook():
    """Налаштування webhook"""
    try:
        webhook_url = f"{WEBHOOK_URL}/webhook"
        logger.info(f"🔗 Встановлюємо webhook: {webhook_url}")
        
        bot.set_webhook(url=webhook_url)
        logger.info("✅ Webhook встановлено!")
    except Exception as e:
        logger.error(f"❌ Помилка при встановленні webhook: {e}")

if __name__ == '__main__':
    logger.info("🚀 Запуск Flask сервера...")
    setup_webhook()
    app.run(host='0.0.0.0', port=PORT, debug=False)
