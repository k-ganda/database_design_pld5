from typing import List
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection setup
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = int(os.getenv("DB_PORT"))

db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=DB_PORT,
    connection_timeout=600
)
cursor = db.cursor()
app = FastAPI()

# Database schemas
class Device(BaseModel):
    device_model: str
    operating_system: str
    number_of_apps_installed: int

class AppUsage(BaseModel):
    app_usage_time: int
    screen_on_time: float
    battery_drain: float
    data_usage: float

class UserBehavior(BaseModel):
    user_behavior_class: int

class UserCreate(BaseModel):
    user_id: int
    age: int
    gender: str
    devices: List[Device]
    app_usage: List[AppUsage]
    user_behavior: UserBehavior

class UserResponse(UserCreate):
    pass

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate):
    # Insert User data
    cursor.execute("INSERT INTO users (UserID, Age, Gender) VALUES (%s, %s, %s)", (user.user_id, user.age, user.gender))
    db.commit()

    # Insert Devices data
    for device in user.devices:
        cursor.execute(
            "INSERT INTO devices (UserID, DeviceModel, OperatingSystem, NumberOfAppsInstalled) VALUES (%s, %s, %s, %s)",
            (user.user_id, device.device_model, device.operating_system, device.number_of_apps_installed)
        )
    db.commit()

    # Insert App Usage data
    for usage in user.app_usage:
        cursor.execute(
            "INSERT INTO appusage (UserID, AppUsageTime, ScreenOnTime, BatteryDrain, DataUsage) VALUES (%s, %s, %s, %s, %s)",
            (user.user_id, usage.app_usage_time, usage.screen_on_time, usage.battery_drain, usage.data_usage)
        )
    db.commit()

    # Insert User Behavior data
    cursor.execute(
        "INSERT INTO userbehavior (UserID, UserBehaviorClass) VALUES (%s, %s)",
        (user.user_id, user.user_behavior.user_behavior_class)
    )
    db.commit()

    return user

@app.get("/users/latest", response_model=UserResponse)
def get_latest_user():
    try:
        # Query to fetch the most recent user by user_id (assuming user_id is auto-incrementing)
        cursor.execute("SELECT UserID, Age, Gender FROM users ORDER BY UserID DESC LIMIT 1")
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(status_code=404, detail="No users found")
        
        # Initialize UserResponse with the basic user data
        user_response = UserResponse(
            user_id=user_data[0],
            age=user_data[1],
            gender=user_data[2],
            devices=[],  # Empty list for devices, will fetch data next
            app_usage=[],  # Empty list for app usage
            user_behavior=UserBehavior(user_behavior_class=0)  # Default valid instance
        )

        # Fetch the related devices data
        cursor.execute("SELECT DeviceModel, OperatingSystem, NumberOfAppsInstalled FROM devices WHERE UserID = %s", (user_data[0],))
        device_data = cursor.fetchall()
        user_response.devices = [
            Device(device_model=row[0], operating_system=row[1], number_of_apps_installed=row[2])
            for row in device_data
        ]
        
        # Fetch the related app usage data
        cursor.execute("SELECT AppUsageTime, ScreenOnTime, BatteryDrain, DataUsage FROM appusage WHERE UserID = %s", (user_data[0],))
        app_usage_data = cursor.fetchall()
        user_response.app_usage = [
            AppUsage(app_usage_time=row[0], screen_on_time=row[1], battery_drain=row[2], data_usage=row[3])
            for row in app_usage_data
        ]
        
        # Fetch the related user behavior data
        cursor.execute("SELECT UserBehaviorClass FROM userbehavior WHERE UserID = %s", (user_data[0],))
        user_behavior_data = cursor.fetchone()
        if user_behavior_data:
            user_response.user_behavior = UserBehavior(user_behavior_class=user_behavior_data[0])

        return user_response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving the latest user: {str(e)}")



@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    # Retrieve User data
    cursor.execute("SELECT UserID, Age, Gender FROM users WHERE UserID = %s", (user_id,))
    user_data = cursor.fetchone()
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Initialize UserResponse with default values
    user_response = UserResponse(
        user_id=user_data[0],
        age=user_data[1],
        gender=user_data[2],
        devices=[],  # Empty list for devices
        app_usage=[],  # Empty list for app_usage
        user_behavior=UserBehavior(user_behavior_class=0)  # Default valid instance of UserBehavior
    )

    # Retrieve Device data
    cursor.execute("SELECT DeviceModel, OperatingSystem, NumberOfAppsInstalled FROM devices WHERE UserID = %s", (user_id,))
    device_data = cursor.fetchall()
    user_response.devices = [
        Device(device_model=row[0], operating_system=row[1], number_of_apps_installed=row[2])
        for row in device_data
    ]

    # Retrieve App Usage data
    cursor.execute("SELECT AppUsageTime, ScreenOnTime, BatteryDrain, DataUsage FROM appusage WHERE UserID = %s", (user_id,))
    app_usage_data = cursor.fetchall()
    user_response.app_usage = [
        AppUsage(app_usage_time=row[0], screen_on_time=row[1], battery_drain=row[2], data_usage=row[3])
        for row in app_usage_data
    ]

    # Retrieve User Behavior data
    cursor.execute("SELECT UserBehaviorClass FROM userbehavior WHERE UserID = %s", (user_id,))
    user_behavior_data = cursor.fetchone()
    if user_behavior_data:
        user_response.user_behavior = UserBehavior(user_behavior_class=user_behavior_data[0])
    

    return user_response

@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate):
    # Check if the user exists
    cursor.execute("SELECT UserID FROM users WHERE UserID = %s", (user_id,))
    existing_user = cursor.fetchone()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update User data
    cursor.execute(
        "UPDATE users SET Age = %s, Gender = %s WHERE UserID = %s",
        (user.age, user.gender, user_id)
    )

    # Update Devices data
    for device in user.devices:
        cursor.execute(
            "UPDATE devices SET DeviceModel = %s, OperatingSystem = %s, NumberOfAppsInstalled = %s WHERE UserID = %s",
            (device.device_model, device.operating_system, device.number_of_apps_installed, user_id)
        )

    # Update App Usage data
    for usage in user.app_usage:
        cursor.execute(
            "UPDATE appusage SET AppUsageTime = %s, ScreenOnTime = %s, BatteryDrain = %s, DataUsage = %s WHERE UserID = %s",
            (usage.app_usage_time, usage.screen_on_time, usage.battery_drain, usage.data_usage, user_id)
        )

    # Update User Behavior data
    cursor.execute(
        "UPDATE userbehavior SET UserBehaviorClass = %s WHERE UserID = %s",
        (user.user_behavior.user_behavior_class, user_id)
    )
    
    db.commit()

    return user


@app.delete("/users/{user_id}", response_model=dict)
def delete_user(user_id: int):
    # Check if the user exists
    cursor.execute("SELECT UserID FROM users WHERE UserID = %s", (user_id,))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    
    cursor.execute("DELETE FROM devices WHERE UserID = %s", (user_id,))
    cursor.execute("DELETE FROM appusage WHERE UserID = %s", (user_id,))
    cursor.execute("DELETE FROM userbehavior WHERE UserID = %s", (user_id,))

    # Delete from the Users table
    cursor.execute("DELETE FROM users WHERE UserID = %s", (user_id,))
    db.commit()

    return {"message": f"User with ID {user_id} and all related data have been deleted"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
