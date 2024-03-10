from aiogram.types import Message
from aiogram.fsm.context import FSMContext


async def repeat_email(message: Message, state: FSMContext, option_group):
    await message.answer('Пожалуйста, введите верную почту!')

    await state.set_state(option_group.waiting_for_email)


async def repeat_phone_number(message: Message, state: FSMContext, option_group):
    await message.answer('Пожалуйста, введите верный номер телефона!')
    await state.set_state(option_group.waiting_for_phone_number)
