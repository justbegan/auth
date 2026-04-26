## Требования
Перед началом работы убедитесь, что у вас установлены следующие зависимости:  
- Python 3.11+  
- Django 5.1+  
- PostgreSQL 16  


## Установка
1. Клонируйте репозиторий:  
   git clone <URL-репозитория>  
   cd <название-проекта>

2. Создайте виртуальное окружение и активируйте его:  
    python -m venv venv  
    Для Linux: source venv/bin/activate  
    Для Windows: venv\Scripts\activate  

3. Установите зависимости:  
    pip install -r requirements.txt

4. Создайте .env файл в корневой директории из example.env:  

5. Добавить приложение(кастомное, под эту структуру):  
    python .\manage.py create_app <приложение>  

6. Выполните миграции базы данных:  
    python manage.py migrate  

7. Создание суперпользователя:  
    python manage.py createsuperuser  

8. Запустите сервер:  
    python manage.py runserver  


## Использование
Swagger(Доступен только в debug режиме):  
    http://127.0.0.1:8000/api/docs  

Админ панель:  
    http://127.0.0.1:8000/api/admin  

## Тестирование
python manage.py test apps  


## Структура проекта
/main_app - корневой каталог проекта  
/apps/* - приложения  
/core - общее (базовое) приложение проекта  


## Структурное описание модулей и файлов
используется шаблон «Service Layer»  
project/  
│── apps/  
│   │── my_app/  
│   │   ├── models.py              # Модели (структура БД)  
│   │   ├── signals.py             # Django сигналы  
│   │   ├── admin.py               # Django админ  
│   │   ├── services.py            # общие сервисы  
│   │   │  
│   │   └── api/  
│   │       └── v1/  
│   │           ├── views.py       # Обработка HTTP-запросов (API слой)  
│   │           ├── serializers.py # Контракт API (что отдаём/принимаем)  
│   │           ├── services.py    # Сервисы API (что отдаём/принимаем)  
│   │           └── urls.py        # Маршруты API v1  
│  
│── docker-compose.yml             # основной docker-compose файл  
│── dockerfile                     # основной docker файл  
│── start.sh                       # скрипт запуска контейнеров  
│── .gitlab-ci.yml                 # CI/CD конфигурация  


## Стиль написания кода
переменные и методы - snake_case (user_name)  
классы - PascalCase (UserProfile)  


## Проверка кода
Используется библиотека flake8(добавлен в requirements.txt)  
конфиг файл .flake8  
запуск ./flake8  