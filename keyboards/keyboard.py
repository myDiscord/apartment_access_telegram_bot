from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

b1 = KeyboardButton('/start')
b2 = KeyboardButton('/info')


kb_startup_menu = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton(text='About the bot', callback_data='info'),
    InlineKeyboardButton(text='Join the chat', callback_data='check_apartment')
)

kb_info_menu = InlineKeyboardMarkup(row_width=1).row(
    InlineKeyboardButton(text='Join the chat', callback_data='check_apartment')
)

kb_yes_no = InlineKeyboardMarkup(row_width=2).row(
    InlineKeyboardButton('Yes', callback_data='yes'),
    InlineKeyboardButton('No', callback_data='no')
)