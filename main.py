#ИМПОРТЫ
from aiogram import types, executor, Dispatcher, Bot
import datetime
import sqlite3 as sq
from pathlib import Path
import re
import request
import asyncio
import testoplata
import creator_bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import urlextract
import random
from datetime import datetime
import nest_asyncio
import configparser
import os
import requests
import subprocess
from webserver import keep_alive

# ФИКС РАБОТЫ ЦИКЛОВ LOOP
#nest_asyncio.apply()

#ПОЛУЧЕНИЕ ДАННЫХ КОНФИГУРАЦИИ
def getSettings(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    dataCfg = []
    dataCfg.append(config.get("settings", "BOT_TOKEN"))
    dataCfg.append(config.get("settings", "CASH_BOOST_USER"))
    dataCfg.append(config.get("settings", "DEFAULT_CASH_BOOST"))
    return dataCfg


# СОЗДАНЕ ФАЙЛА БД
createbse = Path('telegrammoney.db')
createbse.touch(exist_ok=True)

#КОННЕКТ БАЗЫ ДАННЫХ
global baseMain, cur
baseMain = sq.connect('telegrammoney.db')
cur = baseMain.cursor()

# ТОКЕН БОТА
bot = Bot(token = getSettings('config_main.txt')[0], parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())
botNotification = Bot(token = '5906203663:AAEngC8A1I1R-rKG8ETpmhktPfZM2v6kitY', parse_mode="HTML")
dpNotification = Dispatcher(botNotification, storage=MemoryStorage())

#МАНИШЫ СОСТОЯНИЙ
class InputCountNumber(StatesGroup):
    link_text = State()
    number_count = State()
    sum_cost = State()
    sum_cashout = State()
    data_cashout = State()
    waiting_for_new_percent = State()
    waiting_for_token = State()
    waiting_for_percent = State()

#СОЗДАНИЕ ТАБЛИЦЫ БАЗЫ ДАННЫХ
def create_tables():
    baseMain.execute('''CREATE TABLE IF NOT EXISTS USER_ORDER
                    (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    id_user INTEGER NOT NULL,
                    date STRING NOT NULL,
                    id_uslygi INTEGER NOT NULL,
                    link_on_group STRING NOT NULL,
                    quantity INTEGER NOT NULL,
                    money DOUBLE NOT NULL,
                    order_number INTEGER NOT NULL,
                    status STRING NOT NULL);''')                           
    baseMain.commit()
    baseMain.execute('''CREATE TABLE IF NOT EXISTS USERS 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        money DOUBLE NOT NULL DEFAULT 0,
                        earned DOUBLE DEFAULT 0,
                        user_bot STRING,
                        bot_token STRING,
                        cash_up INTEGER);''')
    baseMain.commit()                    
    baseMain.execute('''CREATE TABLE IF NOT EXISTS USER_PAY 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        date STRING NOT NULL,
                        sum_cash DOUBLE NOT NULL,
                        status STRING NOT NULL DEFAULT WAIT,
                        secretLabel STRING NOT NULL DEFAULT 0,
                        good_pay_check STRING DEFAULT False);''')
    baseMain.commit()


def register_user(user_id):
    create_tables()
    user_check_data = baseMain.execute("SELECT user_id FROM USERS WHERE user_id = ?",(str(user_id), )).fetchone()
    if str(user_id) not in str(user_check_data):
        money = 0
        baseMain.execute(f'INSERT INTO USERS (user_id, money) VALUES ("{user_id}", "{money}");')
        baseMain.commit()

def restart_all_bots():
    botsUser = baseMain.execute("SELECT user_bot FROM USERS").fetchall()
    for onceBot in botsUser:
        print(onceBot[0], "started...")
        command = f"cd {onceBot[0]}&&python main.py"
        subprocess.Popen(["start", "/wait", "cmd", "/K", command], shell=True)
restart_all_bots()


#ГЛАВНОЕ МЕНЮ
@dp.message_handler(commands=["start"], state="*")
async def handler(msg: types.Message):
    user_id = msg.from_user.id
    register_user(user_id)
    markup_inline = types.InlineKeyboardMarkup()
    nakrutka = types.InlineKeyboardButton(text="Накрутка 💎", callback_data="nakrutkaaMain")
    test_btn_create_bot = types.InlineKeyboardButton(text="Создай своего бота💎", callback_data="create_new_bot")
    balans = types.InlineKeyboardButton(text="Мой кошелёк 💵", callback_data="balanss")
    infoButton = types.InlineKeyboardButton(text="Информация", callback_data="infoButton")
    markup_inline.add(nakrutka).add(balans).add(infoButton).add(test_btn_create_bot)

    await msg.answer('🎉В настоящее время аккаунт с большим количеством лайков и подписчиков ценится намного выше и выглядит намного привлекательнее.\n\n🔥Сервис @botapbot_bot поможет вам  экономить время: достаточно выбрать нужную социальную сеть и количество подписчиков или лайков, все остальное мы сделаем за вас.\n\nКроме того, @botapbot_bot - это уникальный инструмент для создания коммерческого бота для накрутки, который можно создать всего в несколько кликов.\n\nВыберите действие:', reply_markup=markup_inline)


#КАЛБЕК ГЛАВНОГО МЕНЮ
@dp.callback_query_handler(text_startswith="Start", state="*")
async def start_callback(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    current_state = await state.get_state()
    if current_state:  
        await state.finish()
    print("current state: ", current_state)

    checkMoneyTake.work = False

    markup_inline = types.InlineKeyboardMarkup()
    test_btn_create_bot = types.InlineKeyboardButton(text="Создай своего бота💎", callback_data="create_new_bot")
    nakrutka = types.InlineKeyboardButton(text="Накрутка 💎", callback_data="nakrutkaaMain")
    balans = types.InlineKeyboardButton(text="Мой кошелёк 💵", callback_data="balanss")
    infoButton = types.InlineKeyboardButton(text="Информация", callback_data="infoButton")
    markup_inline.add(nakrutka).add(balans).add(infoButton).add(test_btn_create_bot)

    await call.message.edit_text('🎉В настоящее время аккаунт с большим количеством лайков и подписчиков ценится намного выше и выглядит намного привлекательнее.\n\n🔥Сервис @botapbot_bot поможет вам  экономить время: достаточно выбрать нужную социальную сеть и количество подписчиков или лайков, все остальное мы сделаем за вас.\n\nКроме того, @botapbot_bot - это уникальный инструмент для создания коммерческого бота для накрутки, который можно создать всего в несколько кликов.\n\nВыберите действие:', reply_markup=markup_inline)

#КАЛБЕК КНОПКИ "НАКРУТКА"
@dp.callback_query_handler(text_startswith="nakrutkaaMain", state="*")
async def nakrutkaaMain(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    current_state = await state.get_state()
    if current_state:  
        await state.finish()

    checkMoneyTake.work = False

    markup_inline = types.InlineKeyboardMarkup()
    nakrutka = types.InlineKeyboardButton(text="Накрутка 💎", callback_data="nakrutkaa")
    zakaz = types.InlineKeyboardButton(text="Мои заказы 💯", callback_data="zakazz")
    back_btn = types.InlineKeyboardButton(text="❌Назад", callback_data="Start")
    markup_inline.add(nakrutka).add(zakaz).add(back_btn)

    await call.message.edit_text(text="Выберите действие:", reply_markup=markup_inline)

#КАЛБЕК КНОПКИ "ИНФОРМАЦИЯ"
@dp.callback_query_handler(text_startswith="infoButton", state="*")
async def infoButton(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    current_state = await state.get_state()
    if current_state:  
        await state.finish()

    checkMoneyTake.work = False

    markup_inline = types.InlineKeyboardMarkup()
    nakrutka = types.InlineKeyboardButton(text="Поддержка 🤷", callback_data="podecjkaa")
    zakaz = types.InlineKeyboardButton(text="Правила", callback_data="pravilaa")
    back_btn = types.InlineKeyboardButton(text="❌Назад", callback_data="Start")
    markup_inline.add(nakrutka).add(zakaz).add(back_btn)

    await call.message.edit_text(text="Выберите действие:", reply_markup=markup_inline)


#КАЛБЕК СОЗДАНИЯ НОВОГО БОТА
@dp.callback_query_handler(text_startswith="create_new_bot")
async def create_new_bot(call: types.CallbackQuery):
    await call.answer()

    markup_inline = types.InlineKeyboardMarkup()
    startCreateBot = types.InlineKeyboardButton(text="Создать бота 💎", callback_data="startCreateBot")
    bot_settings = types.InlineKeyboardButton(text="Настрйоки ⚙️", callback_data="bot_settings")
    bot_instruction = types.InlineKeyboardButton(text="Инструкиця 💻", callback_data="bot_instruction")
    back_btn = types.InlineKeyboardButton(text="❌Назад", callback_data="Start")
    markup_inline.add(startCreateBot).add(bot_settings, bot_instruction).add(back_btn)
    await call.message.edit_text("➡️В вашем созданном боте все услуги будут скоординированы под вашу наценку, которая и является вашим заработком. Весь доход от услуг будет приходить в основного бота @botapbot_bot, где вы сможете удобно и быстро вывести заработанные средства.\nМы гарантируем оперативную поддержку в случае возникновения вопросов. \n\nРаботайте с нашим ботом и получайте стабильный доход!", reply_markup=markup_inline)

@dp.callback_query_handler(text_startswith="bot_instruction")
async def bot_instruction(call: types.CallbackQuery, state: FSMContext):
    await call.answer()

    markup_inline = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton(text="❌Назад", callback_data="delImage")
    markup_inline.add(back_btn)
    
    photo_input = open('create_inst.jpg', 'rb')
    await bot.send_photo(chat_id=call.from_user.id, photo=photo_input, caption="Инструкция, где найти API ключ своего бота", reply_markup= markup_inline)
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    async with state.proxy() as data:
        data['callMessageIDdel'] = call.message.message_id

@dp.callback_query_handler(text_startswith="delImage")
async def delImage(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    data_state = await state.get_data()
    dellId = data_state['callMessageIDdel']
    await bot.delete_message(chat_id=call.from_user.id, message_id=dellId + 1)
    await state.finish()
    markup_inline = types.InlineKeyboardMarkup()
    nakrutka = types.InlineKeyboardButton(text="Накрутка 💎", callback_data="nakrutkaaMain")
    test_btn_create_bot = types.InlineKeyboardButton(text="Создай своего бота💎", callback_data="create_new_bot")
    balans = types.InlineKeyboardButton(text="Мой кошелёк 💵", callback_data="balanss")
    infoButton = types.InlineKeyboardButton(text="Информация", callback_data="infoButton")
    markup_inline.add(nakrutka).add(balans).add(infoButton).add(test_btn_create_bot)

    await call.message.answer('🎉В настоящее время аккаунт с большим количеством лайков и подписчиков ценится намного выше и выглядит намного привлекательнее.\n\n🔥Сервис @botapbot_bot поможет вам  экономить время: достаточно выбрать нужную социальную сеть и количество подписчиков или лайков, все остальное мы сделаем за вас.\n\nКроме того, @botapbot_bot - это уникальный инструмент для создания коммерческого бота для накрутки, который можно создать всего в несколько кликов.\n\nВыберите действие:', reply_markup=markup_inline)



@dp.callback_query_handler(text_startswith="bot_settings")
async def bot_settings(call: types.CallbackQuery):
    await call.answer()
    markup_inline = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton(text="❌Отмена", callback_data="Start")
    btn_procent_50 = types.InlineKeyboardButton('5%', callback_data='5p')
    btn_procent_75 = types.InlineKeyboardButton('10%', callback_data='10p')
    btn_procent_100 = types.InlineKeyboardButton('15%', callback_data='15p')
    btn_procent_125 = types.InlineKeyboardButton('20%', callback_data='20p')
    markup_inline.add(btn_procent_50, btn_procent_75, btn_procent_100, btn_procent_125).add(back_btn)

    bot_token = baseMain.execute(f'SELECT bot_token FROM USERS WHERE user_id = {call.from_user.id}').fetchone()[0]
    url = f"https://api.telegram.org/bot{bot_token}/getMe"

    headers = {
        "accept": "application/json",
        "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)"
    }

    response = requests.post(url, headers=headers)
    data = response.json()
    responseOrder = data['result']
    responseOrder1 = responseOrder['username']
    anwerLink = "@" + f"{responseOrder1}"
    cash_up = baseMain.execute(f'SELECT cash_up FROM USERS WHERE user_id = {call.from_user.id}').fetchone()[0]
    await call.message.edit_text(f"✅Ваш бот: {anwerLink}\n💎Наценка: {cash_up}%\n\nВыберите желаемую наценку: ", reply_markup=markup_inline)
    chekOptionsEdit.worksettings = False
    await InputCountNumber.waiting_for_percent.set()
                                                                    

#КАЛБЕК НАЧАЛА СОЗДАНИЯ НОВОГО БОТА
@dp.callback_query_handler(text_startswith="startCreateBot")
async def startCreateBot(call: types.CallbackQuery):
    await call.answer()
    check_bots_limit = baseMain.execute(f'SELECT bot_token FROM USERS WHERE user_id = {call.from_user.id}').fetchone()[0]
    if len(str(check_bots_limit)) != 46:
        markup_inline = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton(text="❌Отмена", callback_data="Start")
        btn_procent_50 = types.InlineKeyboardButton('5%', callback_data='5p')
        btn_procent_75 = types.InlineKeyboardButton('10%', callback_data='10p')
        btn_procent_100 = types.InlineKeyboardButton('15%', callback_data='15p')
        btn_procent_125 = types.InlineKeyboardButton('20%', callback_data='20p')
        markup_inline.add(btn_procent_50, btn_procent_75, btn_procent_100, btn_procent_125).add(back_btn)
        await call.message.edit_text("💎Выберете желаемый процент наценки:", reply_markup=markup_inline)
        chekOptionsEdit.worksettings = True
        await InputCountNumber.waiting_for_percent.set()
    else:
        url = f"https://api.telegram.org/bot{check_bots_limit}/getMe"

        headers = {
            "accept": "application/json",
            "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)"
        }

        response = requests.post(url, headers=headers)
        data = response.json()
        responseOrder = data['result']
        responseOrder1 = responseOrder['username']
        anwerLink = "@" + f"{responseOrder1}"
        cash_up = baseMain.execute(f'SELECT cash_up FROM USERS WHERE user_id = {call.from_user.id}').fetchone()[0]
        markup_inline = types.InlineKeyboardMarkup()
        back_btn = types.InlineKeyboardButton(text="❌Отмена", callback_data="Start")
        btn_procent_50 = types.InlineKeyboardButton('5%', callback_data='5p')
        btn_procent_75 = types.InlineKeyboardButton('10%', callback_data='10p')
        btn_procent_100 = types.InlineKeyboardButton('15%', callback_data='15p')
        btn_procent_125 = types.InlineKeyboardButton('20%', callback_data='20p')
        markup_inline.add(btn_procent_50, btn_procent_75, btn_procent_100, btn_procent_125).add(back_btn)
        await call.message.edit_text(f"❌Ошибка! У вас уже есть активный бот\nВаш бот: {anwerLink}\n💎Наценка: {cash_up}%\n\nВыберите желаемую наценку: ", reply_markup=markup_inline)
        await InputCountNumber.waiting_for_percent.set()

class chekOptionsEdit:
    worksettings = True
    #МАШИНА ОЖИДАНИЯ НАЧАЛА СОЗДАНИЯ НОВОГО БОТА(ПРОЦЕНТЫ)
    @dp.callback_query_handler(lambda c: c.data in ['5p', '10p', '15p', '20p'], state=InputCountNumber.waiting_for_percent)
    async def process_percent_choice(query: types.CallbackQuery, state: FSMContext):
        while chekOptionsEdit.worksettings:
            percent = query.data[:-1]
            await state.update_data(percent=percent)
            message = query.message
            
            await bot.delete_message(chat_id=query.message.chat.id, message_id=query.message.message_id)
            await query.message.edit_text('🟠API ключ бота (который вы получили в @botfather):')

            async with state.proxy() as data:
                data['callMessageID'] = query.message.message_id
            await InputCountNumber.waiting_for_token.set()
        else:
            percent = query.data[:-1]
            await state.update_data(percent=percent)
            baseMain.execute(f'UPDATE USERS SET cash_up = {percent} WHERE user_id="{query.from_user.id}"')
            baseMain.commit()
            markup_inline = types.InlineKeyboardMarkup()
            back_btn = types.InlineKeyboardButton(text="❌Отмена", callback_data="Start")
            btn_procent_50 = types.InlineKeyboardButton('5%', callback_data='5p')
            btn_procent_75 = types.InlineKeyboardButton('10%', callback_data='10p')
            btn_procent_100 = types.InlineKeyboardButton('15%', callback_data='15p')
            btn_procent_125 = types.InlineKeyboardButton('20%', callback_data='20p')
            markup_inline.add(btn_procent_50, btn_procent_75, btn_procent_100, btn_procent_125).add(back_btn)
            bot_token = baseMain.execute(f'SELECT bot_token FROM USERS WHERE user_id = {query.from_user.id}').fetchone()[0]
            url = f"https://api.telegram.org/bot{bot_token}/getMe"

            headers = {
                "accept": "application/json",
                "User-Agent": "Telegram Bot SDK - (https://github.com/irazasyed/telegram-bot-sdk)"
            }

            response = requests.post(url, headers=headers)
            data = response.json()
            responseOrder = data['result']
            responseOrder1 = responseOrder['username']
            anwerLink = "@" + f"{responseOrder1}"
            cash_up = baseMain.execute(f'SELECT cash_up FROM USERS WHERE user_id = {query.from_user.id}').fetchone()[0]
            directory = baseMain.execute(f'SELECT user_bot FROM USERS WHERE user_id = {query.from_user.id}').fetchone()[0]
            await creator_bot.changeSettings(directory, cash_up)
            await query.message.edit_text(f"✅Ваш бот: {anwerLink}\n💎Наценка: {cash_up}%\n\nВыберите желаемую наценку: ", reply_markup=markup_inline)
            await state.finish()
            chekOptionsEdit.worksettings = False
            await InputCountNumber.waiting_for_percent.set()

    

#МАШИНА ОЖИДАНИЯ НАЧАЛА СОЗДАНИЯ НОВОГО БОТА(ТОКЕН)
@dp.message_handler(state=InputCountNumber.waiting_for_token)
async def process_new_bot(message: types.Message, state: FSMContext):
    data = await state.get_data()
    percent = data.get('percent')
    callMessageID = data.get("callMessageID")
    async with state.proxy() as proxy:
        proxy['messagesend'] = message.text 
    if proxy["messagesend"] != "" and proxy["messagesend"] != "/start":
        
        bot_token = message.text
        if len(bot_token) != 46:
            await bot.delete_message(message.chat.id, message.message_id)
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=callMessageID, text="❌Неверный формат токена. Токен должен быть длиной 46 символов.")
            await state.finish()
            async with state.proxy() as data:
                data['callMessageID'] = callMessageID
            await InputCountNumber.waiting_for_token.set()

        else:
            await bot.delete_message(message.chat.id, message.message_id)
            bot_name = f"{message.from_user.id}" + "_bot"
            try:
                baseMain.execute(f'UPDATE USERS SET user_bot= "{bot_name}", bot_token = "{bot_token}", cash_up = {percent} WHERE user_id="{message.from_user.id}"')
                baseMain.commit()
            except Exception as eroor:
                print(eroor)
            answer_good = await creator_bot.create_folder(percent, bot_token, bot_name)
            markup_inline = types.InlineKeyboardMarkup()
            test_btn_create_bot = types.InlineKeyboardButton(text="Создай своего бота💎", callback_data="create_new_bot")
            nakrutka = types.InlineKeyboardButton(text="Накрутка 💎", callback_data="nakrutkaaMain")
            balans = types.InlineKeyboardButton(text="Мой кошелёк 💵", callback_data="balanss")
            infoButton = types.InlineKeyboardButton(text="Информация", callback_data="infoButton")
            markup_inline.add(nakrutka).add(balans).add(infoButton).add(test_btn_create_bot)
            try:
                await bot.delete_message(message.chat.id, callMessageID + 1)
                await bot.send_message(chat_id=message.from_user.id, text=f'✅Вы успешно создали своего бота: {answer_good}, который полностью функционирует под вашу выбранную наценку.\nВы также можете изменить наценку для вашего бота в разделе "Создай своего бота - Настройки".', reply_markup=markup_inline)
            except Exception as e:
                print(e)
            await state.finish()
    else:
        await state.finish()

#МЕНЮ НАКРУТОК
@dp.callback_query_handler(text_startswith="nakrutkaa", state="*")
async def prev_page(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    current_state = await state.get_state()
    if current_state:  
        await state.finish()
    markup_inline = types.InlineKeyboardMarkup()
    telegram = types.InlineKeyboardButton(text="Телеграм", callback_data="servicetg")
    vkontakte = types.InlineKeyboardButton(text="ВКонтакте", callback_data="servicevk")
    insta = types.InlineKeyboardButton(text="Instagram", callback_data="serviceinst")
    youtube = types.InlineKeyboardButton(text="Youtube", callback_data="serviceyt")
    tiktok = types.InlineKeyboardButton(text="TikTok", callback_data="servicett")
    twitter = types.InlineKeyboardButton(text="Twitter", callback_data="servicetwt")
    likee = types.InlineKeyboardButton(text="Likee", callback_data="servicelk")
    odnoklassniki = types.InlineKeyboardButton(text="Одноклассники", callback_data="serviceok")
    glavnoe_menu = types.InlineKeyboardButton(text="Меню", callback_data="Start")
    markup_inline.add(telegram, vkontakte).add(insta, youtube).add(tiktok, odnoklassniki).add(twitter, likee).add(glavnoe_menu)

    await call.message.edit_text("Выберите социальную сеть:", reply_markup=markup_inline)

@dp.callback_query_handler(text_startswith="zakazz", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()
    markup = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
    markup.row_width = 1 # кол-во кнопок в строке
    markup.add(glavnoe_menu)

    listOrders = baseMain.execute(f'SELECT order_number, id_uslygi, date, link_on_group, status  FROM USER_ORDER WHERE id_user = {call.from_user.id}').fetchall()
    resultPrint = []
    try:
        for i in listOrders:
            b = f'{i[0]} | {i[2]} | {i[3]} | {i[4]}::'
            resultPrint.append(b)
            removeA = str(resultPrint).replace('::', '\n')
            removeB = str(removeA).replace("['", '')
            removeC = str(removeB).replace("']", '')
            removeD = str(removeC).replace("', '", '')
        await call.message.edit_text(f'⬇️Список заказов в работе⬇️ \n\n{removeD}', reply_markup=markup, disable_web_page_preview=True)
    except:
        await call.message.edit_text(f'⬇️Список заказов в работе⬇️ \n\nУ вас ещё нет заказов', reply_markup=markup, disable_web_page_preview=True)
            

#КАЛБЕК КНОПКИ "КОШЕЛЕК"
@dp.callback_query_handler(text_startswith="balanss", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    markup_inline = types.InlineKeyboardMarkup()
    oplataa = types.InlineKeyboardButton(text="Пополить баланс", callback_data="sendMoney")
    cash_out = types.InlineKeyboardButton(text="Вывести средства", callback_data="cashOutMoney")
    glavnoe_menu = types.InlineKeyboardButton(text="Назад", callback_data="Start")
    markup_inline.add(oplataa, cash_out).add(glavnoe_menu)
    moneyAccount = float('{:.2f}'.format(baseMain.execute(f'SELECT money FROM USERS WHERE user_id = {int(call.from_user.id)}').fetchone()[0]))
    moneyAccountEarned = float('{:.2f}'.format(baseMain.execute(f'SELECT earned FROM USERS WHERE user_id = {int(call.from_user.id)}').fetchone()[0]))
    await call.message.edit_text(f"Баланс для заказа услуг: {moneyAccount}р.\nБаланс на вывод: {moneyAccountEarned}р.", reply_markup=markup_inline)

#СОЗДАНИЕ ЗАЯВКИ НА ВЫВОД СРЕДСТВ
@dp.callback_query_handler(text_startswith="cashOutMoney", state="*")
async def admin_menu(call: types.CallbackQuery):
    await call.answer()
    markup_inline = types.InlineKeyboardMarkup()
    moneyCard = types.InlineKeyboardButton(text="💳На карту", callback_data="cashOutCard")
    moneyQiwi = types.InlineKeyboardButton(text="🥝На Qiwi", callback_data="cashOutQiwi")
    moneyYoomoney = types.InlineKeyboardButton(text="💰На Юмани", callback_data="cashOutYoomoney")
    glavnoe_menu = types.InlineKeyboardButton(text="❌Меню", callback_data="Start")
    markup_inline.add(moneyCard, moneyQiwi).add(moneyYoomoney).add(glavnoe_menu)

    moneyCashOut = baseMain.execute(f'SELECT earned FROM USERS WHERE user_id = {call.from_user.id}').fetchone()[0]

    moneyCard = float('{:.2f}'.format(float(moneyCashOut) - ((float(moneyCashOut)*0.03) + 45)))
    moneyQiwi = float('{:.2f}'.format(float(moneyCashOut) - (float(moneyCashOut)*0.03)))
    moneyYoomoney = float('{:.2f}'.format(float(moneyCashOut) - (float(moneyCashOut)*0.005)))
    await call.message.edit_text(f'✅Доступно к выводу: {moneyCashOut}р. \n\n‼️Минимальный вывод от 200р\n\nС комиссией:\n💳На карту: {moneyCard}р.\n🥝На Qiwi: {moneyQiwi}р.\n💰На Юмани: {moneyYoomoney}р.', reply_markup=markup_inline)

#ВЫВОД НА КАРТУ
@dp.callback_query_handler(text_startswith="cashOutCard", state="*")
async def cashOutCard(call: types.CallbackQuery, state: FSMContext):
    await call.answer()

    markup_inline = types.InlineKeyboardMarkup()
    glavnoe_menu = types.InlineKeyboardButton(text="❌Отмена", callback_data="Start")
    markup_inline.add(glavnoe_menu)
    moneyCashOut = baseMain.execute(f'SELECT earned FROM USERS WHERE user_id = {call.from_user.id}').fetchone()[0]
    moneyCard = float('{:.2f}'.format(float(moneyCashOut) - ((float(moneyCashOut)*0.03) + 45)))

    async with state.proxy() as data:
        data['callMessageID'] = call.message.message_id
        data['type_cash'] = "На карту"
        data['moneyCard'] = moneyCard
    #global_dict(call.message.message_id, "На карту", moneyCard, "add")
    await call.message.edit_text(f'✅Доступно к выводу: {moneyCard}р. \n\n‼️Минимальный вывод от 200р\n\nВведите желаемую сумму к выводу: ', reply_markup=markup_inline)
    await InputCountNumber.sum_cashout.set()

#ВЫВОД НА КИВИ
@dp.callback_query_handler(text_startswith="cashOutQiwi", state="*")
async def cashOutCard(call: types.CallbackQuery, state: FSMContext):
    await call.answer()

    markup_inline = types.InlineKeyboardMarkup()
    glavnoe_menu = types.InlineKeyboardButton(text="❌Отмена", callback_data="Start")
    markup_inline.add(glavnoe_menu)
    moneyCashOut = baseMain.execute(f'SELECT earned FROM USERS WHERE user_id = {call.from_user.id}').fetchone()[0]
    moneyQiwi = float('{:.2f}'.format(float(moneyCashOut) - (float(moneyCashOut)*0.03)))

    async with state.proxy() as data:
        data['callMessageID'] = call.message.message_id
        data['type_cash'] = "На Qiwi"
        data['moneyCard'] = moneyQiwi
    #global_dict(call.message.message_id, "На Qiwi", moneyQiwi, "add")
    await call.message.edit_text(f'✅Доступно к выводу: {moneyQiwi}р. \n\n‼️Минимальный вывод от 200р\n\nВведите желаемую сумму к выводу: ', reply_markup=markup_inline)
    await InputCountNumber.sum_cashout.set()

#ВЫВОД НА ЮМАНИ
@dp.callback_query_handler(text_startswith="cashOutYoomoney", state="*")
async def cashOutCard(call: types.CallbackQuery, state: FSMContext):
    await call.answer()

    markup_inline = types.InlineKeyboardMarkup()
    glavnoe_menu = types.InlineKeyboardButton(text="❌Отмена", callback_data="Start")
    markup_inline.add(glavnoe_menu)
    moneyCashOut = baseMain.execute(f'SELECT earned FROM USERS WHERE user_id = {call.from_user.id}').fetchone()[0]
    moneyYoomoney = float('{:.2f}'.format(float(moneyCashOut) - (float(moneyCashOut)*0.005)))

    async with state.proxy() as data:
        data['callMessageID'] = call.message.message_id
        data['type_cash'] = "На Юмани"
        data['moneyCard'] = moneyYoomoney
    #global_dict(call.message.message_id, "На Юмани", moneyYoomoney, "add")
    await call.message.edit_text(f'✅Доступно к выводу: {moneyYoomoney}р. \n\n‼️Минимальный вывод от 200р\n\nВведите желаемую сумму к выводу: ', reply_markup=markup_inline)
    await InputCountNumber.sum_cashout.set()

#МАШИНА СОСТОЯНИЙ ВЫПЛАТЫ ВОРКЕРУ(Сумма)
@dp.message_handler(state=InputCountNumber.sum_cashout) 
async def naviga(message: types.Message, state: FSMContext):
    data_state = await state.get_data()
    callMessageID = data_state.get("callMessageID")
    type_cash = data_state.get("type_cash")
    moneyCard = data_state.get("moneyCard")
    print(data_state)
    #await state.finish()
    async with state.proxy() as proxy:  # Устанавливаем состояние ожидания
        proxy['messagesendCash'] = message.text
    if proxy["messagesendCash"] != "/start" and proxy["messagesendCash"] != "":
        markup_inline = types.InlineKeyboardMarkup()
        markup_inlineError = types.InlineKeyboardMarkup()
        glavnoe_menu = types.InlineKeyboardButton(text="❌Отмена", callback_data="Start")
        markup_inline.add(glavnoe_menu)
        markup_inlineError.add(glavnoe_menu)
        answerCount = message.text
        messageID = callMessageID

        if float(answerCount) >= 200 and answerCount != "" and float(answerCount) <= float(moneyCard):
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=messageID, text=f'🟢Сумма к выплате: {answerCount}р.\n\nВведите реквезиты для выплаты:', reply_markup=markup_inline)
            #global_dict("", answerCount, "", "add")
            await state.finish()
            async with state.proxy() as data:
                data['callMessageID'] = callMessageID
                data['type_cash'] = type_cash
                data['moneyCard'] = moneyCard
                data['answerCount'] = answerCount
            await InputCountNumber.data_cashout.set() 
        else:
            await bot.delete_message(message.chat.id, message.message_id)
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=messageID, text=f'🔴Введенная сумма: {answerCount}р.\n\n🔼Максимальная сумма к выплате: {moneyCard}р.\n🔽Минимальная сумма выплаты: 200р. \n\n‼️Введите корректную сумму', reply_markup=markup_inlineError)
            await state.finish()
            async with state.proxy() as data:
                data['callMessageID'] = callMessageID
                data['type_cash'] = type_cash
                data['moneyCard'] = moneyCard
                data['answerCount'] = answerCount
            await InputCountNumber.sum_cashout.set()

        await bot.delete_message(message.chat.id, message.message_id)
    else:
        await state.finish()

#МАШИНА СОСТОЯНИЙ ВЫПЛАТЫ ВОРКЕРУ(реквезиты)
@dp.message_handler(state=InputCountNumber.data_cashout) 
async def naviga(message: types.Message, state: FSMContext):
    data_state = await state.get_data()
    callMessageID = data_state.get("callMessageID")
    type_cash = data_state.get("type_cash")
    moneyCard = data_state.get("moneyCard")
    answerCount_summ = data_state.get("answerCount")
    print(data_state)

    async with state.proxy() as proxy:  # Устанавливаем состояние ожидания
        proxy['messagesendCash'] = message.text
    if proxy["messagesendCash"] != "/start" and proxy["messagesendCash"] != "":
        markup_inline = types.InlineKeyboardMarkup()
        markup_inlineError = types.InlineKeyboardMarkup()
        oplataGenOrder = types.InlineKeyboardButton(text="✅Подтвердить", callback_data="startRequestCashOut")
        glavnoe_menu = types.InlineKeyboardButton(text="❌Отмена", callback_data="Start")
        markup_inline.add(oplataGenOrder).add(glavnoe_menu)
        markup_inlineError.add(glavnoe_menu)
        answerCount = message.text
        messageID = callMessageID

        if  answerCount != "" and answerCount != " ":
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=messageID, text=f'🟢Сумма к выплате: {answerCount_summ}р.\nРеквизиты выплаты: {answerCount}\n\nДля подтверждения вывода, нажмите кнопку ниже🔽', reply_markup=markup_inline)
            #global_dict("", answerCount, "", "add")
            await state.finish()
            async with state.proxy() as data:
                data['callMessageID'] = callMessageID
                data['type_cash'] = type_cash
                data['moneyCard'] = moneyCard
                data['answerCount'] = answerCount_summ
                data['answerCount_1'] = answerCount    
        else:
            await bot.delete_message(message.chat.id, message.message_id)
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=messageID, text=f'‼️Введите корректные реквизиты', reply_markup=markup_inlineError)
            await state.finish()
            async with state.proxy() as data:
                data['callMessageID'] = callMessageID
                data['type_cash'] = type_cash
                data['moneyCard'] = moneyCard
                data['answerCount'] = answerCount_summ
                data['answerCount_1'] = answerCount    
            await InputCountNumber.data_cashout.set()

        await bot.delete_message(message.chat.id, message.message_id)
    else:
        await state.finish()

#ЗАВЕРШЕНИЕ ЗАКАЗА ВЫПЛАТЫ
@dp.callback_query_handler(text_startswith="startRequestCashOut", state="*")
async def next_page(call: types.CallbackQuery, state: FSMContext):
    data_state = await state.get_data()
    #callMessageID = data_state.get("callMessageID")
    type_cash = data_state.get("type_cash")
    moneyCard = data_state.get("moneyCard")
    answerCount_summ = data_state.get("answerCount")
    answerCount_requez = data_state.get("answerCount_1")
    print(data_state)
    await call.answer()
    await state.finish()
    current_state = await state.get_state()
    print("pay request finish state: ", current_state)


    markup = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="❌Закрыть", callback_data="Start")
    markup.add(glavnoe_menu)
    

    lastBalance = float('{:.2f}'.format(float(moneyCard) - float(answerCount_summ)))
    baseMain.execute(f'UPDATE USERS SET earned = {float(lastBalance)} WHERE user_id = "{call.from_user.id}"')
    baseMain.commit()
    await botNotification.send_message('407073449', f'✅Новая заявка на выплату\nСумма: {answerCount_summ}р.\nСпособ выплаты: {type_cash}\nРеквизиты: {answerCount_requez}\nВоркер: {call.from_user.id}')
    await call.message.edit_text(f'✅Заявка на выплату успешно сформирована, ожидайте\n\nСумма: {answerCount_summ}р.\nРеквизиты: {answerCount_requez}', reply_markup=markup)
    baseMain.execute(f'DELETE FROM USER_ORDER WHERE status = "Выполнен✅"')
    baseMain.commit()

#ВЫБОР СИСТЕМЫ ОПЛАТЫ
@dp.callback_query_handler(text_startswith="sendMoney", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()
    
    markup_inline = types.InlineKeyboardMarkup()
    popolnenie = types.InlineKeyboardButton(text="Юмани", callback_data="uMoneyCash")
    glavnoe_menu = types.InlineKeyboardButton(text="Меню", callback_data="Start")
    markup_inline.add(popolnenie).add(glavnoe_menu)

    moneyAccount = float('{:.2f}'.format(baseMain.execute(f'SELECT money FROM USERS WHERE user_id = {int(call.from_user.id)}').fetchone()[0]))
    await call.message.edit_text(f'Выберете способ пополнения:\n\nВаш текущий баланс: {moneyAccount}р.', reply_markup=markup_inline)

#ПЛАТЕГА ЮМАНИ
@dp.callback_query_handler(text_startswith="uMoneyCash", state="*")
async def next_page(call: types.CallbackQuery, state: FSMContext):
    await call.answer()

    markup_inline = types.InlineKeyboardMarkup()
    glavnoe_menu = types.InlineKeyboardButton(text="Меню", callback_data="Start")
    markup_inline.add(glavnoe_menu)
    
    async with state.proxy() as data:
        data['message_id_user'] = call.message.message_id
    #global_dict(call.message.message_id, "", "", "add")
    await call.message.edit_text('Введите сумму к пополнению: \n\nМинимальное пополнение от 2р.', reply_markup=markup_inline)
    await InputCountNumber.sum_cost.set()
    

#МАШИНА СОСТОЯНИЯ (СУММА ОПЛАТЫ)
@dp.message_handler(state=InputCountNumber.sum_cost) 
async def naviga(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
            messageID_state = data['message_id_user']   
    async with state.proxy() as proxy:  # Устанавливаем состояние ожидания
        proxy['messagesendCash'] = message.text
    if proxy["messagesendCash"] != "/start" and proxy["messagesendCash"] != "":
        markup_inline = types.InlineKeyboardMarkup()
        oplataGenOrder = types.InlineKeyboardButton(text="Пополнить", callback_data="startRequestOplata")
        glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
        markup_inline.add(oplataGenOrder).add(glavnoe_menu)

        markup_inlineerr = types.InlineKeyboardMarkup()
        oplataGenOrder = types.InlineKeyboardButton(text="Пополнить", callback_data="startRequestOplata")
        glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
        markup_inlineerr.add(glavnoe_menu)
        answerCount = message.text
        messageID = messageID_state

        if int(answerCount) >= 2 and answerCount != "":
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=messageID, text=f'🟢Сумма пополнения: {answerCount}р. \n \n🟠Минимальная сумма пополнения 2р.', reply_markup=markup_inline)
            #global_dict("", answerCount, "", "add")
            await state.finish()
            async with state.proxy() as data:
                data['answer_summPay'] = answerCount  
        else:
            await bot.delete_message(message.chat.id, message.message_id)
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=messageID, text=f'🔴Сумма пополнения: {answerCount}р.\n \n‼️Введенная сумма меньше суммы пополнения \n \n🟠Минимальная сумма пополнения 2р.', reply_markup=markup_inlineerr)
            await state.finish()
            await InputCountNumber.sum_cost.set()

        await bot.delete_message(message.chat.id, message.message_id)
    else:
        await state.finish()
        


@dp.callback_query_handler(text_startswith="startRequestOplata", state="*")
async def next_page(call: types.CallbackQuery, state: FSMContext):
    await call.answer()

    async with state.proxy() as data:
        async with state.proxy() as data:
            sumPay = data['answer_summPay']

    labelSecret = ""
    for x in range(16): #Количество символов (16)
        labelSecret = labelSecret + random.choice(list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ')) #Символы, из которых будет 

    async with state.proxy() as data:
        data['labelSecret'] = labelSecret

    #global_dict("", "",labelSecret , "add")
    sumAddCash = sumPay
    summComissiaBD = float('{:.2f}'.format(float(sumAddCash) - (float(sumAddCash) * 0.03))) #РАСЧЁТ КОМИССИИ
    dateNow = str(datetime.now())
    dateNowG = dateNow.partition('.')[0]
    baseMain.execute(f'INSERT INTO USER_PAY (user_id, date, sum_cash, status, secretLabel) VALUES ("{call.from_user.id}", "{dateNowG}", {summComissiaBD}, "WAIT", "{labelSecret}");')
    baseMain.commit()
    
    linkAddCash =  testoplata.pay(labelSecret,sumAddCash)
    markup_inline = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton('Перейти на страницу оплаты', url=f'{linkAddCash}')
    popolnenie = types.InlineKeyboardButton(text="❌Отменить", callback_data="Start")
    #glavnoe_menu = types.InlineKeyboardButton(text="🔁Проверить оплату", callback_data="CheckOplata")
    markup_inline.add(button).add(popolnenie)

    await call.message.edit_text(f'Пополнение баланса на: {sumAddCash}р.\n\nС учётом комисии: {summComissiaBD}р.\n\n⏳Время на оплату: 15 минут \n\nДля пополнения баланса, нажмите на кнопку: "Перейти на страницу оплаты"', reply_markup=markup_inline)
    loops = asyncio.get_event_loop()
    checkMoneyTake.work = True
    loops.run_until_complete(checkMoneyTake.scheduledOplata(5, call.from_user.id, call.message.message_id)) # авточек баланса(пополнение)

        

@dp.callback_query_handler(text_startswith="CheckOplata")
async def next_page(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    
    markup_inline = types.InlineKeyboardMarkup()
    glavnoe_menu = types.InlineKeyboardButton(text="Меню", callback_data="Start")
    markup_inline.add(glavnoe_menu)

    async with state.proxy() as data:
            labelSecr = data['labelSecret']

    labelSecret = labelSecr
    checkOplata = testoplata.check_pay(labelSecret)
    if checkOplata[0] == "success":
        oldBalance =  baseMain.execute(f'SELECT money FROM USERS WHERE user_id = "{call.from_user.id}"').fetchone()[0]
        balanceToBase = float('{:.2f}'.format(oldBalance + checkOplata[1]))
        baseMain.execute(f'UPDATE USER_PAY SET status="success" WHERE secretLabel="{labelSecret}"')
        baseMain.commit()
        baseMain.execute(f'UPDATE USERS SET money="{balanceToBase}" WHERE user_id="{call.from_user.id}"')
        baseMain.commit()
        await call.message.edit_text(f'✅Ваш баланс успешно пополнен на {checkOplata[1]}р.', reply_markup=markup_inline)
    else:
        await call.message.edit_text(f'⏳Оплата ещё не дошла до нас, ожидайте', reply_markup=markup_inline)


#ЗАВЕРШЕНИЕ ЗАКАЗА УСЛУГИ
@dp.callback_query_handler(text_startswith="completeOrders", state="*")
async def completeOrder(call: types.CallbackQuery, state: FSMContext):

    data_state = await state.get_data()
    link_usr = data_state.get("answer")
    answerCount = data_state.get("answerCount")
    orderCost = data_state.get("orderCost")
    service_id = data_state.get("dictionary[0]")
    print(data_state)
    await call.answer()
    await state.finish()

    current_state = await state.get_state()
    print("state: ",current_state)

    markup_inlineNoBalance = types.InlineKeyboardMarkup()
    popolnenie = types.InlineKeyboardButton(text="✅Пополнить баланс", callback_data="sendMoney") # ТУТ НУЖНО ТЕМКУ СДЕЛАТЬ
    glavnoe_menu = types.InlineKeyboardButton(text="❌Отмена", callback_data="Start")
    markup_inlineNoBalance.add(popolnenie).add(glavnoe_menu)

    markup_inlineErrorServ = types.InlineKeyboardMarkup()
    glavnoe_menu = types.InlineKeyboardButton(text="❌Закрыть", callback_data="Start")
    markup_inlineErrorServ.add(glavnoe_menu)

    markup_inlineGood = types.InlineKeyboardMarkup()
    glavnoe_menu = types.InlineKeyboardButton(text="❌Закрыть", callback_data="Start")
    markup_inlineGood.add(glavnoe_menu)

    dateNow = str(datetime.now())
    dateNowG = dateNow.partition('.')[0]
    userMoney = baseMain.execute(f'SELECT money FROM USERS WHERE user_id = "{call.from_user.id}"').fetchone()[0]
    print(userMoney, orderCost)
    #print("БАЛАС ПОЛЬЗОВАТЕЛЯ ", get_data)
    if float(userMoney) >= float(orderCost):
        try:
            moneyAfter = float('{:.2f}'.format(float(userMoney) - float(orderCost)))
            baseMain.execute(f'UPDATE USERS SET money="{moneyAfter}" WHERE user_id="{call.from_user.id}"')
            baseMain.commit()

            answerCreateOrder = request.createOrder("add", service_id, link_usr, answerCount)
            baseMain.execute(f'INSERT INTO USER_ORDER (id_user, date, id_uslygi, link_on_group, quantity, money, order_number, status) VALUES ("{call.from_user.id}", "{str(dateNowG)}", "{service_id}", "{link_usr}", "{answerCount}", "{orderCost}", "{answerCreateOrder}", "✅В очереди на выполнение");')
            baseMain.commit()

            await call.message.edit_text(f'✅Заказ успешно сформирован!\n\nСылка: "{service_id}"\n➡️Количество: "{answerCount}"\n➡️Статус заказа: ✅В очереди на выполнение\n\n🎉Ждём вас снова!', reply_markup=markup_inlineGood, disable_web_page_preview=True) # делаем вывод инфы 
        except sq.Error as e:
            print("Failure: ", e)
            moneyBack = float('{:.2f}'.format(float(userMoney) + float(orderCost)))
            baseMain.execute(f'UPDATE USERS SET money="{moneyBack}" WHERE user_id="{call.from_user.id}"')
            baseMain.commit()
            await call.message.edit_text(f'❌Произошла ошибка на стороне сервера\n\n➡️Баланс возвращён: +{orderCost}р.', reply_markup=markup_inlineErrorServ) # делаем вывод инфы 
    else:
        await call.message.edit_text(f'❌У вас недостаточно средств для совершения операции \n\nВаш баланс: "{userMoney}"\n\nСтоимость заказа: "{orderCost}"', reply_markup=markup_inlineNoBalance) # делаем вывод инфы



@dp.callback_query_handler(text_startswith="podecjkaa", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()
    markup_inline = types.InlineKeyboardMarkup()
    glavnoe_menu = types.InlineKeyboardButton(text="Меню", callback_data="Start")
    markup_inline.add(glavnoe_menu)
    await call.message.edit_text('Часто задавемые  вопросы:\n\nКак долго создается бот и что такое наценка?\nСоздание бота происходит автоматически. Вам потребуется только указать свою наценку и отправить ваш токен, который вы получите у @botFather. После создания бота цены на услуги будут скоординированы под вашу выбранную наценку, где наценка и будет вашим заработком. Например, если установить наценку в 200%, услуга, которая стоила 1 рубль, будет стоить 2 рубля, где 1 рубль будет являться вашим доходом.\n\nГде посмотреть, сколько я заработал?\nВы можете найти эту информацию в основном боте в разделе "Мой кошелек". Учтите, что вывод средств происходит с задержкой с минимальной суммой вывода 200 рублей. Вы можете вывести средства на банковскую карту, YooMoney и Qiwi.\n\nПрисутствует ли комиссия при выводе средств?\nДа, при выводе средств может быть удержана комиссия. Её размер зависит от способа вывода и может быть разным. Подробнее об этом вы можете узнать в разделе "Мой кошелек" в основном боте.\n\nКакая задержка при выводе средств?\nЗадержка при выводе средств может быть разной в зависимости от выбранного способа вывода. Обычно она составляет от 1 часа до 5 рабочих дней. Некоторые способы вывода могут предусматривать более длительную задержку.\n\nЧто такое настройки?\nВы можете изменять наценку для уже созданного бота в любое время в разделе "Настройки" в основном боте.\n\nЕсли у вас осталсиь какие-либо вопросы, то можете написать в поддержку:\n@bk169\n@delowerCL', reply_markup=markup_inline)

@dp.callback_query_handler(text_startswith="pravilaa", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()
    markup_inline = types.InlineKeyboardMarkup()
    glavnoe_menu = types.InlineKeyboardButton(text="Меню", callback_data="Start")
    markup_inline.add(glavnoe_menu)
    await call.message.edit_text("Использование услуг, предоставляемых данных ботом - SMM сервисом, устанавливает согласие с этими условиями. Регистрируясь или используя наши сервисы, вы соглашаетесь с тем, что вы прочитали и полностью согласны с нижеприведёнными условиями обслуживания,"
                                 " и SMM сервис не будет нести ответственность за убытки в любом случае для пользователей, которые не читали нижеприведенные условия обслуживания."
                                 "\n""SMM сервис будет использоваться только для продвижения вашего аккаунта в Instagram / ВКонтакте / Telegram / Twitter / TikTok / YouTube или в любой другой социальной сети и только для повышения «внешнего вида» Вашего аккаунта. "
                                 "\n""Мы НЕ гарантируем, что ваши новые подписчики будут взаимодействовать с вами, мы просто гарантируем, что вы получите подписчиков, за которых вы платите. "
                                 "\n""Мы НЕ гарантируем, что 100% наших учетных записей будут иметь изображение профиля, полную биографию и загруженные изображения, хотя мы стремимся сделать это реальностью для всех учетных записей."
                                 "\n""То описание, которое мы предоставляем об услугах (от поставщиков) - являются только примерной оценкой, и описание может не соответствовать действительности. Мы стараемся исключать недоброкачественных поставщиков,"
                                 " и реализовывать взаимодействие с новыми, тем самым отбирая поставщиков с более качественными услугами. "
                                 "\n""Вы не будете отправлять на продвижение / накрутку любой запрещённый материал, включая обнаженные тела или любые материалы, которые не принимаются или не подходят для сообщества Instagram / ВКонтакте / Telegram / Twitter / YouTube и других социальных сетей"
                                 "\n""SMM бот НЕ гарантирует полную доставку в течение 24 часов. Мы не даем никаких гарантий на время доставки вообще. Мы предоставляем нашу лучшую оценку для заказов во время размещения заказов, однако, это оценки. Мы не несём"
                                 "ответственность за потерю средств, отрицательные отзывы или за то, что вас забанили за несвоевременную доставку. Если вы используете продвигаемый "
                                 "аккаунт(ы) в социальной сети(ях), которые требуют чувствительных ко времени результатов, то Вы используете SMM бота на свой страх и риск. "
                                 "\n""При формировании заказа, убедитесь что Ваша ссылка на накручиваемый обьект не является закрытой и не имеет возрастные ограничения. Если ссылка является закрытой, или имеет возрастные ограничения - средства поставщиком будут списаны, а сам факт накрутки может быть не произведён (в виду того что боты или пользователи,"
                                 " в автоматическом режиме не смогли выполнить услугу). В таком случае мы вернуть Вам средства не сможем."
                                 "\n""Учтите! Политика социальных сетей предполагает только живое, человеческое общение. "
                                 "Поэтому социальные сети как правило обычно выступают против любых попыток автоматизации и постоянно совершенствуют свои алгоритмы, которые выявляют автоматизированное продвижение. Под запрет так же попадают и сервисы автопродвижения. Если вы используете такие сервисы, для вас всегда существует риск получить бан аккаунта в социальной сети. При этом вы не сможете предъявить никакие претензии, "
                                 "ни к сервису, ни к администрации социальной сети, где использовали автопродвижение. Помните, что все действия вы проводите на свой страх и риск. "
                                 "\n""Возврат средств не производится, за исключением случаев, возникновения ошибок во время продвижения, о чём Вы должны сообщить через систему тикетов в личном кабинете. После того, как баланс в боте был пополнен, вернуть данные средства уже невозможно. "
                                 "Вы должны использовать свой баланс только на заказы"
                                 "\n""Вы соглашаетесь с тем, что после завершения платежа вы не будете подавать спор или возврат средств против нас по любой из причин."
                                 "\n""Если после пополнения баланса или оплаты услуги Вы подадите против нас спор или требование возвратного платежа за услуги,"
                                 " которые были оказаны (или переданы поставщику), мы оставляем за собой право аннулировать все Ваши будущие заказы, заблокировав вас в данном боте."
                                 "За оскорбления, или грубое проявление в сторону администрации, мы так же оставляем за собой право блокировки Вашего аккаунта."
                                 " Если у Вас возник какой то вопрос, или какие то неполадки - задавайте вопрос в вежливой, адекватной форме в телеграме, указанном в разделе Поддержка.", reply_markup=markup_inline)
#МЕНЮ ТЕЛЕГА
@dp.callback_query_handler(text_startswith="servicetg", state="*")
async def next_page(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    current_state = await state.get_state()
    print("state: ",current_state)
    if current_state:  
        await state.finish()
    markup_inline = types.InlineKeyboardMarkup()
    podpichiki = types.InlineKeyboardButton(text="Телеграм подписчики", callback_data="telegrampodpichiki")
    podpichiki_RU = types.InlineKeyboardButton(text="Телеграм подписчики (Россия)", callback_data="telegramsubscrivers_RU")
    telegram_views = types.InlineKeyboardButton(text="Телеграм просмотры", callback_data="telegram_views")
    telegram_react_all = types.InlineKeyboardButton(text="Телеграм реакции (для любых тематик)", callback_data="telegram_react_all")
    telegram_react = types.InlineKeyboardButton(text="Телеграм реакции🆕", callback_data="telegram_react")
    telegram_react_prem = types.InlineKeyboardButton(text="Телеграм премиум реакции", callback_data="telegram_react_prem")
    telegram_comment = types.InlineKeyboardButton(text="Телеграм комментарии", callback_data="telegram_comment")
    telegram_repost = types.InlineKeyboardButton(text="Телеграм репосты, опросы", callback_data="telegram_repost")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="nakrutkaa")
    markup_inline.add(podpichiki).add(podpichiki_RU).add(telegram_views).add(telegram_react_all).add(telegram_react).add(telegram_react_prem).add(telegram_comment).add(telegram_repost).add(nazad)

    await call.message.edit_text("Выберете тип накрутки:", reply_markup=markup_inline)



@dp.callback_query_handler(text_startswith="telegrampodpichiki", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Telegram") 
    markup = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="servicetg")
    markup.row_width = 1 # кол-во кнопок в строке
    #print(testdata)
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata: # цикл для создания кнопок
        if (str(i[0]) == str(288) or str(i[0]) == str(261) or str(i[0]) == str(269) or str(i[0]) == str(262) or str(i[0]) == str(70) or str(i[0]) == str(263)):
            
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=i[0])) #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    

    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

@dp.callback_query_handler(text_startswith="telegramsubscrivers_RU", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Telegram") 
    markup1 = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="servicetg")
    markup1.row_width = 1 # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata: # цикл для создания кнопок
        if (str(i[0]) == str(112) or str(i[0]) == str(47) or str(i[0]) == str(1) or str(i[0]) == str(192) or str(i[0]) == str(282) or str(i[0]) == str(283)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup1.add(types.InlineKeyboardButton(nameButton, callback_data=i[0])) #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup1.add(nazad)
    markup1.add(glavnoe_menu)

    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup1)

@dp.callback_query_handler(text_startswith="telegram_views", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Telegram") 
    markup = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="servicetg")
    markup.row_width = 1 # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata: # цикл для создания кнопок
        if (str(i[0]) == str(266) or str(i[0]) == str(100) or str(i[0]) == str(14) or str(i[0]) == str(111) or str(i[0]) == str(259) or str(i[0]) == str(26) or str(i[0]) == str(276) or str(i[0]) == str(275) or str(i[0]) == str(52)):
            nameButton = f'{i[1]} |Цена: {float("{:.3f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=i[0])) #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)

    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

@dp.callback_query_handler(text_startswith="telegram_react_all", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Telegram") 
    markup = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="servicetg")
    markup.row_width = 1 # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata: # цикл для создания кнопок
        if (str(i[0]) == str(277) or str(i[0]) == str(228) or str(i[0]) == str(216) or str(i[0]) == str(217) or str(i[0]) == str(218) or str(i[0]) == str(219) or str(i[0]) == str(220) or str(i[0]) == str(221) or str(i[0]) == str(222) or str(i[0]) == str(223) or str(i[0]) == str(224) or str(i[0]) == str(225) or str(i[0]) == str(226) or str(i[0]) == str(257) or str(i[0]) == str(258)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'      
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=i[0])) #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

@dp.callback_query_handler(text_startswith="telegram_react", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Telegram") 
    markup = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="servicetg")
    markup.row_width = 1 # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata: # цикл для создания кнопок
        if (str(i[0]) == str(233) or str(i[0]) == str(232) or str(i[0]) == str(245) or str(i[0]) == str(244) or str(i[0]) == str(243) or str(i[0]) == str(242) or str(i[0]) == str(241) or str(i[0]) == str(240) or str(i[0]) == str(239) or str(i[0]) == str(238) or str(i[0]) == str(237) or str(i[0]) == str(235) or str(i[0]) == str(234) or str(i[0]) == str(294)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=i[0])) #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)

    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

@dp.callback_query_handler(text_startswith="telegram_react_prem", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Telegram") 
    markup = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="servicetg")
    markup.row_width = 1 # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata: # цикл для создания кнопок
        if (str(i[0]) == str(247) or str(i[0]) == str(256) or str(i[0]) == str(248) or str(i[0]) == str(249) or str(i[0]) == str(250) or str(i[0]) == str(251) or str(i[0]) == str(252) or str(i[0]) == str(253) or str(i[0]) == str(254) or str(i[0]) == str(255)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=i[0])) #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

@dp.callback_query_handler(text_startswith="telegram_comment", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Telegram") 
    markup = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="servicetg")
    markup.row_width = 1 # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata: # цикл для создания кнопок
        if (str(i[0]) == str(431254321421)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=i[0])) #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)

    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

