from aiogram import Bot


async def send_order_to_admin(admin_id, order_type, order, bot: Bot):
    await bot.send_message(chat_id=admin_id, text=f'Поступила новая заявка, тип заявки {order_type}')
    print(order)
    message = ''.join(f'{i + 1}. {elem}: {order[elem]}\n' for i, elem in enumerate(order))
    await bot.send_message(chat_id=admin_id, text=message)
