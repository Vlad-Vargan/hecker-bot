from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    PicklePersistence,
)
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton
)
import logging # used for error detection
from os import environ, path
from dotenv import load_dotenv
load_dotenv()

print("Modules import succesfull")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

ASK_PHONE, POST_NEWS = range(2)

channel_id = environ["CHANNEL_ID"]
start_msg = "Это сплетни ОНЕУ\n\nЧто бы получать или отправлять сплетни нужно зарегестрироваться\n"
registred_msg = "Вы зарегестрированы и можете публиковать сплетни, предоставляйте пруфы вашей инфы"
final_msg = "Отлично, новость появится в завтрашней рассылке сплетен, после проверки модератором"


def start(update, context):
    user_id = update.message.chat_id
    with open("authorized.txt", "r") as auth:
        if str(user_id) in auth.read():
            update.message.reply_text(text = registred_msg)
            return POST_NEWS
    phone_key = [[KeyboardButton(text="Зарегестрироватьcя", request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(phone_key, resize_keyboard=True, one_time_keyboard=True)
    print(update.message.from_user.username , update.message.chat_id)
    update.message.reply_text(text = start_msg, reply_markup=reply_markup)
    return ASK_PHONE

def stop(update, context):
    return -1

def invite(update, context):
    contact = update.message.contact.user_id
    with open("authorized.txt", "a+") as auth:
        auth.write(str(contact)+"\n")
    update.message.reply_text(text=registred_msg, reply_markup = ReplyKeyboardRemove())
    context.bot.forward_message(channel_id, update.message.chat_id, update.message.message_id, \
                                    disable_notification=False, timeout=None)
    return POST_NEWS

def post_news(update, context):
    update.message.reply_text(text = final_msg, reply_markup = ReplyKeyboardRemove())
    context.bot.forward_message(channel_id, update.message.chat_id, update.message.message_id,\
                                    disable_notification=False, timeout=None)
    return POST_NEWS

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    print("Starting bot main_function")

    token = environ["API_KEY"]
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    st = CommandHandler('start', start)

    conv_handler = ConversationHandler(
        entry_points=[
                        CommandHandler('start', start),
                    ],
        states={
            ASK_PHONE: [st, MessageHandler(Filters.contact, invite)],
            POST_NEWS: [st, MessageHandler(Filters.all & ~ Filters.command, post_news)],         
        },
        fallbacks=[CommandHandler('stop', stop)],
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error)
    updater.start_polling()
    print("Bot launched succesfully")
    updater.idle()


if __name__ == '__main__':
    main()