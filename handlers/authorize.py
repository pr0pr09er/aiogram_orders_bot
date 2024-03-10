import os
from typing import Any

from sqlalchemy_file.types import File

from utils import convert_to_pdf

from aiogram.filters import StateFilter
from aiogram.types import Message
from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import Connection, CursorResult

from keyboards.simple_keyboard import make_row_keyboard
from main import admin_ids
from database import FirstOrderData, SecondOrderData, ThirdOrderData, engine, Base
import sqlalchemy as sa

router = Router()


@router.message(StateFilter(None), Command('admin'))
async def authorisation(message: Message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        await message.answer('Добрый день, у вас нет доступа к этой функции',
                             reply_markup=make_row_keyboard(['Вернуться обратно']).as_markup(resize_keyboard=True))
    else:
        await message.answer("""
        Выберите какие заявки вы хотите получить
        Почты Outlook, Битрикс, базы 1C - Выберите первый вариант (/first_orders),
        Заявки на доступ к объектам FaceID - Выберите второй вариант (/second_orders)
        Заявки на установку программного обеспечения - Выберите третий вариант (/third_orders)
        """, reply_markup=make_row_keyboard([
            '/first_orders',
            '/second_orders',
            '/third_orders',
            'Вернуться обратно'
        ]).as_markup(resize_keyboard=True))


def connect_to_database(table: Base, conn: Connection) -> CursorResult[Any]:
    query = sa.select(table)
    result = conn.execute(query)
    return result


async def make_orders(result: CursorResult, message: Message, conn: Connection) -> None:
    result_dict = {elem: [] for elem in result.keys()._keys}  # noqa
    all_orders = result.all()[:]
    print(all_orders)
    if not all_orders:
        await message.answer('Активных заявок нет')
    for i in range(len(all_orders)):
        if type(all_orders[i][5]) is File or type(all_orders[i][8]) is File:
            print('print')
            try:
                file_path = all_orders[i][5]['path']
                await message.answer('Договор с ОЭЗ:')
            except:
                file_path = all_orders[i][8]['path']
                await message.answer('Подписанная СЗ:')
            with open(os.path.join('files/', file_path), 'rb') as file:
                convert_to_pdf.convert_buffer_to_pdf(file, f'output_files/{file_path}')
            with open('output_files/' + file_path + '.pdf', 'r') as new_file:
                await message.answer_document(types.FSInputFile(new_file.name))
        for index, elem in enumerate(result_dict):
            result_dict[elem].append(all_orders[i][index])
    for i in range(len(result_dict['id'])):
        new_message = ''
        for key in result_dict:
            if key != 'document':
                new_message += f'{key}: {result_dict[key][i]}\n'
        await message.answer(new_message)
        conn.close()


@router.message(Command('first_orders'), lambda message: message.from_user.id in admin_ids)
async def get_first_orders(message: Message):
    connection = engine.connect()
    result = connect_to_database(FirstOrderData, connection)
    await make_orders(result, message, connection)


@router.message(Command('second_orders'), lambda message: message.from_user.id in admin_ids)
async def get_second_orders(message: Message):
    connection = engine.connect()
    result = connect_to_database(SecondOrderData, connection)
    await make_orders(result, message, connection)


@router.message(Command('third_orders'), lambda message: message.from_user.id in admin_ids)
async def get_third_orders(message: Message):
    connection = engine.connect()
    result = connect_to_database(ThirdOrderData, connection)
    await make_orders(result, message, connection)
