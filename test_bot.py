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


bot = Bot("1972867313:AAHgZ9CY7WslJqw9HSBmHvmMTHfmIqrv-yM")

dp = Dispatcher(bot, storage=MemoryStorage())

findTeacher = KeyboardButton('Найти преподавателя')
findGroup = KeyboardButton('Найти группу')

kb_schedule = ReplyKeyboardMarkup(resize_keyboard=True)
kb_schedule.row(findTeacher, findGroup)

cancelButton = InlineKeyboardButton(text="Отмена", callback_data="cancel_")

days = InlineKeyboardMarkup(row_width=2)
days.add(InlineKeyboardButton(text="Понедельник", callback_data="day_Понедельник")).add(InlineKeyboardButton(text="Вторник", callback_data="day_Вторник")).\
    add(InlineKeyboardButton(text="Среда", callback_data="day_Среда")).add(InlineKeyboardButton(text="Четверг", callback_data="day_Четверг")).\
    add(InlineKeyboardButton(text="Пятница", callback_data="day_Пятница")).add(InlineKeyboardButton(text="Суббота", callback_data="day_Суббота")).\
add(cancelButton)

times = InlineKeyboardMarkup(row_width=2)
times.add(InlineKeyboardButton(text="7:30", callback_data="time_7:30")).add(InlineKeyboardButton(text="9:20", callback_data="time_9:20")).\
    add(InlineKeyboardButton(text="11:10", callback_data="time_11:10")).add(InlineKeyboardButton(text="13:15", callback_data="time_13:15")).\
    add(InlineKeyboardButton(text="15:00", callback_data="time_15:00")).add(InlineKeyboardButton(text="16:45", callback_data="time_16:45"))


@dp.callback_query_handler(Text(equals="cancel_"))
async def cancel_command(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.delete()
    await callback.message.answer("Действие отменено")
    await callback.answer()
    await state.finish()

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer("Начинаем тест расписания", reply_markup=kb_schedule)

@dp.message_handler(lambda message: message.text == 'Найти группу')
async def find_group(message: types.Message):
    groups = getTeacher.getAvailableGroups()
    groupsKb = InlineKeyboardMarkup(row_width=2)
    counter = 0
    for group in groups:
        groupsKb.add(InlineKeyboardButton(text=group, callback_data=f"gr_{group}"))
        counter += 1
        if counter == 5:
            break
    groupsKb.row(InlineKeyboardButton(text="Назад", callback_data=f"prGroups|{counter}"), InlineKeyboardButton(text="Вперед", callback_data=f"nxGroups|{counter}"))
    groupsKb.add(cancelButton)
    await message.answer("Выберите группу", reply_markup=groupsKb)

@dp.callback_query_handler(Text(startswith="nxGroups"))
async def next_groups(callback: types.CallbackQuery, state: FSMContext):
    counter = callback.data.split("|")[1]
    query = callback.data.split("|")
    groupsKb = InlineKeyboardMarkup(row_width=2)
    counter = int(query[1])
    listEnd = False
    counterTmp = 0
    keys = getTeacher.getAvailableGroups()
    for i in range(counter, counter + 5):
        if (i >= len(keys)):
            listEnd = True
            break
        data = f"gr_{keys[i]}"
        print("buttonSize: " + str(len(data.encode('utf-8'))))
        groupsKb.add(InlineKeyboardButton(text=keys[i], callback_data=data))
        counterTmp += 1
        if counterTmp % 5 == 0:
            break
    if listEnd:
        groupsKb.row(InlineKeyboardButton(text="Назад", callback_data=f"prGroups|{counter + counterTmp}"))
    else:
        groupsKb.row(InlineKeyboardButton(text="Назад", callback_data=f"prGroups|{counter + counterTmp}"),InlineKeyboardButton(text="Далее", callback_data=f"nxGroups|{counter + counterTmp}"))
    print("#######################")
    groupsKb.add(cancelButton)
    await callback.message.edit_reply_markup(reply_markup=groupsKb)
    await callback.answer()

@dp.callback_query_handler(Text(startswith="prGroups"))
async def previous_group(callback: types.CallbackQuery):
    query = callback.data.split("|")
    groupsKb = InlineKeyboardMarkup(row_width=2)
    counter = int(query[1])
    keys = getTeacher.getAvailableGroups()
    listEnd = False
    counterTmp = 0
    for i in range(counter, counter - 5, -1):
        if (i < 0):
            listEnd = True
            break
        if (i >= len(keys)):
            continue
        groupsKb.add(InlineKeyboardButton(text=keys[i], callback_data=f"gr_{keys[i]}"))
        counterTmp += 1
        if counterTmp % 5 == 0:
            break
    if listEnd:
        groupsKb.row(InlineKeyboardButton(text="Далее", callback_data=f"nxGroups|{counter - counterTmp}"))
    else:
        groupsKb.row(InlineKeyboardButton(text="Назад", callback_data=f"prGroups|{counter - counterTmp}"),InlineKeyboardButton(text="Далее", callback_data=f"nxGroups|{counter - counterTmp}"))
    groupsKb.add(cancelButton)
    await callback.message.edit_reply_markup(reply_markup=groupsKb)
    await callback.answer()

@dp.callback_query_handler(Text(startswith="gr_"))
async def chosen_group(callback: types.CallbackQuery, state: FSMContext):
    group = callback.data.split("_")[1]
    await callback.message.delete()
    await callback.message.answer(f"Группа: {group}")
    async with state.proxy() as data:
        data['groupState'] = group
    await callback.message.answer("Выберите день", reply_markup=days)
    await callback.answer()

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
    teachers.add(cancelButton)
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
    if (data.get("groupState") != None):
        lesson = getTeacher.findGroup(group=data.get("groupState"), day=data.get("chosenDay"), time=callback.data.split("_")[1], schedule=getTeacher.getSchedule())
        if (lesson != None):
            strLesson = getTeacher.lessonToString(lesson)
            await callback.message.answer(f"Ближайшее занятие группы: \n{strLesson}\n")
        else:
            await callback.message.answer(f"Не удалось найти ближайшее занятие")
    else:
        lesson = getTeacher.findTeacher(teacher=data.get("teacherState"), day=data.get("chosenDay"), time=callback.data.split("_")[1], schedule=getTeacher.getSchedule())
        if (lesson != None):
            strLesson = getTeacher.lessonToString(lesson=lesson)
            await callback.message.answer(f"Ближайшее занятие преподавателя: \n{strLesson}\n")
        lessons = getTeacher.findTeacherOnAllDay(teacher=data.get("teacherState"), day=data.get("chosenDay"), schedule=getTeacher.getSchedule())
        messageAnswer = "Все предметы в этот день:\n"
        for lesson in lessons:
            strLesson = getTeacher.lessonToString(lesson=lesson)
            message = f"{strLesson}\n\n"
            messageAnswer += message
        messageAnswer = messageAnswer[0:len(messageAnswer) - 1]
        await callback.message.answer(messageAnswer)
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
    teachers.add(cancelButton)
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
    teachers.add(cancelButton)
    await callback.message.edit_reply_markup(reply_markup=teachers)
    await callback.answer()


@dp.message_handler()
async def echo_send(message: types.Message):
    await message.reply("Извини, я тебя не понимаю :с")


executor.start_polling(dp, skip_updates=True)