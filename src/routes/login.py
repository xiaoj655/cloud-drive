from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from src import auth, db
from src.models import User, Response

router = APIRouter()

@router.post('/register')
async def post(form_data: OAuth2PasswordRequestForm = Depends()):
    return db.insert('User', {
        'name': form_data.username,
        'password': auth.hash_password(form_data.password)
    }, unique_key=['name'])

@router.post('/login')
async def post(form_data: OAuth2PasswordRequestForm = Depends()):
    if len(form_data.username) < 1:
        return Response(status_code=404)
    user = db.query_one('User', {'name': form_data.username})
    if not user:
        return Response(detail='无该用户', status_code=404)
    if auth.verify_password(form_data.password, user.password):
        return Response(data={"access_token": auth.create_access_token({"sub": user.name})})
    else:
        return Response(status_code=401)