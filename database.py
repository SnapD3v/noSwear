import json
import datetime as dt
import os


def time_now():
    return (dt.datetime.utcnow() + dt.timedelta(hours=5)).strftime("%H:%M:%S")


def ExceptionHandler(exception):
    print(f'[{time_now()}]')
    print(type(exception))
    print(exception)
    print('\n')


def open_db():
    try:
        with open('noSwear/users.json', 'r', encoding='utf-8') as f:
            db_users = json.load(f)
        return db_users
    except Exception as e:
        ExceptionHandler(e)


def save_db(db_users):
    try:
        with open('noSwear/users.json', 'w', encoding='utf-8') as f:
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


def edit_user_data(user_id, data, value):
    try:
        db = open_db()
        if check_user_id_in_db(user_id):
            db[f'{user_id}'][f'{data}'] = value
            save_db(db)
            return True
        else:
            create_user_data(user_id)
            edit_user_data(user_id, data, value)
    except Exception as e:
        ExceptionHandler(e)


def edit_user_current_task(user_id, data, value):
    try:
        db = open_db()
        if data == 'format':
            db[f'{user_id}'][f'current_task']['format'] = value
        elif data == 'ban_list':
            db[f'{user_id}'][f'current_task']['ban_list'] = value
        elif data == 'word_list':
            db[f'{user_id}'][f'current_task']['word_list'] = value
        elif data == 'effect':
            db[f'{user_id}'][f'current_task']['effect'] = value
        elif data == 'file_exist':
            db[f'{user_id}'][f'current_task']['file_exist'] = value
        else:
            return False
        save_db(db)
    except Exception as e:
        ExceptionHandler(e)


def get_user_current_task(user_id, data):
    db = open_db()
    return db[f'{user_id}'][f'current_task'][f'{data}']


def clear_user_current_files(user_id):
    if os.path.exists(f'noSwear/files/non_filtered/{user_id}.mp3'):
        os.remove(f'noSwear/files/non_filtered/{user_id}.mp3')
    elif os.path.exists(f'noSwear/files/non_filtered/{user_id}.mp4'):
        os.remove(f'noSwear/files/non_filtered/{user_id}.mp4')
    elif os.path.exists(f'noSwear/files/non_filtered/{user_id}.wav'):
        os.remove(f'noSwear/files/non_filtered/{user_id}.wav')