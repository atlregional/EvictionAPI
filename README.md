# Eviction API and Database

This project is developed to store the eviction data to database, provide the access to the eviction data, and geocode and aggregate the eviction data from case level to census tract level. It provides postgreSQL database and REST API on the basis of the open source project - [subZero postgrest-starter-kit](https://github.com/subzerocloud/postgrest-starter-kit). The backend of the project is written in python and mainly driven by [ArcGIS API for Python](https://github.com/Esri/arcgis-python-api)

## Directory

```bash
.
├── API                                                  # code for data manipulation, housing analysis and 
│   │                                                      database update
│   ├── data                                             # Geodata for data aggregation from individual 
│   │    │                                                 level to tract or blockgroup level 
│   │    │                                                   
│   │    ├── Census_2010_Blockgroups_Georgia.geojson     
│   │    └── Census_2010_Tracts_Georgia.geojson
│   ├── db_schema_development                            # Tool kit for the initialization and update of 
│   │                                                      the database schema, user authorization and API  
│   │    │                                                   
│   │    └── db
│   │        ├── migrations                              # sql scripts for deploying the database settings 
│   │        └── src                                     # interactive tool for designing the database
│   ├── addhistoricalfultontodb.py                       # add historical fulton data to db
│   ├── checkCurrentDatabaseByMonthly.py                 # db summary by month and county
│   ├── checkStatus.py                                   # scraping report by comparing the previous round 
│   │                                                      with the current round 
│   ├── config.json                                      # settings for data manipulation script 
│   ├── dataManipulation.py                              # data manipulation by following the procedure  
│   │                                                      (load the scraping result -> read the data ->  
│   │                                                      clean the data -> geocoding -> data aggregation  
│   │                                                      -> housing analysis -> import the result into db 
│   │                                                      -> backup result -> reload the data for the next  
│   │                                                      scraping -> find the top addresses with the 
│   │                                                      largest number of evcitions )
│   │                                                      
│   ├── index.js                                         # schedual scraping and email notification 
│   ├── report.js                                        # API status checking and scraping monitoring 
│   ├── topEvicProperties.py                             # find the top addresses with the largest number of
│   │                                                      evcitions
│   └── utils                                            # toolsets for data manipulation  
│       ├── aggregater.py              
│       ├── dataClean.py             
│       ├── dataReader.py              
│       ├── geocoder.py     
│       └── insertCsvToDB.py       
│                
├── data                                                 # results of the data manipulation 
│   ├── 20210923
│       └── ...
│   └── current                
│       ├── addon              
│       ├── cleanedGeocodedCases             
│       ├── dataByIndividual              
│       ├── outlines
│       │   ├── lowQualityAddress
│       │   └── outOfBoundary
│       ├── preRawData
│       ├── updateByTract              
│       ├── updateByTractSeperate     
│       ├── updatedDataWithLatLongTract 
│       └── rawData                    
│               
├── Scraper                                              # data scraping
│   ├── csvs                    
│   ├── modules                  
│   ├── utils
│   ├── config.json   
│   └── EvictionScraper.js
└──.env

```
## .env template
```bash

GMAIL_USERNAME= ***
GMAIL_PASSWORD= ***

MANAGER_EMAIL = ***

EMAIL_POOL = ***,***,*** 

TOP_MANAGER_EMAIL = ***,***,***

DEVELOPER_EMAIL = ***

USERNAMEE = *** 
PASSWORD = ***

dbHost = ***
dbPort = ***
dbName = ***
dbUser = ***
dbPassword = ***

```
## Prerequisites
* [PostgreSQL]
* [PostgREST]
* [openresty]
* [Node.js]
* [Python]

## DB Schema
```bash
              Table "data.atlanta_metro_area_tract"
        Column        |  Type   | Collation | Nullable | Default
----------------------+---------+-----------+----------+---------
 id                   | integer |           |          |
 filedate             | text    |           |          |
 tractid              | text    |           |          |
 countyfp10           | text    |           |          |
 totalfilings         | integer |           |          |
 totalansweredfilings | integer |           |          |
 indexid              | text    |           | not null |
Indexes:
    "atlanta_metro_area_tract_pkey" PRIMARY KEY, btree (indexid)
 ```
 
 ```bash
             Table "data.atlanta_metro_area_case"
       Column        | Type | Collation | Nullable | Default
---------------------+------+-----------+----------+---------
 id                  | text |           | not null |
 street              | text |           |          |
 city                | text |           |          |
 zip                 | text |           |          |
 filingdate          | date |           |          |
 answer              | text |           |          |
 county              | text |           |          |
 latitude            | text |           |          |
 longitude           | text |           |          |
 services            | text |           |          |
 dismiss             | text |           |          |
 defaultjudgment     | text |           |          |
 judgment            | text |           |          |
 answerdate          | date |           |          |
 servicesdate        | date |           |          |
 dismissdate         | date |           |          |
 defaultjudgmentdate | date |           |          |
 judgmentdate        | date |           |          |
 tractid             | text |           |          |
 blockgroupid        | text |           |          |
Indexes:
    "atlanta_metro_area_case_pkey" PRIMARY KEY, btree (id)
 ```
 ```bash
          Table "data.fulton_county_case"
  Column  | Type | Collation | Nullable | Default
----------+------+-----------+----------+---------
 filedate | text |           |          |
 caseid   | text |           | not null |
Indexes:
    "fulton_county_case_pkey" PRIMARY KEY, btree (caseid)
 
 ```
## How to initial and deploy?
1 Start postgrest API service(listen to postgresql port) \
`
postgrest.exe postgrest.conf
`\
2 start nginx service(listen to postgrest port and open 80 port for public facing ):\
`
start nginx
nginx.exe -s quit
nginx -s reload
`\
3 Initial the schema \
`
psql -U postgres -d eviction -f 20201113170528-initial.sql
`

## How to commit the updates?
1 Run the scraper and update the database every saturday morning\
`
npm start
`\
2 update the database schema (sample)\
`
psql -U postgres -d eviction -f 20201120194937-fulton_county_cases.sql
`

## API call samples
#### Atlanta Metro Area tract level data:
`
curl http://evictions.design.gatech.edu/rest/atlanta_metro_area_tracts
`
#### Simplified fulton case level data:
`
curl http://evictions.design.gatech.edu/rest/fulton_county_cases
`
