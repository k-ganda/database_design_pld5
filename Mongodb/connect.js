const { MongoClient } = require('mongodb');

const uri = "mongodb://localhost:27017";
const client = new MongoClient(uri);

async function connectToDatabase() {
    await client.connect();
    return client.db('user_data');
}

module.exports = connectToDatabase;