import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import os

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфігурація
BOT_TOKEN = os.getenv("BOT_TOKEN", "8281150360:AAEHkDvp9XCWtE9XTNRZfJUE7LA4wILBz2o")
GROUP_CHAT_ID = -1002798600170

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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробка повідомлень"""
    try:
        # Ігноруємо повідомлення від самого бота
        if update.message.from_user.is_bot:
            return
        
        # Отримуємо інформацію про повідомлення
        text = update.message.text or ""
        username = update.message.from_user.first_name or "Друже"
        chat_id = update.message.chat_id
        
        logger.info(f"📨 Нове повідомлення від {username} (chat_id: {chat_id}): {text[:100]}")
        
        # Перевіряємо чи це групова повідомлення
        if chat_id != GROUP_CHAT_ID:
            logger.info(f"❌ Повідомлення з іншого чату (ID: {chat_id}), ігноруємо")
            return
        
        logger.info(f"✅ Повідомлення з групи! Перевіряємо...")
        
        # Перевіряємо чи це коучинг запит
        if coaching_bot.is_coaching_request(text):
            logger.info(f"🎯 Коучинг запит виявлено!")
            
            # Генеруємо коучингову відповідь
            response = coaching_bot.generate_response(text, username)
            
            logger.info(f"💬 Генеруємо відповідь...")
            
            # Відправляємо відповідь
            await update.message.reply_text(
                response,
                parse_mode=ParseMode.HTML
            )
            logger.info("✅ Відповідь надіслана!")
        else:
            logger.info("⏭️  Не коучинг запит, ігноруємо")
    
    except Exception as e:
        logger.error(f"❌ Помилка: {e}", exc_info=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start"""
    await update.message.reply_text(
        "🤖 Привіт! Я - коуч з турботливої дисципліни.\n\n"
        "Напиши мені своє питання або проблему, і я допоможу! 💪"
    )

def main() -> None:
    """Запуск бота"""
    logger.info("🚀 Запуск бота...")
    
    # Створюємо Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обробники
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаємо бота
    logger.info("✅ Бот готовий! Слухаємо Telegram...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == '__main__':
    main()
