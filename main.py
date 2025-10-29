import logging
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
import google.generativeai as genai

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8281150360:AAEHkDvp9XCWtE9XTNRZfJUE7LA4wILBz2o")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROUP_CHAT_ID = -1002798600170

# Налаштовуємо Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

class CoachingBot:
    def __init__(self):
        self.coaching_prompt = """Ти - коуч з турботливої дисципліни. 
        Характеристики:
        - Чітка та пряма комунікація
        - Фокус на рішеннях та результатах
        - Справжня турбота та емпатія
        - Спонукаєш людину до самостійного розуміння
        - Встановлюєш високі очікування
        - Розмовляєш як приятель, не як вчитель
        
        Відповідай коротко (2-3 речення максимум).
        Запитай уточнюючі питання для кращого розуміння.
        Будь конкретним, не теоретичним.
        Використовуй емодзі відповідно."""
        
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
    
    def generate_gemini_response(self, text, username):
        """Генерує відповідь через Gemini AI"""
        try:
            prompt = f"""{self.coaching_prompt}
            
            Користувач {username} запитує: "{text}"
            
            Дай мудру, розгорнуту відповідь як коуч."""
            
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"❌ Помилка Gemini: {e}")
            return f"{username}, вибачте, технічна помилка. Спробуйте ще раз! 🤖"

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
            logger.info(f"🎯 Коучинг запит! Запитуємо Gemini...")
            
            # Генеруємо відповідь через Gemini
            response = coaching_bot.generate_gemini_response(text, username)
            
            await update.message.reply_text(response, parse_mode=ParseMode.HTML)
            logger.info("✅ Gemini відповідь надіслана!")
        else:
            logger.info("⏭️  Не коучинг")
    
    except Exception as e:
        logger.error(f"❌ Помилка: {e}")

def main() -> None:
    logger.info("🚀 Запуск бота з Gemini AI...")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("✅ Бот готовий!")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=False)

if __name__ == '__main__':
    main()
