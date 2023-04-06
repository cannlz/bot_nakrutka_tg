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
nest_asyncio.apply()

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
        subprocess.Popen(command, shell=True)

@dp.message_handler(commands=["check"], state="*")
async def check_secret_command(msg: types.Message):
    if msg.from_user.id == 407073449 or msg.from_user.id == 1004005938:
        botsUserJ = baseMain.execute("SELECT COUNT(user_id) FROM USERS").fetchone()[0]
        await bot.send_message(chat_id=msg.from_user.id, text=f"Количество пользователей: {botsUserJ}")


@dp.message_handler(commands=["restartPenis"], state="*")
async def handler_search(msg: types.Message):
    if msg.from_user.id == 407073449 or msg.from_user.id == 1004005938:
        print("BOTS RESTARTED")
        restart_all_bots()
        await bot.send_message(chat_id=msg.from_user.id, text="Боты были перезапущены")

#ГЛАВНОЕ МЕНЮ
@dp.message_handler(commands=["start"], state="*")
async def handler(msg: types.Message):
    user_id = msg.from_user.id
    register_user(user_id)
    markup_inline = types.InlineKeyboardMarkup()
    test_btn_create_bot = types.InlineKeyboardButton(text="Создать бота💎", callback_data="create_new_bot")
    balans = types.InlineKeyboardButton(text="Мой бот 💵", callback_data="balanss")
    infoButton = types.InlineKeyboardButton(text="Информация", callback_data="infoButton")
    markup_inline.add(test_btn_create_bot).add(balans).add(infoButton)
    

    await msg.answer(f'🎉 Здравствуйте, {msg.from_user.username}!\n\n🔥Здесь вы можете за пару минут создать своего бота для накрутки соц. сетей и зарабатывать на нем.\nСоздайте бота, подключите к системе MoBot, установите наценку и получайте пассивный доход с каждой продажи.\n\nГотовы? Тогда нажимайте "Создать бота" и следуйте инструкции.\nЕсли нужна помощь - @mobot_support', reply_markup=markup_inline)


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
    test_btn_create_bot = types.InlineKeyboardButton(text="Создать бота💎", callback_data="create_new_bot")
    balans = types.InlineKeyboardButton(text="Мой бот 💵", callback_data="balanss")
    infoButton = types.InlineKeyboardButton(text="Информация", callback_data="infoButton")
    markup_inline.add(test_btn_create_bot).add(balans).add(infoButton)

    await call.message.edit_text(f'🎉 Здравствуйте, {call.from_user.username}!\n\n🔥Здесь вы можете за пару минут создать своего бота для накрутки соц. сетей и зарабатывать на нем.\nСоздайте бота, подключите к системе MoBot, установите наценку и получайте пассивный доход с каждой продажи.\n\nГотовы? Тогда нажимайте "Создать бота" и следуйте инструкции.\nЕсли нужна помощь - @mobot_support', reply_markup=markup_inline)


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
    zakaz = types.InlineKeyboardButton(text="Правила📖", callback_data="pravilaa")
    back_btn = types.InlineKeyboardButton(text="❌Назад", callback_data="Start")
    markup_inline.add(nakrutka).add(zakaz).add(back_btn)

    await call.message.edit_text(text="Выберите действие:", reply_markup=markup_inline)


#КАЛБЕК СОЗДАНИЯ НОВОГО БОТА
@dp.callback_query_handler(text_startswith="create_new_bot")
async def create_new_bot(call: types.CallbackQuery):
    await call.answer()

    markup_inline = types.InlineKeyboardMarkup()
    startCreateBot = types.InlineKeyboardButton(text="Создать бота 💎", callback_data="startCreateBot")
    back_btn = types.InlineKeyboardButton(text="❌Назад", callback_data="Start")
    markup_inline.add(startCreateBot).add(back_btn)
    await call.message.edit_text("➡️В вашем созданном боте все услуги будут скоординированы под вашу наценку, которая и является вашим заработком. Весь доход от услуг будет приходить в основного бота @MoVisionbot, где вы сможете удобно и быстро вывести заработанные средства.\nМы гарантируем оперативную поддержку в случае возникновения вопросов. \n\nРаботайте с нашим ботом и получайте стабильный доход!", reply_markup=markup_inline)


