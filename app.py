from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mysql.connector import pooling, errors
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the database connection details from environment variables
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = int(os.getenv("DB_PORT"))

# Database connection pool setup
db_config = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME,
    "port": DB_PORT,
    "connection_timeout": 600
}

db_pool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **db_config)

# Function to get a database connection
def get_db_connection():
    try:
        return db_pool.get_connection()
    except errors.PoolError:
        raise HTTPException(status_code=500, detail="Database connection pool is full.")

app = FastAPI()

# Models for request validation and response schemas
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

class AppUsage(BaseModel):
    app_usage_id: int
    user_id: int
    app_usage_time: int
    screen_on_time: float
    battery_drain: float
    data_usage: float

class UserBehavior(BaseModel):
    behavior_id: int = None  # Set to None initially, will be set after DB insert
    user_id: int
    user_behavior_class: int

# Endpoint: Create User (POST)
@app.post("/users/", response_model=User)
def create_user(user: User):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (UserID, Age, Gender) VALUES (%s, %s, %s)", (user.user_id, user.age, user.gender))
        db.commit()
        return user
    except errors.DatabaseError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to insert user")
    finally:
        cursor.close()
        db.close()

# Endpoint: Create Device (POST)
@app.post("/devices/", response_model=Device)
def create_device(device: Device):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO devices (UserID, DeviceModel, OperatingSystem, NumberOfAppsInstalled) VALUES (%s, %s, %s, %s)", 
                       (device.user_id, device.device_model, device.operating_system, device.number_of_apps_installed))
        db.commit()
        device.device_id = cursor.lastrowid
        return device
    except errors.DatabaseError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to insert device")
    finally:
        cursor.close()
        db.close()

# Endpoint: Create App Usage (POST)
@app.post("/app-usage/", response_model=AppUsage)
def create_app_usage(app_usage: AppUsage):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO appusage (UserID, AppUsageTime, ScreenOnTime, BatteryDrain, DataUsage) VALUES (%s, %s, %s, %s, %s)", 
                       (app_usage.user_id, app_usage.app_usage_time, app_usage.screen_on_time, app_usage.battery_drain, app_usage.data_usage))
        db.commit()
        app_usage.app_usage_id = cursor.lastrowid
        return app_usage
    except errors.DatabaseError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to insert app usage data")
    finally:
        cursor.close()
        db.close()

# Endpoint: Create User Behavior (POST)
@app.post("/user-behavior/", response_model=UserBehavior)
def create_user_behavior(user_behavior: UserBehavior):
    with get_db_connection() as db:
        with db.cursor() as cursor:
            try:
                cursor.execute(
                    """INSERT INTO userbehavior 
                       (UserID, UserBehaviorClass) 
                       VALUES (%s, %s)""",
                    (user_behavior.user_id, user_behavior.user_behavior_class)
                )
                db.commit()
                user_behavior.behavior_id = cursor.lastrowid
                return user_behavior
            except MySQLError as e:
                db.rollback()
                if "foreign key constraint fails" in str(e):
                    raise HTTPException(
                        status_code=400,
                        detail="UserID does not exist in the users table."
                    )
                raise HTTPException(
                    status_code=500,
                    detail=f"Database error occurred: {str(e)}"
                )

# Endpoint: Get All Users (GET)
@app.get("/users/", response_model=List[User])
def get_all_users():
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return [User(user_id=row[0], age=row[1], gender=row[2]) for row in rows]
    except errors.DatabaseError:
        raise HTTPException(status_code=500, detail="Failed to fetch users")
    finally:
        cursor.close()
        db.close()

# Endpoint: Get All Devices (GET)
@app.get("/devices/", response_model=List[Device])
def get_all_devices():
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM devices")
        rows = cursor.fetchall()
        return [Device(device_id=row[0], user_id=row[1], device_model=row[2], operating_system=row[3], number_of_apps_installed=row[4]) for row in rows]
    except errors.DatabaseError:
        raise HTTPException(status_code=500, detail="Failed to fetch devices")
    finally:
        cursor.close()
        db.close()

# Endpoint: Get All App Usage Data (GET)
@app.get("/app-usage/", response_model=List[AppUsage])
def get_all_app_usage():
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM appusage")
        rows = cursor.fetchall()
        return [AppUsage(app_usage_id=row[0], user_id=row[1], app_usage_time=row[2], screen_on_time=row[3], battery_drain=row[4], data_usage=row[5]) for row in rows]
    except errors.DatabaseError:
        raise HTTPException(status_code=500, detail="Failed to fetch app usage data")
    finally:
        cursor.close()
        db.close()

# Endpoint: Get All User Behaviors (GET)
@app.get("/user-behavior/", response_model=List[UserBehavior])
def get_all_user_behavior():
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM userbehavior")
        rows = cursor.fetchall()
        return [UserBehavior(behavior_id=row[0], user_id=row[1], user_behavior_class=row[2]) for row in rows]
    except errors.DatabaseError:
        raise HTTPException(status_code=500, detail="Failed to fetch user behavior data")
    finally:
        cursor.close()
        db.close()

# Endpoint: Update User (PUT)
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: User):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("UPDATE users SET Age = %s, Gender = %s WHERE UserID = %s", (user.age, user.gender, user_id))
        db.commit()
        if cursor.rowcount > 0:
            return User(user_id=user_id, age=user.age, gender=user.gender)
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except errors.DatabaseError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update user")
    finally:
        cursor.close()
        db.close()

# Endpoint: Delete User (DELETE)
@app.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE UserID = %s", (user_id,))
        db.commit()
        if cursor.rowcount > 0:
            return {"message": "User deleted"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except errors.DatabaseError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete user")
    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
