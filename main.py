import logging
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from anthropic import Anthropic

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8281150360:AAEHkDvp9XCWtE9XTNRZfJUE7LA4wILBz2o")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GROUP_CHAT_ID = -1002798600170

# Налаштовуємо Claude
if not ANTHROPIC_API_KEY:
    logger.error("❌ ANTHROPIC_API_KEY не знайдена!")
    raise ValueError("Missing ANTHROPIC_API_KEY")

client = Anthropic()

class CoachingBot:
    def __init__(self):
        self.coaching_system = """Ти - експертний коуч з турботливої дисципліни. 

ТВОЇ ХАРАКТЕРИСТИКИ:
- Чітка та пряма комунікація (без багатослів'я)
- Фокус на рішеннях та результатах
- Справжня турбота та емпатія
- Спонукаєш людину до самостійного розуміння
- Встановлюєш високі очікування
- Розмовляєш як приятель, не як учитель
- Даєш конкретні, практичні поради

ПРАВИЛА:
1. Відповідай КОРОТКО (2-3 речення максимум)
2. Запитай уточнюючі питання для кращого розуміння
3. Будь конкретним, не теоретичним
4. Використовуй емодзі розумно (не більше 2-3)
5. Фокусуйся на дії, а не на почуттях
6. Давай людині власне рішення знайти, але спрямовуй її

ФОРМАТ:
Починай з імені людини, дай короткий коментар, запитай уточнююче питання або дай конкретний совіт."""
        
        self.help_keywords = {
            "питання": ["як", "що", "чому", "якщо", "чи", "де"],
            "проблема": ["не вдається", "не можу", "затруднення", "застряг"],
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
    
    def generate_claude_response(self, text, username):
        """Генерує відповідь через Claude API"""
        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=300,
                system=self.coaching_system,
                messages=[
                    {
                        "role": "user",
                        "content": f"{username} запитує: \"{text}\"\n\nДай мудру, розгорнуту відповідь як коуч."
                    }
                ]
            )
            
            return message.content[0].text
        except Exception as e:
            logger.error(f"❌ Помилка Claude: {e}")
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
            logger.info(f"🎯 Коучинг запит! Генерую відповідь через Claude...")
            
            # Генеруємо відповідь через Claude
            response = coaching_bot.generate_claude_response(text, username)
            
            logger.info(f"💬 Відповідь готова, надсилаю...")
            
            # Надсилаємо відповідь в групу
            await update.message.reply_text(
                response,
                parse_mode=ParseMode.HTML
            )
            logger.info("✅ Claude відповідь надіслана!")
        else:
            logger.info("⏭️  Не коучинг запит")
    
    except Exception as e:
        logger.error(f"❌ Помилка: {e}")

def main() -> None:
    logger.info("🚀 Запуск бота з Claude AI...")
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обробник повідомлень
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ Бот готовий!")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=False)

if __name__ == '__main__':
    main()
