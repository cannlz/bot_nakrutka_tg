#ИМПОРТЫ
from aiogram import types, executor, Dispatcher, Bot
import datetime
import sqlite3 as sq
from pathlib import Path
import re
import request
import asyncio
import testoplata
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import urlextract
import random
from datetime import datetime
import nest_asyncio
import configparser
import os
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
bot = Bot(token = getSettings('config.txt')[0], parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())


#МАНИШЫ СОСТОЯНИЙ
class InputCountNumber(StatesGroup):
    link_text = State()
    number_count = State()
    sum_cost = State()
    sum_cashout = State()
    data_cashout = State()

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
                    status STRING NOT NULL,
                    check_cash_out INTEGER DEFAULT 0);''')                           
    baseMain.commit()
    baseMain.execute('''CREATE TABLE IF NOT EXISTS USERS 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        money DOUBLE NOT NULL DEFAULT 0,
                        earned DOUBLE DEFAULT 0);''')
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
create_tables()

def register_user(user_id):
    user_check_data = baseMain.execute("SELECT user_id FROM USERS WHERE user_id = ?",(str(user_id), )).fetchone()
    if str(user_id) not in str(user_check_data):
        money = 0
        baseMain.execute(f'INSERT INTO USERS (user_id, money) VALUES ("{user_id}", "{money}");')
        baseMain.commit()
        

#ГЛАВНОЕ МЕНЮ
@dp.message_handler(commands=["start"], state="*")
async def handler(msg: types.Message):
    user_id = msg.from_user.id
    register_user(user_id)

    markup_inline = types.InlineKeyboardMarkup()
    markup_inline_prem = types.InlineKeyboardMarkup()
    nakrutka = types.InlineKeyboardButton(text="Накрутка 💎", callback_data="nakrutkaaMain")
    balans = types.InlineKeyboardButton(text="Баланс 💵", callback_data="balanss")
    podecjka = types.InlineKeyboardButton(text="Поддержка 📚", callback_data="podecjkaa")
    pravila = types.InlineKeyboardButton(text="Правила пользования ботом 🤷‍", callback_data="pravilaa")
    kabinet = types.InlineKeyboardButton(text="Заработай на своём боте💰", url="https://t.me/MoVisionbot")
    markup_inline.add(nakrutka, balans).add(podecjka, pravila).add(kabinet)
    markup_inline_prem.add(nakrutka, balans).add(podecjka, pravila)

    dir_db = os.path.abspath(os.curdir)
    new_path = os.path.split(dir_db)[0]
    baseMainNotification = sq.connect(f"{new_path}/telegrammoney.db")
    basePays = baseMainNotification.execute(f'SELECT money FROM USERS WHERE user_id = {msg.from_user.id}').fetchone()[0]
    if basePays > 150:
        await msg.answer('🎉В настоящее время аккаунт с большим количеством лайков и подписчиков ценится намного выше и выглядит намного привлекательнее.\n\nВыберите действие:', reply_markup=markup_inline_prem)
    else:
        await msg.answer('🎉В настоящее время аккаунт с большим количеством лайков и подписчиков ценится намного выше и выглядит намного привлекательнее.\n\nВыберите действие:', reply_markup=markup_inline)


#КАЛБЕК ГЛАВНОГО МЕНЮ
@dp.callback_query_handler(text_startswith="Start", state="*")
async def start_callback(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    current_state = await state.get_state()
    if current_state:  
        await state.finish()

    checkMoneyTake.work = False

    markup_inline = types.InlineKeyboardMarkup()
    markup_inline_prem = types.InlineKeyboardMarkup()
    nakrutka = types.InlineKeyboardButton(text="Накрутка 💎", callback_data="nakrutkaaMain")
    balans = types.InlineKeyboardButton(text="Баланс 💵", callback_data="balanss")
    podecjka = types.InlineKeyboardButton(text="Поддержка 📚", callback_data="podecjkaa")
    pravila = types.InlineKeyboardButton(text="Правила пользования ботом 🤷‍", callback_data="pravilaa")
    kabinet = types.InlineKeyboardButton(text="Заработай на своём боте💰", url="https://t.me/MoVisionbot")
    markup_inline.add(nakrutka, balans).add(podecjka, pravila).add(kabinet)
    markup_inline_prem.add(nakrutka, balans).add(podecjka, pravila)

    dir_db = os.path.abspath(os.curdir)
    new_path = os.path.split(dir_db)[0]
    baseMainNotification = sq.connect(f"{new_path}/telegrammoney.db")
    basePays = baseMainNotification.execute(f'SELECT money FROM USERS WHERE user_id = {call.from_user.id}').fetchone()[0]
    if basePays > 150:
        await call.message.edit_text('🎉В настоящее время аккаунт с большим количеством лайков и подписчиков ценится намного выше и выглядит намного привлекательнее.\n\nВыберите действие:', reply_markup=markup_inline_prem)
    else:
        await call.message.edit_text('🎉В настоящее время аккаунт с большим количеством лайков и подписчиков ценится намного выше и выглядит намного привлекательнее.\n\nВыберите действие:', reply_markup=markup_inline)

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
            

#ПРОВЕРКА БАЛАНСА
@dp.callback_query_handler(text_startswith="balanss", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()

    markup_inline = types.InlineKeyboardMarkup()
    oplataa = types.InlineKeyboardButton(text="Пополнить баланс", callback_data="sendMoney")
    glavnoe_menu = types.InlineKeyboardButton(text="Назад", callback_data="Start")
    markup_inline.add(oplataa).add(glavnoe_menu)

    moneyAccount = float('{:.2f}'.format(baseMain.execute(f'SELECT money FROM USERS WHERE user_id = {int(call.from_user.id)}').fetchone()[0]))
    moneyAccountEarned = float('{:.2f}'.format(baseMain.execute(f'SELECT earned FROM USERS WHERE user_id = {int(call.from_user.id)}').fetchone()[0]))
    await call.message.edit_text(f"Баланс для заказа услуг: {moneyAccount}р.", reply_markup=markup_inline)

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

        if answerCount.isdigit():
            if int(answerCount) >= 2:
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=messageID, text=f'🟢Сумма пополнения: {answerCount}р. \n \n🟠Минимальная сумма пополнения 2р.', reply_markup=markup_inline)
                await state.finish()
                async with state.proxy() as data:
                    data['answer_summPay'] = answerCount  
            else:
                await bot.delete_message(message.chat.id, message.message_id)
                await bot.edit_message_text(chat_id=message.from_user.id, message_id=messageID, text=f'🔴Сумма пополнения: {answerCount}р.\n \n‼️Введенная сумма меньше суммы пополнения \n \n🟠Минимальная сумма пополнения 2р.', reply_markup=markup_inlineerr)
                await state.finish()
                async with state.proxy() as data:
                    data['message_id_user'] = messageID
                await InputCountNumber.sum_cost.set()
        else:
            await bot.delete_message(message.chat.id, message.message_id)
            await bot.edit_message_text(chat_id=message.from_user.id, message_id=messageID, text=f'🔴Сумма пополнения: {answerCount}р.\n \n‼️Введите число \n \n🟠Минимальная сумма пополнения 2р.', reply_markup=markup_inlineerr)
            await state.finish()
            async with state.proxy() as data:
                data['message_id_user'] = messageID
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
        await call.message.edit_text(f'❌У вас недостаточно средств для совершения операции \n\nВаш баланс: "{userMoney}р."\n\nСтоимость заказа: "{orderCost}р."', reply_markup=markup_inlineNoBalance) # делаем вывод инфы



@dp.callback_query_handler(text_startswith="podecjkaa", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()
    markup_inline = types.InlineKeyboardMarkup()
    glavnoe_menu = types.InlineKeyboardButton(text="Меню", callback_data="Start")
    markup_inline.add(glavnoe_menu)
    await call.message.edit_text('1. Как работает бот для накрутки подписчиков?\nОтвет: Наш бот работает на основе сбора и добавления ботов-подписчиков на ваш аккаунт. Эти боты являются настоящими ботами социальных сетей, которые добавятся на ваш аккаунт и будут увеличивать количество ваших подписчиков.\n\n2. Насколько быстро я могу увеличить количество подписчиков на своем аккаунте с помощью бота?\nОтвет: Скорость увеличения количества подписчиков зависит от вашей целевой аудитории и региона. Мы можем предоставить Вам накрутку подписчиков с разной скоростью, начиная от нескольких тысяч в месяц до нескольких сотен тысяч.\n\n3. Безопасна ли накрутка подписчиков с помощью бота?\nОтвет: Мы гарантируем безопасность и соответствие правилам социальных сетей при использовании нашего бота для накрутки подписчиков. Мы используем безопасные и надежные методы накрутки, чтобы убедиться, что ваш аккаунт остается в безопасности.\n\n4. Будут ли эти боты искажать мою статистику?\nОтвет: Нет, они не будут искажать статистику вашего аккаунта, так как они не являются настоящими людьми. Это подписчики, которые добавятся на ваш аккаунт, чтобы увеличить вашу видимость и популярность в социальных сетях.\n\nЕсли у вас осталсиь какие-либо вопросы:\nПоддержка: @mobot_support', reply_markup=markup_inline)

@dp.callback_query_handler(text_startswith="pravilaa", state="*")
async def next_page(call: types.CallbackQuery):
    await call.answer()
    markup_inline = types.InlineKeyboardMarkup()
    glavnoe_menu = types.InlineKeyboardButton(text="Меню", callback_data="Start")
    markup_inline.add(glavnoe_menu)
    await call.message.edit_text("Использование услуг, предоставляемых сервисом MoBot, устанавливает согласие с нижеприведенными условиями. Регистрируясь или используя наши сервисы, вы соглашаетесь с тем, что вы прочитали и полностью согласны с нижеприведенными условиями обслуживания, и MoBot не будет нести ответственность за убытки в любом случае для пользователей, которые не ознакомились с ними.\n\n Мы НЕ гарантируем, что 100% наших учетных записей будут иметь изображение профиля, полную биографию и загруженные изображения, хотя мы стремимся сделать это реальностью для всех учетных записей.\n\nОписание услуг, которые мы предоставляем (от поставщиков), является только примерной оценкой, и описание может не соответствовать действительности. Мы стараемся исключать недоброкачественных поставщиков и реализовывать взаимодействие с новыми, тем самым отбирая поставщиков с более качественными услугами.\n\nMoBot не гарантирует полную доставку в течение 24 часов. Мы не даем никаких гарантий на время доставки вообще. Мы предоставляем нашу лучшую оценку для заказов во время размещения заказов, однако, это только оценка.\n\nМы не несём ответственности за потерю средств, отрицательные отзывы или за то, что вас забанили за несвоевременную доставку. Если вы используете продвигаемый аккаунт(ы) в социальной сети(ях), которые требуют чувствительных к времени результатов, то Вы используете бота на свой страх и риск.\n\nПри формировании заказа, убедитесь, что ваша ссылка на накручиваемый объект не является закрытой и не имеет возрастных ограничений. Если ссылка является закрытой или имеет возрастные ограничения, средства поставщиком будут списаны, а сам факт накрутки может быть не произведен (в виду того, что боты или пользователи в автоматическом режиме не смогли выполнить услугу). В таком случае мы не сможем вернуть вам средства.\n\nУчтите! Политика социальных сетей предполагает только живое, человеческое общение. Поэтому социальные сети, как правило, выступают против любых попыток автоматизации и постоянно совершенствуют свои алгоритмы, которые выявляют автоматизированное продвижение. Под запрет также попадают и сервисы автопродвижения. Если вы используете такие сервисы, для вас всегда существует риск получить бан аккаунта в социальной сети. При этом вы не сможете предъявить никакие претензии, ни к сервису, ни к администрации социальной сети, где использовали автопродвижение. \n\nВажно отметить, что сервис MoBot предлагает услуги автоматизированного продвижения в социальных сетях, однако мы рекомендуем использовать его с осторожностью и не нарушать правила социальных сетей. Помните, что все действия вы проводите на свой страх и риск. \n\nПосле пополнения баланса в боте, возврат средств возможен только в случае возникновения ошибок во время продвижения, о чём Вы должны сообщить через систему тикетов в личном кабинете. В остальных случаях возврат средств не производится, и вы должны использовать свой баланс только на заказы. При оплате услуги, вы соглашаетесь с тем, что не будете подавать споры или требования о возврате средств по любой причине. Если вы подадите против нас спор или требование возврата платежа после пополнения баланса или оплаты услуги, которые были оказаны, мы оставляем за собой право аннулировать все ваши будущие заказы и заблокировать ваш аккаунт в данном боте. Кроме того, за оскорбления или грубое поведение в сторону администрации, мы также оставляем за собой право блокировки вашего аккаунта. Если у вас возникнут вопросы или проблемы, обращайтесь к нам в телеграме, указанном в разделе Поддержка.\n\nОбращаем ваше внимание, что использование сервиса MoBot является вашим собственным риском, так как социальные сети могут выступать против любых попыток автоматизации и постоянно совершенствуют свои алгоритмы для выявления автоматизированного продвижения. Мы не несём ответственности за возможную потерю средств, отрицательные отзывы или за то, что вас забанили за использование автоматического продвижения. Пожалуйста, будьте внимательны и ознакомьтесь с политикой социальных сетей перед использованием нашего сервиса.\n\n", reply_markup=markup_inline)

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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    nazad = types.InlineKeyboardButton(text="▶️Вернуться к выбору соц.сети", callback_data="serviceyt")
    markup.row_width = 1  # кол-во кнопок в строке
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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
    cashUser = getSettings('config.txt')[1]
    cashAdmin = getSettings('config.txt')[2]
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

        cashUser = getSettings('config.txt')[1]
        cashAdmin = getSettings('config.txt')[2]
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
    try:
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
    except Exception as e:
        print("ОШИБКА ПРОВЕРКИ СТАТУСА ЗАКАЗОВ: ", e)

    baseMoney = baseMain.execute('SELECT money, order_number, quantity FROM USER_ORDER WHERE status = "Выполнен✅" AND check_cash_out = "0"').fetchall()
    moneyUser = 0
    for moneybase in baseMoney:
        origPrice = request.checkingOrderStatus("status", moneybase[1])
        try:
            moneyUser = float(moneyUser) + float("{:.6f}".format(( (float(moneybase[0]) - (((float(getSettings('config.txt')[2]))/100) * float(origPrice[1]) + float(origPrice[1]))) )))
            dir_db = os.path.abspath(os.curdir)
            new_path = os.path.split(dir_db)[0]
            baseMainNotification = sq.connect(f"{new_path}/telegrammoney.db")
            baseMainNotification.execute(f'UPDATE USERS SET earned="{moneyUser}" WHERE user_id="{orderB[1]}"')
            baseMainNotification.commit()
            print("Прибыль пользователя: ", moneyUser)
        except Exception as e:
            print(e)
    baseMoney = baseMain.execute('UPDATE USER_ORDER SET check_cash_out = "1" WHERE status = "Выполнен✅"').fetchall()
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