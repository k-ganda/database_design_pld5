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