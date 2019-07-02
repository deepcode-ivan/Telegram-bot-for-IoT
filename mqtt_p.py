# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import time
import config
import sql

def publish(topic, payload):  # Публикации топиков от telegram-бота
    client = mqtt.Client()
    client.username_pw_set(username=config.mqtt_username, password=config.mqtt_password)
    client.connect(host=config.mqtt_host, port=config.mqtt_port, keepalive=60)
    print("Connecting to broker for publish", config.mqtt_host)
    client.publish(topic, payload)
    time.sleep(0.3)
    client.publish(topic, payload)
    time.sleep(0.3)
    client.publish(topic, payload)
    sql.parametr_update(topic, payload)