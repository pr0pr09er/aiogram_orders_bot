from aiogram import F, Router
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command, StateFilter, ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.handlers import ErrorHandler
from aiogram.types import Message, ReplyKeyboardRemove, ErrorEvent
from keyboards.simple_keyboard import make_row_keyboard

router = Router()


@router.message(F.text == 'Вернуться обратно')
async def return_back(message: Message, state: FSMContext):
    await cmd_start(message, state)


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="""
Это бот помощник в получении доступа к инф. ресурсам.\n
Выберите опцию, которая вам нужна.\n
Команды: \n
Получить доступ к учетной записи для компьютера, почта Outlook, Битрикс, базы 1C - Выберите первый вариант (/first)\n
Получить доступ к объектам FaceID - Выберите второй вариант (/second)\n
Оставить заявку на установку программного обеспечения - Выберите третий вариант (/third)\n
Получить доступ к всем заявкам(для администраторов) - Выберите четвертый вариант (/admin)
             """,
        reply_markup=make_row_keyboard(
            ['/first', '/second', '/third', '/admin']
        ).as_markup(resize_keyboard=True)
    )


@router.message(StateFilter(None), F.text.lower() == "отменить заполнение заявки")
async def cmd_cancel_no_state(message: Message, state: FSMContext):
    # Стейт сбрасывать не нужно, удалим только данные
    await state.set_data({})
    await message.answer(
        text="Заявка пуста",
        reply_markup=ReplyKeyboardRemove()
    )
    await cmd_start(message, state)


@router.message(F.text.lower() == "отменить заполнение заявки")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text="Процесс заполнения формы отменен. Введенные данные удалены.",
        reply_markup=ReplyKeyboardRemove()
    )
    await cmd_start(message, state)


@router.error(ExceptionTypeFilter(TelegramNetworkError), F.update.message.as_("message"))
async def handle_network_error(event: ErrorEvent, message: Message):
    await message.answer('Произошла ошибка сети, пожалуйста отправьте свое сообщение снова!')
