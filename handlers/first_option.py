import re

from utils.database_utills import session_scope
from utils.errors import repeat_email, repeat_phone_number

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.types import ReplyKeyboardRemove
from keyboards.simple_keyboard import make_row_keyboard
from database import FirstOrderData
from utils.send_order_to_admin import send_order_to_admin

from main import admin_id

router = Router()


# Класс для хранения состояний бота
class FirstOptionGroup(StatesGroup):
    waiting_for_new_or_old_employer = State()
    waiting_for_fio = State()
    waiting_for_email = State()
    waiting_for_position = State()
    waiting_for_basis = State()
    waiting_for_phone_number = State()
    waiting_for_supervisor_name = State()
    waiting_for_project_supervisor_name = State()
    waiting_for_access_resources = State()
    waiting_for_confirm_form = State()
    waiting_for_edit_form = State()
    waiting_for_check_form = State()


@router.message(StateFilter(None), Command("first"))
async def start(message: Message, state: FSMContext):
    await message.answer("Добрый день! Мы готовы приступить к созданию вашей заявки."
                         "Пожалуйста, укажите, желаете ли вы получить новый доступ или"
                         " внести изменения в уже имеющийся."
                         " Выберите соответствующий вариант ответа.",
                         reply_markup=make_row_keyboard(['Новый', 'Изменить старый']).as_markup(
                             resize_keyboard=True))

    await state.set_state(FirstOptionGroup.waiting_for_new_or_old_employer)


@router.message(FirstOptionGroup.waiting_for_new_or_old_employer)
async def process_order_type(message: Message, state: FSMContext):
    await message.answer('Тип заявки сохранен')
    await state.update_data(order_type=message.text)
    await message.answer('Введите своё ФИО в родительном падеже. \nПример: <i><b>Иванова Ивана Ивановича</b></i>.',
                         parse_mode=ParseMode.HTML,
                         reply_markup=make_row_keyboard(['Отменить заполнение заявки']).as_markup(
                             resize_keyboard=True))

    await state.set_state(FirstOptionGroup.waiting_for_fio)


