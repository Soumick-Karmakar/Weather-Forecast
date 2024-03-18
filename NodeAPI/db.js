const mongoose =require('mongoose');
const mongoURI = "mongodb://127.0.0.1:27017/AppDB"

async function connectToMongo() {
    await mongoose.connect(mongoURI, console.log('Connected to MongoDB Successfully...'))
}

module.exports = connectToMongo;
