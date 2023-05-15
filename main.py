import logging

from aiogram import Bot, Dispatcher, types, executor

import pandas as pd

from waiting_list import queue, members_cash, neighbour_cash
from config_reader import config
from keyboards import keyboard
from text_information import WELCOME_MESSAGE, INFO, GROUP_LINK, CHAT_ID


bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)


async def on_startup(_):
    print("I'm started.")


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer(text=f'{WELCOME_MESSAGE}'
                         '\nPlease enter number of your apartment.',
                         parse_mode='HTML',
                         reply_markup=keyboard.kb_startup_menu)


@dp.callback_query_handler(text=['info'])
async def cmd_info(callback: types.CallbackQuery):
    await callback.message.answer(text=INFO,
                                  parse_mode='HTML',
                                  reply_markup=keyboard.kb_info_menu)


@dp.callback_query_handler(text=['check_apartment'])
async def cmd_check(callback: types.CallbackQuery):
    await callback.message.answer(text='Enter number of your apartment.')


@dp.message_handler(content_types=types.ContentType.TEXT)
async def number_handler(message: types.Message):
    df = pd.read_csv('data/apartments.csv')
    apart_col = df['apartments']
    msg = int(message.text)

    if msg not in apart_col:
        await message.answer('This apartment number does not exist.'
                             '\nPlease try again.')

    else:
        user_id = df.loc[df['apartments'] == msg, 'owner_id'].item()
        members_cash[message.from_user.id] = msg

        if user_id == 0:
            # df.loc[apart_col == msg, 'owner_id'] = message.from_user.id
            # df.to_csv('data/apartments.csv', index=False)
            await message.answer(text='Access granted, please follow the link.\n'
                                      f'{GROUP_LINK}')

        else:
            queue[user_id] = message.from_user.id
            neighbour_cash[message.from_user.id] = True
            await bot.send_message(chat_id=user_id,
                                   text='Hello!\n'
                                        f'User @{message.from_user.username} '
                                        f'requests access to the chat at home.'
                                        f'\nIs this your roommate?',
                                   reply_markup=keyboard.kb_yes_no)


@dp.callback_query_handler(lambda c: c.data in ['yes', 'no'])
async def process_callback_button(callback_query: types.CallbackQuery):
    user_1 = queue[callback_query.from_user.id]

    if callback_query.data == 'yes':
        invite_link = await bot.export_chat_invite_link(chat_id=CHAT_ID)
        await bot.send_message(chat_id=user_1,
                               text='Access granted, please follow the link.\n'
                                    f'{invite_link}')
        # df = pd.read_csv('data/apartments.csv')
        # df.loc[df['owner_id'] == callback_query.from_user.id, 'neighbor_id'] = user_1
        # df.to_csv('data/apartments.csv', index=False)
        del queue[callback_query.from_user.id]

    elif callback_query.data == 'no':
        del members_cash[user_1]
        await bot.send_message(chat_id=user_1,
                               text='Access denied.')
        del queue[callback_query.from_user.id]


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def handle_new_chat_members(message: types.Message):
    new_members = message.new_chat_members

    df = pd.read_csv('data/apartments.csv')

    for member in new_members:
        user_id = member.id
        number = members_cash[user_id]

        if user_id in neighbour_cash:
            df.loc[df['apartments'] == number, 'neighbor_id'] = user_id
            del neighbour_cash[user_id]
        else:
            df.loc[df['apartments'] == number, 'owner_id'] = user_id

        df.to_csv('data/apartments.csv', index=False)
        del members_cash[user_id]


@dp.message_handler(content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def handle_left_chat_member(message: types.Message):
    user_id = message.left_chat_member.id

    df = pd.read_csv('data/apartments.csv')

    df.loc[df['owner_id'] == user_id, 'owner_id'] = 0
    df.loc[df['neighbor_id'] == user_id, 'neighbor_id'] = 0
    df.to_csv('data/apartments.csv', index=False)


if __name__ == "__main__":
    executor.start_polling(dispatcher=dp,
                           skip_updates=True,
                           on_startup=on_startup)
