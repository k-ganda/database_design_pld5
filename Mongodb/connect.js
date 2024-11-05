const { MongoClient } = require('mongodb');

const uri = "mongodb+srv://sbabalola:Samuel2006@cluster0.n5f49.mongodb.net/";
const client = new MongoClient(uri);

async function connectToDatabase() {
    try {
        await client.connect();
        console.log("Connected to MongoDB successfully!");
        return client.db('user_data'); // You can return the database object if needed
    } catch (error) {
        console.error("Error connecting to MongoDB:", error);
    } finally {
        await client.close(); // Close the connection after testing
    }
}

connectToDatabase().catch(console.error);
