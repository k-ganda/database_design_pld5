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
                        UserID: row['User ID'],
                        Age: row['Age'],
                        Gender: row['Gender'],
                        Device: {
                            Device_Model: row['Device Model'],
                            Operating_System: row['Operating System']
                        },
                        Usage_Metrics: {
                            App_Usage_Time: row['App Usage Time (min/day)'],
                            Screen_On_Time: row['Screen On Time (hours/day)'],
                            Battery_Drain: row['Battery Drain (mAh/day)'],
                            Apps_Installed: row['Number of Apps Installed'],
                            Data_Usage: row['Data Usage (MB/day)']
                        },
                        User_Behavior_Class: row['User Behavior Class'] 
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