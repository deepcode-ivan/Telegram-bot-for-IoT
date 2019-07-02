import subprocess
import tempfile
import os
import xml.etree.ElementTree as XmlElementTree
import httplib2
import uuid
from config import YANDEX_API_KEY

# Перекодирование в PCM 16000 Гц 16 бит
def convert_to_pcm16b16000r(in_filename=None, in_bytes=None):
    with tempfile.TemporaryFile() as temp_out_file:
        temp_in_file = None
        if in_bytes:
            temp_in_file = tempfile.NamedTemporaryFile(delete=False)
            temp_in_file.write(in_bytes)
            in_filename = temp_in_file.name
            temp_in_file.close()
        if not in_filename:
            raise Exception('Neither input file name nor input bytes is specified.')

        # Запрос в командную строку для обращения к FFmpeg
        command = [
            r'bin\ffmpeg.exe',  # путь до ffmpeg.exe
            '-i', in_filename,
            '-f', 's16le',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-'
        ]

        proc = subprocess.Popen(command, stdout=temp_out_file, stderr=subprocess.DEVNULL)
        proc.wait()

        if temp_in_file:
            os.remove(in_filename)

        temp_out_file.seek(0)
        return temp_out_file.read()

# Передача аудиозаписи по частям
def read_chunks(chunk_size, bytes):
    while True:
        chunk = bytes[:chunk_size]
        bytes = bytes[chunk_size:]

        yield chunk

        if not bytes:
            break

# Отправка запроса к Yandex API и парсинг ответа
YANDEX_ASR_HOST = 'asr.yandex.net'
YANDEX_ASR_PATH = '/asr_xml'
CHUNK_SIZE = 1024 ** 2

def speech_to_text(filename=None, bytes=None, request_id=uuid.uuid4().hex, topic='notes', lang='ru-RU',
                   key=YANDEX_API_KEY):
    # Если передан файл
    if filename:
        with open(filename, 'br') as file:
            bytes = file.read()
    if not bytes:
        raise Exception('Neither file name nor bytes provided.')

    # Конвертирование в нужный формат
    bytes = convert_to_pcm16b16000r(in_bytes=bytes)

    # print('bytes', bytes)

    # Формирование тела запроса к Yandex API
    url = YANDEX_ASR_PATH + '?uuid=%s&key=%s&topic=%s&lang=%s' % (
        request_id,
        key,
        topic,
        lang
    )

    # Считывание блока байтов
    chunks = read_chunks(CHUNK_SIZE, bytes)

    # Установление соединения и формирование запроса
    connection = httplib2.HTTPConnectionWithTimeout(YANDEX_ASR_HOST)

    # print('connection', connection)

    connection.connect()
    connection.putrequest('POST', url)
    connection.putheader('Transfer-Encoding', 'chunked')
    connection.putheader('Content-Type', 'audio/x-pcm;bit=16;rate=16000')
    connection.endheaders()

    # Отправка байтов блоками
    for chunk in chunks:
        connection.send(('%s\r\n' % hex(len(chunk))[2:]).encode())
        connection.send(chunk)
        connection.send('\r\n'.encode())

    connection.send('0\r\n\r\n'.encode())
    response = connection.getresponse()

    # Обработка ответа сервера
    # print('response.code -- ', response.code)
    if response.code == 200:
        response_text = response.read()
        xml = XmlElementTree.fromstring(response_text)

        if int(xml.attrib['success']) == 1:
            max_confidence = - float("inf")
            text = ''

            for child in xml:
                if float(child.attrib['confidence']) > max_confidence:
                    text = child.text
                    max_confidence = float(child.attrib['confidence'])

            if max_confidence != - float("inf"):
                return text

            else:
                print('No text found.')
        else:
            print('No text found.')
    else:
        print('Unknown error.')

