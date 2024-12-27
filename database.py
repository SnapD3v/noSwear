import datetime as dt
import os
from config import *


def time_now():
    return (dt.datetime.utcnow() + dt.timedelta(hours=5)).strftime("%H:%M:%S")


def ExceptionHandler(exception):
    print(f'\n---\n'
          f'[{time_now()}] Возникла ошибка! [database.py]\n'
          f'[Type]: {type(exception)}\n'
          f'[Exception Context]: {exception.__context__}\n'
          f'[Exception Cause]: {exception.__cause__}\n'
          f'[Exception Suppress Context]: {exception.__suppress_context__}\n'
          f'---\n')


def open_db():
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            db_users = json.load(f)
        return db_users
    except Exception as error:
        ExceptionHandler(error)


def save_db(db_users):
    try:
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(db_users, f, ensure_ascii=False, indent=4)
        return
    except Exception as error:
        ExceptionHandler(error)


def check_user_id_in_db(user_id: int):
    try:
        db = open_db()
        return f'{user_id}' in db
    except Exception as error:
        ExceptionHandler(error)


def create_user_data(user_id: int):
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
    except Exception as error:
        ExceptionHandler(error)


def edit_user_data(user_id: int, data: str, value):
    try:
        db = open_db()
        if check_user_id_in_db(user_id):
            db[f'{user_id}'][data] = value
            save_db(db)
            return True
        else:
            create_user_data(user_id)
            edit_user_data(user_id, data, value)
    except Exception as error:
        ExceptionHandler(error)


def edit_user_current_task(user_id: int, data: str, value):
    try:
        db = open_db()
        data_list = [
            'format',  # Формат файла ( Аудио / Видео )
            'ban_list',  # Какой список запрещенных слов использовать ( default / own )
            'word_list',  # Если кастомный список, то слова записываются сюда (list)
            'file_path',  # Путь к папке, где расположен файл юзера ( files/.../ )
            'file_extension'  # расширение файла (напр. - .mp4)
        ]
        if data in data_list:
            db[f'{user_id}'][f'current_task'][data] = value
        else:
            return False
        save_db(db)
    except Exception as error:
        ExceptionHandler(error)


def get_user_task_detail(user_id: int, data: str):
    try:
        db = open_db()
        return db[f'{user_id}'][f'current_task'][data]
    except Exception as error:
        ExceptionHandler(error)


def is_exist_user_task_detail(user_id: int, data: str):
    try:
        db = open_db()
        return True if data in db[f'{user_id}']['current_task'] else False
    except Exception as error:
        ExceptionHandler(error)


def clear_user_current_files(user_id: int, folder) -> None:
    try:
        path = f'files/{folder}/'
        for file_name in os.listdir(path):
            if str(user_id) in file_name:
                os.remove(path+file_name)
    except Exception as error:
        ExceptionHandler(error)


def reset_user_task(user_id: int) -> None:
    edit_user_data(user_id, 'current_task', {})
    clear_user_current_files(user_id, 'filtered')
    clear_user_current_files(user_id, 'non_filtered')