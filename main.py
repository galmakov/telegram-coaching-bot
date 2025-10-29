import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from telegram.constants import ParseMode

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8281150360:AAEHkDvp9XCWtE9XTNRZfJUE7LA4wILBz2o"
GROUP_CHAT_ID = -1002798600170
OWNER_ID = 204234630  # Твій User ID

class CoachingBot:
    def __init__(self):
        self.help_keywords = {
            "питання": ["як", "що", "чому", "якщо", "чи", "де"],
            "проблема": ["не вдається", "не можу", "затруднення", "застряг"],
            "запит": ["допоможи", "порадь", "підскажи"],
            "мета": ["хочу", "мета", "план", "мрія"]
        }
        self.pending_responses = {}  # {message_id: (username, original_text)}
    
    def is_coaching_request(self, text):
        text_lower = text.lower()
        if "#коуч" in text:
            return True
        for keywords in self.help_keywords.values():
            if any(kw in text_lower for kw in keywords):
                return True
        return False

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
            logger.info(f"🎯 Коучинг запит! Перенаправляю...")
            
            # Перенаправляємо запит тобі
            forward_text = f"📨 НОВИЙ КОУЧИНГ ЗАПИТ\n\n👤 {username}:\n💬 \"{text}\"\n\nЯ очікую твою відповідь!"
            
            msg = await context.bot.send_message(
                chat_id=OWNER_ID,
                text=forward_text,
                parse_mode=ParseMode.HTML
            )
            
            # Зберігаємо інформацію для подальшої відповіді
            coaching_bot.pending_responses[msg.message_id] = {
                "group_chat_id": GROUP_CHAT_ID,
                "username": username,
                "original_text": text,
                "original_message_id": update.message.message_id
            }
            
            logger.info(f"✅ Запит перенаправлено!")
        else:
            logger.info("⏭️  Не коучинг")
    
    except Exception as e:
        logger.error(f"❌ Помилка: {e}")

async def handle_reply(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробка твоєї відповіді на коучинг запит"""
    try:
        if not update.message.reply_to_message:
            return
        
        original_msg_id = update.message.reply_to_message.message_id
        
        if original_msg_id not in coaching_bot.pending_responses:
            return
        
        coaching_data = coaching_bot.pending_responses[original_msg_id]
        response_text = update.message.text or ""
        
        logger.info(f"💬 Генеруюється відповідь...")
        
        # Надсилаємо твою відповідь в групу
        final_response = f"{coaching_data['username']}, {response_text}"
        
        await context.bot.send_message(
            chat_id=coaching_data["group_chat_id"],
            text=final_response,
            reply_to_message_id=coaching_data["original_message_id"],
            parse_mode=ParseMode.HTML
        )
        
        # Видаляємо з очікування
        del coaching_bot.pending_responses[original_msg_id]
        
        logger.info("✅ Відповідь надіслана в групу!")
    
    except Exception as e:
        logger.error(f"❌ Помилка при відправці відповіді: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start"""
    await update.message.reply_text(
        "🤖 Привіт! Я - коучинг бот.\n\n"
        "Коли хтось запитає в групі - я перенаправлю тобі.\n"
        "Просто відповідь на моє повідомлення, і я надішлю відповідь в групу! 💪"
    )

def main() -> None:
    logger.info("🚀 Запуск бота з перенаправленням...")
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обробники
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.REPLY, handle_reply))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ Бот готовий!")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=False)

if __name__ == '__main__':
    main()
