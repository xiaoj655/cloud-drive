import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import datetime
import jwt
from jwt.exceptions import PyJWTError
import os
from src.models import Response

SECRET = os.environ.get('JWT_SECRET')
ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
def verify_password(plain_pwd: str | bytes, hashed_pwd: bytes):
    if not isinstance(plain_pwd, bytes):
        try:
            plain_pwd = plain_pwd.encode('utf-8')
        except Exception as e:
            print(f"check pass in plain_pwd argument, should be bytes or str type, but it's {type(plain_pwd)} and value is {plain_pwd}")
            print(e)
            return
    return bcrypt.checkpw(plain_pwd, hashed_pwd)

def hash_password(plain_pwd: str, salt: bytes = bcrypt.gensalt()):
    plain_pwd = plain_pwd.encode('utf-8')
    return bcrypt.hashpw(plain_pwd, salt)

def create_access_token(data: dict, expire_delta: datetime.timedelta = datetime.timedelta(hours=12)):
    expire_time = datetime.datetime.now() + expire_delta
    to_encode = data.copy()
    to_encode.update({"exp": expire_time})
    print(123,SECRET)
    return jwt.encode(to_encode, SECRET, algorithm='HS256')

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET, algorithms=['HS256'])
        return payload
    except PyJWTError:
        return Response(status_code=401)
    except Exception:
        return Response(status_code=500, detail='联系管理员, 服务器错误')

def get_identity(token: str):
    return decode_token(token)['sub']