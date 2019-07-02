# -*- coding: utf-8 -*-
import telebot
from telebot import types
import config               # файл с константами
import time
import sql
import voice
import requests
import urllib3
import copy
from threading import Thread

bot = telebot.TeleBot(config.bot_token)

@bot.message_handler(commands=["start"])
def autontify(message):
    """Авторизация или регистрация пользователя, запрос номера телефона"""
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="🔑 Авторизация / 👤 Регистрация", request_contact=True)
    keyboard.add(button_phone)
    msg = bot.send_message(message.chat.id, text="Вход", reply_markup=keyboard)
    try:
        bot.register_next_step_handler(msg, check_phone)
    except (ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError,
            urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
        print('!!!')

def check_phone(msg):
    """Проверка номера телефона"""
    bot.send_message(msg.chat.id, text=msg.contact.phone_number)
    telnum = sql.check_phone(msg.contact.phone_number[-11:])
    if  telnum != True:
        sql.add_user(msg.contact.phone_number[-11:], msg.from_user.id)
    menu(msg)

def menu(message):
    """Главное меню"""
    keyboard_menu = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    keyboard_menu.add(*[types.KeyboardButton(name) for name in ["🚀 Устройства", "⚙ Настройки",
                                                                "🗣 Голосовые команды","🚪 Выход"]])
    try:
        bot.send_message(message.from_user.id, text="Добро пожаловать 😊", reply_markup=keyboard_menu)

        t = Thread(target=security, args=(message,)) # Создание паралленльного потока
        t.start()

    except (ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError):
        print('!!!')


def security(m):                ################################################
    """Уведомления безопасности"""
    new_topics=[]
    old_topics=[]
    old_sec_data=[]
    while True:
        sec_data = sql.device_data_for_user('SENSOR',
                                            m.from_user.id)  # topic, topic_alias, measurement, value, climat_mode, alarm_mode
        for topic in sec_data:
            if topic[5] == 1:
                new_topics.append(topic[0])

        for topic in old_sec_data:
            if topic[5] == 1:
                old_topics.append(topic[0])
        # print(old_sec_data)

        # начальное состояние
        for topic in new_topics:
            if topic not in old_topics:
                for i in sec_data:
                    if i[0] == topic:
                        if i[3] == 'Opened': txt = 'Открыто'
                        elif i[3] == 'Closed': txt = 'Закрыто'
                        elif i[3] == 'Motion detected': txt = 'Есть движение'
                        elif i[3] == 'No motion': txt = 'Нет движения'
                        else: txt = i[3]
                        bot.send_message(m.from_user.id,
                                         text='%s %s %s %s'%(i[0],i[1],i[2],txt))

        # есть изменения в value
        for topic in new_topics:
            if topic in old_topics:
                for i in sec_data:
                    for j in old_sec_data:
                        if i[0] == topic and i[0] == j[0] and i[3] != j[3]:
                            if i[3] == 'Opened':
                                txt = 'Открыто'
                            elif i[3] == 'Closed':
                                txt = 'Закрыто'
                            elif i[3] == 'Motion detected':
                                txt = 'Есть движение'
                            elif i[3] == 'No motion':
                                txt = 'Нет движения'
                            else: txt = i[3]
                            bot.send_message(m.from_user.id,
                                             text='%s %s %s %s' % (i[0], i[1], i[2], txt))

        old_sec_data = copy.deepcopy(sec_data)
        sec_data.clear()
        new_topics.clear()
        old_topics.clear()


@bot.message_handler(content_types=["text"])
def control(message):
    """Устройства->Меню управления устройствами"""
    # print('выключатели', message.from_user.id)
    if message.text == "🚀 Устройства":
        btn_switches = types.InlineKeyboardButton("Выключатели", callback_data='switches')
        btn_sensors = types.InlineKeyboardButton("Датчики", callback_data='sensors')
        btn_modes = types.InlineKeyboardButton("Режимы и безопасность", callback_data='modes')
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(btn_switches, btn_sensors, btn_modes)
        try:
            bot.send_message(message.from_user.id, "Меню управления устройствами:", reply_markup=keyboard)
        except (ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
            print('!!!')

    elif message.text == "⚙ Настройки":
        btn_modulesInfo = types.InlineKeyboardButton("Инфо о всех доступных Wi-Fi модулях", callback_data='m_info')
        btn_modulesAddDel = types.InlineKeyboardButton("Добавление/Удаление Wi-Fi модулей", callback_data='m_add')
        btn_devNames = types.InlineKeyboardButton("Имена моих устройств", callback_data='d_names')
        btn_voiceCom = types.InlineKeyboardButton("Голосовые команды моих устройств", callback_data='v_com')
        btn_modesUsers = types.InlineKeyboardButton("Управление пользователями", callback_data='m_users')
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(btn_modulesInfo, btn_modulesAddDel, btn_devNames, btn_voiceCom,  btn_modesUsers)
        try:
            bot.send_message(message.from_user.id, "Выберите категорию:", reply_markup=keyboard)
        except (ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
            print('!!!')

    elif message.text == "🗣 Голосовые команды":
        topics_names = sql.topics_names(message.from_user.id)
        # print(topics_names)
        voice_com = sql.voice_com()
        # print(voice_com)
        rez = []
        for i in voice_com:
            for j in topics_names:
                if i[1] == j[0]:
                    typecom=''
                    if i[3] == 'DATA': typecom = 'Получить данные'
                    elif i[3] == 'ON': typecom = 'Включить'
                    elif i[3] == 'OFF': typecom = 'Выключить'
                    rez_consist = [i[1], j[1], i[2], typecom]
                    rez.append(rez_consist)
        bot.send_message(message.from_user.id, 'Список голосовых команд для доступных устройств, скажи мне текст команды и я выполню:')
        for i in rez:
            bot.send_message(message.from_user.id, '🔺Топик: '+i[0] +'\n🔹Имя устройства:\n'+'<b>'+i[1]+'</b>\n🔸Тип команды: '+i[3]+'\n🗣Текст команды:\n'+'<i>'+i[2]+'</i>', parse_mode='HTML')

    elif message.text == "🚪 Выход":
        autontify(message)


############################################################################################## --- Устройства ---
# Получаем значения об устройствах SWITCH из БД
@bot.callback_query_handler(func=lambda call: call.data == 'switches')
def switches(call):
    # print('call.from_user.id',call.from_user.id)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btns=sql.device_data_for_user('SWITCH', call.from_user.id)  # topic, topic_alias, measurement, value, alarm_mode
    # print(btns)
    for btn in btns:
        if btn[3] == '1': emoji = '💡'
        else: emoji = '✨'
        b=types.InlineKeyboardButton(emoji + btn[1], callback_data=btn[0]+','+btn[3]+',sw') # 0-топик, 1-алиас, 3-валуе
        keyboard.add(b)
    for btn in btns:
        if btn[3] != '0':
            keyboard.add(types.InlineKeyboardButton('🔘 Выключить всё', callback_data='alloff,sw'))
            break
    try:
        bot.send_message(call.from_user.id, "💡 - Устройство включено \n✨ - Устройство выключено", reply_markup=keyboard)
    except (ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        print('!!!')


@bot.callback_query_handler(func=lambda call: call.data[-2:] == 'sw')
def switches2(call):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    call.data = call.data.split(',')
    # print('call.data in', call.data)
    btns = sql.device_data_for_user('SWITCH', call.from_user.id)
    # print('btns in:', btns)

    if call.data[0] != 'alloff':
        for btn in btns:
            if btn[0] == call.data[0]:
                bot_answer = btn[1]
                if call.data[1] =='0':
                    btn[3] = '1'
                    bot_answer +=' ВКЛЮЧЕНО'
                else:
                    btn[3] = '0'
                    bot_answer += ' ВЫКЛЮЧЕНО'

                sql.topic_value(btn[0], btn[3])
                bot.answer_callback_query(call.id, text='⚠ ' + bot_answer)  # всплывающее уведомление
                # bot.send_message(call.from_user.id, text='⚠ ' + bot_answer)

            if btn[3] == '1': emoji = '💡'
            else: emoji = '✨'

            b = types.InlineKeyboardButton(emoji + btn[1], callback_data=btn[0] + ',' + btn[3] + ',sw')  # 0-топик, 1-алиас, 3-валуе
            keyboard.add(b)

            print('btns out:', btns)

    else: # кнопка Выключить всё
        bot.answer_callback_query(call.id, text='⚠ ВЫКЛЮЧЕНИЕ')  # всплывающее уведомление
        for btn in btns:
            if btn[3] != '0':
                btn[3] = '0'
                sql.topic_value(btn[0], btn[3])
            b = types.InlineKeyboardButton('✨' + btn[1],
                                           callback_data=btn[0] + ',' + btn[3] + ',sw')  # 0-топик, 1-алиас, 3-валуе
            keyboard.add(b)

    for btn in btns:
        if btn[3] != '0':
            keyboard.add(types.InlineKeyboardButton('🔘 Выключить всё', callback_data='alloff,sw'))
            break

    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,  text="💡 - Устройство включено \n✨ - Устройство выключено", reply_markup=keyboard)
    except (ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        print('!!! telebot.apihelper.ApiException or !!! ConnectionResetError or !!! requests.exceptions.ConnectionError')


# Получаем значения об устройствах SENSOR из БД
@bot.callback_query_handler(func=lambda call: call.data == 'sensors')
def sensors(call):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btns = sql.device_data_for_user('SENSOR', call.from_user.id)
    print('btns in:', btns)
    for btn in btns:
        b = types.InlineKeyboardButton('📊 '+btn[1], callback_data=btn[0]+','+btn[3]+',sn')  # 0-топик, 1-алиас, 3-value !!!calldata - 42 символа max
        keyboard.add(b)
    keyboard.add(types.InlineKeyboardButton('📊 данные со всех датчиков', callback_data='alldata,sn'))
    try:
        bot.send_message(chat_id=call.from_user.id, text="📊 - Получить данные с датчиков:", reply_markup=keyboard)
    except (ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        print('!!!')


@bot.callback_query_handler(func=lambda call: call.data[-2:] == 'sn')
def sensors2(call):
    call.data = call.data.split(',')
    print('call.data in', call.data)
    btns = sql.device_data_for_user('SENSOR', call.from_user.id) # topic, topic_alias, measurement, value, alarm_mode

    for btn in btns:
        if btn[0] == call.data[0]:
            if btn[3] == 'Opened': btn[3]='Открыто'
            if btn[3] == 'Closed': btn[3]='Закрыто'
            if btn[3] == 'Motion detected': btn[3]='Есть движние'
            if btn[3] == 'No motion': btn[3] = 'Нет движния'
            bot.answer_callback_query(call.id, text='⚠ '+btn[1]+' '+btn[2]+': '+btn[3])  # всплывающее уведомление
            bot.send_message(call.from_user.id, text='⚠ '+btn[1]+' '+btn[2]+': '+btn[3])

    if call.data[0] == 'alldata':
        all=''
        try:
            for btn in btns:
                if btn[3] == 'Opened': btn[3]='Открыто'
                if btn[3] == 'Closed': btn[3]='Закрыто'
                if btn[3] == 'Motion detected': btn[3]='Есть движние'
                if btn[3] == 'No motion': btn[3] = 'Нет движния'
                all += '▫'+btn[1] + ' ' + btn[2] + ' ' + btn[3] + '\n'
            bot.answer_callback_query(call.id, text='⚠ Данные получены')
            bot.send_message(call.message.chat.id, all) # сообщение с данными от всех датчиков
        except:
            bot.send_message(call.message.chat.id, "Нет данных")


# Режимы
@bot.callback_query_handler(func=lambda call: call.data == 'modes')
def modes(call):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn_climat = types.InlineKeyboardButton('🌡 Установить температуру', callback_data='climat')
    btn_security = types.InlineKeyboardButton('🚨 Уведомления безопасности', callback_data='security')
    keyboard.add(btn_climat, btn_security)
    try:
        bot.send_message(chat_id=call.from_user.id, text="Режимы и безопасность. Установка режимов:", reply_markup=keyboard)
    except (ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        print('!!!')

# Установить температуру в помещении
@bot.callback_query_handler(func=lambda call: call.data == 'climat')
def climat(call):
    climat_dev = sql.climat_devices(call.from_user.id) # [] topic, topic_alias, climat_mode
    heat = '-'
    cool = '-'
    metering = '-'
    for i in climat_dev:
        if i[2] == 'HEAT':
            heat = i[0] + ', ' + i[1]
        elif i[2] == 'COOL':
            cool = i[0] + ', ' + i[1]
        elif i[2] == 'METERING':
            metering = i[0] + ', ' + i[1]

    text = 'Устройство обогрева:\n' + heat + '\nУстройство охлаждения:\n' + cool + '\nСенсор температуры:\n' + metering
    keyboard2 = types.InlineKeyboardMarkup(row_width=1)
    b_heat = types.InlineKeyboardButton('Устройство обогрева', callback_data='heat')
    b_cool = types.InlineKeyboardButton('Устройство охлаждения', callback_data='cool')
    b_tem = types.InlineKeyboardButton('Сенсор температуры', callback_data='temper')
    keyboard2.add(b_heat, b_cool, b_tem)
    bot.send_message(chat_id=call.from_user.id, text=text + '\nНазначить устройства:', reply_markup=keyboard2)

    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard.add(*[types.InlineKeyboardButton(str(15+i)+'°C', callback_data=str(15+i)+',c') for i in range(20)])
    bot.send_message(chat_id=call.from_user.id, text='🌡 Установить температуру в помещении: ', reply_markup=keyboard)


# Выбор устройства обогрева
@bot.callback_query_handler(func=lambda call: call.data == 'heat')
def heater(call):
    switches = sql.my_switches(call.from_user.id) # topic, topic_alias, climat_mode
    keyboard = types.InlineKeyboardMarkup()
    print(switches)
    for sw in switches:
        if sw[2] == 'HEAT':
            simbo = '♨'
            b = types.InlineKeyboardButton(simbo+' '+sw[0]+' '+sw[1], callback_data=sw[0]+',_heat')
        else:
            b = types.InlineKeyboardButton(sw[0]+' '+sw[1], callback_data=sw[0]+',s_heat')
        keyboard.add(b)
    bot.send_message(chat_id=call.from_user.id, text='Выбор устройства обогрева:\n♨ - выбранное устройство', reply_markup=keyboard)

# Установка устройства обогрева
@bot.callback_query_handler(func=lambda call: call.data[-6:] == 's_heat')
def set_heat(call):
    call.data = call.data.split(',')
    print(call.data)
    switches = sql.my_switches(call.from_user.id)
    for sw in switches:
        if sw[2] == 'HEAT':
            sql.set_climat_device(sw[0], 'NONE')
    sql.set_climat_device(call.data[0], 'HEAT')

    climat_dev = sql.climat_devices(call.from_user.id)  # [] topic, topic_alias, climat_mode
    heat = '-'
    cool = '-'
    metering = '-'
    for i in climat_dev:
        if i[2] == 'HEAT':
            heat = i[0] + ', ' + i[1]
        elif i[2] == 'COOL':
            cool = i[0] + ', ' + i[1]
        elif i[2] == 'METERING':
            metering = i[0] + ', ' + i[1]

    text = 'Устройство обогрева:\n' + heat + '\nУстройство охлаждения:\n' + cool + '\nСенсор температуры:\n' + metering
    keyboard2 = types.InlineKeyboardMarkup(row_width=1)
    b_heat = types.InlineKeyboardButton('Устройство обогрева', callback_data='heat')
    b_cool = types.InlineKeyboardButton('Устройство охлаждения', callback_data='cool')
    b_tem = types.InlineKeyboardButton('Сенсор температуры', callback_data='temper')
    keyboard2.add(b_heat, b_cool, b_tem)
    bot.send_message(chat_id=call.from_user.id, text=text + '\nНазначить устройства:', reply_markup=keyboard2)

    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard.add(*[types.InlineKeyboardButton(str(15 + i) + '°C', callback_data=str(15 + i) + ',c') for i in range(20)])
    bot.send_message(chat_id=call.from_user.id, text='🌡 Установить температуру в помещении: ', reply_markup=keyboard)

# Убирание устройства обогрева (если выбрать уже выбранное)
@bot.callback_query_handler(func=lambda call: call.data[-5:] == '_heat')
def set_heat2(call):
    call.data = call.data.split(',')
    sql.set_climat_device(call.data[0], 'NONE')

    climat_dev = sql.climat_devices(call.from_user.id)  # [] topic, topic_alias, climat_mode
    heat = '-'
    cool = '-'
    metering = '-'
    for i in climat_dev:
        if i[2] == 'HEAT':
            heat = i[0] + ', ' + i[1]
        elif i[2] == 'COOL':
            cool = i[0] + ', ' + i[1]
        elif i[2] == 'METERING':
            metering = i[0] + ', ' + i[1]

    text = 'Устройство обогрева:\n' + heat + '\nУстройство охлаждения:\n' + cool + '\nСенсор температуры:\n' + metering
    keyboard2 = types.InlineKeyboardMarkup(row_width=1)
    b_heat = types.InlineKeyboardButton('Устройство обогрева', callback_data='heat')
    b_cool = types.InlineKeyboardButton('Устройство охлаждения', callback_data='cool')
    b_tem = types.InlineKeyboardButton('Сенсор температуры', callback_data='temper')
    keyboard2.add(b_heat, b_cool, b_tem)
    bot.send_message(chat_id=call.from_user.id, text=text + '\nНазначить устройства:', reply_markup=keyboard2)

    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard.add(*[types.InlineKeyboardButton(str(15 + i) + '°C', callback_data=str(15 + i) + ',c') for i in range(20)])
    bot.send_message(chat_id=call.from_user.id, text='🌡 Установить температуру в помещении: ', reply_markup=keyboard)


# Выбор устройства охлаждения
@bot.callback_query_handler(func=lambda call: call.data == 'cool')
def cooler(call):
    switches = sql.my_switches(call.from_user.id)
    keyboard = types.InlineKeyboardMarkup()
    print(switches)
    for sw in switches:
        simbo =''
        if sw[2] == 'COOL':
            simbo = '🌀'
            b = types.InlineKeyboardButton(simbo+' '+sw[0]+ ' '+ sw[1], callback_data=sw[0]+',_cool')
        else:
            b = types.InlineKeyboardButton(simbo+' '+sw[0]+ ' '+ sw[1], callback_data=sw[0]+',s_cool')
        keyboard.add(b)
    bot.send_message(chat_id=call.from_user.id, text='Выбор устройства охлаждения:\n🌀 - выбранное устройство', reply_markup=keyboard)

# Установка устройства охлаждения
@bot.callback_query_handler(func=lambda call: call.data[-6:] == 's_cool')
def set_cool(call):
    call.data = call.data.split(',')
    print(call.data)
    switches = sql.my_switches(call.from_user.id)
    for sw in switches:
        if sw[2] == 'COOL':
            sql.set_climat_device(sw[0], 'NONE')
    sql.set_climat_device(call.data[0], 'COOL')

    climat_dev = sql.climat_devices(call.from_user.id)  # [] topic, topic_alias, climat_mode
    heat = '-'
    cool = '-'
    metering = '-'
    for i in climat_dev:
        if i[2] == 'HEAT':
            heat = i[0] + ', ' + i[1]
        elif i[2] == 'COOL':
            cool = i[0] + ', ' + i[1]
        elif i[2] == 'METERING':
            metering = i[0] + ', ' + i[1]

    text = 'Устройство обогрева:\n' + heat + '\nУстройство охлаждения:\n' + cool + '\nСенсор температуры:\n' + metering
    keyboard2 = types.InlineKeyboardMarkup(row_width=1)
    b_heat = types.InlineKeyboardButton('Устройство обогрева', callback_data='heat')
    b_cool = types.InlineKeyboardButton('Устройство охлаждения', callback_data='cool')
    b_tem = types.InlineKeyboardButton('Сенсор температуры', callback_data='temper')
    keyboard2.add(b_heat, b_cool, b_tem)
    bot.send_message(chat_id=call.from_user.id, text=text + '\nНазначить устройства:', reply_markup=keyboard2)

    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard.add(*[types.InlineKeyboardButton(str(15 + i) + '°C', callback_data=str(15 + i) + ',c') for i in range(20)])
    bot.send_message(chat_id=call.from_user.id, text='🌡 Установить температуру в помещении: ', reply_markup=keyboard)

# Убирание устройства охлаждения
@bot.callback_query_handler(func=lambda call: call.data[-5:] == '_cool')
def set_cool2(call):
    call.data = call.data.split(',')
    sql.set_climat_device(call.data[0], 'NONE')

    climat_dev = sql.climat_devices(call.from_user.id)  # [] topic, topic_alias, climat_mode
    heat = '-'
    cool = '-'
    metering = '-'
    for i in climat_dev:
        if i[2] == 'HEAT':
            heat = i[0] + ', ' + i[1]
        elif i[2] == 'COOL':
            cool = i[0] + ', ' + i[1]
        elif i[2] == 'METERING':
            metering = i[0] + ', ' + i[1]

    text = 'Устройство обогрева:\n' + heat + '\nУстройство охлаждения:\n' + cool + '\nСенсор температуры:\n' + metering
    keyboard2 = types.InlineKeyboardMarkup(row_width=1)
    b_heat = types.InlineKeyboardButton('Устройство обогрева', callback_data='heat')
    b_cool = types.InlineKeyboardButton('Устройство охлаждения', callback_data='cool')
    b_tem = types.InlineKeyboardButton('Сенсор температуры', callback_data='temper')
    keyboard2.add(b_heat, b_cool, b_tem)
    bot.send_message(chat_id=call.from_user.id, text=text + '\nНазначить устройства:', reply_markup=keyboard2)

    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard.add(*[types.InlineKeyboardButton(str(15 + i) + '°C', callback_data=str(15 + i) + ',c') for i in range(20)])
    bot.send_message(chat_id=call.from_user.id, text='🌡 Установить температуру в помещении: ', reply_markup=keyboard)

# Выбор сенсора температуры
@bot.callback_query_handler(func=lambda call: call.data == 'temper')
def temperature(call):
    switches = sql.my_sensors(call.from_user.id)
    keyboard = types.InlineKeyboardMarkup()
    print(switches)
    for sw in switches:
        simbo =''
        if sw[2] == 'METERING':
            simbo = '✔'
            b = types.InlineKeyboardButton(simbo+' '+sw[0]+ ' '+ sw[1], callback_data=sw[0]+',_temper')
        else:
            b = types.InlineKeyboardButton(simbo+' '+sw[0]+ ' '+ sw[1], callback_data=sw[0]+',s_temper')
        keyboard.add(b)
    bot.send_message(chat_id=call.from_user.id, text='Выбор сенсора для замеров температуры:\n✔ - выбранное устройство', reply_markup=keyboard)

# Установка сенсора температуры
@bot.callback_query_handler(func=lambda call: call.data[-8:] == 's_temper')
def set_temper(call):
    call.data = call.data.split(',')
    # print(call.data)
    switches = sql.my_sensors(call.from_user.id)
    for sw in switches:
        if sw[2] == 'METERING':
            sql.set_climat_device(sw[0], 'NONE')
    sql.set_climat_device(call.data[0], 'METERING')

    climat_dev = sql.climat_devices(call.from_user.id)  # [] topic, topic_alias, climat_mode
    heat = '-'
    cool = '-'
    metering = '-'
    for i in climat_dev:
        if i[2] == 'HEAT':
            heat = i[0] + ', ' + i[1]
        elif i[2] == 'COOL':
            cool = i[0] + ', ' + i[1]
        elif i[2] == 'METERING':
            metering = i[0] + ', ' + i[1]

    text = 'Устройство обогрева:\n' + heat + '\nУстройство охлаждения:\n' + cool + '\nСенсор температуры:\n' + metering
    keyboard2 = types.InlineKeyboardMarkup(row_width=1)
    b_heat = types.InlineKeyboardButton('Устройство обогрева', callback_data='heat')
    b_cool = types.InlineKeyboardButton('Устройство охлаждения', callback_data='cool')
    b_tem = types.InlineKeyboardButton('Сенсор температуры', callback_data='temper')
    keyboard2.add(b_heat, b_cool, b_tem)
    bot.send_message(chat_id=call.from_user.id, text=text + '\nНазначить устройства:', reply_markup=keyboard2)

    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard.add(*[types.InlineKeyboardButton(str(15 + i) + '°C', callback_data=str(15 + i) + ',c') for i in range(20)])
    bot.send_message(chat_id=call.from_user.id, text='🌡 Установить температуру в помещении: ', reply_markup=keyboard)

# Убирание сенсора температуры
@bot.callback_query_handler(func=lambda call: call.data[-7:] == '_temper')
def set_temper2(call):
    call.data = call.data.split(',')
    sql.set_climat_device(call.data[0], 'NONE')

    climat_dev = sql.climat_devices(call.from_user.id)  # [] topic, topic_alias, climat_mode
    heat = '-'
    cool = '-'
    metering = '-'
    for i in climat_dev:
        if i[2] == 'HEAT':
            heat = i[0] + ', ' + i[1]
        elif i[2] == 'COOL':
            cool = i[0] + ', ' + i[1]
        elif i[2] == 'METERING':
            metering = i[0] + ', ' + i[1]

    text = 'Устройство обогрева:\n' + heat + '\nУстройство охлаждения:\n' + cool + '\nСенсор температуры:\n' + metering
    keyboard2 = types.InlineKeyboardMarkup(row_width=1)
    b_heat = types.InlineKeyboardButton('Устройство обогрева', callback_data='heat')
    b_cool = types.InlineKeyboardButton('Устройство охлаждения', callback_data='cool')
    b_tem = types.InlineKeyboardButton('Сенсор температуры', callback_data='temper')
    keyboard2.add(b_heat, b_cool, b_tem)
    bot.send_message(chat_id=call.from_user.id, text=text + '\nНазначить устройства:', reply_markup=keyboard2)

    keyboard = types.InlineKeyboardMarkup(row_width=4)
    keyboard.add(*[types.InlineKeyboardButton(str(15 + i) + '°C', callback_data=str(15 + i) + ',c') for i in range(20)])
    bot.send_message(chat_id=call.from_user.id, text='🌡 Установить температуру в помещении: ', reply_markup=keyboard)

climat_clients=[]
# запуск установки температуры
@bot.callback_query_handler(func=lambda call: call.data[-2:] == ',c')    ################################################ нужна асинхронность отрубается от работы security()
def start_climat(call):
    call.data = call.data.split(',')
    print(call.data)
    # Проверка, все ли устройства заданы
    climat_dev = sql.climat_devices(call.from_user.id) # [] topic, topic_alias, climat_mode
    # print(climat_dev)
    heat = False
    cool = False
    metering = False
    for i in climat_dev:
        if i[2] == 'HEAT': heat = True
        elif i[2] == 'COOL': cool = True
        elif i[2] == 'METERING': metering = True
    mes=''
    if heat == False: mes += 'Не задано устройство обогрева\n'
    if cool == False: mes += 'Не задано устройство охлаждения\n'
    if metering == False: mes += 'Не задан сенсор температуры'
    if len(mes) > 0:
        bot.send_message(chat_id=call.from_user.id, text=mes)
    # Все устройства заданы, тогда
    else:
        sensors_data = sql.device_data_for_user('SENSOR',
                                        call.from_user.id)  # topic, topic_alias, measurement, value, climat_mode, alarm_mode

        for sen_dat in sensors_data:
            if sen_dat[4] == 'METERING':
                now_temperature = sen_dat[3]  # текущая температура

                try:
                    float(sen_dat[3]) # является ли значение температуры числом
                    keyboard = types.InlineKeyboardMarkup()
                    stop_temper=types.InlineKeyboardButton('Остановить', callback_data='stop_clim')
                    keyboard.add(stop_temper)
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          text='⚠ Идет установка температуры\nТекущее значение ' + sen_dat[
                                              3] + ' °C\nУстанавливаемое значение ' +
                                               call.data[0] + ' °C', reply_markup=keyboard)

                    # Установка температуры
                    global climat_clients
                    climat_clients.append(call.from_user.id)

                    t = Thread(target=set_temperature, args=(call, climat_dev))
                    t.start()

                except:
                    bot.send_message(chat_id=call.from_user.id,
                                     text='Выбран некорректный сенсор температуры')

# Установка температуры
def set_temperature(call, climat_dev):
    while call.from_user.id in climat_clients:
        sensors_data = sql.device_data_for_user('SENSOR',
                                                call.from_user.id)  # topic, topic_alias, measurement, value, climat_mode, alarm_mode
        for sen_dat in sensors_data:
            if sen_dat[4] == 'METERING':
                now_temperature = sen_dat[3]

        print('current', float(now_temperature), 'set', float(call.data[0]))
        if float(now_temperature) < float(call.data[0]):
            for device in climat_dev:
                if device[2] == 'HEAT':
                    sql.topic_value(device[0], '1')
                elif device[2] == 'COOL':
                    sql.topic_value(device[0], '0')

        elif float(now_temperature) > float(call.data[0]):
            for device in climat_dev:
                if device[2] == 'HEAT':
                    sql.topic_value(device[0], '0')
                elif device[2] == 'COOL':
                    sql.topic_value(device[0], '1')

        elif float(now_temperature) == float(call.data[0]):
            for device in climat_dev:
                if device[2] == 'HEAT':
                    sql.topic_value(device[0], '0')
                elif device[2] == 'COOL':
                    sql.topic_value(device[0], '0')
            bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id,
                                  text='⚠ Установлена температура ' + call.data[0] + ' °C')
            climat_clients.remove(call.from_user.id)

# Ручная остановка установки температуры
@bot.callback_query_handler(func=lambda call: call.data == 'stop_clim')
def stop_climat(call):
    global climat_clients
    climat_clients.remove(call.from_user.id)
    climat_dev = sql.climat_devices(call.from_user.id)  # [] topic, topic_alias, climat_mode
    for device in climat_dev:
        if device[2] == 'HEAT':
            sql.topic_value(device[0], '0')
        elif device[2] == 'COOL':
            sql.topic_value(device[0], '0')
    bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text='⚠ Установка температуры остановлена')


# ВКЛ/ВЫКЛ уведомлений от сенсоров
@bot.callback_query_handler(func=lambda call: call.data == 'security')
def security_activation(call):
    # print('call.from_user.id',call.from_user.id)
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btns = sql.device_data_for_user('SENSOR', call.from_user.id) # topic, topic_alias, measurement, value, climat_mode, alarm_mode
    # print(btns)
    for btn in btns:
        if btn[5] == 1:
            emoji = '🚨'
        else:
            emoji = '✨'
        b = types.InlineKeyboardButton(emoji + btn[1],
                                       callback_data=btn[0] + ',' + str(btn[5]) + ',sen')  # topic, topic_alias, measurement, value, climat_mode, alarm_mode
        keyboard.add(b)

    for btn in btns:
        if btn[5] != 0:
            keyboard.add(types.InlineKeyboardButton('🔘 Выключить все уведомления', callback_data='alloff,sen'))
            break
    try:
        bot.send_message(call.from_user.id, "ВКЛ/ВЫКЛ уведомлений от сенсоров\n🚨 - уведомления включены\n✨ - уведомления выключены",
                         reply_markup=keyboard)
    except (
    ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError, urllib3.exceptions.ReadTimeoutError,
    requests.exceptions.ReadTimeout):
        print('!!!')

@bot.callback_query_handler(func=lambda call: call.data[-3:] == 'sen')
def security_activation2(call):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    call.data = call.data.split(',')
    # print('call.data in', call.data)
    btns = sql.device_data_for_user('SENSOR', call.from_user.id)
    # print('btns in:', btns)

    if call.data[0] != 'alloff':
        for btn in btns:
            if btn[0] == call.data[0]:
                bot_answer = btn[1]
                if call.data[1] == '0':
                    btn[5] = 1
                    bot_answer += ' УВЕДОМЛЕНИЯ ВКЛ'
                else:
                    btn[5] = 0
                    bot_answer += ' УВЕДОМЛЕНИЯ ВЫКЛ'

                sql.set_alarm_mode(btn[0], btn[5])
                bot.answer_callback_query(call.id, text='⚠ ' + bot_answer)  # всплывающее уведомление
                # bot.send_message(call.from_user.id, text='⚠ ' + bot_answer)

            if btn[5] == 1:
                emoji = '🚨'
            else:
                emoji = '✨'

            b = types.InlineKeyboardButton(emoji + btn[1],
                                           callback_data=btn[0] + ',' + str(btn[5]) + ',sen')
            keyboard.add(b)

            # print('btns out:', btns)

    else:  # кнопка Выключить всё
        bot.answer_callback_query(call.id, text='⚠ ВЫКЛЮЧЕНИЕ')  # всплывающее уведомление
        for btn in btns:
            if btn[5] != 0:
                btn[5] = 0
                sql.set_alarm_mode(btn[0], btn[5])
            b = types.InlineKeyboardButton('✨' + btn[1],
                                           callback_data=btn[0] + ',' + str(btn[5]) + ',sen')  # топик, алиас, валу, межурмент, алярм_мод
            keyboard.add(b)

    for btn in btns:
        if btn[5] != 0:
            keyboard.add(types.InlineKeyboardButton('🔘 Выключить все уведомления', callback_data='alloff,sen'))
            break

    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="ВКЛ/ВЫКЛ уведомлений от сенсоров\n🚨 - уведомления включены\n✨ - уведомления выключены", reply_markup=keyboard)
    except (
    ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError, urllib3.exceptions.ReadTimeoutError,
    requests.exceptions.ReadTimeout):
        print(
            '!!! telebot.apihelper.ApiException or !!! ConnectionResetError or !!! requests.exceptions.ConnectionError')

####################################################################################################--- Устройства

####################################################################################################--- Настройки
# Мои Wi-Fi модули (Добавление/Удаление модулей)
@bot.callback_query_handler(func=lambda call: call.data == 'm_add')
def modules_add_del(call):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    modules = sql.modules_root1(call.from_user.id)
    for module in modules:
        b = types.InlineKeyboardButton('❎  ' + module, callback_data=module + ',del')
        keyboard.add(b)
    keyboard.add(types.InlineKeyboardButton('✅ Добавить новый модуль', callback_data='new'))
    try:
        bot.send_message(call.from_user.id, "Вы - владелец Wi-Fi модулей: \n❎ - По нажатию модуль будет удален", reply_markup=keyboard)
    except (
    ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError, urllib3.exceptions.ReadTimeoutError,
    requests.exceptions.ReadTimeout):
        print('!!!')

@bot.callback_query_handler(func=lambda call: call.data[-3:] == 'del')
def modules_del(call):
    call.data = call.data.split(',')
    sql.del_module(call.data[0])

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    modules = sql.modules_root1(call.from_user.id)
    for module in modules:
        b = types.InlineKeyboardButton('❎  ' + module, callback_data=module + ',del')
        keyboard.add(b)
    keyboard.add(types.InlineKeyboardButton('✅ Добавить новый модуль', callback_data='new'))

    bot.answer_callback_query(call.id, text='⚠ Удален модуль ' + call.data[0])  # всплывающее уведомление

    try:
        bot.send_message(call.from_user.id, "Вы - владелец Wi-Fi модулей: \n❎ - По нажатию модуль будет удален",
                         reply_markup=keyboard)
    except (
            ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError,
            urllib3.exceptions.ReadTimeoutError,
            requests.exceptions.ReadTimeout):
        print('!!!')

@bot.callback_query_handler(func=lambda call: call.data == 'new')
def modules_new(call):
    code = bot.send_message(call.from_user.id, 'Введите код активации для нового Wi-Fi модуля')
    bot.register_next_step_handler(code, check_code)

def check_code(msg):
    a_codes = sql.activation_codes()
    true_code = False
    for code in a_codes:
        if code == msg.text:
            true_code = True  # код найден
            sql.new_module(code, msg.from_user.id)
            # bot.answer_callback_query(msg.id, text='⚠ Добавлен новый модуль')  # всплывающее уведомление

            keyboard = types.InlineKeyboardMarkup(row_width=1)
            modules = sql.modules_root1(msg.from_user.id)
            for module in modules:
                b = types.InlineKeyboardButton('❎  ' + module, callback_data=module + ',del')
                keyboard.add(b)
            keyboard.add(types.InlineKeyboardButton('✅ Добавить новый модуль', callback_data='new'))
            try:
                bot.send_message(msg.from_user.id, "Вы - владелец Wi-Fi модулей: \n❎ - По нажатию модуль будет удален",
                                 reply_markup=keyboard)
            except (
                    ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError,
                    urllib3.exceptions.ReadTimeoutError,
                    requests.exceptions.ReadTimeout):
                print('!!!')

    if true_code == False:  # Код не найден
        bot.send_message(msg.from_user.id, text="⚠ Не верный код активации. Модуль уже используется или не существует")

# Имена моих устройств
@bot.callback_query_handler(func=lambda call: call.data == 'd_names')
def device_names(call):
    topics_names = sql.topics_names(call.from_user.id)
    # print(topics_names)
    bot.send_message(call.from_user.id, 'Список устройств:')
    for name in topics_names:
        keyboard = types.InlineKeyboardMarkup()
        b = types.InlineKeyboardButton('Изменить имя устройства ⬆', callback_data = name[0]+',xtopic')
        keyboard.add(b)
        bot.send_message(call.from_user.id, 'Топик: '+name[0]+'\nИмя устройства: '+name[1], reply_markup=keyboard)

topic=''
@bot.callback_query_handler(func=lambda call: call.data[-6:] == 'xtopic')
def device_names2(call):
    call.data = call.data.split(',')
    topics_names = sql.topics_names(call.from_user.id)
    global topic
    topic = call.data[0]
    for t in topics_names:
        if t[0] == call.data[0]:
            n_name = bot.send_message(call.from_user.id, 'Топик: '+call.data[0]+'\nВведите для устройства желаемое имя')
            bot.register_next_step_handler(n_name, new_name)

def new_name(msg):
    global topic
    # print('--topic', topic)
    # print('--name', msg.text)
    sql.new_device_name(topic, msg.text)
    bot.send_message(msg.from_user.id, 'Присвоено новое имя устройству \nТопик: '+topic+'\nИмя: '+msg.text)

# Голосовые команды моих устройств
@bot.callback_query_handler(func=lambda call: call.data == 'v_com')
def voice_comm(call):
    #############################################################
    topics_names = sql.topics_names_root1(call.from_user.id)
    # print(topics_names)
    voice_com = sql.voice_com()
    # print(voice_com)
    #############################################################
    rez=[]
    for i in voice_com:
        for j in topics_names:
            if i[1] == j[0]:
                rez_consist=[i[0], i[1], j[1], i[2], i[3]]
                rez.append(rez_consist)
    bot.send_message(call.from_user.id, 'Список голосовых команд моих устройств:')
    # print(rez)

    for comm in rez:
        type=''
        if comm[4] == 'DATA': type = 'Получить данные'
        elif comm[4] == 'ON': type = 'Включение'
        elif comm[4] == 'OFF': type = 'Выключение'
        keyboard = types.InlineKeyboardMarkup()
        b = types.InlineKeyboardButton('❎ Удалить голосовую команду ⬆', callback_data=str(comm[0]) + ',del_com')
        keyboard.add(b)
        bot.send_message(call.from_user.id, 'Топик: ' + comm[1] + '\nИмя устройства: ' + comm[2]+'\nТип команды: '+type+'\nТекст команды: '+'<i>'+comm[3]+'</i>', parse_mode='HTML', reply_markup=keyboard)
    keyboard2 = types.InlineKeyboardMarkup()
    new_com = types.InlineKeyboardButton('✅ Добавить новую команду', callback_data='new_com' )
    keyboard2.add(new_com)
    bot.send_message(call.from_user.id, '🆕', reply_markup=keyboard2)

@bot.callback_query_handler(func=lambda call: call.data[-7:] == 'del_com')
def del_command(call):
    call.data = call.data.split(',')
    sql.del_command(call.data[0])
    bot.answer_callback_query(call.id, text='⚠ Голосовая команда удалена')  # всплывающее уведомление

    topics_names = sql.topics_names(call.from_user.id)
    # print(topics_names)
    voice_com = sql.voice_com()
    # print(voice_com)
    rez = []
    for i in voice_com:
        for j in topics_names:
            if i[1] == j[0]:
                rez_consist = [i[0], i[1], j[1], i[2], i[3]]
                rez.append(rez_consist)
    bot.send_message(call.from_user.id, 'Список голосовых команд моих устройств:')
    # print(rez)

    for comm in rez:
        type = ''
        if comm[4] == 'DATA':
            type = 'Получить данные'
        elif comm[4] == 'ON':
            type = 'Включение'
        elif comm[4] == 'OFF':
            type = 'Выключение'
        keyboard = types.InlineKeyboardMarkup()
        b = types.InlineKeyboardButton('❎ Удалить голосовую команду ⬆', callback_data=str(comm[0]) + ',del_com')
        keyboard.add(b)
        bot.send_message(call.from_user.id, 'Топик: ' + comm[1] + '\nИмя устройства: ' + comm[
            2] + '\nТип команды: ' + type + '\nТекст команды: ' + '<i>' + comm[3] + '</i>', parse_mode='HTML',
                         reply_markup=keyboard)
    keyboard2 = types.InlineKeyboardMarkup()
    new_com = types.InlineKeyboardButton('✅ Добавить новую команду', callback_data='new_com')
    keyboard2.add(new_com)
    bot.send_message(call.from_user.id, '🆕', reply_markup=keyboard2)


@bot.callback_query_handler(func=lambda call: call.data == 'new_com')
def new_command(call):
    topics_names = sql.topics_names(call.from_user.id)
    keyboard = types.InlineKeyboardMarkup()

    for t in topics_names:
        print('--t--', t)
        b = types.InlineKeyboardButton(t[0]+'; '+t[1], callback_data=t[0]+',type_com')
        keyboard.add(b)
    bot.send_message(call.from_user.id, 'Выберите устройство:', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data[-8:] == 'type_com')
def new_command(call):
    call.data=call.data.split(',')
    # print('call.data--', call.data)
    type_device = sql.type_device(call.data[0])
    type_command=[]
    if type_device == 'SENSOR':
        type_command=[('Получить данные', 'DATA'),]
    elif type_device == 'SWITCH':
        type_command=[('Включить','ON'),('Выключить','OFF')]
    keyboard = types.InlineKeyboardMarkup()

    for t in type_command:
        b = types.InlineKeyboardButton(t[0], callback_data=call.data[0]+','+t[1]+',enter_text') # 0-рус тип команды,1-тип команды
        keyboard.add(b)
    bot.send_message(call.from_user.id,'Выберите тип команды для '+call.data[0], reply_markup=keyboard)

topic_comtype=[]
@bot.callback_query_handler(func=lambda call: call.data[-10:] == 'enter_text')
def text_command(call):
    call.data = call.data.split(',')
    global topic_comtype
    topic_comtype =[call.data[0], call.data[1]]
    type_com=''
    if call.data[1] == 'DATA': type_com = 'Получить данные'
    elif call.data[1] == 'ON': type_com = 'Включить'
    elif call.data[1] == 'OFF': type_com = 'Выключить'
    txt = bot.send_message(call.from_user.id, '🆕 Введите текст новой команды для устройства:\n'+call.data[0]+ '\nтип команды:\n'+ type_com + '\n(для обозначающих номера "Один/Первый/Первая", "Два/Второй/Вторая", "Три/Третий/Третья", и т. д. ипользуйте при вводе цифры 1, 2, 3, и т.п.)')
    bot.register_next_step_handler(txt, txt_command)

def txt_command(txt):
    global topic_comtype
    # print(topic_comtype)

    sql.new_voice_command(topic_comtype[0], topic_comtype[1], txt.text.lower()) # топик, тип команды, текст команды
    device_name = sql.alias_device(topic_comtype[0])
    bot.send_message(txt.from_user.id, 'Добавлена новая голосовая команда устройству\n'+topic_comtype[0]+'; '+device_name+':\n'+txt.text)


# Инфо о всех доступных Wi-Fi модули
@bot.callback_query_handler(func=lambda call: call.data == 'm_info')
def modules_info(call):
    keyboard = types.InlineKeyboardMarkup()
    modules = sql.modules(call.from_user.id)
    for module in modules:
        b = types.InlineKeyboardButton('🌐  ' + module, callback_data=module+',inf')
        keyboard.add(b)
    try:
        bot.send_message(call.from_user.id, "Все доступные Wi-Fi модули. \nДля подробностей выберите какой-либо из представленных:", reply_markup=keyboard)
    except (ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError, urllib3.exceptions.ReadTimeoutError, requests.exceptions.ReadTimeout):
        print('!!!')

@bot.callback_query_handler(func=lambda call: call.data[-3:] == 'inf')
def modules_info2(call):
    call.data = call.data.split(',')
    info = '🔹 Общая информация: '
    inf = sql.module_info(call.data[0])
    if not inf:
        info += '-'
    else:
        info+='\n'+inf
    info += '\n🔹 Владелец: '
    owner = sql.owner(call.data[0])
    for ow in owner:
        info+='\n'+ow
    info += '\n🔹 Другие пользователи: '
    users = sql.another_users(call.data[0])
    if not users:
        info += '-'
    else:
        for user in users:
            info+='\n'+user
    info += '\n🔹 Имена устройств и топики: '
    names = sql.names(call.data[0])
    if not names:
        info += '-'
    else:
        for name in names:
            info += '\n--Имя: '+name[1]+'\n   Топик: '+name[0]

    bot.send_message(call.from_user.id, info)


# Добавление/Удаление пользователей
@bot.callback_query_handler(func=lambda call: call.data == 'm_users')
def another_users(call):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    modules = sql.modules_root1(call.from_user.id)
    for module in modules:
        b = types.InlineKeyboardButton('🌐 '+module, callback_data=module+',another')
        keyboard.add(b)
    try:
        bot.send_message(call.from_user.id, "Wi-Fi модули, которым можно добавить и удалить других пользователей:",
                         reply_markup=keyboard)
    except (
            ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError,
            urllib3.exceptions.ReadTimeoutError,
            requests.exceptions.ReadTimeout):
        print('!!!')

@bot.callback_query_handler(func=lambda call: call.data[-7:] == 'another')
def another_users(call):
    call.data = call.data.split(',')
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    a_us =sql.another_users(call.data[0])

    for a_u in a_us:
        b = types.InlineKeyboardButton('❎ ' + a_u, callback_data=a_u +','+call.data[0]+',del_a_u')
        keyboard.add(b)
    keyboard.add(types.InlineKeyboardButton('✅ Открыть доступ новому пользователю', callback_data=call.data[0]+',new_u'))

    try:
        bot.send_message(call.from_user.id, 'Wi-Fi модуль 🌐 '+call.data[0]+' доступен для использования следующим пользователям: \n❎ - По нажатию пользователь будет отключен', reply_markup=keyboard)
    except (
            ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError,
            urllib3.exceptions.ReadTimeoutError,
            requests.exceptions.ReadTimeout):
        print('!!!')

@bot.callback_query_handler(func=lambda call: call.data[-7:] == 'del_a_u')
def another_users2(call):
    call.data = call.data.split(',')
    # print('--call.data--', call.data)
    sql.del_user(call.data[0], call.data[1])

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    a_us = sql.another_users(call.data[1])

    for a_u in a_us:
        b = types.InlineKeyboardButton('❎ ' + a_u, callback_data=a_u + ','+call.data[1]+',del_a_u')
        keyboard.add(b)
    keyboard.add(types.InlineKeyboardButton('✅ Открыть доступ новому пользователю', callback_data=call.data[1]+',new_u'))

    bot.answer_callback_query(call.id, text='⚠ Пользователь '+call.data[0]+' отключен')  # всплывающее уведомление

    try:
        bot.send_message(call.from_user.id,
                         'Wi-Fi модуль 🌐 '+call.data[1]+' доступен для использования следующим пользователям: \n❎ - По нажатию пользователь будет отключен',
                         reply_markup=keyboard)
    except (
            ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError,
            urllib3.exceptions.ReadTimeoutError,
            requests.exceptions.ReadTimeout):
        print('!!!')

controller_id=''
@bot.callback_query_handler(func=lambda call: call.data[-5:] == 'new_u')
def another_user_new(call):
    call.data = call.data.split(',')
    print('new_u', call.data)
    global controller_id
    controller_id = call.data[0]
    new_phone = bot.send_message(call.from_user.id, 'Введите номер телефона (только цифры) для нового пользователя данного Wi-Fi модуля')
    # print(type(new_phone))
    bot.register_next_step_handler(new_phone, add_phone)
    # print(new_phone.text)
    # add_phone(call.data[0], new_phone)

def add_phone(new_ph):
    try:
        global controller_id
        len_num = len(new_ph.text)
        num=(int(new_ph.text))    # съедает нули в начале
        num = str(num)

        if len_num != len(num):
            zeros = len_num - len(num)
            for i in range(zeros):
                num = '0' + num

        print('num', num)
        telnum = sql.check_phone_module(num, controller_id)
        if telnum == True:
            bot.send_message(new_ph.from_user.id, '⚠ Пользователю '+num+ ' этот Wi-Fi модуль уже доступен')
        else:
            sql.insert_user(num, controller_id)

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        a_us = sql.another_users(controller_id)

        for a_u in a_us:
            b = types.InlineKeyboardButton('❎ ' + a_u, callback_data=a_u + ',' + controller_id + ',del_a_u')
            keyboard.add(b)
        keyboard.add(
            types.InlineKeyboardButton('✅ Открыть доступ новому пользователю', callback_data=controller_id + ',new_u'))

        # bot.answer_callback_query(new_ph.from_user.id, text='⚠ Пользователь ' + num + ' удален')  # всплывающее уведомление

        try:
            bot.send_message(new_ph.from_user.id,
                             'Wi-Fi модуль 🌐 ' + controller_id + ' доступен для использования следующим пользователям: \n❎ - По нажатию пользователь будет отключен',
                             reply_markup=keyboard)
        except (
                ConnectionResetError, urllib3.exceptions.ProtocolError, ConnectionError,
                urllib3.exceptions.ReadTimeoutError,
                requests.exceptions.ReadTimeout):
            print('!!!')

    except ValueError:
        bot.send_message(new_ph.chat.id, "⚠ Введенный номер содержит неверные знаки")
################################################################################################---Настройки

################################################################################################---Голосовое управление
@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    '''Голосовое управление'''
    bot.send_message(message.chat.id, "⏳...")
    file_info = bot.get_file(message.voice.file_id)
    file = requests.get(
        'https://api.telegram.org/file/bot{0}/{1}'.format(config.bot_token, file_info.file_path))
    print(file.content)

    speech_text = voice.speech_to_text(bytes=file.content)
    print(speech_text)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id+1)
    bot.send_message(message.chat.id, speech_text)

    topics_names = sql.topics_names(message.from_user.id)
    # print(topics_names)
    voice_com = sql.voice_com()
    # print(voice_com)

    rez = []
    for i in voice_com:
        for j in topics_names:
            if i[1] == j[0]:
                rez_consist = [i[0], i[1], j[1], i[2], i[3]]
                rez.append(rez_consist)

    print('rez', rez)
    for i in rez:
        if i[3] == speech_text:
            if i[4] == 'DATA':
                value = sql.return_topic_value(i[1])
                bot.send_message(message.from_user.id, i[2]+': '+value[0]+' '+value[1])
            elif i[4] == 'ON':
                sql.topic_value(i[1], '1')
                bot.send_message(message.from_user.id, '💡 '+i[2] + ': Включено')
            elif i[4] == 'OFF':
                sql.topic_value(i[1], '0')
                bot.send_message(message.from_user.id, '✨ ' + i[2] + ': Выключено')
################################################################################################---Голосовое управление

if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)

        except Exception as e:
            print(e)
            time.sleep(15)


    # while(1):
    #     try:
    #         bot.polling(none_stop=True)
    #     except (ConnectionResetError, urllib3.exceptions.ProtocolError, requests.exceptions.ConnectionError):
    #         continue

    # try:
    #     bot.polling(none_stop=True)
    # except:
    #     time.sleep(3)
    #     os.system('main.py')
    # else:
    #     print('system OK')

