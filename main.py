import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8281150360:AAEHkDvp9XCWtE9XTNRZfJUE7LA4wILBz2o")
GROUP_CHAT_ID = -1002798600170

class CoachingBot:
    def __init__(self):
        self.help_keywords = {
            "питання": ["як", "що", "чому", "якщо", "чи", "де"],
            "проблема": ["не вдається", "не можу", "затруднення", "застряг", "проблема"],
            "запит": ["допоможи", "порадь", "підскажи"],
            "мета": ["хочу", "мета", "план", "мрія"]
        }
    
    def is_coaching_request(self, text):
        text_lower = text.lower()
        if "#коуч" in text:
            return True
        for keywords in self.help_keywords.values():
            if any(kw in text_lower for kw in keywords):
                return True
        return False
    
    def generate_response(self, text, username):
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in self.help_keywords['питання']):
            return f"{username}, хороше питання! 🎯\n\nРозповідь мені більше:\n• Що саме тебе цікавить?\n• Яка твоя ситуація?\n• Що ти спробував?\n\nЗ деталями я дам конкретну пораду. 💡"
        
        if any(kw in text_lower for kw in self.help_keywords['проблема']):
            return f"{username}, розумію. 💪\n\nНо це можливість для росту! Давай розібратись:\n• Що не вдається?\n• Коли це почалось?\n• Що ти спробував?\n\nЗнайдемо рішення. 🔍"
        
        if any(kw in text_lower for kw in self.help_keywords['мета']):
            return f"{username}, чудово! 🎯\n\nТепер план:\n• Яка точно мета?\n• Коли досягти?\n• Перші 3 кроки?\n\nДавай! 🚀"
        
        return f"{username}, я слухаю. 👂\n\nРозповідь мені більше про твою проблему. 🤔"

coaching_bot = CoachingBot()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        if update.message.from_user.is_bot:
            return
        
        text = update.message.text or ""
        username = update.message.from_user.first_name or "Друже"
        chat_id = update.message.chat_id
        
        logger.info(f"📨 {username}: {text[:80]}")
        
        if chat_id != GROUP_CHAT_ID:
            return
        
        if coaching_bot.is_coaching_request(text):
            logger.info(f"🎯 Коучинг запит!")
            response = coaching_bot.generate_response(text, username)
            await update.message.reply_text(response, parse_mode=ParseMode.HTML)
            logger.info("✅ Відповідь надіслана!")
        else:
            logger.info("⏭️  Не коучинг")
    
    except Exception as e:
        logger.error(f"❌ Помилка: {e}")

def main() -> None:
    logger.info("🚀 Запуск бота (polling)...")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("✅ Бот готовий!")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=False)

if __name__ == '__main__':
    main()
