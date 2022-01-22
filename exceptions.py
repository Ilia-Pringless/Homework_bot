class EndPointError(Exception):
    """Ошибка доступа эндпоинта."""

    pass


class StatusTypeError(Exception):
    """Неверный тип данных для parse_status."""

    pass


class SendMessageError(Exception):
    """Неудалось отправить сообщение."""

    pass


class TokenError(Exception):
    """Отсутствие обязательных переменных окружения."""

    pass
