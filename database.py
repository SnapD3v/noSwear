import json
import datetime as dt
import os


def time_now():
    return (dt.datetime.utcnow() + dt.timedelta(hours=5)).strftime("%H:%M:%S")


def ExceptionHandler(exception):
    print(f'[{time_now()}] Возникла ошибка!')
    print(exception)
    print('---')


def open_db():
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            db_users = json.load(f)
        return db_users
    except Exception as e:
        ExceptionHandler(e)


def save_db(db_users):
    try:
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(db_users, f, ensure_ascii=False, indent=4)
        return
    except Exception as e:
        ExceptionHandler(e)


def check_user_id_in_db(user_id):
    try:
        db = open_db()
        return f'{user_id}' in db
    except Exception as e:
        ExceptionHandler(e)


def create_user_data(user_id):
    try:
        db = open_db()
        if not check_user_id_in_db(user_id):
            db[f'{user_id}'] = {}
            db[f'{user_id}']['tasks_done'] = 0
            db[f'{user_id}']['tokens'] = 0
            db[f'{user_id}']['current_task'] = {}
            save_db(db)
            return True
        return False
    except Exception as e:
        ExceptionHandler(e)


def edit_user_data(user_id, data: str, value):
    try:
        db = open_db()
        if check_user_id_in_db(user_id):
            db[f'{user_id}'][data] = value
            save_db(db)
            return True
        else:
            create_user_data(user_id)
            edit_user_data(user_id, data, value)
    except Exception as e:
        ExceptionHandler(e)


def edit_user_current_task(user_id, data: str, value):
    try:
        db = open_db()
        data_list = [
            'format',  # Формат файла ( Аудио / Видео )
            'ban_list',  # Какой список запрещенных слов использовать ( default / own )
            'word_list',  # Если кастомный список, то слова записываются сюда (list)
            'effect',  # Эффект для цензуры (напр. - Тишина)
            'file_path',  # Путь к папке, где расположен файл юзера ( files/.../ )
            'file_extension'  # расширение файла (напр. - .mp4)
        ]
        if data in data_list:
            db[f'{user_id}'][f'current_task'][data] = value
        else:
            return False
        save_db(db)
    except Exception as e:
        ExceptionHandler(e)


def get_user_current_task(user_id, data: str):
    try:
        db = open_db()
        return db[f'{user_id}'][f'current_task'][data]
    except Exception as e:
        ExceptionHandler(e)


def clear_user_current_files(user_id, folder):
    try:
        extensions = ['mp3', 'wav', 'mp4', 'avi']
        for extension in extensions:
            path = f'files/{folder}/{user_id}.{extension}'
            if os.path.exists(path):
                os.remove(path)
    except Exception as e:
        ExceptionHandler(e)
