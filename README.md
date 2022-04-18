## homework_bot
# Описание 
Телеграм бот для получения уведомлений о статусе проверки домашней работы. 
# Функционал
Делает запрос к API Яндекс Практикум каждые 10 минут. При изменении статуса проверки проекта отправляет сообщение. Подключены логи (модуль logging). 
> Ход работы программы: 
> > - Проверка наличия переменных окружения (tokens)
> > - Запрос к эндпоинту API сервиса
> > - Проверка ответа API на корректность
> > - Определение статуса ревью
> > - Отправка сообщения 
# Технологии 
Python
# Автор 
Ilia Iliukhin
