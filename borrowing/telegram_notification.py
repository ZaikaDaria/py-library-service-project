import telegram
from library.settings import TELEGRAM_CHAT_ID as chat_id, TELEGRAM_BOT_TOKEN as bot_token

bot = telegram.Bot(token=bot_token)


def send_telegram_notification(message):
    bot.send_message(chat_id=chat_id, text=message)
