import re
from datetime import datetime

from utils.database_utills import session_scope
from utils.errors import repeat_phone_number

from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.types import ReplyKeyboardRemove, document

from database import SecondOrderData
from keyboards.simple_keyboard import make_row_keyboard
from utils.send_order_to_admin import send_order_to_admin

router = Router()


# Класс для хранения состояний бота
class SecondOptionGroup(StatesGroup):
    waiting_for_new_or_old_employer = State()
    waiting_for_fio = State()
    waiting_for_employer_or_contractor = State()
    waiting_for_basis = State()
    waiting_for_document = State()
    waiting_for_phone_number = State()
    waiting_for_project_supervisor_name = State()
    waiting_for_date = State()
    waiting_for_objects_name = State()
    waiting_for_access_resources = State()
    waiting_for_confirm_form = State()
    waiting_for_edit_form = State()
    waiting_for_check_form = State()


@router.message(StateFilter(None), Command("second"))
async def start(message: Message, state: FSMContext):
    await message.answer("Добрый день! Давайте начнем процесс создания заявки."
                         "Вы хотите получить новый доступ, или изменить старый, выберите вариант ответа.",
                         reply_markup=make_row_keyboard(['Новый', 'Изменить старый']).as_markup(
                             resize_keyboard=True))

    await state.set_state(SecondOptionGroup.waiting_for_new_or_old_employer)


@router.message(SecondOptionGroup.waiting_for_new_or_old_employer)
async def process_order_type(message: Message, state: FSMContext):
    await message.answer('Тип заявки сохранен')
    await state.update_data(order_type=message.text)
    await message.answer('Введите своё ФИО в именительном падеже. \nПример: <i><b>Иванов Иван Иванович</b></i>.',
                         parse_mode=ParseMode.HTML,
                         reply_markup=make_row_keyboard(['Отменить заполнение заявки']).as_markup(
                             resize_keyboard=True))

    await state.set_state(SecondOptionGroup.waiting_for_fio)


@router.message(SecondOptionGroup.waiting_for_fio)
async def process_fio(message: Message, state: FSMContext, repeated=None):
    if not repeated:
        await state.update_data(fio=message.text)
        await message.answer('ФИО сохранено.')
    await message.answer(
        'Выберите пожалуйста, кем вы являетесь, сотрудником или подрядчиком',
        parse_mode=ParseMode.HTML,
        reply_markup=make_row_keyboard(['Я сотрудник', 'Я подрядчик']).as_markup(resize_keyboard=True)
    )

    await state.set_state(SecondOptionGroup.waiting_for_employer_or_contractor)


@router.message(F.text.lower() == 'я сотрудник',
                SecondOptionGroup.waiting_for_employer_or_contractor)
async def process_td_number(message: Message, state: FSMContext):
    await message.answer('Введите номер своего трудового договора с датой.'
                         '\n<b><i>Пример: ТД-0000/24 от 11 ноября 2024 года</i></b>.',
                         parse_mode=ParseMode.HTML,
                         reply_markup=make_row_keyboard(['Отменить заполнение заявки']).as_markup(
                             resize_keyboard=True))

    await state.set_state(SecondOptionGroup.waiting_for_basis)
    await state.update_data(user_role=message.text)


@router.message(F.text.lower() == 'я подрядчик',
                SecondOptionGroup.waiting_for_employer_or_contractor)
async def process_files(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, отправьте договор с ОЭЗ, либо иной документ. Документ может быть в формате'
                         ' word или pdf и иметь размер не больше 5 мегабайт.',
                         reply_markup=make_row_keyboard(['Отменить заполнение заявки']).as_markup(
                             resize_keyboard=True))

    await state.set_state(SecondOptionGroup.waiting_for_document)
    await state.update_data(user_role=message.text)


@router.message(SecondOptionGroup.waiting_for_basis)
async def process_phone_number(message: Message, state: FSMContext):
    await message.answer('Номер сохранен.')
    await state.update_data(basis=message.text)
    await message.answer('Введите свой номер телефона.')

    await state.set_state(SecondOptionGroup.waiting_for_phone_number)


