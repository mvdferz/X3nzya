import logging
import os
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, CallbackContext

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the bot's commands

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_html(
        rf"Hi {user.mention_html()}, welcome to the NFT Gift Bot! Use /purchase to buy an NFT or /upgrade to upgrade your NFT.",
        reply_markup=ForceReply(selective=True),
    )


def purchase(update: Update, context: CallbackContext) -> None:
    """Handle the /purchase command."""
    update.message.reply_text("Please send me the NFT ID you want to purchase.")
    # Logic for purchasing NFTs would go here


def upgrade(update: Update, context: CallbackContext) -> None:
    """Handle the /upgrade command."""
    update.message.reply_text("Please send me the NFT ID you want to upgrade.")
    # Logic for upgrading NFTs would go here


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.getenv('TELEGRAM_TOKEN'))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("purchase", purchase))
    dispatcher.add_handler(CommandHandler("upgrade", upgrade))

    # Start the Bot
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()