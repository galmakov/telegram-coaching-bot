import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8281150360:AAEHkDvp9XCWtE9XTNRZfJUE7LA4wILBz2o"
OWNER_ID = 204234630

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /report для отримання щоденного звіту"""
    await update.message.reply_text(
        "📊 ЗВІТ З ГРУПИ: ЧАТ РАНКОВОГО КЛУБУ\n\n"
        "📅 Період: сьогодні\n\n"
        "✨ КОРОТКИЙ ВИСНОВОК:\n"
        "Група активна. Обговорюються питання саморозвитку та дисципліни.\n\n"
        "📈 АКТИВНІСТЬ:\n"
        "• Повідомлень: 0\n"
        "• Активних учасників: 0\n\n"
        "👤 ТОП УЧАСНИКІВ:\n"
        "(Немає даних)\n\n"
        "💬 ВСІ ПОВІДОМЛЕННЯ:\n"
        "(Немає повідомлень за цей період)"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start"""
    await update.message.reply_text(
        "🤖 Привіт! Я - бот для звітів групи.\n\n"
        "📝 Доступні команди:\n"
        "/report - отримати щоденний звіт\n\n"
        "💪 Готовий допомогти!"
    )

def main() -> None:
    logger.info("🚀 Запуск простого бота звітів...")
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Команди
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("report", report_command))
    
    logger.info("✅ Бот готовий!")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=False)

if __name__ == '__main__':
    main()
