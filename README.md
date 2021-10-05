# Yatube.
Социальная сеть блогеров с возможностью добавлять и комментировать записи, создавать группы, подписываться на избранных авторов.

## Зависимости:
- Python3
- Django
- Bootstrap4

## Локальный запуск проекта.
1. Откройте терминал и перейдите в ту директорию, в которой будет располагаться проект.
2. Склонируйте проект к себе на машину:
```python
git clone https://github.com/RomanMelnikS/Yatube.git
```
3. Перейдите в корневую директорию проекта создайте виртуальное, активируйте виртуальное окружение и установите зависимости:
```python
python -m venv 'venv'
source venv/Scripts/activate
pip install -r requirements.txt
```
4. Выполните миграции, соберите статику и создайте суперпользователя:
```python
python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```
5. Запустите проект:
```python
python manage.py runserver
```

Готово!
