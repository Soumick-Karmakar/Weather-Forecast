const mongoose = require('mongoose');
const connectToMongo = require('./db');
const express = require('express');
const data = require('./data');
const cors = require('cors');
connectToMongo()


const app = express()
app.use(express.json())


// Allowing requests from all origins
app.use(cors());

// Allowing requests only from frontend
// app.use(cors({
//   origin: 'http://localhost:5500'
// }));

const port = process.env.PORT || 5000;


// Receives the modified data and saves it in the mongodb
app.post('/modified', async (req, res) => {
  console.log('printing data from NodeJS')
  console.log(req.body)
  try {
    for (let i = 0; i < req.body.length; i++) {
      //Creating new data
      var id = new mongoose.Types.ObjectId()
      var newData = new data({
        _id: id,
        aqi: req.body[i].aqi,
        city: req.body[i].city_name,
        datetime: req.body[i].datetime,
        temp: req.body[i].temp,
        clouds: req.body[i].clouds,
        snow: req.body[i].snow,
        year: req.body[i].year,
        value: req.body[i].value,
        sex: req.body[i].sex,
        reliability: req.body[i].reliabilty
      }, { collection: 'Modified' });
      // Pushing the new data into mongo
      await newData.save();
    }
    // Sends a success response back to the client
    res.status(200).json({ message: 'Data submitted successfully' });
  }
  catch (error) {
    console.error('Error saving data:', error);
    res.status(500).json({ error: 'An error occurred while saving data' });
  }
})

app.listen(port, () => {
  console.log(`NodeJS API listening at http://localhost:${port}`);
});
