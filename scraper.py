import constants
import sys
import time
from bs4 import BeautifulSoup
import requests
from io import BytesIO

# Assign default character encoding
if sys.version_info[0] < 3:
    sys.setdefaultencoding('utf8')
else:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

# Telegram bot token and channel ID
bot_token = constants.bot_token
channel_id = constants.channel_id

# URL of the website you want to scrape
source = 'https://qefira.com.et/listings/'


def send_message(chat_id, message, token):
    """
    Send a message to a Telegram channel.

    Args:
        chat_id: Telegram channel username.
        message: Message to be sent.
        token: Bot token.

    Returns:
        dict: Response from Telegram API.
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=payload)
    return response.json()


def send_photo(chat_id, photo, caption, token):
    """
    Send a photo to a Telegram channel.

    Args:
        chat_id: Telegram chat ID.
        photo: Photo to be sent as a BytesIO object.
        caption: Caption for the photo.
        token: Telegram bot token.

    Returns:
        dict: Response from Telegram API.
    """
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        'chat_id': chat_id,
        'caption': caption,
        'parse_mode': 'HTML'
    }
    files = {
        'photo': photo.getvalue()
    }
    response = requests.post(url, data=payload, files=files)
    return response.json()


def scrape_website(desired_category=None):
    """
    Scrape data from a website and send it to a Telegram channel.

    Args:
        desired_category: The desired category to filter the scraped data (optional).
    """
    try:
        # Send a GET request to the website
        response = requests.get(source)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the content of the request with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            items = soup.find_all(lambda tag: tag.name == 'article' and 'hp-listing' in tag.get('class', []))
            for item in items:
                # Extract categories
                categories = item.find('div', class_='hp-listing__categories')
                category_list = [a.text for a in categories.find_all('a')] if categories else []

                # Check if desired_category is provided and if item belongs to that category
                if desired_category and desired_category.lower() not in [cat.lower() for cat in category_list]:
                    continue  # Skip this item as it does not match the desired category

                # Extract item details
                title = item.find('h4', class_='hp-listing__title')
                name = title.text.strip()
                link = title.find('a').get('href')
                image_url = item.find('img').get('src')
                image = BytesIO(requests.get(image_url, stream=True).content)
                added_on = item.find('time').text.strip().replace('Added on ', '')
                price = item.find('div', class_='hp-listing__attribute hp-listing__attribute--price-range').text.replace(
                    ' Price: ', '')
                phone = (item.find('div', class_='hp-listing__attribute hp-listing__attribute--phone-number').text.replace(
                    ' Phone: 0', ''))

                # Message to be sent to the channel
                caption = (f'<b>{name}</b>\n\n'
                           f'Price: {price}\n\n'
                           f'Call the provider: +251{phone}\n\n'
                           f'Posted on: {added_on}\n\n\n\n'
                           f'<a href="{link}">View on site</a>')

                if image:
                    send_photo(chat_id=channel_id, photo=image, caption=caption, token=bot_token)
                else:
                    send_message(chat_id=channel_id, message=caption, token=bot_token)

                # Take a rest after every message
                time.sleep(5)

        else:
            print("Failed to retrieve the website")
    except Exception as e:
        print(f"An error occurred: {e}")
