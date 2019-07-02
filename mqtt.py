# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time
import config
import sql

# Определение события-колбэка подключения (смотри subs())
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("connected OK")
    else:
        print("Bad connected Returned code=", rc)

return_subs={} # словарь с данными подписок на топики
def on_message(client, userdata, message):
    global return_subs
    # print(str(message.topic))
    # print(str(message.payload))
    return_subs[str(message.topic)] = str(message.payload)

def subs_pubs():
    # Подписки
    topics_from_db = sql.sensor_topic_list()
    print(topics_from_db)
    client = mqtt.Client()
    client.username_pw_set(username=config.mqtt_username, password=config.mqtt_password)
    client.connect(host=config.mqtt_host, port=config.mqtt_port, keepalive=60)
    client.on_connect = on_connect  # приписываем колбэк подключения
    print("Connecting to broker", config.mqtt_host)
    client.loop_start()
    for i in range(len(topics_from_db)):
        # print(topics_from_db[i])
        client.subscribe(topics_from_db[i], 0)
        client.on_message = on_message  # приписываем колбэк сообщения

    time.sleep(2.5)
    client.loop_stop()

    for i in return_subs.keys():
        print('sensor--', i, return_subs.get(i)[2:-1])
        sql.parametr_update(i, return_subs.get(i)[2:-1])  # обновление value в device_data

    # Публикации
    sw_from_db = sql.switch_topic_list()
    # print(sw_from_db)
    client.loop_start()
    for i in sw_from_db:
        print('switch--', i[0], i[1])
        client.publish(i[0], i[1])
    client.loop_stop()

while(1):
    subs_pubs()