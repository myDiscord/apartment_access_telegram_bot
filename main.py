import logging

from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import pandas as pd

from config_reader import config
from keyboards import keyboard
from text_information import *
from waiting_list import queue

storage = MemoryStorage()
bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher(bot=bot,
                storage=storage)

logging.basicConfig(level=logging.INFO)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message) -> None:
    await message.answer(text=f'{WELCOME_MESSAGE}'
                         '\nPlease enter number of your apartment.',
                         reply_markup=keyboard.kb_startup_menu)


@dp.callback_query_handler(text=['info'])
async def cmd_info(callback: types.CallbackQuery) -> None:
    await callback.message.answer(text=INFO,
                                  reply_markup=keyboard.kb_info_menu)


@dp.callback_query_handler(text=['check_apartment'])
async def cmd_check(callback: types.CallbackQuery) -> None:
    await callback.message.answer(text='Enter number of your apartment.')


@dp.message_handler(content_types=types.ContentType.TEXT)
async def number_handler(message: types.Message) -> None:
    df = pd.read_csv('data/apartments.csv')
    room = message.text
    owner = df.loc[df['room'] == room, 'owner_id'].item()

    if room in df['room'].values:

        if owner == 0:
            queue[message.from_user.id] = [message.from_user.id, room]
            await message.answer(text='Access granted, please follow the link.\n'
                                      f'{GROUP_LINK}')

        else:
            queue[message.from_user.id] = [owner, room]
            try:
                await bot.send_message(chat_id=owner,
                                       text='Hello!\n'
                                            f'User @{message.from_user.username} '
                                            f'requests access to the chat at home.'
                                            f'\nIs this your roommate?',
                                       reply_markup=keyboard.kb_yes_no)
            except BlockingIOError:
                await message.answer(text='Error, the bot is blocked by the owner.')
    else:
        await message.answer(text='This number does not exist, please try again.')


def find_key(owner_id):
    for neighbor_id, value in queue.items():
        if value[0] == owner_id:
            return neighbor_id


@dp.callback_query_handler(lambda c: c.data in ['yes', 'no'])
async def process_callback_button(callback_query: types.CallbackQuery):
    user_1 = queue[find_key(callback_query.from_user.id)]

    if callback_query.data == 'yes':
        invite_link = await bot.export_chat_invite_link(chat_id=CHAT_ID)
        await bot.send_message(chat_id=user_1,
                               text='Access granted, please follow the link.\n'
                                    f'{invite_link}')

    elif callback_query.data == 'no':
        await bot.send_message(chat_id=user_1,
                               text='Access denied.')

        del queue[callback_query.from_user.id]


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS)
async def handle_new_chat_members(message: types.Message):
    new_members = message.new_chat_members

    owner, room = queue[message.from_user.id]

    df = pd.read_csv('data/apartments.csv')

    for member in new_members:
        user_id = member.id

        if user_id != owner:
            df.loc[df['room'] == room, 'neighbor_id'] = user_id
        else:
            df.loc[df['room'] == room, 'owner_id'] = user_id

        df.to_csv('data/apartments.csv', index=False)

    del queue[message.from_user.id]


@dp.message_handler(content_types=types.ContentType.LEFT_CHAT_MEMBER)
async def handle_left_chat_member(message: types.Message):
    user_id = message.left_chat_member.id

    df = pd.read_csv('data/apartments.csv')

    df.loc[df['owner_id'] == user_id, 'owner_id'] = df.loc[df['owner_id'] == user_id, 'neighbor_id']
    df.loc[df['neighbor_id'] == user_id, 'neighbor_id'] = 0

    df.to_csv('data/apartments.csv', index=False)


if __name__ == "__main__":
    executor.start_polling(dispatcher=dp,
                           skip_updates=True)
