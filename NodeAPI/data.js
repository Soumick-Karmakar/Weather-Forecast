const mongoose = require('mongoose');
const { Schema } = mongoose;

//creating schema for the data to be entered
const data = new mongoose.Schema({
    aqi:{
        type: String
    },
    city:{
        type: String
    },
    datetime:{
        type: String
    },
    temp:{
        type: String
    },
    clouds:{
        type: String
    },
    snow:{
        type: String
    },
    year:{
        type: String
    },
    value:{
        type: String
    },
    sex:{
        type: String
    },
    reliabilty:{
        type: String
    }
});

module.exports = mongoose.model('data', data);