@dp.callback_query_handler(text_startswith="telegram_repost", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Telegram") 
    markup = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="servicetg")
    markup.row_width = 1 # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata: # цикл для создания кнопок
        if (str(i[0]) == str(152) or str(i[0]) == str(76)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=i[0])) #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)

    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

#МЕНЮ ВК
@dp.callback_query_handler(text_startswith="servicevk", state="*")
async def next_page(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    current_state = await state.get_state()
    print("state: ",current_state)
    if current_state:  
        await state.finish()
    markup_inline = types.InlineKeyboardMarkup()
    vkLikes = types.InlineKeyboardButton(text="Вконтакте лайки", callback_data="vklike")
    vkSubs = types.InlineKeyboardButton(text="Вконтакте подписчики", callback_data="vksubs")
    vkViews = types.InlineKeyboardButton(text="Вконтакте просмотры", callback_data="vkviews")
    vkReposts = types.InlineKeyboardButton(text="Вконтакте репосты", callback_data="vkrepost")
    vkComments = types.InlineKeyboardButton(text="Вконтакте комментарии", callback_data="vkcomment")
    vkOpros = types.InlineKeyboardButton(text="Вконтакте опросы", callback_data="vkopros")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="nakrutkaa")
    markup_inline.add(vkLikes).add(vkSubs).add(vkViews).add(vkReposts).add(vkReposts).add(vkComments).add(vkOpros).add(nazad)
    await call.message.edit_text("Выберете тип накрутки:", reply_markup=markup_inline)

