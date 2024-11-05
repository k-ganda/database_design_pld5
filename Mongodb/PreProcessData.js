const fs = require('fs');
const csv = require('csv-parser'); // Make sure to install this package
const MongoClient = require('mongodb').MongoClient;

// Function to preprocess data from a CSV file and insert it into MongoDB
const preprocessData = async (filePath, dbName, collectionName) => {
    const results = [];

    // Read and parse CSV file
    fs.createReadStream(filePath)
        .pipe(csv())
        .on('data', (data) => results.push(data))
        .on('end', async () => {
            try {
                // Insert processed data into MongoDB
                const client = await MongoClient.connect('mongodb+srv://sbabalola:Samuel2006@cluster0.n5f49.mongodb.net/');
                const db = client.db(dbName); // Use the variable dbName
                const collection = db.collection(collectionName); // Use the variable collectionName

                for (const row of results) {
                    const userDocument = {
                        _id: row['User ID'],
                        age: row['Age'],
                        gender: row['Gender'],
                        device_info: {
                            device_model: row['Device Model'],
                            operating_system: row['Operating System']
                        },
                        usage_metrics: {
                            app_usage_time: row['App Usage Time (min/day)'],
                            screen_on_time: row['Screen On Time (hours/day)'],
                            battery_drain: row['Battery Drain (mAh/day)'],
                            apps_installed: row['Number of Apps Installed'],
                            data_usage: row['Data Usage (MB/day)']
                        },
                        behavior_class: row['User Behavior Class'] 
                    };

                    await collection.insertOne(userDocument);
                }

                console.log('Data successfully inserted into MongoDB');
                client.close();
            } catch (error) {
                console.error('Error inserting data into MongoDB:', error);
            }
        });
};

// Call the function with your specific file path and database/collection names
const filePath = './user_behavior_dataset.csv';
preprocessData(filePath, 'User_Behaviour', 'User'); // Pass names as strings