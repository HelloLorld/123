from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import getTeacher

class UserState(StatesGroup):
    teacherState = State()
    chosenDay = State()
    timeSchedule = State()


bot = Bot("1972867313:AAHyPXCEWemfWDrQtvAC-rO6V3yGi9rG0OM")

dp = Dispatcher(bot, storage=MemoryStorage())

findTeacher = KeyboardButton('Найти преподавателя')
findGroup = KeyboardButton('Найти группу')

kb_schedule = ReplyKeyboardMarkup(resize_keyboard=True)
kb_schedule.row(findTeacher, findGroup)

days = InlineKeyboardMarkup(row_width=2)
days.add(InlineKeyboardButton(text="Понедельник", callback_data="day_Понедельник")).add(InlineKeyboardButton(text="Вторник", callback_data="day_Вторник")).\
    add(InlineKeyboardButton(text="Среда", callback_data="day_Среда")).add(InlineKeyboardButton(text="Четверг", callback_data="day_Четверг")).\
    add(InlineKeyboardButton(text="Пятница", callback_data="day_Пятница")).add(InlineKeyboardButton(text="Суббота", callback_data="day_Суббота"))

times = InlineKeyboardMarkup(row_width=2)
times.add(InlineKeyboardButton(text="7:30", callback_data="time_7:30")).add(InlineKeyboardButton(text="9:20", callback_data="time_9:20")).\
    add(InlineKeyboardButton(text="11:10", callback_data="time_11:10")).add(InlineKeyboardButton(text="13:15", callback_data="time_13:15")).\
    add(InlineKeyboardButton(text="15:00", callback_data="time_15:00")).add(InlineKeyboardButton(text="16:45", callback_data="time_16:45"))

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Начинаем тест расписания", reply_markup=kb_schedule)

@dp.message_handler(lambda message: message.text == 'Найти преподавателя')
async def find_teacher(message: types.Message):
    schedule: dict = getTeacher.getSchedule()
    counter = 0
    teachers = InlineKeyboardMarkup(row_width=2)
    for teacher in schedule.keys():
        teachers.add(InlineKeyboardButton(text=teacher, callback_data=f"tcr_{teacher}"))
        counter += 1
        if counter == 5:
            break
    teachers.row(InlineKeyboardButton(text="Назад", callback_data=f"prTchrs|{counter}"),InlineKeyboardButton(text="Далее", callback_data=f"nxTchrs|{counter}"))
    await message.answer("Выберите преподавателя", reply_markup=teachers)

@dp.callback_query_handler(Text(startswith="tcr_"))
async def chosen_teacher(callback: types.CallbackQuery, state: FSMContext):
    teacher = callback.data.split("_")[1]
    await callback.message.delete()
    await callback.message.answer(f"Преподаватель: {teacher}")
    async with state.proxy() as data:
        data['teacherState'] = teacher
    await callback.message.answer("Выберите день", reply_markup=days)
    await callback.answer()

@dp.callback_query_handler(Text(startswith="day_"))
async def set_day(callback: types.CallbackQuery, state: FSMContext):
    chosenDay = callback.data.split("_")[1]
    async with state.proxy() as data:
        data['chosenDay'] = chosenDay
    await callback.message.delete()
    await callback.message.answer(f"День: {chosenDay}")
    await callback.message.answer("Выберите время", reply_markup=times)
    await callback.answer()

@dp.callback_query_handler(Text(startswith="time_"))
async def set_time(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    chosenTime = callback.data.split("_")[1]
    await callback.message.delete()
    await callback.message.answer(f"Время: {chosenTime}")
    lesson = getTeacher.findTeacher(teacher=data.get("teacherState"), day=data.get("chosenDay"), time=callback.data.split("_")[1], schedule=getTeacher.getSchedule())
    if (lesson != None):
        nameOfLesson = lesson.get("nameOfLesson")
        groups = lesson.get("groups")
        office = lesson.get("office")
        typeOfLesson = lesson.get("type")
        await callback.message.answer(f"Ближайшее занятие преподавателя: \n{nameOfLesson}\nКабинет: {office}\nГруппы: {groups}\nВид занятия: {typeOfLesson}")
    else:
        await callback.message.answer("В это время преподавателя нет")
    await state.finish()

@dp.callback_query_handler(lambda c: c.data.startswith("nxTchrs"))
async def next_teacher(callback: types.CallbackQuery):
    schedule: dict = getTeacher.getSchedule()
    query = callback.data.split("|")
    teachers = InlineKeyboardMarkup(row_width=2)
    counter = int(query[1])
    keys = list(schedule.keys())
    listEnd = False
    counterTmp = 0
    for i in range(counter, counter + 5):
        if (i >= len(keys)):
            listEnd = True
            break
        data = f"tcr_{keys[i]}"
        print("buttonSize: " + str(len(data.encode('utf-8'))))
        teachers.add(InlineKeyboardButton(text=keys[i], callback_data=data))
        counterTmp += 1
        if counterTmp % 5 == 0:
            break
    if listEnd:
        teachers.row(InlineKeyboardButton(text="Назад", callback_data=f"prTchrs|{counter + counterTmp}"))
    else:
        teachers.row(InlineKeyboardButton(text="Назад", callback_data=f"prTchrs|{counter + counterTmp}"),InlineKeyboardButton(text="Далее", callback_data=f"nxTchrs|{counter + counterTmp}"))
    print("#######################")
    await callback.message.edit_reply_markup(reply_markup=teachers)
    await callback.answer()
    
@dp.callback_query_handler(lambda c: c.data.startswith("prTchrs"))
async def previous_teacher(callback: types.CallbackQuery):
    schedule: dict = getTeacher.getSchedule()
    query = callback.data.split("|")
    teachers = InlineKeyboardMarkup(row_width=2)
    counter = int(query[1])
    keys = list(schedule.keys())
    listEnd = False
    counterTmp = 0
    for i in range(counter, counter - 5, -1):
        if (i < 0):
            listEnd = True
            break
        if (i >= len(keys)):
            continue
        teachers.add(InlineKeyboardButton(text=keys[i], callback_data=f"tcr_{keys[i]}"))
        counterTmp += 1
        if counterTmp % 5 == 0:
            break
    if listEnd:
        teachers.row(InlineKeyboardButton(text="Далее", callback_data=f"nxTchrs|{counter - counterTmp}"))
    else:
        teachers.row(InlineKeyboardButton(text="Назад", callback_data=f"prTchrs|{counter - counterTmp}"),InlineKeyboardButton(text="Далее", callback_data=f"nxTchrs|{counter - counterTmp}"))
    await callback.message.edit_reply_markup(reply_markup=teachers)
    await callback.answer()


@dp.message_handler()
async def echo_send(message: types.Message):
    await message.reply("Извини, я тебя не понимаю :с")


executor.start_polling(dp, skip_updates=True)