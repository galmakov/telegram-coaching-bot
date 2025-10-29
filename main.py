import logging
import smtplib
from email.mime.text import MIMEText
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import pytz

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8281150360:AAEHkDvp9XCWtE9XTNRZfJUE7LA4wILBz2o"
OWNER_ID = 204234630

# Gmail налаштування
GMAIL = "galmakov@gmail.com"
PASSWORD = "rsil ufnp oosb ilgm"

# Київський часовий пояс
KYIV_TZ = pytz.timezone('Europe/Kyiv')

def send_email(text):
    """Відправляє звіт на пошту"""
    try:
        msg = MIMEText(text)
        msg['Subject'] = "📊 Щоденний звіт з групи Телеграму"
        msg['From'] = GMAIL
        msg['To'] = GMAIL
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL, PASSWORD)
        server.send_message(msg)
        server.quit()
        logger.info("✅ Email відправлений")
        return True
    except Exception as e:
        logger.error(f"❌ Помилка при відправці email: {e}")
        return False

def get_report_text():
    """Генерує текст звіту"""
    return (
        "📊 ЗВІТ З ГРУПИ: ЧАТ РАНКОВОГО КЛУБУ\n\n"
        f"📅 Період: {datetime.now(KYIV_TZ).strftime('%d.%m.%Y')}\n\n"
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

async def send_daily_report(application: Application) -> None:
    """Відправляє щоденний звіт"""
    report_text = get_report_text()
    
    try:
        # Відправляємо в телеграм
        await application.bot.send_message(chat_id=OWNER_ID, text=report_text)
        logger.info(f"✅ Звіт відправлений в Телеграм о {datetime.now(KYIV_TZ).strftime('%H:%M')}")
    except Exception as e:
        logger.error(f"❌ Помилка при відправці в Телеграм: {e}")
    
    # Відправляємо на пошту
    send_email(report_text)

async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /report для ручної відправки звіту"""
    report_text = get_report_text()
    
    # Відправляємо в телеграм
    await update.message.reply_text(report_text)
    
    # Відправляємо на пошту
    send_email(report_text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start"""
    await update.message.reply_text(
        "🤖 Привіт! Я - бот для звітів групи.\n\n"
        "📝 Доступні команди:\n"
        "/report - отримати щоденний звіт (ручна відправка)\n\n"
        "⏰ Автоматична відправка щодня о 5:00 за київським часом\n"
        "💪 Готовий допомогти!"
    )

def main() -> None:
    logger.info("🚀 Запуск бота зі звітами...")
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Команди
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("report", report_command))
    
    # Планувальник для автоматичної відправки
    scheduler = BackgroundScheduler(timezone=KYIV_TZ)
    scheduler.add_job(
        send_daily_report,
        'cron',
        hour=5,
        minute=0,
        timezone=KYIV_TZ,
        args=[application]
    )
    scheduler.start()
    logger.info("⏰ Планувальник запущений! Звіти буде відправляти щодня о 05:00 (Київ)")
    
    logger.info("✅ Бот готовий!")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=False)

if __name__ == '__main__':
    main()
