import logging
import logging.handlers
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

import exceptions

EndPointError = exceptions.EndPointError
StatusTypeError = exceptions.StatusTypeError
SendMessageError = exceptions.SendMessageError

load_dotenv()
PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

# path = os.path.expanduser('~')
path = os.getcwd()
logging.basicConfig(
    level=logging.DEBUG,
    filename=os.path.join(path, 'main.log'),
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s'
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


def send_message(bot, message):
    """Отправка сообщения пользователю."""
    try:
        chat_id = TELEGRAM_CHAT_ID
        bot.send_message(chat_id=chat_id, text=message)
        logging.info('Успешная отправка сообщения')
    except SendMessageError as error:
        logging.error(f'Сбой при отправке сообщения: {error}')


def get_api_answer(current_timestamp):
    """Запрос к эндпоинту API сервиса."""
    try:
        timestamp = current_timestamp or int(time.time())
        if not isinstance(timestamp, (float, int)):
            raise EndPointError('Неверный формат даты')
        params = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code == 200:
            return response.json()
        if response.status_code == 404:
            raise EndPointError(f'Нет ответа API: {response.status_code}')
        else:
            response = response.json()
            answer_code = response.get('code')
            answer_error = response.get('error')
            if not answer_code:
                raise EndPointError(f'Нет ответа API: {answer_error}')
            else:
                raise EndPointError(f'Нет ответа API: {answer_code}')
    except EndPointError as error:
        raise(error)


def check_response(response):
    """Проверка ответа API на корректность."""
    if not isinstance(response, dict):
        raise TypeError('Неверный тип данных')
    hworks = response.get('homeworks')
    if not isinstance(hworks, list):
        raise TypeError('Неверный тип данных')
    if len(hworks) != 0:
        return hworks
    else:
        raise IndexError('Список пуст')


def parse_status(homework):
    """Определяет статус ревью."""
    if not isinstance(homework, dict):
        raise StatusTypeError('Ожидается словарь')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if not homework_name and homework_status:
        raise KeyError('Нет доступных ключей')
    else:
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверка наличия переменных окружения."""
    try:
        token = True
        if PRACTICUM_TOKEN is None:
            logging.critical(
            f'Нет обязательных переменных окружения: PRACTICUM_TOKEN')
            token = False
        if TELEGRAM_TOKEN is None:
            logging.critical(
            f'Нет обязательных переменных окружения: TELEGRAM_TOKEN')
            token = False
        if TELEGRAM_CHAT_ID is None:
            logging.critical(
            f'Нет обязательных переменных окружения: TELEGRAM_CHAT_ID')
            token = False
        return token
    except Exception as error:
        raise (f'Нет обязательных переменных окружения: {error}')


def send_message_error(error):
    """Отправка сообщения об ошибке."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    message = f'Сбой в работе программы: {error}'
    send_message(bot, message)


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    # current_timestamp = int(0)
    message_error = None
    if check_tokens() is False:
        raise logging.error('Ошибка токенов')
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            for hw in homework:
                message = parse_status(hw)
                send_message(bot, message)
                logger.debug('Бот работает')
                current_timestamp = response['current_date']

        except IndexError as error:
            logging.debug(f'Нет новых статусов: {error}')
            logger.debug('Бот работает')

        except (EndPointError,
                TypeError,
                StatusTypeError,
                KeyError) as error:
            logging.error(f'Сбой в работе программы: {error}')
            if message_error is None:
                send_message_error(error)
                message_error = error
        time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
