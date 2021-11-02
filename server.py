#FastAPI server
import hmac
import hashlib
import base64
from typing import Optional

from fastapi import FastAPI, Form, Cookie
from fastapi.responses import Response
from starlette import responses

app = FastAPI()

SECRET_KEY = '6b3a8722e818a07e6675777c105d502845b1a96f6bef69da774d5cbb6cc944f7'
PASSWORD_SALT = '497166f192bc8629d7449cf8ad8ea371331ebc2df53b1ee485cf03db9279c3d9'

def sign_data(data: str) -> str:
    '''Возвращает подписанны данные data; use hashlib library'''
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest().upper()

def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    '''Возвращает валидный username из хэшированной cookie'''
    username_base64, sign = username_signed.split('.')
    username = base64.b64decode(username_base64.encode()).decode()
    valid_sign = sign_data(username)
    if hmac.compare_digest(valid_sign, sign):
        return username

def verify_password(username: str, password: str) -> bool:
    '''Проверяет соответствие хэшей пароля введенного и хранящегося в базе'''
    password_hash = hashlib.sha256( (password + PASSWORD_SALT).encode() )\
        .hexdigest().lower()     
    stored_password_hash = users[username]["password"].lower()
    return password_hash == stored_password_hash


'''Естественно, в продакшене все логины, хэши паролей и константы 
храним в базе данных, а её в переменном окружении. Здесь dict для примера'''
users = {
    "alex@user.com": {  # пароль для теста: some_password_1
        "name": "Алексей",
        "password": "ac214e34b71c2aa3ca80209e2d6e9a55e0f6a82a6652b13bedce957c010813c1",
        "balance": 100_000
    },
    "petr@user.com": {  # пароль для теста: some_password_2
        "name": "Петр",
        "password": "a69b64034ef30fc1bebd9dbb243791ab716039f55f02e8e6157d6d62713ccb6b",
        "balance": 555_555
    }
}

# проверяем cookie: есть - приветствуем, нет - ощищаем и на главную страницу
@app.get("/")  
def index_page(username: Optional[str] = Cookie(default=None)):
    with open('templates/login.html', 'r') as f:
        login_page = f.read()
    if not username:
        return Response(login_page, media_type="text/html")
    valid_username = get_username_from_signed_string(username)
    if not valid_username:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key="username")
        return response

    try:    #обрабатываем исключения, когда пользователь в базе не найден
        user = users[valid_username]
    except KeyError:
        response = Response(login_page, media_type="text/html")
        response.delete_cookie(key="username")
        return response           
    return Response(f"Привет, {users[valid_username]['name']}!", media_type="text/html")


#сохранена cookie или аутоидентификация пройдена - приветствуем, нет - "я вас незнаю!"
@app.post("/login")     
def process_login_page(username : str = Form(...), password : str = Form(...)):
    user = users.get(username)
    if not user or not verify_password(username, password):
        return Response("Я вас не знаю!", media_type="text/html")
    
    response = Response(
        f"Привет, {user['name']}!<br /> Баланс: {user['balance']}", 
        media_type='text/html')
    
    username_signed = base64.b64encode(username.encode()).decode() + "." + \
        sign_data(username)
    response.set_cookie(key="username", value=username_signed)
    return response
