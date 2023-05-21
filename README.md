# Apartment Access Control Bot

This is a Telegram bot implemented using the Aiogram library for managing apartment access control. The bot allows users to request access to an apartment chat group by entering their apartment number. The bot notifies the apartment owner and provides access to the chat group if approved.

## Prerequisites

- Python 3.7 or higher
- Aiogram library
- pandas library

## Getting Started

1. Clone the repository:

   ```
   git clone <repository_url>
   ```

2. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Create a Telegram bot and obtain the API token. You can create a bot and obtain the token by following the [BotFather](https://core.telegram.org/bots#botfather) instructions.

4. Open file ```.env```:

   ```BOT_TOKEN=59684292:AAHaOwbQEkjW2313123
   ```

   Replace `YOUR_BOT_TOKEN` with the token of your Telegram bot.

5. Open a `data/apartments.csv` file and add the apartment information in the following format:

   ```csv
   room,owner_id,neighbor_id
   1-1,0,0
   1-2,0,0
   ...
   ```

   Add as many rows as there are apartments in your building. The `owner_id` and `neighbor_id` columns will be populated automatically by the bot.

6. Customize the messages and keyboard options in the `text_information.py` and `keyboards.py` files according to your requirements.

7. Run the bot:

   ```
   python main.py
   ```

## Usage

- Add bot to group chat.
- Start the bot by sending the `/start` command.
- Enter your apartment number when prompted.
- The bot will check if the entered apartment number exists in the `data/apartments.csv` file.
- If the apartment number is valid:
  - If the apartment is unoccupied (`owner_id` is 0), the bot will grant access to the chat group and provide a link.
  - If the apartment is occupied, the bot will notify the apartment owner and ask for approval.
    - If the owner approves, the bot will grant access to the chat group and provide a link.
    - If the owner denies, the bot will inform the requester.
- If the apartment number is invalid, the bot will ask to try again.

## License

This project is licensed under the [MIT License](LICENSE).