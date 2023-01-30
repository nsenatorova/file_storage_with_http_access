import hashlib
import os
from datetime import datetime
from functools import wraps

from flask import Flask, request, send_file, abort

UPLOAD_FOLDER = 'store\\'
LOG_FILE = 'log.txt'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['LOG_FILE'] = LOG_FILE


def check_auth(username, password):
    """
    Проверка авторизации
    """
    return (username == 'first_user' and password == 'first_password') or \
           (username == 'second_user' and password == 'second_password')


def login_required(f):
    """
    Декоратор для авторизации
    """

    @wraps(f)
    def wrapped_view(**kwargs):
        auth = request.authorization
        if not (auth and check_auth(auth.username, auth.password)):
            return 'Unauthorized', 401
        return f(**kwargs)

    return wrapped_view


def find_file(filename):
    """
    Поиск файла по директориям
    """
    result = []
    search_path = os.path.dirname(__file__)
    for root, directory, files in os.walk(search_path):
        if filename in files:
            result.append(os.path.join(root, filename))
    return result


@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """
    Загрузка файла авторизованным пользователем
    """
    if 'file' not in request.files:
        return 'There is no file!', 400
    uploaded_file = request.files['file']
    hasher = hashlib.new('sha256')
    content = uploaded_file.read()
    hasher.update(content)
    hash_name = hasher.hexdigest()
    hash_dir = str(hash_name)[0:2]
    directory = os.path.join(os.path.dirname(__file__), app.config['UPLOAD_FOLDER'], hash_dir)
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = os.path.join(directory, hash_name)
    uploaded_file.save(path)
    with open(path, 'wb') as file:
        file.write(content)
    if not os.path.exists(path):
        abort(404)
    else:
        with open(app.config['LOG_FILE'], 'a', encoding='utf-8') as log_file:
            log_file.write(f"{datetime.now()}: {hash_name} "
                           f"uploaded by {request.authorization.username}\n")
            log_file.close()
        return f"Uploaded file's hash: {hash_name}, file uploaded by " \
               f"{request.authorization.username}", 201


@app.route('/download', methods=['POST'])
def download_file():
    """
    Загрузка файла для любого пользователя
    """
    jdata = request.get_json()
    hash_name = str(jdata['hash_name'])
    result = find_file(hash_name)
    if result:
        return send_file(result[0])
    return 'Not found', 404


@app.route('/delete', methods=['POST'])
@login_required
def delete_file():
    """
    Удаление файла из директории. Перед удалением с помощью лога проверяется,
    тот ли пользователь добавлял файл изначально
    """
    jdata = request.get_json()
    hash_name = str(jdata['hash_name'])
    result = find_file(hash_name)
    if result:
        file_not_found_in_info = True
        with open(app.config['LOG_FILE'], 'r+', encoding='utf-8') as log_file:
            for line in log_file:
                if hash_name in line and request.authorization.username in line:
                    file_not_found_in_info = False
                    os.remove(result[0])
                    log_file.write(f"{datetime.now()}: {hash_name} "
                                   f"deleted by {request.authorization.username}\n")
                    log_file.close()
                    return f'File has been deleted (hash: {hash_name})', 200
        if file_not_found_in_info:
            return 'File was initially uploaded by another user', 403
    else:
        return 'Not found', 404


if __name__ == '__main__':
    app.run()
