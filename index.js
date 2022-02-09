const cron = require('node-cron');
const express = require('express');
const childProcess = require('child_process');
const {spawn} = require('child_process');
const nodemailer = require('nodemailer');

const path = require('path')
require('dotenv').config({ path: path.resolve(__dirname, '../.env') })

// run scraper JS from scraper package 
function runScraper(scraperPath, arguments, callback) {

  var process = childProcess.fork(scraperPath,arguments);

  process.on('error', function (err) {
      callback(err);
  });

  process.on('exit', function (code) {
      var err = code === 0 ? null : new Error('exit code ' + code);
      callback(err);
  });

}

app = express();

var transporter = nodemailer.createTransport({
  service: 'Gmail',
  auth: {
    
      user: process.env.GMAIL_USERNAME,
      pass: process.env.GMAIL_PASSWORD
   
  }
});


// run scraping and geocoding 
cron.schedule(' 10 13 * * 5', function() {
  console.log('---------------------');
  console.log('Running Weekly Update');

  runScraper('../Scraper/EvictionScraper.js', ['Fulton',''], function (err) {
    if (err) throw err;

    runScraper('../Scraper/EvictionScraper.js', ['Gwinnett','DeKalb'], function (err1) {
      if (err1) throw err1;
      runScraper('../Scraper/EvictionScraper.js', ['Chatham','Maconbibb'], function (err2) {
        if (err2) throw err2;
        runScraper('../Scraper/EvictionScraper.js', ['Clayton','Cobb'], function (err3) {
          if (err3) throw err3;
          runScraper('../Scraper/EvictionScraper.js', ['','Henry'], function (err4) {
            if (err4) throw err4;

            console.log('-- finished running scraper');
            console.log('-- start geocoding and aggregating');
            // console.log(__dirname)
            //change the work directory
            process.chdir(__dirname);

            const API = spawn('python', ['./dataManipulation.py']);
            var result = '';

            API.stdout.on('data', function (data) {
              //console.log('-- general output: ');
              result += data.toString();
              // console.log(dataToSend)

              //send email from here for weekly report
              // console.log('Sending Mail to Folks');

              // var messageOptions = {
              //   from: process.env.GMAIL_USERNAME,
              //   to: process.env.MANAGER_EMAIL,
              //   subject: 'Eviction API Weekly Report',
              //   html:'<p>'+dataToSend+'</p>'
              // };

              // transporter.sendMail(messageOptions, function(error, info) {
              //   if (error) {
              //     throw error;
              //   } else {
              //     console.log('Email successfully sent to Folks!');
              //   }
              // });

              // const API_TOP = spawn('python', ['./topEvicProperties.py']);

              // API_TOP.stdout.on('data', function (dataTop) {

                //console.log('-- top 10 output: ');
                // dataToSendTop10 = dataToSend + dataTop.toString();
                // console.log(dataToSendTop10)

                //send email from here for weekly report
                

              // })

              // API_TOP.on('close', (code) => {
              //   console.log(`-- calculate top properties is finished with code ${code}`);
              // });

              // API_TOP.on('error', function(err) {
              //   console.log( err);
              // });


            });

            API.on('close', (code) => {
              console.log(`-- geocoding and data aggregation is finished with code ${code}`);
              console.log('Sending Mail to Elora and others');

                var messageOptionsTop = {
                  from: process.env.GMAIL_USERNAME,
                  to: process.env.TOP_MANAGER_EMAIL,
                  subject: 'Eviction API Weekly Report',
                  html:'<p>'+result+'</p>'
                };

                transporter.sendMail(messageOptionsTop, function(error, info) {
                  if (error) {
                    throw error;
                  } else {
                    console.log('Email successfully sent to Elora and others!');
                  }
                });
            });

            API.stderr.on('error', function(err) {
              console.log( err.toString());
            })

            API.on('error', function(err) {
              console.log( err);
            });

          
          })
        })
      })
    });
  })
});



app.listen(3000);

