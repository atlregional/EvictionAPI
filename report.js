const cron = require('node-cron');
const express = require('express');
const {spawn} = require('child_process');
const nodemailer = require('nodemailer');

const path = require('path')
require('dotenv').config({ path: path.resolve(__dirname, '../.env') })

app = express();

var transporter = nodemailer.createTransport({
  service: 'Gmail',
  auth: {
    
      user: process.env.GMAIL_USERNAME,
      pass: process.env.GMAIL_PASSWORD
   
  }
});


console.log("server monitoring started..")

//10 mins checking
cron.schedule(' 20 13 * * 5', function() {

  const API = spawn('python', ['./checkStatus.py']);
  API.stdout.on('data', function (data) {

    dataToSend = data.toString();
    // console.log(dataToSend)

    var messageOptionsTop = {
      from: process.env.GMAIL_USERNAME,
      to: process.env.DEVELOPER_EMAIL,
      subject: '10 mins Scraping Report',
      html:'<p>'+dataToSend+'</p>'
    };

    transporter.sendMail(messageOptionsTop, function(error, info) {
      if (error) {
        throw error;
      } else {
        console.log('Email successfully sent to Developers!');
      }
    });

  });

  API.on('close', (code) => {
    console.log(`-- scraping checking is finished with code ${code}`);
  });

  API.on('error', function(err) {
    console.log( err);
  });

});

//6 hours checking
cron.schedule(' 00 08 * * 6', function() {

  const API = spawn('python', ['./checkStatus.py']);
  API.stdout.on('data', function (data) {

    dataToSend = data.toString();
    // console.log(dataToSend)

    var messageOptionsTop = {
      from: process.env.GMAIL_USERNAME,
      to: process.env.DEVELOPER_EMAIL,
      subject: '17 hours Scraping Report',
      html:'<p>'+dataToSend+'</p>'
    };

    transporter.sendMail(messageOptionsTop, function(error, info) {
      if (error) {
        throw error;
      } else {
        console.log('Email successfully sent to Developers!');
      }
    });

  });

  API.on('close', (code) => {
    console.log(`-- scraping checking is finished with code ${code}`);
  });

  API.on('error', function(err) {
    console.log( err);
  });

});

//15 hours checking
cron.schedule(' 00 20 * * 6', function() {

  const API = spawn('python', ['./checkStatus.py']);
  API.stdout.on('data', function (data) {

    dataToSend = data.toString();
    // console.log(dataToSend)

    var messageOptionsTop = {
      from: process.env.GMAIL_USERNAME,
      to: process.env.DEVELOPER_EMAIL,
      subject: '28 hours Scraping Report',
      html:'<p>'+dataToSend+'</p>'
    };

    transporter.sendMail(messageOptionsTop, function(error, info) {
      if (error) {
        throw error;
      } else {
        console.log('Email successfully sent to Developers!');
      }
    });

  });

  API.on('close', (code) => {
    console.log(`-- scraping checking is finished with code ${code}`);
  });

  API.on('error', function(err) {
    console.log( err);
  });

});

//23 hours checking
cron.schedule(' 00 08 * * 0', function() {

  const API = spawn('python', ['./checkStatus.py']);
  API.stdout.on('data', function (data) {

    dataToSend = data.toString();
    // console.log(dataToSend)

    var messageOptionsTop = {
      from: process.env.GMAIL_USERNAME,
      to: process.env.DEVELOPER_EMAIL,
      subject: '43 hours Scraping Report',
      html:'<p>'+dataToSend+'</p>'
    };

    transporter.sendMail(messageOptionsTop, function(error, info) {
      if (error) {
        throw error;
      } else {
        console.log('Email successfully sent to Developers!');
      }
    });

  });

  API.on('close', (code) => {
    console.log(`-- scraping checking is finished with code ${code}`);
  });

  API.on('error', function(err) {
    console.log( err);
  });

});

// API running checking
cron.schedule(' 00 08 * * *', function() {
  var messageOptions = {
    from: process.env.GMAIL_USERNAME,
    to: process.env.DEVELOPER_EMAIL,
    subject: 'API Status Report',
    html:'<p>'+'API is running.'+'</p>'
  };

  transporter.sendMail(messageOptions, function(error, info) {
    if (error) {
      throw error;
    } else {
      console.log('Server checking email successfully sent to Developers!');
    }
  });
})



app.listen(3001);