@router.message(FirstOptionGroup.waiting_for_fio)
async def process_fio(message: Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await message.answer('ФИО сохранено.')
    await message.answer(
        'Теперь введите свою корпоративную почту (для сотрудников). \n'
        'Пример: <i><b>example@alabuga.ru</b></i>.\n'
        'Если вы новый сотрудник, нажмите на кнопку <i><b>Пропустить</b></i>.',
        parse_mode=ParseMode.HTML,
        reply_markup=make_row_keyboard(['Пропустить', 'Отменить заполнение заявки']).as_markup(resize_keyboard=True)
    )
    await state.set_state(FirstOptionGroup.waiting_for_email)


@router.message(F.text.lower() == 'пропустить', FirstOptionGroup.waiting_for_email)
async def process_position_without_email(message: Message, state: FSMContext):
    await message.answer(
        "Укажите свою должность.",
        reply_markup=make_row_keyboard(['Отменить заполнение заявки']).as_markup(resize_keyboard=True)
    )
    await state.set_state(FirstOptionGroup.waiting_for_position)
    await state.update_data(position=message.text)


@router.message(F.text.lower() != 'пропустить', FirstOptionGroup.waiting_for_email)
async def process_position_with_email(message: Message, state: FSMContext):
    email_regex = re.compile(r'^.{4,}@alabuga\.ru$')
    if email_regex.search(message.text):
        await state.update_data(email=message.text)
        await message.answer('Почта сохранена.')
        await message.answer(
            "Укажите свою должность.",
            reply_markup=make_row_keyboard(['Отменить заполнение заявки']).as_markup(resize_keyboard=True)
        )
        await state.set_state(FirstOptionGroup.waiting_for_position)
    else:
        await repeat_email(message, state, FirstOptionGroup)


@router.message(FirstOptionGroup.waiting_for_position)
async def process_basis(message: Message, state: FSMContext):
    await message.answer('Должность сохранена.')
    await state.update_data(position=message.text)
    await message.answer('Введите номер своего трудового договора с датой.'
                         '\n<b><i>Пример: ТД-0000/24 от 11 ноября 2024 года</i></b>.',
                         parse_mode=ParseMode.HTML)

    await state.set_state(FirstOptionGroup.waiting_for_basis)


@router.message(FirstOptionGroup.waiting_for_basis)
async def process_phone_number(message: Message, state: FSMContext):
    await message.answer('Номер сохранен.')
    await state.update_data(basis=message.text)
    await message.answer('Введите свой номер телефона.',
                         parse_mode=ParseMode.HTML)

    await state.set_state(FirstOptionGroup.waiting_for_phone_number)


@router.message(FirstOptionGroup.waiting_for_phone_number)
async def process_supervisor_name(message: Message, state: FSMContext):
    phone_number_regex = re.compile(r'^\+?\d{1,3}[- ]?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}$')
    if phone_number_regex.match(message.text):
        await message.answer('Номер сохранен.')
        await state.update_data(phone_number=message.text)
        await message.answer('Введите фио своего прямого руководителя(закрывающего цели в системе KPI).')
        await state.set_state(FirstOptionGroup.waiting_for_supervisor_name)
    else:
        await repeat_phone_number(message, state, FirstOptionGroup)


@router.message(FirstOptionGroup.waiting_for_supervisor_name)
async def process_project_supervisor_name(message: Message, state: FSMContext):
    await message.answer('ФИО руководителя сохранено.')
    await state.update_data(manager_fio=message.text)
    await message.answer('Введите фио своего руководителя проекта.')

    await state.set_state(FirstOptionGroup.waiting_for_project_supervisor_name)


@router.message(FirstOptionGroup.waiting_for_project_supervisor_name)
async def process_project_supervisor_name(message: Message, state: FSMContext):
    await state.update_data(project_supervisor_fio=message.text)
    await message.answer('ФИО руководителя сохранено. \n'
                         'Нажмите на кнопку <i><b>Завершить заполнение формы</b></i>.',
                         reply_markup=make_row_keyboard(['Завершить заполнение формы']).as_markup(resize_keyboard=True),
                         parse_mode=ParseMode.HTML)

    await state.set_state(FirstOptionGroup.waiting_for_access_resources)


@router.message(FirstOptionGroup.waiting_for_access_resources)
async def process_access_resources(message: Message, state: FSMContext):
    await message.answer('Процесс заполнения формы завершен, пожалуйста перепроверьте данные.',
                         reply_markup=ReplyKeyboardRemove())
    data = await state.get_data()
    confirmation_message = f"Вы ввели следующие данные:\n"
    counter = 0
    for value in data.values():
        if value is not None:
            counter += 1
            confirmation_message += f"<b>{counter}:</b> {value}\n"
    await message.answer(confirmation_message, parse_mode=ParseMode.HTML)
    await message.answer('Если все верно, напишите выберите пункт <i><b>"Верно"</b></i>',
                         reply_markup=make_row_keyboard(['Верно',
                                                         'Отменить заполнение заявки',
                                                         'Изменить данные']).as_markup(resize_keyboard=True),
                         parse_mode=ParseMode.HTML)

    await state.set_state(FirstOptionGroup.waiting_for_confirm_form)


async def edit_data(field: str, new_data: str, state: FSMContext):
    field_mappings = {
        '1. Тип заявки': 'order_type',
        '2. ФИО': 'fio',
        '3. Почта(изменить или добавить)': 'email',
        '4. Должность': 'position',
        '5. Номер трудового договора': 'basis',
        '6. Номер телефона': 'phone_number',
        '7. ФИО руководителя': 'manager_fio',
        '8. ФИО руководителя проекта': 'project_supervisor_fio'
    }
    if field in field_mappings:
        await state.update_data({field_mappings[field]: new_data})


@router.message(FirstOptionGroup.waiting_for_confirm_form)
async def form_confirmed(message: Message, state: FSMContext, bot: Bot):
    if message.text.lower() == 'верно':
        data = await state.get_data()
        if 'field' in data:
            data.pop('field')
        # Сохраняем данные в базу данных
        with session_scope() as session:
            user_data = FirstOrderData(**data)
            session.add(user_data)
            await state.clear()
        await message.answer("Ваши данные сохранены. Спасибо за заявку!", reply_markup=ReplyKeyboardRemove())
        await send_order_to_admin(admin_id=6746189705,
                                  bot=bot,
                                  order_type='Оформление доступа к Outlook и т.д.',
                                  database=FirstOrderData)
    elif message.text.lower() == 'изменить данные':
        await message.answer('Выберите пункт, который хотите изменить',
                             reply_markup=make_row_keyboard([
                                 '1. Тип заявки',
                                 '2. ФИО',
                                 '3. Почта(изменить или добавить)',
                                 '4. Должность',
                                 '5. Номер трудового договора',
                                 '6. Номер телефона',
                                 '7. ФИО руководителя',
                                 '8. ФИО руководителя проекта',
                             ]).as_markup(resize_keyboard=True))

        await state.set_state(FirstOptionGroup.waiting_for_edit_form)


@router.message(FirstOptionGroup.waiting_for_edit_form)
async def enter_new_data(message: Message, state: FSMContext):
    await state.update_data(field=message.text)
    if message.text == '1. Тип заявки':
        await message.answer("Вы хотите получить новый доступ или изменить старый? Выберите вариант ответа.",
                             reply_markup=make_row_keyboard(['Новый', 'Изменить старый']).as_markup(
                                 resize_keyboard=True))
    else:
        await message.answer('Введите новые данные:', reply_markup=ReplyKeyboardRemove())

    await state.set_state(FirstOptionGroup.waiting_for_check_form)


@router.message(FirstOptionGroup.waiting_for_check_form)
async def check_new_data(message: Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    field = data['field']
    await state.update_data(field=None)
    await edit_data(field, text, state)
    await process_access_resources(message, state)
