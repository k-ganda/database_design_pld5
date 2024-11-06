from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT

# Database connection
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=DB_PORT
)
cursor = db.cursor()

app = FastAPI()
class User(BaseModel):
    user_id: int
    age: int
    gender: str

class Device(BaseModel):
    device_id: int
    user_id: int
    device_model: str
    operating_system: str
    number_of_apps_installed: int
