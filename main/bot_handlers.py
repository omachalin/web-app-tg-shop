import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from django.conf import settings
from main.models import TgUserAllow

bot = telebot.TeleBot(settings.BOT_TG_KEY)

@bot.message_handler(func=lambda message: True)
def all_messages(message):
    if not TgUserAllow.objects.filter(telegram_id=message.from_user.id).exists():
        bot.send_message(message.chat.id, "У вас нет доступа к этому боту")
        return

    markup = InlineKeyboardMarkup()
    web_app_info = WebAppInfo(url=f"{settings.CURRENT_PROTOCOL}{settings.SHOP_DOMAIN}/?tg=1")
    button = InlineKeyboardButton("Открыть мини-приложение", web_app=web_app_info)
    markup.add(button)
    bot.send_message(message.chat.id, "Нажми кнопку:", reply_markup=markup)
