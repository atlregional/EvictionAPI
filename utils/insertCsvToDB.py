
# import sys
# import json
# import collections
import csv
from turtle import dot
from pymongo import MongoClient
# import pymongo
from dotenv import dotenv_values, load_dotenv, find_dotenv
import os
from pathlib import Path  # Python 3.6+ only
import datetime


def main():
    env_path = Path('../') / '.env'
    load_dotenv(dotenv_path=env_path)
    # print(os.getenv("dbHost"))


def getDatabaseCollection(collectionName):
    envPath = Path('../') / '.env'
    load_dotenv(dotenv_path=envPath)
    mongoURI = os.getenv('MONGODB_URI')
    # mongoURI = os.getenv('MONGODB_URI_DEV')
    dbName = os.getenv('DB_NAME')
    client = MongoClient(mongoURI)
    db = client[dbName]

    return db[collectionName]


def insertDataFromcsvToDB(filePathForWorkFolder, fileName):
    inserts = 0
    updates = 0

    dbCollection = getDatabaseCollection('filingsbytractdaily')

    if dbCollection is not None:
        fileName = fileName[:-17]

        with open(filePathForWorkFolder + 'updateByTract/' + fileName + '-generalCountByDateTract.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row.

            for row in reader:
                # row.append(row[1]+row[2]+row[3]) --- want to use uniqueId here?
                newTractDict = {
                    'FilingDate': row[1],
                    'TractID': row[2],
                    'CountyID': row[3],
                    'TotalFilings': row[4],
                    'TotalAnsweredFilings': row[5]
                }

                existingTract = dbCollection.find_one(
                    {'FilingDate': row[1], 'TractID': row[2], 'CountyID': row[3]})

                if existingTract is not None:
                    if existingTract['TotalAnsweredFilings'] != newTractDict['TotalAnsweredFilings']:
                        dbCollection.update_one(
                            {'_id': existingTract['_id']}, {'$set': {
                                'TotalAnsweredFilings': newTractDict['TotalAnsweredFilings']}})
                        updates += 1

                else:
                    dbCollection.insert_one(newTractDict)
                    inserts += 1

            print('---Evictions By Tract---')
            print("Inserts:", inserts, 'Updates:', updates)
            print('')
    else:
        print('No Collection Found')


# def insertFultonDataFromcsvToDB(filePathForWorkFolder):
#     env_path = Path('../') / '.env'
#     load_dotenv(dotenv_path=env_path)

#     # conn = psycopg2.connect("host="+os.getenv("dbHost") + " port=" + os.getenv("dbPort") + " dbname=" +
#     #                         os.getenv("dbName") + " user=" + os.getenv("dbUser") + " password=" + os.getenv("dbPassword"))
#     # cur = conn.cursor()
#     with open(filePathForWorkFolder + 'dataByIndividual/2020FultonCountyEvictionCaseEvents--final.csv', 'r') as f:
#         reader = csv.reader(f)
#         print(reader)
#         next(reader)  # Skip the header row.
    #     for row in reader:
    #         cur.execute(
    #             "SELECT EXISTS(SELECT 1 FROM data.fulton_county_case WHERE caseid = %s )", [row[2]])
    #         # if exists update else insert
    #         if cur.fetchone()[0]:
    #             cur.execute("Update data.fulton_county_case set filedate = %s WHERE caseid = %s ",
    #                         (row[1], row[2])
    #                         )
    #         else:
    #             cur.execute(
    #                 "INSERT INTO data.fulton_county_case VALUES (%s, %s)", [
    #                     row[1], row[2]]
    #             )

    # conn.commit()


def insertCaseLevelDataFromcsvToDB(filePathForWorkFolder, fileName):
    updates = 0
    inserts = 0

    dbCollection = getDatabaseCollection('cases')

    if dbCollection is not None:
        fileName = fileName[:-17]

        with open(filePathForWorkFolder + 'dataByIndividual/' + fileName + '-final.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header row.

            for row in reader:
                # use caseid + tractID + countycode as
                uniqueId = row[2] + row[41] + row[44]
                tractId = row[41]
                blockGroupId = row[45]

                if row[47] != "N/A":
                    street = row[47].split(",")[0]
                    city = row[47].split(",")[1]
                    zipcode = row[47].split(",")[3]
                else:
                    street = ""
                    city = ""
                    zipcode = ""

                if (len(row[1].split('/')[2]) == 2):
                    fileDate = datetime.datetime.strptime(
                        row[1], '%m/%d/%y').strftime('%m/%d/%Y')
                else:
                    # print(row[1])
                    fileDate = datetime.datetime.strptime(
                        row[1], '%m/%d/%Y').strftime('%m/%d/%Y')
                    # print(fileDate)

                if row[23] != "N/A":
                    if (len(row[23].split(' ')[0].split('/')[2]) == 2):
                        answerDate = datetime.datetime.strptime(
                            row[23].split(' ')[0], '%m/%d/%y').strftime('%m/%d/%Y')
                    else:
                        # print(row[1])
                        answerDate = datetime.datetime.strptime(
                            row[23].split(' ')[0], '%m/%d/%Y').strftime('%m/%d/%Y')
                else:
                    answerDate = "9999-12-12"

                if row[26] != "N/A":
                    if (len(row[26].split(' ')[0].split('/')[2]) == 2):
                        serviceDate = datetime.datetime.strptime(
                            row[26].split(' ')[0], '%m/%d/%y').strftime('%m/%d/%Y')
                    else:
                        # print(row[1])
                        serviceDate = datetime.datetime.strptime(
                            row[26].split(' ')[0], '%m/%d/%Y').strftime('%m/%d/%Y')
                else:
                    serviceDate = "9999-12-12"

                if row[29] != "N/A":
                    if (len(row[29].split(' ')[0].split('/')[2]) == 2):
                        dismissDate = datetime.datetime.strptime(
                            row[29].split(' ')[0], '%m/%d/%y').strftime('%m/%d/%Y')
                    else:
                        # print(row[29])
                        dismissDate = datetime.datetime.strptime(
                            row[29].split(' ')[0], '%m/%d/%Y').strftime('%m/%d/%Y')
                else:
                    dismissDate = "9999-12-12"

                if row[32] != "N/A":
                    if (len(row[32].split(' ')[0].split('/')[2]) == 2):
                        defaultJudgmentDate = datetime.datetime.strptime(
                            row[32].split(' ')[0], '%m/%d/%y').strftime('%m/%d/%Y')
                    else:
                        # print(row[32])
                        defaultJudgmentDate = datetime.datetime.strptime(
                            row[32].split(' ')[0], '%m/%d/%Y').strftime('%m/%d/%Y')
                else:
                    defaultJudgmentDate = "9999-12-12"

                if row[35] != "N/A":
                    if (len(row[35].split(' ')[0].split('/')[2]) == 2):
                        judgmentDate = datetime.datetime.strptime(
                            row[35].split(' ')[0], '%m/%d/%y').strftime('%m/%d/%Y')
                    else:
                        # print(row[35])
                        judgmentDate = datetime.datetime.strptime(
                            row[35].split(' ')[0], '%m/%d/%Y').strftime('%m/%d/%Y')
                else:
                    judgmentDate = "9999-12-12"

                geometryDict = {
                    "type": "Point",
                    "coordinates": [float(row[39]), float(row[40])]
                }

                newCaseDict = {
                    "filingDate": fileDate,
                    "answer": row[24],
                    "geometry": geometryDict,
                    "latitude": row[40],
                    "longitude": row[39],
                    "services": row[27],
                    "dismiss": row[30],
                    "defaultJudgment": row[33],
                    "judgment": row[36],
                    "answerDate": answerDate,
                    "servicesDate": serviceDate,
                    "dismissDate": dismissDate,
                    "defaultJudgmentDate": defaultJudgmentDate,
                    "judgmentDate": judgmentDate,
                    "tractID": tractId,
                    "blockGroupID": blockGroupId
                }

                existingCase = dbCollection.find_one({'id': uniqueId})

                if existingCase is not None:
                    updateDict = {}

                    for key in newCaseDict:
                        if existingCase[key] != newCaseDict[key]:
                            updateDict[key] = newCaseDict[key]

                    if bool(updateDict):
                        dbCollection.update_one(
                            {'_id': existingCase['_id']}, {'$set': updateDict})
                        updates += 1

                else:
                    newCaseDict['id'] = uniqueId
                    newCaseDict['street'] = street.strip()
                    newCaseDict['city'] = city.strip()
                    newCaseDict['zip'] = zipcode.strip()

                    dbCollection.insert_one(newCaseDict)
                    inserts += 1

            print('---Eviction Cases---')
            print('Inserts:', inserts, 'Updates:', updates)
            print('')

    else:
        print('No collection found')
        #         cur.execute(
        #             "SELECT EXISTS(SELECT 1 FROM data.atlanta_metro_area_case WHERE id = %s  )", [uniqueId])
        #         # if exists update else insert
        #         if cur.fetchone()[0]:
        #             cur.execute("Update data.atlanta_metro_area_case set filingdate = %s, answer = %s, latitude= %s, longitude= %s, services= %s,dismiss= %s,defaultJudgment= %s,judgment= %s,answerdate= %s,servicesdate= %s,dismissdate= %s,defaultJudgmentdate= %s,judgmentdate= %s,tractid= %s,blockgroupid= %s WHERE id = %s ",
        #                         (fileDate, row[24], row[40], row[39], row[27], row[30], row[33], row[36], answerDate,
        #                          serviceDate, dismissDate, defaultJudgmentDate, judgmentDate, tractid, blockgroupid, uniqueId)
        #                         )
        #         else:
        #             # id, street, city, zip, filingdate, answer, county, latitude, longitude,services,dismiss,defaultJudgment,judgment,answerdate,servicesdate,dismissdate,defaultJudgmentdate,judgmentdate,tractid,blockgroupid
        #             cur.execute(
        #                 "INSERT INTO data.atlanta_metro_area_case VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s)",
        #                 [uniqueId, street, city, zipcode, fileDate, row[24], row[44], row[40], row[39], row[27], row[30], row[33],
        #                     row[36], answerDate, serviceDate, dismissDate, defaultJudgmentDate, judgmentDate, tractid, blockgroupid]
        #             )

        # conn.commit()


if __name__ == "__main__":
    main()