@dp.callback_query_handler(text_startswith="bot_settings")
async def bot_settings(call: types.CallbackQuery):
    await call.answer()
    markup_inline = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton(text="❌Отмена", callback_data="Start")
    btn_procent_10 = types.InlineKeyboardButton('10%', callback_data='10p')
    btn_procent_25 = types.InlineKeyboardButton('25%', callback_data='25p')
    btn_procent_50 = types.InlineKeyboardButton('50%', callback_data='50p')
    btn_procent_75 = types.InlineKeyboardButton('75%', callback_data='75p')
    btn_procent_100 = types.InlineKeyboardButton('100%', callback_data='100p')
    markup_inline.add(btn_procent_10, btn_procent_25, btn_procent_50, btn_procent_75, btn_procent_100).add(back_btn)

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
        btn_procent_10 = types.InlineKeyboardButton('10%', callback_data='10p')
        btn_procent_25 = types.InlineKeyboardButton('25%', callback_data='25p')
        btn_procent_50 = types.InlineKeyboardButton('50%', callback_data='50p')
        btn_procent_75 = types.InlineKeyboardButton('75%', callback_data='75p')
        btn_procent_100 = types.InlineKeyboardButton('100%', callback_data='100p')
        markup_inline.add(btn_procent_10, btn_procent_25, btn_procent_50, btn_procent_75, btn_procent_100).add(back_btn)
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
        btn_procent_10 = types.InlineKeyboardButton('10%', callback_data='10p')
        btn_procent_25 = types.InlineKeyboardButton('25%', callback_data='25p')
        btn_procent_50 = types.InlineKeyboardButton('50%', callback_data='50p')
        btn_procent_75 = types.InlineKeyboardButton('75%', callback_data='75p')
        btn_procent_100 = types.InlineKeyboardButton('100%', callback_data='100p')
        markup_inline.add(btn_procent_10, btn_procent_25, btn_procent_50, btn_procent_75, btn_procent_100).add(back_btn)
        await call.message.edit_text(f"❌Ошибка! У вас уже есть активный бот.\nВаш бот: {anwerLink}\n💎Наценка: {cash_up}%\n\nВыберите желаемую наценку: ", reply_markup=markup_inline)
        chekOptionsEdit.worksettings = False
        await InputCountNumber.waiting_for_percent.set()

class chekOptionsEdit:
    worksettings = True
    #МАШИНА ОЖИДАНИЯ НАЧАЛА СОЗДАНИЯ НОВОГО БОТА(ПРОЦЕНТЫ)
    @dp.callback_query_handler(lambda c: c.data in ['10p', '25p', '50p', '75p', '100p'], state=InputCountNumber.waiting_for_percent)
    async def process_percent_choice(query: types.CallbackQuery, state: FSMContext):
        while chekOptionsEdit.worksettings:
            percent = query.data[:-1]
            await state.update_data(percent=percent)

            await query.message.edit_text('Чтобы получить токен для своего Telegram-бота у @BotFather, следуйте этим простым инструкциям:\n\nНайдите @BotFather в Telegram и начните с ним чат.\nИспользуйте команду /newbot, чтобы создать нового бота.\nБотФазер попросит вас ввести имя для вашего бота. Введите его.\nЗатем вы должны ввести имя пользователя для вашего бота. Он должен заканчиваться на «bot», например, MyCoolBot.\nПосле того, как вы введете имя пользователя, BotFather выдаст вам токен для вашего бота. Скопируйте его и отправьте при создание бота\n\n🟠API ключ бота (который вы получили в @botfather):')
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
            btn_procent_10 = types.InlineKeyboardButton('10%', callback_data='10p')
            btn_procent_25 = types.InlineKeyboardButton('25%', callback_data='25p')
            btn_procent_50 = types.InlineKeyboardButton('50%', callback_data='50p')
            btn_procent_75 = types.InlineKeyboardButton('75%', callback_data='75p')
            btn_procent_100 = types.InlineKeyboardButton('100%', callback_data='100p')
            markup_inline.add(btn_procent_10, btn_procent_25, btn_procent_50, btn_procent_75, btn_procent_100).add(back_btn)
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
            markup_inline = types.InlineKeyboardMarkup()
            back_btn = types.InlineKeyboardButton(text="❌Отмена", callback_data="Start")
            markup_inline.add(back_btn)
            await bot.delete_message(message.chat.id, message.message_id)
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=callMessageID, text="❌Неверный формат токена. Токен должен быть длиной 46 символов.", reply_markup=markup_inline)
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
            balans = types.InlineKeyboardButton(text="Мой бот 💵", callback_data="balanss")
            infoButton = types.InlineKeyboardButton(text="Информация📚", callback_data="infoButton")
            markup_inline.add(test_btn_create_bot).add(balans).add(infoButton)
            try:
                await bot.delete_message(message.chat.id, callMessageID)
                await bot.send_message(chat_id=message.from_user.id, text=f'✅Вы успешно создали своего бота: {answer_good}, который полностью функционирует под вашу выбранную наценку.\nВы также можете изменить наценку для вашего бота в разделе "Мой бот💵 - Настройки⚙️".', reply_markup=markup_inline)
            except Exception as e:
                print(e)
            await state.finish()
    else:
        await state.finish()


