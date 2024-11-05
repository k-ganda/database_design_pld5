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
CREATE TABLE Users (
    UserID INT PRIMARY KEY,
    Age INT NOT NULL,
    Gender VARCHAR(10) NOT NULL
);

-- Insert data into Users table
INSERT INTO Users (UserID, Age, Gender)
SELECT DISTINCT UserID, Age, Gender FROM TempData;

-- Creating the Devices table
CREATE TABLE Devices (
    DeviceID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT,
    DeviceModel VARCHAR(50) NOT NULL,
    OperatingSystem VARCHAR(20) NOT NULL,
    NumberOfAppsInstalled INT NOT NULL,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

-- Insert data into Devices table
INSERT INTO Devices (UserID, DeviceModel, OperatingSystem, NumberOfAppsInstalled)
SELECT DISTINCT UserID, DeviceModel, OperatingSystem, NumberOfAppsInstalled FROM TempData;