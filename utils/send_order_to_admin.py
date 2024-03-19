from aiogram import Bot
from aiogram import types
import os

from sqlalchemy_file import File

from handlers.authorize import connect_to_database

from utils import convert_to_pdf


async def send_order_to_admin(admin_id, order_type, bot: Bot, database, order):
    await bot.send_message(chat_id=admin_id, text=f'Поступила новая заявка, тип заявки: {order_type}')
    result = connect_to_database(database)
    result_dict = {elem: [] for elem in result.keys()._keys} # noqa
    order = result.first()
    if type(order[5]) is File or type(order[8]) is File:
        try:
            file_path = order[5]['path']
            await bot.send_message(admin_id, 'Договор с ОЭЗ:')
        except:
            file_path = order[8]['path']
            await bot.send_message(admin_id, 'Подписанная СЗ:')
        with open(os.path.join('files/', file_path), 'rb') as file:
            convert_to_pdf.convert_buffer_to_pdf(file, f'output_files/{file_path}')
        with open('output_files/' + file_path + '.pdf', 'r') as new_file:
            await bot.send_document(admin_id, types.FSInputFile(new_file.name))
    for index, elem in enumerate(result_dict):
        result_dict[elem].append(order[index])
    message = ''
    for elem in order:
        message += elem + order[elem] + '\n'
    await bot.send_message(admin_id, message)