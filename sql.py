# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import MySQLConnection, Error
import config

cnx = mysql.connector.connect(user=config.mysql_username,
                              password=config.mysql_password,
                              host=config.mysql_host,
                              database=config.mysql_database)

# Проверка номера телефона +
def check_phone(tel_number):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT phone FROM users")
    numbers = cursor.fetchall()
    # print(numbers)
    for number in numbers:
        # print(str(number)[2:-3])
        if tel_number == str(number)[2:-3]:
            conn.commit()
            cursor.close()
            conn.close()
            return True
    conn.commit()
    cursor.close()
    conn.close()
    return False




# Добавление пользователя +
def add_user(phone, telegram_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (phone, telegram_id) VALUES ('{}', '{}')".format(phone, telegram_id))
    conn.commit()
    cursor.close()
    conn.close()

# Выборка topic, topic_alias, climat-mode из доступных пользователю устройств по telegram_id
def climat_devices(t_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("""SELECT topic, topic_alias, climat_mode FROM device_data
                    LEFT JOIN users_controllers
                    ON device_data.controller_id = users_controllers.controller_id
                    LEFT JOIN users
                    ON users_controllers.phone = users.phone
                    WHERE users.telegram_id = '{}'""".format(t_id))
    tmp = cursor.fetchall()
    cl_dev =[]
    for i in tmp:
        cl_dev.append(list(i))
    conn.commit()
    cursor.close()
    conn.close()
    return cl_dev

# c_d = climat_devices('431713612')
# print(c_d)

# Выборка всех SWITCH c root 1 по telegram_id +
def my_switches(t_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("""SELECT topic, topic_alias, climat_mode FROM device_data
                    LEFT JOIN users_controllers
                    ON device_data.controller_id = users_controllers.controller_id
                    LEFT JOIN users
                    ON users_controllers.phone = users.phone
                    WHERE users.telegram_id = '{}'
                    AND device_type = 'SWITCH'""".format(t_id))
    tmp = cursor.fetchall()
    switches = []
    for i in tmp:
        switches.append(list(i))
    conn.commit()
    cursor.close()
    conn.close()
    return switches

# Выборка всех SENSOR c root 1 по telegram_id
def my_sensors(t_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("""SELECT topic, topic_alias, climat_mode FROM device_data
                       LEFT JOIN users_controllers
                       ON device_data.controller_id = users_controllers.controller_id
                       LEFT JOIN users
                       ON users_controllers.phone = users.phone
                       WHERE users.telegram_id = '{}'
                       AND device_type = 'SENSOR'""".format(t_id))
    tmp = cursor.fetchall()
    sensors = []
    for i in tmp:
        sensors.append(list(i))
    conn.commit()
    cursor.close()
    conn.close()
    return sensors

# Установка climat_mode +
def set_climat_device(topic, climat_mode):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE device_data SET climat_mode = '{}' WHERE topic = '{}'".format(climat_mode, topic))
    conn.commit()
    cursor.close()
    conn.close()


# Отбор topic_alias по device_type (SWITCH или SENSOR) +
def device_data_for_user(device_type, t_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    # cursor.execute("""SELECT topic_alias FROM device_data WHERE controller_id =
    #                 (SELECT controller_id FROM users_controllers WHERE phone =
    #                 (SELECT phone FROM users WHERE telegram_id = '{}'))""".format(t_id))
    cursor.execute("""SELECT topic, topic_alias, measurement, value, climat_mode, alarm_mode FROM device_data 
                    LEFT JOIN users_controllers
                    ON device_data.controller_id = users_controllers.controller_id
                    LEFT JOIN users
                    ON users_controllers.phone = users.phone
                    WHERE users.telegram_id = '{}' 
                    AND device_data.device_type = '{}'""".format(t_id, device_type))
    tmp = cursor.fetchall()
    topic_aliases_and_values = []
    for i in tmp:
        topic_aliases_and_values.append(list(i))
            # print(topic_aliases_and_values)
    conn.commit()
    cursor.close()
    conn.close()
    return topic_aliases_and_values

# Установка значения alarm_mode
def set_alarm_mode(topic, mode):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE device_data SET alarm_mode = {} WHERE topic = '{}'".format(mode, topic))
    conn.commit()
    cursor.close()
    conn.close()

# set_alarm_mode('id_1/door', 1)

# Возвращает список topic_alias устройств с типом SWITCH или SENSOR в devices
# def topic_aliases_in_db(device_type):
#     conn = MySQLConnection(**config.db_config)
#     cursor = conn.cursor()
#     cursor.execute("""SELECT topic, topic_alias, measurement, value, updated
#                       FROM pubs_n_subs
#                       INNER JOIN devices
#                       ON pubs_n_subs.device_id = devices.device_id
#                       WHERE devices.device_type = '{}'""".format(device_type))
#     tmp=cursor.fetchall()
#     topic_aliases_and_values =[]
#     for i in tmp:
#         topic_aliases_and_values.append(list(i))
#     # print(topic_aliases_and_values)
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return topic_aliases_and_values


# Возвращает список controller_id доступных пользователю +
def modules(t_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("""SELECT controller_id FROM users_controllers
                    LEFT JOIN users
                    ON users_controllers.phone = users.phone
                    WHERE users.telegram_id = '{}'
                    ORDER BY controller_id""".format(t_id))
    tmp = cursor.fetchall()
    # print(tmp)
    controllers=[]
    for i in tmp:
        controllers.append(i[0])
    # print(controllers)
    conn.commit()
    cursor.close()
    conn.close()
    return controllers

# Возвращает info о контроллере +
def module_info(controller_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT info FROM controllers WHERE controller_id = '{}'".format(controller_id))
    info = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return info[0][0]

# Владелец контроллера +
def owner(controller_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT phone FROM users_controllers WHERE controller_id = '{}' AND root = 1".format(controller_id))
    tmp = cursor.fetchall()
    owner = []
    for i in tmp:
        owner.append(i[0])
    conn.commit()
    cursor.close()
    conn.close()
    return owner
# print(owner('id_1'))

# Другие пользователи +
def another_users(controller_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT phone FROM users_controllers WHERE controller_id = '{}' AND root = 0".format(controller_id))
    tmp = cursor.fetchall()
    users = []
    for i in tmp:
        users.append(i[0])
    conn.commit()
    cursor.close()
    conn.close()
    return users
# print(another_users('id_1'))

# Топики и пользовательские имена из device_data +
def names(controller_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT topic, topic_alias FROM device_data WHERE controller_id = '{}'".format(controller_id))
    tmp = cursor.fetchall()
    names = []
    for i in tmp:
        names.append(i)
    # print(info)
    conn.commit()
    cursor.close()
    conn.close()
    return names
# print(names('id_1'))

# Возвращает список controller_id доступных пользователю c root 1 +
def modules_root1(t_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("""SELECT controller_id FROM users_controllers
                    LEFT JOIN users
                    ON users_controllers.phone = users.phone
                    WHERE users.telegram_id = '{}'
                    AND users_controllers.root = 1
                    ORDER BY controller_id""".format(t_id))
    tmp = cursor.fetchall()
    # print(tmp)
    controllers=[]
    for i in tmp:
        controllers.append(i[0])
    # print(controllers)
    conn.commit()
    cursor.close()
    conn.close()
    return controllers

# Удаление строки из users_controllers +
def del_module(controller_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users_controllers WHERE controller_id = '{}'".format(controller_id))
    conn.commit()
    cursor.close()
    conn.close()

# Получение списка activation_code из controllers +
def activation_codes():
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("""SELECT activation_code FROM controllers
                    LEFT JOIN users_controllers
                    ON controllers.controller_id = users_controllers.controller_id
                    WHERE users_controllers.controller_id IS NULL""")
    tmp = cursor.fetchall()
    a_codes=[]
    for i in tmp:
        a_codes.append(i[0])
    conn.commit()
    cursor.close()
    conn.close()
    return a_codes

# Добавление root 1 модуля в users_controllers +
def new_module(code, t_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO users_controllers (phone, controller_id, root)
                    VALUES ((SELECT phone FROM users WHERE telegram_id = '{}'),
                            (SELECT controller_id FROM controllers WHERE activation_code = '{}'), 1)""".format(t_id, code))
    conn.commit()
    cursor.close()
    conn.close()

# Удаление строки с пользователем root 0 из users_controllers +
def del_user(phone, controller_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users_controllers WHERE phone = '{}' AND controller_id = '{}' AND root = '0'".format(phone, controller_id))
    conn.commit()
    cursor.close()
    conn.close()

# Добавление нового пользователя +
def insert_user(phone, con_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT phone FROM users")
    usrs = cursor.fetchall()
    usrs = [usr[0] for usr in usrs]
    if phone not in usrs:
        cursor.execute(
            "INSERT INTO users (phone) VALUES ('{}')".format(phone))
    cursor.execute(
        "INSERT INTO users_controllers (phone, controller_id, root) VALUES ('{}', '{}', 0)".format(phone, con_id))
    conn.commit()
    cursor.close()
    conn.close()

# insert_user('00000', 'id_4')

# Проверка доступности модуля для номера телефона +
def check_phone_module(tel_number, con_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT phone, controller_id FROM users_controllers")
    numbers = cursor.fetchall()
    # print(numbers)
    for number in numbers:
        # print(str(number[0]))
        if tel_number == str(number[0]) and con_id == str(number[1]):
            conn.commit()
            cursor.close()
            conn.close()
            return True
    conn.commit()
    cursor.close()
    conn.close()
    return False

# Топики и имена устройств +
def topics_names(t_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("""SELECT topic, topic_alias FROM device_data
                    LEFT JOIN users_controllers
                    ON device_data.controller_id = users_controllers.controller_id
                    LEFT JOIN users
                    ON users_controllers.phone = users.phone
                    WHERE telegram_id = '{}' ORDER BY topic""".format(t_id))
    t_n = cursor.fetchall()
    # print(t_n)
    conn.commit()
    cursor.close()
    conn.close()
    return t_n
# topics_names('431713612')

# Топики и имена устройств пользователя с root 1 +
def topics_names_root1(t_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("""SELECT topic, topic_alias FROM device_data
                    LEFT JOIN users_controllers
                    ON device_data.controller_id = users_controllers.controller_id
                    LEFT JOIN users
                    ON users_controllers.phone = users.phone
                    WHERE telegram_id = '{}' 
                    AND root = 1
                    ORDER BY topic""".format(t_id))
    t_n = cursor.fetchall()
    # print(t_n)
    conn.commit()
    cursor.close()
    conn.close()
    return t_n
# topics_names('431713612')

# Присвоение нового имени устройству по топику +
def new_device_name(topic, name):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("""UPDATE device_data SET topic_alias = "{}" WHERE topic = '{}'""".format(name, topic))
    conn.commit()
    cursor.close()
    conn.close()
# new_device_name('id_1/door', 'Главная дверь')

# def voice_com_root1(t_id):
#     conn = MySQLConnection(**config.db_config)
#     cursor = conn.cursor()
#     cursor.execute()
#     v_com = cursor.fetchall("""SELECT * FROM voice_commands ORDER BY topic""")
#     conn.commit()
#     cursor.close()
#     conn.close()
#     return v_com

# Содержимое таблицы voice_commands +
def voice_com():
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM voice_commands ORDER BY topic")
    v_com = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return v_com
# v = voice_com()
# for i in v:
#     print(i)

# Удаление голосовой команды +
def del_command(com_id):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM voice_commands WHERE command_id = {}".format(com_id))
    conn.commit()
    cursor.close()
    conn.close()

# Определение device_type по topic +
def type_device(topic):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT device_type FROM device_data WHERE topic = '{}'".format(topic))
    type = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return type[0]

# t = type_device('id_1/door')
# print(t)

# Добавление новой команды +
def new_voice_command(topic, comtype, text):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO voice_commands (topic, command_text, command_type) VALUES ('{}', '{}', '{}')".format(topic, text, comtype))
    conn.commit()
    cursor.close()
    conn.close()

# Определение topic_alias по topic +
def alias_device(topic):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT topic_alias FROM device_data WHERE topic = '{}'".format(topic))
    ta = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return ta[0]

# t = alias_device('id_1/hum')
# print(t)

# Возвращает measurment и value по topic
def return_topic_value(topic):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT measurement, value FROM device_data WHERE topic = '{}'".format(topic))
    v = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return v
# v = return_topic_value('id_1/tem')
# print(v)
# Для БД
###############################################################################################
# Заполнение value у device_data +
def parametr_update(name, value):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE device_data SET value = '{}' WHERE topic = '{}'".format(value, name))
    conn.commit()
    cursor.close()
    conn.close()

# Возвращает список topic'ов SENSOR из device_data +
def sensor_topic_list():
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT topic FROM device_data WHERE device_type = 'SENSOR'")
    tmp = cursor.fetchall()
    # print(tmp)
    topics = []
    for i in tmp:
        topics.append(i[0])
    # print(topics)
    conn.commit()
    cursor.close()
    conn.close()
    return topics

# Возвращает список topic'ов SWITH и значениий value из device_data +
def switch_topic_list():
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT topic, value FROM device_data WHERE device_type = 'SWITCH'")
    topics_values = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return topics_values
# print(switch_topic_list())

# Вставка новых value для SWITH +
def topic_value(topic, value):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE device_data SET value = '{}' WHERE topic = '{}'".format(value, topic))
    conn.commit()
    cursor.close()
    conn.close()
# topic_value('id_2/socket4', '0')

################################################################################################

# словарь пользователей
def users():
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT phone, root, created FROM users")
    users = cursor.fetchall()
    print(users)
    conn.commit()
    cursor.close()
    conn.close()
    return users

# удаление строки из таблицы
def delete(table, field, val):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM {} WHERE {} = {}".format(table, field, val))
    conn.commit()
    cursor.close()
    conn.close()

# Вставка новой строки
def insert(table, field, val):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO {} ({}) VALUES ({})".format(table, field, val))
    conn.commit()
    cursor.close()
    conn.close()

# Замена данных
def update(table, field, val):
    conn = MySQLConnection(**config.db_config)
    cursor = conn.cursor()
    cursor.execute("UPDATE {} SET {} = {}".format(table, field, val))
    conn.commit()
    cursor.close()
    conn.close()



# check_phone('2222222')
# parametr_update('id_1/door', '222')
# modules()
# topic_aliases_in_db('Switch')
# users()
#delete('users', 'phone', '11111')
# add_phone('88889999')
# t=topic_list()
# print(t)
# t=device_data_for_user('SWITCH', '431713612')
# print(t)
# c = modules('431713612')
# print(c)
# inf = module_info('id_2')
# print(inf)
# del_module('id_3')
# ac=activation_codes()
# print(ac)
# new_module('5555', '431713612')
# print(owner('id_4'))
# print(another_users('id_2'))