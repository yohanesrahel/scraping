import constants
import time
import requests
import telebot
from scraper import scrape_website

# Initialize the Telegram bot with your token
bot = telebot.TeleBot(constants.bot_token)


@bot.message_handler(commands=['start'])
def start(message):
    """
    Handle the /start command from the user.

    Args:
        message: The Telegram message object.
    """
    # Check if the user provided a category in the message
    words = message.text.split()
    if len(words) > 1:
        # Extract the category from the message
        category = ' '.join(words[1:])
        bot.send_message(message.chat.id, f"Welcome to the Qefira Scraper Bot!\n"
                                          f"Started scraping items in the category: {category}\n"
                                          f"/start category: to scrape specific category products")
        send_updates(message.chat.id, category)
    else:
        bot.send_message(message.chat.id, "Started scraping all items.")
        send_updates(message.chat.id)  # Call scrape_website without specifying a category


@bot.message_handler(commands=['help'])
def help(message):
    """
    Handle the /help command from the user.

    Args:
        message: The Telegram message object.
    """
    bot.send_message(message.chat.id, f"This bot sends updates periodically.\n"
                                      f"Just type /start: to begin receiving updates."
                                      f"/start category: to begin receiving updates.")


def send_updates(chat_id, category=None):
    """
    Send periodic updates to the user based on the specified category.

    Args:
        chat_id: The chat ID of the user.
        category: The category to filter updates (optional).
    """
    if category:
        scrape_website(category)
    else:
        scrape_website()  # Call scrape_website without specifying a category
    time.sleep(60)  # Wait for 60 seconds before checking for new updates


# Start the bot with polling
bot.polling(none_stop=True)
