from jose import jwt
from fastapi.security import OAuth2PasswordBearer
from typing import Union
from datetime import datetime, timedelta

from config import setting

SECRET_KEY = setting.secret_key
ALGORITHM = setting.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = setting.timeout

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# TODO: Not used anywhere but useful code
# def verify_token(token:str, cred_exception):
#     # try:
#         payload = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])
#         print(payload)
#         user_id = payload.get('user_id')
#         company_id =  payload.get('company_id')
#         # if user_id is None:
#         #     raise cred_exception
#         return TokenData(user_id=user_id,company_id=company_id)
#     # except:
#     #     raise cred_exception


# TODO: Not used anywhere but useful code
# def get_current_user(token:str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
#     cred_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Credentials can not be verified', headers={"WWW-Authenticate": "Bearer"})
#     token = verify_token(token, cred_exception)
#     logged_in_usr = db.query(User).filter(User.id == token.user_id).first()
#     return logged_in_usr