@dp.callback_query_handler(text_startswith="vklike", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Вконтакте") 
    markup = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="servicevk")
    markup.row_width = 1 # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata: # цикл для создания кнопок
        if (str(i[0]) == str(289) or str(i[0]) == str(138) or str(i[0]) == str(286) or str(i[0]) == str(56) or str(i[0]) == str(141) or str(i[0]) == str(151) or str(i[0]) == str(104) or str(i[0]) == str(72) or str(i[0]) == str(106) or str(i[0]) == str(201) or str(i[0]) == str(209)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(f'vk{i[0]}'))) #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

@dp.callback_query_handler(text_startswith="vksubs", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Вконтакте") 
    markup = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="servicevk")
    markup.row_width = 1 # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata: # цикл для создания кнопок
        if (str(i[0]) == str(211) or str(i[0]) == str(136) or str(i[0]) == str(64) or str(i[0]) == str(212) or str(i[0]) == str(137) or str(i[0]) == str(65) or str(i[0]) == str(290) or str(i[0]) == str(215) or str(i[0]) == str(135) or str(i[0]) == str(205) or str(i[0]) == str(181)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(f'vk{i[0]}'))) #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

@dp.callback_query_handler(text_startswith="vkviews", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Вконтакте") 
    markup = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="servicevk")
    markup.row_width = 1 # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata: # цикл для создания кнопок
        if (str(i[0]) == str(265) or str(i[0]) == str(122) or str(i[0]) == str(143) or str(i[0]) == str(161) or str(i[0]) == str(142) or str(i[0]) == str(140) or str(i[0]) == str(195) or str(i[0]) == str(202)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(f'vk{i[0]}'))) #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