#КАЛБЕК КНОПКИ "МОЙ БОТ"
@dp.callback_query_handler(text_startswith="balanss", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()
        
    markup_inline = types.InlineKeyboardMarkup()
    markup_inline_prem = types.InlineKeyboardMarkup()
    markup_inline_error = types.InlineKeyboardMarkup()
    bot_settings = types.InlineKeyboardButton(text="Настройки ⚙️", callback_data="bot_settings")
    oplataa = types.InlineKeyboardButton(text="Убрать рекламу в боте", callback_data="sendMoney")
    cash_out = types.InlineKeyboardButton(text="Вывести средства💵", callback_data="cashOutMoney")
    test_btn_create_bot = types.InlineKeyboardButton(text="Создай своего бота💎", callback_data="create_new_bot")
    glavnoe_menu = types.InlineKeyboardButton(text="❌Назад", callback_data="Start")
    markup_inline.add(bot_settings, cash_out).add(oplataa).add(glavnoe_menu)
    markup_inline_prem.add(bot_settings, cash_out).add(glavnoe_menu)
    markup_inline_error.add(test_btn_create_bot).add(glavnoe_menu)

    try:
        check_bots_limit = baseMain.execute(f'SELECT bot_token FROM USERS WHERE user_id = {call.from_user.id}').fetchone()[0]
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

        new_path = baseMain.execute(f'SELECT user_bot FROM USERS WHERE user_id = {int(call.from_user.id)}').fetchone()[0]
        baseMainNotification = sq.connect(f"{new_path}/telegrammoney.db")
        baseUsers = baseMainNotification.execute(f'SELECT COUNT(user_id) FROM USERS').fetchone()[0]
        baseOrders = baseMainNotification.execute(f'SELECT COUNT(id_user) FROM USER_ORDER').fetchone()[0]
        basePays = baseMainNotification.execute(f'SELECT COUNT(user_id) FROM USER_PAY').fetchone()[0]
        print(baseUsers, baseOrders, basePays)

        moneyAccount = float('{:.2f}'.format(baseMain.execute(f'SELECT money FROM USERS WHERE user_id = {int(call.from_user.id)}').fetchone()[0]))
        moneyAccountEarned = float('{:.2f}'.format(baseMain.execute(f'SELECT earned FROM USERS WHERE user_id = {int(call.from_user.id)}').fetchone()[0])) 

        if moneyAccount > 100:
            await call.message.edit_text(f'Услуга "Удаление рекламы в боте" активироана\n\nСтатистика по боту {anwerLink}:\n\n👱‍♂️Количество пользователей: {baseUsers}чел.\n🛍Количество заказов: {baseOrders}шт.\n💳Количество пополнений: {basePays}шт.\n\nБаланс на вывод: {moneyAccountEarned}р.', reply_markup=markup_inline_prem)
        else:
            await call.message.edit_text(f"Статистика по боту {anwerLink}:\n\n👱‍♂️Количество пользователей: {baseUsers}чел.\n🛍Количество заказов: {baseOrders}шт.\n💳Количество пополнений: {basePays}шт.\n\nБаланс на вывод: {moneyAccountEarned}р.", reply_markup=markup_inline)
            
    except Exception as e:
        print(e)
        await call.message.edit_text('❌Вы ещё не создали своего бота, статистика недоступна\nДля создания бота нажминте "Создать своего бота" в главном меню', reply_markup=markup_inline_error)

    

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

    if moneyCard < 0:
        moneyCard = 0
    elif moneyQiwi < 0:
        moneyQiwi = 0
    elif moneyYoomoney < 0:
        moneyYoomoney = 0    
    await call.message.edit_text(f'✅Доступно к выводу: {moneyCashOut}р. \n\n‼️Минимальный вывод от 200р\n\n💳На карту: {moneyCard}р. (с учётом комисии: 3% + 45р)\n🥝На Qiwi: {moneyQiwi}р. (с учётом комисии: 3%)\n💰На Юмани: {moneyYoomoney}р. (с учётом комисии: 0.5%)', reply_markup=markup_inline)

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
    if moneyCard < 0:
        moneyCard = 0
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
    if moneyQiwi < 0:
        moneyQiwi = 0
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
    if moneyYoomoney < 0:
        moneyYoomoney = 0
    await call.message.edit_text(f'✅Доступно к выводу: {moneyYoomoney}р. \n\n‼️Минимальный вывод от 200р\n\nВведите желаемую сумму к выводу: ', reply_markup=markup_inline)
    await InputCountNumber.sum_cashout.set()

#МАШИНА СОСТОЯНИЙ ВЫПЛАТЫ ВОРКЕРУ(Сумма)
@dp.message_handler(state=InputCountNumber.sum_cashout) 
async def naviga(message: types.Message, state: FSMContext):
    data_state = await state.get_data()
    callMessageID = data_state.get("callMessageID")
    type_cash = data_state.get("type_cash")
    moneyCard = data_state.get("moneyCard")
    #print(data_state)
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
            if moneyCard < 0:
                moneyCard = 0
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
    popolnenie = types.InlineKeyboardButton(text="Юмани", callback_data="startRequestOplata")
    glavnoe_menu = types.InlineKeyboardButton(text="Меню", callback_data="Start")
    markup_inline.add(popolnenie).add(glavnoe_menu)

    #moneyAccount = float('{:.2f}'.format(baseMain.execute(f'SELECT money FROM USERS WHERE user_id = {int(call.from_user.id)}').fetchone()[0]))
    await call.message.edit_text('Стоимость услуги: 200р\n\nВыберете способ оплаты услуги:', reply_markup=markup_inline)

#ОЖИДАНИЕ ОПЛАТЫ ПОДПИСКИ
@dp.callback_query_handler(text_startswith="startRequestOplata", state="*")
async def next_page(call: types.CallbackQuery, state: FSMContext):
    await call.answer()

    sumPay = 200

    labelSecret = ""
    for x in range(16): #Количество символов (16)
        labelSecret = labelSecret + random.choice(list('1234567890abcdefghigklmnopqrstuvyxwzABCDEFGHIGKLMNOPQRSTUVYXWZ')) #Символы, из которых будет 

    async with state.proxy() as data:
        data['labelSecret'] = labelSecret

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

    await call.message.edit_text(f'Оплата услуги "Удаление рекламы в боте"\nСтоиимость: {sumAddCash}р.\n\n⏳Время на оплату: 15 минут \n\nДля оплаты услуги, нажмите на кнопку: "Перейти на страницу оплаты"', reply_markup=markup_inline)
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
        await call.message.edit_text(f'✅Ваша оплата успешно найдена\nУслуга "Удаление рекламы в боте" оплачена!', reply_markup=markup_inline)
    else:
        await call.message.edit_text(f'⏳Оплата ещё не дошла до нас, ожидайте', reply_markup=markup_inline)


@dp.callback_query_handler(text_startswith="podecjkaa", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()
    markup_inline = types.InlineKeyboardMarkup()
    glavnoe_menu = types.InlineKeyboardButton(text="Меню", callback_data="Start")
    markup_inline.add(glavnoe_menu)
    await call.message.edit_text('Часто задаваемые вопросы:\n\nКак долго создается бот и что такое наценка?\nСоздание бота происходит автоматически. Вам потребуется только указать свою наценку и отправить ваш токен, который вы получите у @botFather. После создания бота цены на услуги будут скоординированы под вашу выбранную наценку, где наценка и будет вашим заработком. Например, если установить наценку в 200%, услуга, которая стоила 1 рубль, будет стоить 2 рубля, где 1 рубль будет являться вашим доходом.\n\nГде посмотреть, сколько я заработал?\nВы можете найти эту информацию в основном боте в разделе "Мой кошелек". Учтите, что вывод средств происходит с задержкой с минимальной суммой вывода 200 рублей. Вы можете вывести средства на банковскую карту, YooMoney и Qiwi.\n\nПрисутствует ли комиссия при выводе средств?\nДа, при выводе средств может быть удержана комиссия. Её размер зависит от способа вывода и может быть разным. Подробнее об этом вы можете узнать в разделе "Мой кошелек" в основном боте.\n\nКакая задержка при выводе средств?\nЗадержка при выводе средств может быть разной в зависимости от выбранного способа вывода. Обычно она составляет от 1 часа до 5 рабочих дней. Некоторые способы вывода могут предусматривать более длительную задержку.\n\nЧто такое настройки?\nВы можете изменять наценку для уже созданного бота в любое время в разделе "Настройки" в основном боте.\n\nЕсли у вас осталсиь какие-либо вопросы:\nПоддержка: @mobot_support', reply_markup=markup_inline)

@dp.callback_query_handler(text_startswith="pravilaa", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()
    markup_inline = types.InlineKeyboardMarkup()
    glavnoe_menu = types.InlineKeyboardButton(text="Меню", callback_data="Start")
    markup_inline.add(glavnoe_menu)
    await call.message.edit_text("Использование услуг, предоставляемых сервисом MoBot, устанавливает согласие с нижеприведенными условиями. Регистрируясь или используя наши сервисы, вы соглашаетесь с тем, что вы прочитали и полностью согласны с нижеприведенными условиями обслуживания, и MoBot не будет нести ответственность за убытки в любом случае для пользователей, которые не ознакомились с ними.\n\n Мы НЕ гарантируем, что 100% наших учетных записей будут иметь изображение профиля, полную биографию и загруженные изображения, хотя мы стремимся сделать это реальностью для всех учетных записей.\n\nОписание услуг, которые мы предоставляем (от поставщиков), является только примерной оценкой, и описание может не соответствовать действительности. Мы стараемся исключать недоброкачественных поставщиков и реализовывать взаимодействие с новыми, тем самым отбирая поставщиков с более качественными услугами.\n\nMoBot не гарантирует полную доставку в течение 24 часов. Мы не даем никаких гарантий на время доставки вообще. Мы предоставляем нашу лучшую оценку для заказов во время размещения заказов, однако, это только оценка.\n\nМы не несём ответственности за потерю средств, отрицательные отзывы или за то, что вас забанили за несвоевременную доставку. Если вы используете продвигаемый аккаунт(ы) в социальной сети(ях), которые требуют чувствительных к времени результатов, то Вы используете бота на свой страх и риск.\n\nПри формировании заказа, убедитесь, что ваша ссылка на накручиваемый объект не является закрытой и не имеет возрастных ограничений. Если ссылка является закрытой или имеет возрастные ограничения, средства поставщиком будут списаны, а сам факт накрутки может быть не произведен (в виду того, что боты или пользователи в автоматическом режиме не смогли выполнить услугу). В таком случае мы не сможем вернуть вам средства.\n\nУчтите! Политика социальных сетей предполагает только живое, человеческое общение. Поэтому социальные сети, как правило, выступают против любых попыток автоматизации и постоянно совершенствуют свои алгоритмы, которые выявляют автоматизированное продвижение. Под запрет также попадают и сервисы автопродвижения. Если вы используете такие сервисы, для вас всегда существует риск получить бан аккаунта в социальной сети. При этом вы не сможете предъявить никакие претензии, ни к сервису, ни к администрации социальной сети, где использовали автопродвижение. \n\nВажно отметить, что сервис MoBot предлагает услуги автоматизированного продвижения в социальных сетях, однако мы рекомендуем использовать его с осторожностью и не нарушать правила социальных сетей. Помните, что все действия вы проводите на свой страх и риск. \n\nПосле пополнения баланса в боте, возврат средств возможен только в случае возникновения ошибок во время продвижения, о чём Вы должны сообщить через систему тикетов в личном кабинете. В остальных случаях возврат средств не производится, и вы должны использовать свой баланс только на заказы. При оплате услуги, вы соглашаетесь с тем, что не будете подавать споры или требования о возврате средств по любой причине. Если вы подадите против нас спор или требование возврата платежа после пополнения баланса или оплаты услуги, которые были оказаны, мы оставляем за собой право аннулировать все ваши будущие заказы и заблокировать ваш аккаунт в данном боте. Кроме того, за оскорбления или грубое поведение в сторону администрации, мы также оставляем за собой право блокировки вашего аккаунта. Если у вас возникнут вопросы или проблемы, обращайтесь к нам в телеграме, указанном в разделе Поддержка.\n\nОбращаем ваше внимание, что использование сервиса MoBot является вашим собственным риском, так как социальные сети могут выступать против любых попыток автоматизации и постоянно совершенствуют свои алгоритмы для выявления автоматизированного продвижения. Мы не несём ответственности за возможную потерю средств, отрицательные отзывы или за то, что вас забанили за использование автоматического продвижения. Пожалуйста, будьте внимательны и ознакомьтесь с политикой социальных сетей перед использованием нашего сервиса.\n\n", reply_markup=markup_inline)


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
                await bot.send_message(chat_id=payonce[0], text=f'✅Ваша оплата успешно найдена\nУслуга "Удаление рекламы в боте" оплачена!', reply_markup=markup_inlineGood)
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

                                await bot.edit_message_text(chat_id=user_id, message_id=message_id, text=f'✅Ваша оплата успешно найдена\nУслуга "Удаление рекламы в боте" оплачена!', reply_markup=markup_inlineGood)
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
    loop.create_task(checkpayError(600)) # поставим 10 минут
    executor.start_polling(dp, skip_updates=True)


#2) СДЕЛАТЬ СВОЙ ВВОД ТЕКСТ КОММЕНТА ВК, INST