-- Creates the database(schema)
CREATE SCHEMA app_user_behavior;
-- Switch to this to perform queries
USE app_user_behavior;

-- Creates a temporary table that will hold the data from csv file
CREATE TABLE Tempdata (
    UserID INT,
    DeviceModel VARCHAR(50),
    OperatingSystem VARCHAR(20),
    AppUsageTime INT,
    ScreenOnTime DECIMAL(4,2),
    BatteryDrain DECIMAL(7,3),
    NumberOfAppsInstalled INT,
    DataUsage DECIMAL(6,2),
    Age INT,
    Gender VARCHAR(10),
    UserBehaviorClass INT
);

-- This enables loading of data from local files
SET GLOBAL local_infile = 1;

-- Loads the data from a local CSV file into the Tempdata table,
-- ignoring the first row(header) and mapping columns to table fields
LOAD DATA LOCAL INFILE 'C:/Users/Administrator/OneDrive/Documents/user_behavior_data.csv'
INTO TABLE Tempdata
FIELDS TERMINATED BY ',' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(UserID, DeviceModel, OperatingSystem, AppUsageTime, ScreenOnTime, BatteryDrain
, NumberOfAppsInstalled, DataUsage, Age, Gender, UserBehaviorClass);

-- Now creating the users table
CREATE TABLE users (
    UserID INT PRIMARY KEY,
    Age INT NOT NULL,
    Gender VARCHAR(10) NOT NULL
);

-- Insert data into Users table
INSERT INTO users (UserID, Age, Gender)
SELECT DISTINCT UserID, Age, Gender FROM Tempdata;

-- Creating the Devices table
CREATE TABLE devices (
    DeviceID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT,
    DeviceModel VARCHAR(50) NOT NULL,
    OperatingSystem VARCHAR(20) NOT NULL,
    NumberOfAppsInstalled INT NOT NULL,
    FOREIGN KEY (UserID) REFERENCES users(UserID)
);

-- Insert data into Devices table
INSERT INTO devices (UserID, DeviceModel, OperatingSystem, NumberOfAppsInstalled)
SELECT DISTINCT UserID, DeviceModel, OperatingSystem, NumberOfAppsInstalled FROM Tempdata;

-- Create AppUsage table
CREATE TABLE appusage (
    AppUsageID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT,
    AppUsageTime INT NOT NULL,
    ScreenOnTime DECIMAL(4,2) NOT NULL,
    BatteryDrain DECIMAL(7,3) NOT NULL,
    DataUsage DECIMAL(6,2) NOT NULL,
    FOREIGN KEY (UserID) REFERENCES users(UserID)
);

-- Insert data into AppUsage table
INSERT INTO appusage (UserID, AppUsageTime, ScreenOnTime, BatteryDrain, DataUsage)
SELECT DISTINCT UserID, AppUsageTime, ScreenOnTime, BatteryDrain, DataUsage FROM tempdata;

-- Create UserBehavior table
CREATE TABLE userbehavior (
    BehaviorID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT UNIQUE,
    UserBehaviorClass INT NOT NULL,
    FOREIGN KEY (UserID) REFERENCES users(UserID)
);

-- Insert data into UserBehavior table
INSERT INTO userbehavior (UserID, UserBehaviorClass)
SELECT DISTINCT UserID, UserBehaviorClass FROM Tempdata;