@dp.callback_query_handler(text_startswith="vkrepost", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Вконтакте") 
    markup = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="servicevk")
    markup.row_width = 1 # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata: # цикл для создания кнопок
        if (str(i[0]) == str(206) or str(i[0]) == str(210) or str(i[0]) == str(203)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(f'vk{i[0]}'))) #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

@dp.callback_query_handler(text_startswith="vkcomment", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Вконтакте") 
    markup = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="servicevk")
    markup.row_width = 1 # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata: # цикл для создания кнопок
        if (str(i[0]) == str(204)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(f'vk{i[0]}'))) #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

@dp.callback_query_handler(text_startswith="vkopros", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Вконтакте") 
    markup = types.InlineKeyboardMarkup() # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору соц.сети", callback_data="servicevk")
    markup.row_width = 1 # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata: # цикл для создания кнопок
        if (str(i[0]) == str(268) or str(i[0]) == str(165)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(f'vk{i[0]}'))) #Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

#МЕНЮ ИНСТА
@dp.callback_query_handler(text_startswith="serviceinst", state="*")
async def next_page(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    current_state = await state.get_state()
    print("state: ",current_state)
    if current_state:  
        await state.finish()
    markup_inline = types.InlineKeyboardMarkup()
    instalike = types.InlineKeyboardButton(text="Instagram лайки (микс)", callback_data="instagramlike")
    instalikereal = types.InlineKeyboardButton(text="Instagram лайки (реальные)", callback_data="instagramlikereal")
    instasub = types.InlineKeyboardButton(text="Instagram подписчики (микс)", callback_data="instagramsubsriber")
    instasubreal = types.InlineKeyboardButton(text="Instagram подписчики (реальные)", callback_data="instagramsubcriberreal")
    instasubpod = types.InlineKeyboardButton(text="Instagram подписчики (с докруткой)🔃", callback_data="instagramsubcriberpod")
    instaview = types.InlineKeyboardButton(text="Instagram просмотры", callback_data="instagramview")
    instacomm = types.InlineKeyboardButton(text="Instagram комментарии", callback_data="instagramcomments")
    instastat = types.InlineKeyboardButton(text="Instagram статистика", callback_data="instagramstatic")
    instaque = types.InlineKeyboardButton(text="❓❓❓", callback_data="instagramquestion")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="nakrutkaa")
    markup_inline.add(instalike).add(instalikereal).add(instasub).add(instasubreal).add(instasubpod).add(instaview).add(instacomm).add(instastat).add(instaque).add(nazad)

    await call.message.edit_text("Выберете тип накрутки:", reply_markup=markup_inline)


