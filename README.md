Yatube.
Социальная сеть блогеров с возможностью добавлять и комментировать записи, создавать группы, подписываться на избранных авторов.

Локальный запуск проекта:
- Откройте терминал и перейдите в ту директорию, в которой будет располагаться проект.
- Выполните команду git clone https://github.com/RomanMelnikS/Yatube.git и дождитесь окончания загрузки проекта из
GitHub.
- Перейдите в корневую директорию проекта создайте виртуальное, активируйте виртуальное окружение и установите зависимости:
    - python -m venv 'venv'
    - source venv/Scripts/activate
    - pip install -r requirements.txt
- Выполните миграции, соберите статику и создайте суперпользователя:
  - python manage.py collectstatic
  - python manage.py makemigrations
  - python manage.py migrate
  - python manage.py createsuperuser
- Запустите проект:
  - python manage.py runserver

Готово!
