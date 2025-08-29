import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from dotenv import load_dotenv
load_dotenv() #load env variables, reads .env makes values available via os.getenv
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret") #to sign/verify jwt
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 #how long token stays valid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #configure passlib to use bcrypt hashing algo, passlib will warn if algo becomes outdated

def hash_password(password: str) -> str:  #takes raw pasww and returns a bcrypt hash
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:  #compare raw passw w stored hash return true if they match
    return pwd_context.verify(password, hashed)

def create_access_token(subject: str) -> str:  #jwt creation, input is subject- email, userid
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) #encodes and signs token with secret key returns a compact jwt string

def decode_token(token: str) -> dict:   ##verify token signature w secret key, raises error if ivalid 
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) 
# returns the decoded payload a dict "sub" - who the token belogs to and "exp" expiry timestamp