@router.message(SecondOptionGroup.waiting_for_document)
async def process_document(message: Message, state: FSMContext, bot: Bot):
    user_document = message.document
    if (user_document is None or user_document.file_size > 5 * 1024 * 1024 or user_document.mime_type not in
            ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/pdf']):
        await message.answer('Пожалуйста, отправьте файл соответствующий условиям!')

    else:
        file_id = user_document.file_id
        await message.answer('Документ сохранен.')
        print(user_document)
        await state.update_data(document=file_id)
        await message.answer('Введите свой номер телефона.',
                             parse_mode=ParseMode.HTML)

        await state.set_state(SecondOptionGroup.waiting_for_phone_number)


@router.message(SecondOptionGroup.waiting_for_phone_number)
async def process_supervisor_name(message: Message, state: FSMContext):
    phone_number_regex = re.compile(r'^\+?\d{1,3}[- ]?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}$')
    if phone_number_regex.match(message.text):
        await message.answer('Номер сохранен.')
        await state.update_data(phone_number=message.text)
        data = await state.get_data()
        if data.get('user_role') == 'Я сотрудник':
            await message.answer('Введите фио своего руководителя проекта.')
            await state.set_state(SecondOptionGroup.waiting_for_project_supervisor_name)
        elif data.get('user_role') == 'Я подрядчик':
            await message.answer('Введите срок, на который нужно оформить доступ к FaceID, в формате: \n'
                                 '<i><b>DD.MM.YYYY-DD.MM.YYYY</b></i>.', parse_mode=ParseMode.HTML)
            await state.set_state(SecondOptionGroup.waiting_for_date)
    else:
        await repeat_phone_number(message, state, SecondOptionGroup)


@router.message(SecondOptionGroup.waiting_for_project_supervisor_name)
async def process_project_supervisor_name(message: Message, state: FSMContext):
    await message.answer('ФИО руководителя сохранено')
    await state.update_data(project_supervisor_fio=message.text)
    await message.answer('Введите пожалуйста дату конца существующего года в формате,'
                         ' <i><b>DD.MM.YYYY</b></i>, на этот срок вам будет оформлен FaceID.',
                         parse_mode=ParseMode.HTML)

    await state.set_state(SecondOptionGroup.waiting_for_date)


async def incorrect_date(message: Message, state: FSMContext):
    await message.answer('Пожалуйста введите дату в верном формате!')
    await state.set_state(SecondOptionGroup.waiting_for_date)


@router.message(SecondOptionGroup.waiting_for_date)
async def process_project_supervisor_name(message: Message, state: FSMContext):
    data = await state.get_data()
    if data['user_role'] == 'Я подрядчик':
        date_pattern = re.compile(r'^\d{1,2}.\d{1,2}.\d{4}-\d{1,2}.\d{1,2}.\d{4}$')
    else:
        date_pattern = re.compile(r'^\d{1,2}.\d{1,2}.\d{4}$')

    if date_pattern.match(message.text):
        await state.update_data(date=''.join(message.text))
        await message.answer('Дата сохранена. \n'
                             'Введите пожалуйста через запятую названия объектов, к которым нужен доступ \n'
                             'Пример: <i><b>Синергия 8.1-8.2, Синергия 13.2 Яковлев, Синергия 13.1</b></i>',
                             parse_mode=ParseMode.HTML)

        await state.set_state(SecondOptionGroup.waiting_for_objects_name)
    else:
        await incorrect_date(message, state)


@router.message(SecondOptionGroup.waiting_for_objects_name)
async def process_objects_name(message: Message, state: FSMContext):
    await message.answer('Название(-я) объекта(-ов) сохранены')
    await state.update_data(objects=message.text)
    await message.answer('Пожалуйста, нажмите на кнопку \n<i><b>Завершить заполнение формы</b></i>',
                         parse_mode=ParseMode.HTML,
                         reply_markup=make_row_keyboard(['Завершить заполнение формы']).as_markup(
                             resize_keyboard=True)
                         )

    await state.set_state(SecondOptionGroup.waiting_for_access_resources)


@router.message(SecondOptionGroup.waiting_for_access_resources)
async def process_access_resources(message: Message, state: FSMContext):
    await message.answer('Процесс заполнения формы завершен, пожалуйста перепроверьте данные',
                         reply_markup=ReplyKeyboardRemove())
    data = await state.get_data()
    confirmation_message = f"Вы ввели следующие данные:\n"
    counter = 0
    for value in data.values():
        if type(value) is document.Document:
            counter += 1
            file_name = value.file_name
            confirmation_message += f"<b>{counter}:</b> {file_name}\n"
        elif value is not None:
            counter += 1
            confirmation_message += f"<b>{counter}:</b> {value}\n"
    await message.answer(confirmation_message, parse_mode=ParseMode.HTML)
    await message.answer('Если все верно, напишите выберите пункт <i><b>"Верно"</b></i>',
                         reply_markup=make_row_keyboard(['Верно',
                                                         'Отменить заполнение заявки',
                                                         'Изменить данные']).as_markup(resize_keyboard=True),
                         parse_mode=ParseMode.HTML)

    await state.set_state(SecondOptionGroup.waiting_for_confirm_form)


async def edit_data(field: str, new_data: str, state: FSMContext):
    field_mappings = {
        '1. Тип заявки': 'order_type',
        '2. ФИО': 'fio',
        '3. Номер ТД': 'basis',
        '4. Договор с ОЭЗ/Иной документ': 'document',
        '5. Номер телефона': 'phone_number',
        '6. ФИО руководителя проекта(если вы сотрудник)': 'project_supervisor_fio',
        '7. Дату(-ы) доступа к FaceID': 'date',
        '8. Название(-я) объекта(-ов)': 'objects'
    }
    if field in field_mappings:
        await state.update_data({field_mappings[field]: new_data})


@router.message(SecondOptionGroup.waiting_for_confirm_form)
async def form_confirmed(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if 'field' in data:
        data.pop('field')
    if message.text.lower() == 'верно':
        common_args = {
            'order_type': data['order_type'],
            'fio': data['fio'],
            'phone_number': data['phone_number'],
            'project_supervisor_fio': data['project_supervisor_fio'] if hasattr(data, 'project_supervisor_fio') else '',
            'objects': data['objects']
        }
        if 'basis' in data:
            session_data = SecondOrderData(**common_args, basis=data['basis'])
        elif 'document' in data:
            file_id = data['document']
            file_info = await bot.get_file(file_id)
            downloaded_file = await bot.download_file(file_info.file_path)
            print(downloaded_file)
            session_data = SecondOrderData(**common_args, document=downloaded_file)
        else:
            raise ValueError("Invalid document type")
        if '-' not in data['date']:
            date_faceid = datetime.strptime(data['date'], "%d.%m.%Y").date()
            session_data.first_date = date_faceid
        else:
            first_date, second_date = (''.join(data['date'])).split('-')
            date_faceid = (datetime.strptime(first_date, "%d.%m.%Y").date(),
                           datetime.strptime(second_date, "%d.%m.%Y").date())
            session_data.first_date, session_data.second_date = date_faceid

        with session_scope() as session:
            await state.clear()
            session.add(session_data)

        await message.answer("Ваши данные сохранены. Спасибо за заявку!", reply_markup=ReplyKeyboardRemove())
        await send_order_to_admin(admin_id=6970846180,
                                  bot=bot,
                                  order_type='Оформление доступа к FaceID',
                                  database=SecondOrderData,
                                  order_dict=data)
    elif message.text.lower() == 'изменить данные':
        await message.answer('Выберите пункт, который хотите изменить',
                             reply_markup=make_row_keyboard([
                                 '1. Тип заявки',
                                 '2. ФИО',
                                 '3. Кем вы являетесь, подрядчиком или сотрудником',
                                 '4. Номер ТД' if data['user_role'] == 'Я сотрудник' else '4. Договор с ОЭЗ/'
                                                                                          'Иной документ',
                                 '5. Номер телефона',
                                 '6. ФИО руководителя проекта(если вы сотрудник)',
                                 '7. Дату(-ы) доступа к FaceID',
                                 '8. Название(-я) объекта(-ов)'
                             ]).as_markup(resize_keyboard=True))

        await state.set_state(SecondOptionGroup.waiting_for_edit_form)


@router.message(SecondOptionGroup.waiting_for_edit_form)
async def enter_new_data(message: Message, state: FSMContext):
    await state.update_data(field=message.text)
    if message.text == '1. Тип заявки':
        await message.answer("Вы хотите получить новый доступ или изменить старый? Выберите вариант ответа.",
                             reply_markup=make_row_keyboard(['Новый', 'Изменить старый']).as_markup(
                                 resize_keyboard=True))
    elif message.text == '3. Кем вы являетесь, подрядчиком или сотрудником':
        await state.update_data(field=None)
        await state.update_data(project_supervisor_fio=None)
        await process_fio(message, state, repeated=True)
    else:
        await message.answer('Введите новые данные или прикрепите новый файл:',
                             reply_markup=ReplyKeyboardRemove()
                             )

        await state.set_state(SecondOptionGroup.waiting_for_check_form)


@router.message(SecondOptionGroup.waiting_for_check_form)
async def check_new_data(message: Message, state: FSMContext):
    text = message.text
    data = await state.get_data()
    field = data['field']
    await state.update_data(field=None)
    await edit_data(field, text, state)
    await process_access_resources(message, state)
