from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import uvicorn
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

class AppUsage(BaseModel):
    app_usage_id: int
    user_id: int
    app_usage_time: int
    screen_on_time: float
    battery_drain: float
    data_usage: float

class UserBehavior(BaseModel):
    behavior_id: int
    user_id: int
    user_behavior_class: int

# Create (POST)
@app.post("/users/", response_model=User)
def create_user(user: User):
    cursor.execute("INSERT INTO Users (UserID, Age, Gender) VALUES (%s, %s, %s)", (user.user_id, user.age, user.gender))
    db.commit()
    return user

@app.post("/devices/", response_model=Device)
def create_device(device: Device):
    cursor.execute("INSERT INTO Devices (UserID, DeviceModel, OperatingSystem, NumberOfAppsInstalled) VALUES (%s, %s, %s, %s)", (device.user_id, device.device_model, device.operating_system, device.number_of_apps_installed))
    db.commit()
    device.device_id = cursor.lastrowid
    return device

@app.post("/app-usage/", response_model=AppUsage)
def create_app_usage(app_usage: AppUsage):
    cursor.execute("INSERT INTO AppUsage (UserID, AppUsageTime, ScreenOnTime, BatteryDrain, DataUsage) VALUES (%s, %s, %s, %s, %s)", (app_usage.user_id, app_usage.app_usage_time, app_usage.screen_on_time, app_usage.battery_drain, app_usage.data_usage))
    db.commit()
    app_usage.app_usage_id = cursor.lastrowid
    return app_usage

@app.post("/user-behavior/", response_model=UserBehavior)
def create_user_behavior(user_behavior: UserBehavior):
    cursor.execute("INSERT INTO UserBehavior (UserID, UserBehaviorClass) VALUES (%s, %s)", (user_behavior.user_id, user_behavior.user_behavior_class))
    db.commit()
    user_behavior.behavior_id = cursor.lastrowid
    return user_behavior

# Read (GET)
@app.get("/users/", response_model=List[User])
def get_all_users():
    cursor.execute("SELECT * FROM Users")
    rows = cursor.fetchall()
    return [User(user_id=row[0], age=row[1], gender=row[2]) for row in rows]

@app.get("/devices/", response_model=List[Device])
def get_all_devices():
    cursor.execute("SELECT * FROM Devices")
    rows = cursor.fetchall()
    return [Device(device_id=row[0], user_id=row[1], device_model=row[2], operating_system=row[3], number_of_apps_installed=row[4]) for row in rows]

@app.get("/app-usage/", response_model=List[AppUsage])
def get_all_app_usage():
    cursor.execute("SELECT * FROM AppUsage")
    rows = cursor.fetchall()
    return [AppUsage(app_usage_id=row[0], user_id=row[1], app_usage_time=row[2], screen_on_time=row[3], battery_drain=row[4], data_usage=row[5]) for row in rows]

@app.get("/user-behavior/", response_model=List[UserBehavior])
def get_all_user_behavior():
    cursor.execute("SELECT * FROM UserBehavior")
    rows = cursor.fetchall()
    return [UserBehavior(behavior_id=row[0], user_id=row[1], user_behavior_class=row[2]) for row in rows]

# Update (PUT)
@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user: User):
    cursor.execute("UPDATE Users SET Age = %s, Gender = %s WHERE UserID = %s", (user.age, user.gender, user_id))
    db.commit()
    if cursor.rowcount > 0:
        return User(user_id=user_id, age=user.age, gender=user.gender)
    else:
        raise HTTPException(status_code=404, detail="User not found")

# Delete (DELETE)
@app.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int):
    cursor.execute("DELETE FROM Users WHERE UserID = %s", (user_id,))
    db.commit()
    if cursor.rowcount > 0:
        return {"message": "User deleted"}
    else:
        raise HTTPException(status_code=404, detail="User not found")
    
# if __name__ == "__main__":
#     uvicorn.run(
#         "app:app",  # Change 'main' to the new filename without '.py'
#         host="0.0.0.0",
#         port=8765,
#         log_level="debug",
#         reload=True,
#     )
        