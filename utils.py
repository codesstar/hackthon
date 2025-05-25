from flask_jwt_extended import create_access_token
from datetime import timedelta
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def create_token(identity):
    return create_access_token(identity=identity, expires_delta=timedelta(days=7))