# INSAGRAM лайки(микс)
@dp.callback_query_handler(text_startswith="instagramlike", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()
    testdata = request.checkList("packages", "Instagram")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="serviceinst")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(21) or str(i[0]) == str(285) or str(i[0]) == str(96) or str(i[0]) == str(157) or str(i[0]) == str(171) or str(i[0]) == str(62) or str(i[0]) == str(134) or str(i[0]) == str(267) or str(i[0]) == str(48) or str(i[0]) == str(110) or str(i[0]) == str(63) or str(i[0]) == str(24) or str(i[0]) == str(105) or str(i[0]) == str(50)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(f'in{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# INSAGRAM лайки(реальные)
@dp.callback_query_handler(text_startswith="instagramlikereal", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Instagram")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="serviceinst")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(6) or str(i[0]) == str(121) or str(i[0]) == str(145) or str(i[0]) == str(89) or str(
                i[0]) == str(99) or str(i[0]) == str(101) or str(i[0]) == str(187) or str(i[0]) == str(60) or str(
                i[0]) == str(144) or str(i[0]) == str(108) or str(i[0]) == str(120) or str(i[0]) == str(49) or str(
                i[0]) == str(53)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(f'in{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# INSAGRAM подписчики(микс)
@dp.callback_query_handler(text_startswith="instagramsubsriber", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Instagram")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="serviceinst")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(163) or str(i[0]) == str(127) or str(i[0]) == str(92) or str(i[0]) == str(31) or str(
                i[0]) == str(33) or str(i[0]) == str(78)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(f'in{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# INSAGRAM подписчики(реальные)
@dp.callback_query_handler(text_startswith="instagramsubcriberreal", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Instagram")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="serviceinst")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(83) or str(i[0]) == str(128) or str(i[0]) == str(23) or str(i[0]) == str(84) or str(
                i[0]) == str(44) or str(i[0]) == str(277) or str(i[0]) == str(85)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(f'in{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# INSAGRAM подписчики(с докруткой)
@dp.callback_query_handler(text_startswith="instagramsubcriberpod", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Instagram")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="serviceinst")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(293) or str(i[0]) == str(75) or str(i[0]) == str(113) or str(i[0]) == str(125) or str(
                i[0]) == str(183) or str(i[0]) == str(132) or str(i[0]) == str(79) or str(i[0]) == str(77) or str(
                i[0]) == str(77) or str(i[0]) == str(130) or str(i[0]) == str(148) or str(i[0]) == str(67)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(f'in{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# INSAGRAM просмотры
@dp.callback_query_handler(text_startswith="instagramview", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Instagram")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="serviceinst")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(146) or str(i[0]) == str(71) or str(i[0]) == str(102) or str(i[0]) == str(43) or str(
                i[0]) == str(158) or str(i[0]) == str(200) or str(i[0]) == str(147) or str(i[0]) == str(55) or str(
                i[0]) == str(40) or str(i[0]) == str(41) or str(i[0]) == str(32) or str(i[0]) == str(38) or str(
                i[0]) == str(8)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(f'in{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# INSAGRAM комментарии
@dp.callback_query_handler(text_startswith="instagramcomments", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Instagram")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="serviceinst")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(177) or str(i[0]) == str(199) or str(i[0]) == str(180) or str(i[0]) == str(189) or str(
                i[0]) == str(51) or str(i[0]) == str(39) or str(i[0]) == str(74)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(f'in{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# INSAGRAM статистика
@dp.callback_query_handler(text_startswith="instagramstatic", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Instagram")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="serviceinst")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(186) or str(i[0]) == str(82) or str(i[0]) == str(10) or str(i[0]) == str(169) or str(
                i[0]) == str(168) or str(i[0]) == str(36) or str(i[0]) == str(149)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(f'in{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# INSAGRAM ???
@dp.callback_query_handler(text_startswith="instagramquestion", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Instagram")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="serviceinst")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(176) or str(i[0]) == str(271) or str(i[0]) == str(22) or str(i[0]) == str(73) or str(
                i[0]) == str(19) or str(i[0]) == str(159) or str(i[0]) == str(54)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(f'in{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)


#МЕНЮ ЮТУБ
@dp.callback_query_handler(text_startswith="serviceyt", state="*")
async def next_page(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    current_state = await state.get_state()
    print("state: ",current_state)
    if current_state:  
        await state.finish()
    markup_inline = types.InlineKeyboardMarkup()
    youtubelike = types.InlineKeyboardButton(text="Youtube лайки и дизлайки", callback_data="youtubelikeanddislike")
    youtubeview = types.InlineKeyboardButton(text="Youtube просмотры", callback_data="youtubeviews")
    youtubesub = types.InlineKeyboardButton(text="Youtube подписчики", callback_data="youtubesubscriber")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="nakrutkaa")
    markup_inline.add(youtubelike).add(youtubeview).add(youtubesub).add(nazad)
    await call.message.edit_text("Выберете тип накрутки:", reply_markup=markup_inline)


#YOUTUBE ЛАЙКИ И ДИЗЛАЙКИ
@dp.callback_query_handler(text_startswith="youtubelikeanddislike", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Youtube")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="serviceyt")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(66) or str(i[0]) == str(119) or str(i[0]) == str(167) or str(i[0]) == str(162)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'yt{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)
    
# YOUTUBE ПРОСМОТРЫ
@dp.callback_query_handler(text_startswith="youtubeviews", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Youtube")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="serviceyt")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(178) or str(i[0]) == str(198) or str(i[0]) == str(197) or str(i[0]) == str(179) or str(
                i[0]) == str(284) or str(i[0]) == str(196)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'yt{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)
    
# YOUTUBE ПОДПИСЧИКИ
@dp.callback_query_handler(text_startswith="youtubesubscriber", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Youtube")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="nakrutkaa")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(118)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'yt{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)


#МЕНЮ ТИК ТОК
@dp.callback_query_handler(text_startswith="servicett", state="*")
async def next_page(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    current_state = await state.get_state()
    print("state: ",current_state)
    if current_state:  
        await state.finish()
    markup_inline = types.InlineKeyboardMarkup()
    tiktoksub = types.InlineKeyboardButton(text="TikTok подписчики", callback_data="tiktoksubscriber")
    tiktokvi = types.InlineKeyboardButton(text="TikTok просмотры", callback_data="tiktokview")
    tiktoklik = types.InlineKeyboardButton(text="TikTok лайки", callback_data="tiktoklike")
    tiktokrep = types.InlineKeyboardButton(text="TikTok репосты", callback_data="tiktokrepost")
    tiktokcom = types.InlineKeyboardButton(text="TikTok комментарии", callback_data="tiktokcomments")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="nakrutkaa")
    markup_inline.add(tiktoksub).add(tiktokvi).add(tiktoklik).add(tiktokrep).add(tiktokcom).add(nazad)
    await call.message.edit_text("Выберете тип накрутки:", reply_markup=markup_inline)

# TIKTOK Подписчики
@dp.callback_query_handler(text_startswith="tiktoksubscriber", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "TikTok")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="servicett")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(68) or str(i[0]) == str(35) or str(i[0]) == str(20) or str(i[0]) == str(4) or str(
                i[0]) == str(273) or str(i[0]) == str(129) or str(i[0]) == str(123) or str(i[0]) == str(156)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'tt{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# TIKTOK просмотры
@dp.callback_query_handler(text_startswith="tiktokview", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "TikTok")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="servicett")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(29) or str(i[0]) == str(190) or str(i[0]) == str(153) or str(i[0]) == str(172) or str(
                i[0]) == str(45) or str(i[0]) == str(28)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'tt{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# TIKTOK лайки
@dp.callback_query_handler(text_startswith="tiktoklike", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "TikTok")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="servicett")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(12) or str(i[0]) == str(61) or str(i[0]) == str(46) or str(i[0]) == str(292) or str(
                i[0]) == str(34) or str(i[0]) == str(11) or str(i[0]) == str(274) or str(i[0]) == str(173) or str(
                i[0]) == str(126)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'tt{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# TIKTOK репосты
@dp.callback_query_handler(text_startswith="tiktokrepost", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "TikTok")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="servicett")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(174) or str(i[0]) == str(193)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'tt{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# TIKTOK комментарии
@dp.callback_query_handler(text_startswith="tiktokcomments", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "TikTok")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="servicett")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(103) or str(i[0]) == str(213)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'tt{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

#МЕНЮ ТВИТТЕР
@dp.callback_query_handler(text_startswith="servicetwt", state="*")
async def next_page(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    current_state = await state.get_state()
    print("state: ",current_state)
    if current_state:  
        await state.finish()
    markup_inline = types.InlineKeyboardMarkup()
    twitterlike = types.InlineKeyboardButton(text="Twitter лайки", callback_data="twitterlik")
    twitterret = types.InlineKeyboardButton(text="Twitter ретвиты", callback_data="twitterretvit")
    twitterfoll = types.InlineKeyboardButton(text="Twitter фолловеры", callback_data="twitterfollow")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="nakrutkaa")
    markup_inline.add(twitterlike).add(twitterret).add(twitterfoll).add(nazad)

    await call.message.edit_text("Выберете тип накрутки:", reply_markup=markup_inline)

# Twitter лайки
@dp.callback_query_handler(text_startswith="twitterlik", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Twitter")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="servicetwt")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(30)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'tw{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# Twitter ретвиты
@dp.callback_query_handler(text_startswith="twitterretvit", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Twitter")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="servicetwt")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(15)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'tw{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# Twitter фолловеры
@dp.callback_query_handler(text_startswith="twitterfollow", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Twitter")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="servicetwt")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(25)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'tw{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

#МЕНЮ ЛАЙК(СЕРВИС ТАКОЙ)
@dp.callback_query_handler(text_startswith="servicelk", state="*")
async def next_page(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    current_state = await state.get_state()
    print("state: ",current_state)
    if current_state:  
        await state.finish()
    markup_inline = types.InlineKeyboardMarkup()
    likeelik = types.InlineKeyboardButton(text="Likee лайки", callback_data="likeelike")
    likeesub = types.InlineKeyboardButton(text="Likee подписчики", callback_data="likeesubscriber")
    likeeprosmoti = types.InlineKeyboardButton(text="Likee просмотры", callback_data="likeeview")
    likeerep = types.InlineKeyboardButton(text="Likee репосты", callback_data="likeerepost")
    likeecom = types.InlineKeyboardButton(text="Likee комментарии", callback_data="likeecomments")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="nakrutkaa")
    markup_inline.add(likeelik).add(likeesub).add(likeeprosmoti).add(likeerep).add(likeecom).add(nazad)

    await call.message.edit_text("Выберете тип накрутки:", reply_markup=markup_inline)

# Likee лайки
@dp.callback_query_handler(text_startswith="likeelike", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Likee")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="servicelk")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(2)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'li{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# Likee ПОДПИСЧИКИ
@dp.callback_query_handler(text_startswith="likeesubscriber", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Likee")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="servicelk")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(59)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'li{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# Likee просмотры
@dp.callback_query_handler(text_startswith="likeeview", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Likee")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="servicelk")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(5)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'li{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# Likee репосты
@dp.callback_query_handler(text_startswith="likeerepost", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Likee")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="servicelk")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(3)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'li{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)

# Likee комментарии
@dp.callback_query_handler(text_startswith="likeecomments", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Likee")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="servicelk")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(9)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'li{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)


#МЕНЮ ОДНОКЛАССНИКИ
@dp.callback_query_handler(text_startswith="serviceok", state="*")
async def next_page(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    current_state = await state.get_state()
    print("state: ",current_state)
    if current_state:  
        await state.finish()
    markup_inline = types.InlineKeyboardMarkup()
    podpichiki = types.InlineKeyboardButton(text="ОК классы", callback_data="okclassi")
    podpichiki_RU = types.InlineKeyboardButton(text="ОК подписчики", callback_data="okpodpichiki")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="nakrutkaa")
    markup_inline.add(podpichiki).add(podpichiki_RU).add(nazad)

    await call.message.edit_text("Выберете тип накрутки:", reply_markup=markup_inline)

# ОК КЛАССЫ
@dp.callback_query_handler(text_startswith="okclassi", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Одноклассники")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="serviceok")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(7)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'ok{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)
    
# ОК ПОДПИСЧИКИ
@dp.callback_query_handler(text_startswith="okpodpichiki", state="*")  # (ПОМЕНЯТЬ АЙДИ)
async def next_page(call: types.CallbackQuery):
    await call.answer()

    testdata = request.checkList("packages", "Одноклассники")
    markup = types.InlineKeyboardMarkup()  # создаём клавиатуру
    glavnoe_menu = types.InlineKeyboardButton(text="▶️Меню", callback_data="Start")
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="serviceok")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config_main.txt')[1]
    cashAdmin = getSettings('config_main.txt')[2]
    for i in testdata:  # цикл для создания кнопок
        if (str(i[0]) == str(150) or str(i[0]) == str(191) or str(i[0]) == str(57) or str(i[0]) == str(214)):
            nameButton = f'{i[1]} |Цена: {float("{:.2f}".format((((i[5]/1000) * (float(int(cashUser) + int(cashAdmin))/100)) + (i[5]/1000)))) }р./1'
            markup.add(types.InlineKeyboardButton(nameButton, callback_data=(
                f'ok{i[0]}')))  # Создаём кнопки, i[1] - название, i[2] - каллбек дата
    markup.add(nazad)
    markup.add(glavnoe_menu)
    await call.message.edit_text("Что хотите накрутить?", reply_markup=markup)


#Каллбек заказа
@dp.callback_query_handler(lambda call: True)
async def stoptopupcall(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    
    markup_inline = types.InlineKeyboardMarkup()
    if call.data.find("vk") == 0:
        callbackButton = "servicevk"
        nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору услуги", callback_data=callbackButton)
        glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
        markup_inline.add(nazad).add(glavnoe_menu)

        rightCall = re.sub(r'[^0-9]+', r'', call.data)
        testdata = request.checkList("packages", "Вконтакте")
        for dictionary in testdata:
            if any(map(str.isdigit, rightCall)):
                if (int(dictionary[0]) == int(rightCall)):
                    answer = dictionary[2].split('⌛')[1]
                    answer1 = re.sub(r'С([^<>]+)О','\nО', answer)
                    answer1 = re.sub(r'!([^<>]+)В','\n‼️В', answer1)
                    await call.message.edit_text(f'{answer1}, \n \n \n Пришлите ссылку для накрутки: ', reply_markup=markup_inline) # делаем вывод инфы
                    async with state.proxy() as data:
                        data['call_message_id1'] = call.message.message_id
                        data['rightCall'] = rightCall
                        data['message_id'] = "Вконтакте"
                    #global_dict(call.message.message_id, rightCall, "Вконтакте", "add")
                    await InputCountNumber.link_text.set()

    elif call.data.find("in") == 0:
        callbackButton = "serviceinst"
        nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору услуги", callback_data=callbackButton)
        glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
        markup_inline.add(nazad).add(glavnoe_menu)

        rightCall = re.sub(r'[^0-9]+', r'', call.data)
        testdata = request.checkList("packages", "Instagram")
        for dictionary in testdata:
            if any(map(str.isdigit, rightCall)):
                if (int(dictionary[0]) == int(rightCall)):
                    answer = dictionary[2].split('⌛')[1]
                    answer1 = re.sub(r'С([^<>]+)О','\nО', answer)
                    answer1 = re.sub(r'!([^<>]+)В','\n‼️В', answer1)
                    await call.message.edit_text(f'{answer1}, \n \n \n Пришлите ссылку для накрутки: ', reply_markup=markup_inline) # делаем вывод инфы
                    async with state.proxy() as data:
                        data['call_message_id1'] = call.message.message_id
                        data['rightCall'] = rightCall
                        data['message_id'] = "Instagram"
                    #global_dict(call.message.message_id, rightCall, "Instagram", "add")
                    await InputCountNumber.link_text.set()

    elif call.data.find("yt") == 0:
        callbackButton = "serviceyt"
        nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору услуги", callback_data=callbackButton)
        glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
        markup_inline.add(nazad).add(glavnoe_menu)

        rightCall = re.sub(r'[^0-9]+', r'', call.data)
        testdata = request.checkList("packages", "Youtube")
        for dictionary in testdata:
            if any(map(str.isdigit, rightCall)):
                if (int(dictionary[0]) == int(rightCall)):
                    answer = dictionary[2].split('⌛')[1]
                    answer1 = re.sub(r'С([^<>]+)О','\nО', answer)
                    answer1 = re.sub(r'!([^<>]+)В','\n‼️В', answer1)
                    await call.message.edit_text(f'{answer1}, \n \n \n Пришлите ссылку для накрутки: ', reply_markup=markup_inline) # делаем вывод инфы
                    async with state.proxy() as data:
                        data['call_message_id1'] = call.message.message_id
                        data['rightCall'] = rightCall
                        data['message_id'] = "Youtube"
                    #global_dict(call.message.message_id, rightCall, "Youtube", "add")
                    await InputCountNumber.link_text.set()

    elif call.data.find("tt") == 0:
        callbackButton = "servicett"
        nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору услуги", callback_data=callbackButton)
        glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
        markup_inline.add(nazad).add(glavnoe_menu)

        rightCall = re.sub(r'[^0-9]+', r'', call.data)
        testdata = request.checkList("packages", "TikTok")
        for dictionary in testdata:
            if any(map(str.isdigit, rightCall)):
                if (int(dictionary[0]) == int(rightCall)):
                    answer = dictionary[2].split('⌛')[1]
                    answer1 = re.sub(r'С([^<>]+)О','\nО', answer)
                    answer1 = re.sub(r'!([^<>]+)В','\n‼️В', answer1)
                    await call.message.edit_text(f'{answer1}, \n \n \n Пришлите ссылку для накрутки: ', reply_markup=markup_inline) # делаем вывод инфы
                    async with state.proxy() as data:
                        data['call_message_id1'] = call.message.message_id
                        data['rightCall'] = rightCall
                        data['message_id'] = "TikTok"
                    #global_dict(call.message.message_id, rightCall, "TikTok", "add")
                    await InputCountNumber.link_text.set()
    
    elif call.data.find("tw") == 0:
        callbackButton = "servicetwt"
        nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору услуги", callback_data=callbackButton)
        glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
        markup_inline.add(nazad).add(glavnoe_menu)

        rightCall = re.sub(r'[^0-9]+', r'', call.data)
        testdata = request.checkList("packages", "Twitter")
        for dictionary in testdata:
            if any(map(str.isdigit, rightCall)):
                if (int(dictionary[0]) == int(rightCall)):
                    answer = dictionary[2].split('⌛')[1]
                    answer1 = re.sub(r'С([^<>]+)О','\nО', answer)
                    answer1 = re.sub(r'!([^<>]+)В','\n‼️В', answer1)
                    await call.message.edit_text(f'{answer1}, \n \n \n Пришлите ссылку для накрутки: ', reply_markup=markup_inline) # делаем вывод инфы
                    async with state.proxy() as data:
                        data['call_message_id1'] = call.message.message_id
                        data['rightCall'] = rightCall
                        data['message_id'] = "Twitter"
                    #global_dict(call.message.message_id, rightCall, "Twitter", "add")
                    await InputCountNumber.link_text.set()

    elif call.data.find("li") == 0:
        callbackButton = "servicelk"
        nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору услуги", callback_data=callbackButton)
        glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
        markup_inline.add(nazad).add(glavnoe_menu)

        rightCall = re.sub(r'[^0-9]+', r'', call.data)
        testdata = request.checkList("packages", "Likee")
        for dictionary in testdata:
            if any(map(str.isdigit, rightCall)):
                if (int(dictionary[0]) == int(rightCall)):
                    answer = dictionary[2].split('⌛')[1]
                    answer1 = re.sub(r'С([^<>]+)О','\nО', answer)
                    answer1 = re.sub(r'!([^<>]+)В','\n‼️В', answer1)
                    await call.message.edit_text(f'{answer1}, \n \n \n Пришлите ссылку для накрутки: ', reply_markup=markup_inline) # делаем вывод инфы
                    async with state.proxy() as data:
                        data['call_message_id1'] = call.message.message_id
                        data['rightCall'] = rightCall
                        data['message_id'] = "Likee"
                    #global_dict(call.message.message_id, rightCall, "Likee", "add")
                    await InputCountNumber.link_text.set()

    elif call.data.find("ok") == 0:
        callbackButton = "serviceok"
        nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору услуги", callback_data=callbackButton)
        glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
        markup_inline.add(nazad).add(glavnoe_menu)

        rightCall = re.sub(r'[^0-9]+', r'', call.data)
        testdata = request.checkList("packages", "Одноклассники")
        for dictionary in testdata:
            if any(map(str.isdigit, rightCall)):
                if (int(dictionary[0]) == int(rightCall)):
                    answer = dictionary[2].split('⌛')[1]
                    answer1 = re.sub(r'С([^<>]+)О','\nО', answer)
                    answer1 = re.sub(r'!([^<>]+)В','\n‼️В', answer1)
                    await call.message.edit_text(f'{answer1}, \n \n \n Пришлите ссылку для накрутки: ', reply_markup=markup_inline) # делаем вывод инфы
                    async with state.proxy() as data:
                        data['call_message_id1'] = call.message.message_id
                        data['rightCall'] = rightCall
                        data['message_id'] = "Одноклассники"
                    #global_dict(call.message.message_id, rightCall, "Одноклассники", "add")
                    await InputCountNumber.link_text.set()
    else:
        callbackButton = "servicetg"
        nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору услуги", callback_data=callbackButton)
        glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
        markup_inline.add(nazad).add(glavnoe_menu)
        
        testdata = request.checkList("packages", "Telegram")
        for dictionary in testdata:
            if any(map(str.isdigit, call.data)):
                if (int(dictionary[0]) == int(call.data)):
                    answer = dictionary[2].split('⌛')[1]
                    answer1 = re.sub(r'С([^<>]+)О','\nО', answer)
                    answer1 = re.sub(r'!([^<>]+)В','\n‼️В', answer1)
                    await call.message.edit_text(f'{answer1}, \n \n \n Пришлите ссылку для накрутки: ', reply_markup=markup_inline) # делаем вывод инфы
                    #global_dict(call.message.message_id, call.data,"Telegram", "add")

                    await state.set_state(InputCountNumber.link_text)
                    async with state.proxy() as data:
                        data['call_message_id1'] = call.message.message_id
                        data['rightCall'] = call.data
                        data['message_id'] = "Telegram"

    
#Ожидание ссылки на накрутку
@dp.message_handler(state=InputCountNumber.link_text)  # Принимаем состояние
async def started(message: types.Message, state: FSMContext):

    data_state = await state.get_data()
    ref_id_1lv = data_state.get("message_id")
    messageID_state = data_state.get("call_message_id1")
    rightCall = data_state.get("rightCall")
    print(data_state)
    #await state.finish()
    current_state = await state.get_state()
    print("state: ",current_state)

    async with state.proxy() as proxy:
        proxy['messagesend'] = message.text 
    if proxy["messagesend"] != "" and proxy["messagesend"] != "/start":
        print("wait link state")
        callbackList = ""
        if ref_id_1lv == "Вконтакте":
            callbackList = "servicevk"
        elif ref_id_1lv == "Instagram":
            callbackList = "serviceinst"
        elif ref_id_1lv == "Youtube":
            callbackList = "serviceyt"
        elif ref_id_1lv == "TikTok":
            callbackList = "servicett"
        elif ref_id_1lv == "Twitter":
            callbackList = "servicetwt"
        elif ref_id_1lv == "Likee":
            callbackList = "servicelk"
        elif ref_id_1lv == "Одноклассники":
            callbackList = "serviceok"
        else:
           callbackList = "servicetg" 

        
        markup_inlinets = types.InlineKeyboardMarkup()
        nazadBtn = types.InlineKeyboardButton(text="▶Вернуться к выбору услуги", callback_data=callbackList)
        glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
        markup_inlinets.add(nazadBtn).add(glavnoe_menu)

        answer = message.text #сохранаяется ссылка
        extractor = urlextract.URLExtract()
        urls = extractor.find_urls(answer)
        
        if urls == []:
            await bot.delete_message(message.chat.id, message.message_id)
                
            messageID = messageID_state
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=messageID, text=f'Некорректная ссылка: {answer} \n \n Пришлите корректную ссылку для накрутки', reply_markup=markup_inlinets)
            #await state.finish()
            await InputCountNumber.link_text.set()
            print("error_link")
        else:    
            #global_dict("", "", answer, "add")
            testdata = request.checkList("packages", ref_id_1lv) 
            for dictionary in testdata:
                if int(dictionary[0]) == int(rightCall):
                    messageID = messageID_state
                    await bot.edit_message_text(chat_id=message.from_user.id, message_id=messageID, text=f'🟢Ваша ссылка: {answer} \n \n🟠Введите количество для накрутки: \n \n⬇️Максимально: {dictionary[4]} \n⬆️Миниимально: {dictionary[3]}\n', reply_markup=markup_inlinets, disable_web_page_preview=True)
                    await state.finish()
                    await InputCountNumber.number_count.set()
                    async with state.proxy() as data:
                        data['answer'] = message.text
                        data['message_id'] = ref_id_1lv
                        data['rightCall'] = rightCall
                        data['call_message_id1'] = messageID_state
        
        await bot.delete_message(message.chat.id, message.message_id)
        #await state.finish()
    else:
        await state.finish()  # Выключаем состояние


#ВТОРАЯ МАШИНА ОЖИДАНИЙ(КОЛИЧЕСТВО)
@dp.message_handler(state=InputCountNumber.number_count) 
async def naviga(message: types.Message, state: FSMContext):
    print("state count agter link")
    data_state = await state.get_data()
    ref_id_1lv = data_state.get("message_id")
    messageID_state = data_state.get("call_message_id1")
    rightCall = data_state.get("rightCall")
    link = data_state.get("answer")
    print(data_state)
    #await state.finish()
    current_state = await state.get_state()
    print("state: ",current_state)
    
    async with state.proxy() as proxy:  # Устанавливаем состояние ожидания
        proxy['messagesendCount'] = message.text
    if proxy["messagesendCount"] != "" and proxy["messagesendCount"] != "/start":


        callbackList = ""
        if ref_id_1lv == "Вконтакте":
            callbackList = "servicevk"
        elif ref_id_1lv == "Instagram":
            callbackList = "serviceinst"
        elif ref_id_1lv == "Youtube":
            callbackList = "serviceyt"
        elif ref_id_1lv == "TikTok":
            callbackList = "servicett"
        elif ref_id_1lv == "Twitter":
            callbackList = "servicetwt"
        elif ref_id_1lv == "Likee":
            callbackList = "servicelk"
        elif ref_id_1lv == "Одноклассники":
            callbackList = "serviceok"
        else:
           callbackList = "servicetg"


        markup_inline = types.InlineKeyboardMarkup()
        oplataGenOrder = types.InlineKeyboardButton(text="✅Подтвердить заказ", callback_data="completeOrders")
        nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору услуги", callback_data=callbackList)
        glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
        markup_inline.add(oplataGenOrder).add(nazad).add(glavnoe_menu)

        markup_inlineBad = types.InlineKeyboardMarkup()
        nazad = types.InlineKeyboardButton(text="▶Вернуться к выбору услуги", callback_data=callbackList)
        glavnoe_menu = types.InlineKeyboardButton(text="▶Меню", callback_data="Start")
        markup_inlineBad.add(nazad).add(glavnoe_menu)

        cashUser = getSettings('config_main.txt')[1]
        cashAdmin = getSettings('config_main.txt')[2]
        answerCount = message.text 
        messageID = messageID_state
        testdata = request.checkList("packages", ref_id_1lv)
        for dictionary in testdata:
            if int(dictionary[0]) == int(rightCall):

                orderCost = float('{:.2f}'.format((((float(dictionary[5])/1000) * float(answerCount)) * (float(int(cashUser) + int(cashAdmin))/100)) + ((float(dictionary[5])/1000) * float(answerCount)))) 
                
                if(int(answerCount) <= int(dictionary[4]) and int(answerCount) >= int(dictionary[3])):
                    await bot.edit_message_text(chat_id=message.from_user.id, message_id=messageID, text=f'✅Ваша ссылка: {link} \n🔥Количество: {answerCount}\n🔥Стоимость: {orderCost}р. \nОплатить и запустить', reply_markup=markup_inline, disable_web_page_preview=True)
                    await state.finish()
                    async with state.proxy() as data:
                        data['answer'] = link
                        data['answerCount'] = answerCount
                        data['orderCost'] = orderCost
                        data['dictionary[0]'] = dictionary[0]
                    #global_dict(answerCount,orderCost,dictionary[0],"add")
                else:
                    await bot.edit_message_text(chat_id=message.from_user.id, message_id=messageID, text=f'❌Количество введено неверно \n \n⬇️Максимально: {dictionary[4]} \n⬆️Миниимально: {dictionary[3]}\n',reply_markup=markup_inlineBad)
                    await InputCountNumber.number_count.set()
                    await state.finish()
                    async with state.proxy() as data:
                        data['answer'] = link
                        data['message_id'] = ref_id_1lv
                        data['rightCall'] = rightCall
                        data['call_message_id1'] = messageID_state
            else:
                await InputCountNumber.number_count.set() #ОЧЕНЬ ОЧЕНЬ ОПАСНО(МОГУТ БЫТЬ ЗАВИСАНИЯ ПРЯМ ГГ)
        await bot.delete_message(message.chat.id, message.message_id)
        #await state.finish()
    else:
        await state.finish()


#ПРОВЕРКА СТАТУСОВ ЗАКАЗА
async def scheduledOrder(wait_for):
  while True:
    await asyncio.sleep(wait_for)
    #ПРОВЕРКА СТАТУСА ЗАКАЗА
    print("ORDER STATUS CHECKING...")
    baseOrders = baseMain.execute(f'SELECT order_number, id_user, money, status FROM USER_ORDER').fetchall()  
    for orderB in baseOrders:
        checkOrders = request.checkingOrderStatus("status", orderB[0])
        if checkOrders[0] == "Completed":
            baseOrders = baseMain.execute(f'UPDATE USER_ORDER SET status = "Выполнен✅" WHERE order_number = "{orderB[0]}"')
            baseMain.commit()
        elif checkOrders[0] == "Inprogress":
            baseOrders = baseMain.execute(f'UPDATE USER_ORDER SET status = "В процессе⏳" WHERE order_number = "{orderB[0]}"')
            baseMain.commit()
        elif checkOrders[0] == "Cancelled" and orderB[3] != "Отменён❌(Баланс возвращен)":
            oldBalace = baseMain.execute(f'SELECT money FROM USERS WHERE user_id = {orderB[1]}').fetchone()[0]
            refBalance = float(oldBalace) + float(orderB[2])

            baseMain.execute(f'UPDATE USERS SET money = {refBalance} WHERE user_id = "{orderB[1]}"')
            baseMain.commit()

            baseOrders = baseMain.execute(f'UPDATE USER_ORDER SET status = "Отменён❌(Баланс возвращен)" WHERE order_number = "{orderB[0]}"')
            baseMain.commit()

#ПРОВЕРКА ОПЛАТ(КОТОРЫЕ БОТ НЕ ЗАМЕТИЛ)
async def checkpayError(wait_for):
  while True:
    await asyncio.sleep(wait_for)
    #ПРОВЕРКА СПИСКА ОПЛАТ
    print("PAY ERROR STATUS CHECKING...")
    basePays = baseMain.execute(f'SELECT user_id, sum_cash, status, secretLabel, date FROM USER_PAY WHERE status = "WAIT" OR status = "success" AND good_pay_check = "False"').fetchall()  
    for payonce in basePays:
        statusCheck = testoplata.check_pay_test(payonce[3])
        print(payonce[3])
        if statusCheck[0] == "success":
            try:
                
                baseMain.execute(f'UPDATE USER_PAY SET status = "success", good_pay_check = "True" WHERE secretLabel = "{payonce[3]}"')
                baseMain.commit()
                oldBalance =  baseMain.execute(f'SELECT money FROM USERS WHERE user_id = "{payonce[0]}"').fetchone()[0]
                balanceToBase = float('{:.2f}'.format(oldBalance + statusCheck[1]))
                baseMain.execute(f'UPDATE USERS SET money="{balanceToBase}" WHERE user_id="{payonce[0]}"')
                baseMain.commit()

                markup_inlineGood = types.InlineKeyboardMarkup()
                glavnoe_menu = types.InlineKeyboardButton(text="❌Закрыть", callback_data="Start")
                markup_inlineGood.add(glavnoe_menu)
                await bot.send_message(chat_id=payonce[0], text=f'✅Ваш баланс успешно пополнен на {statusCheck[1]}р.', reply_markup=markup_inlineGood)
            except Exception as errorP:
                print(errorP)


class checkMoneyTake:
    work = True

    #ПРОВЕРКА СТАТУСОВ ОПЛАТЫ(авточек)
    async def scheduledOplata(wait_for, user_id, message_id):
        while True:
            while checkMoneyTake.work:
                
                print("PAY STATUS CHECKING...")
                #print(get_data)
                await asyncio.sleep(wait_for)
                timeStarOrder = datetime.now().minute
                timeStopOrder = timeStarOrder + 15
                if timeStopOrder >= 60:
                    timeStopOrder = timeStopOrder - 60
                if timeStarOrder != timeStopOrder:
                    basePay = baseMain.execute(f'SELECT user_id, sum_cash, status, secretLabel, date FROM USER_PAY WHERE user_id = {user_id} AND status = "WAIT"').fetchall()
                    for baseStatus in basePay:
                        dateNow = datetime.today().strftime('%Y-%m-%d')
                        dateNowGood = datetime.strptime(dateNow, '%Y-%m-%d')
                        my_dt = datetime.strptime(baseStatus[4], '%Y-%m-%d %H:%M:%S')
                        my_dtNew = my_dt.strftime('%Y-%m-%d')
                        mydtNewGood = datetime.strptime(my_dtNew, '%Y-%m-%d')
                        if baseStatus[2] == "WAIT" and mydtNewGood < dateNowGood:
                            baseMain.execute(f'DELETE FROM USER_PAY WHERE status = "WAIT"')
                            baseMain.commit()
                        requestOplata = testoplata.check_pay(baseStatus[3])
                        try:
                            if requestOplata[0] == "success":
                                basePay = baseMain.execute(f'UPDATE USER_PAY SET status = "success", good_pay_check = "True" WHERE secretLabel = "{baseStatus[3]}"')
                                baseMain.commit()
                                oldBalance =  baseMain.execute(f'SELECT money FROM USERS WHERE user_id = "{user_id}"').fetchone()[0]
                                balanceToBase = float('{:.2f}'.format(oldBalance + requestOplata[1]))
                                baseMain.execute(f'UPDATE USERS SET money="{balanceToBase}" WHERE user_id="{user_id}"')
                                baseMain.commit()

                                markup_inlineGood = types.InlineKeyboardMarkup()
                                glavnoe_menu = types.InlineKeyboardButton(text="❌Закрыть", callback_data="Start")
                                markup_inlineGood.add(glavnoe_menu)

                                await bot.edit_message_text(chat_id=user_id, message_id=message_id, text=f'✅Ваш баланс успешно пополнен на {requestOplata[1]}р.', reply_markup=markup_inlineGood)
                                #await asyncio.sleep(wait_for * 18000) #ЕСЛИ СЛОМАЛОСЬ ОЖИДАНИЕ РЕЗУЛЬТАТА, ТО ВКЛ ЭТО
                                return "good"
                        except Exception:
                            #print("error")
                            continue
                else:
                    return "time"
            else:
                return "stop"
    
#keep_alive()
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(scheduledOrder(600)) # поставим 10 минут, в качестве теста
    loop.create_task(checkpayError(600)) # поставим 10 минут
    executor.start_polling(dp, skip_updates=True)


#2) СДЕЛАТЬ СВОЙ ВВОД ТЕКСТ КОММЕНТА ВК, INST