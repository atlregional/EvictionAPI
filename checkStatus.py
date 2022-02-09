import csv     
import json
import utils.dataReader as dataReader
import pandas as pd
import warnings
warnings.filterwarnings('ignore')


def import_csv(csvfilename): 
    data = [] 
    with open(csvfilename, "r", encoding="utf-8", errors="ignore") as scraped: 
        reader = csv.reader(scraped, delimiter=',') 
        row_index = 0
        for row in reader: 
            if row:  # avoid blank lines 
                row_index += 1 
                columns = [str(row_index), row[0], row[1], row[2]] 
                data.append(columns) 
    return data 
 
with open('./config.json') as configFile:
    config = json.load(configFile)
#define global variables
filePathForRawCaseData = config['filePathForRawCaseData']
filePathForPreRawCaseData = config['filePathForPreRawCaseData']
filePathForBackUpFolderOneLevelUp = config['filePathForBackUpFolderOneLevelUp']
counties = config['counties']
filePathForWorkFolder = config['filePathForWorkFolder']
filePathForWorkFolderRawData = config['filePathForWorkFolderRawData']

fileNamePool,countyCodePool = dataReader.findRawData(filePathForRawCaseData,counties)
prefileNamePool,precountyCodePool = dataReader.findRawData(filePathForPreRawCaseData,counties)
	#fileNamePool = ['2020ClaytonCountyEvictionCaseEvents-SCRAPE-09-25-2020','2020CobbCountyEvictionCaseEvents-SCRAPE-09-25-2020','2020DeKalbCountyEvictionCaseEvents-SCRAPE-09-25-2020','2020FultonCountyEvictionCaseEvents-SCRAPE-09-25-2020','2020GwinnettCountyEvictionCaseEvents-SCRAPE-09-25-2020'] 
	#countyCodePool = ['063','067','089','121','135']
for key, ele in enumerate(fileNamePool):
    countyName = ''
    preFileName = ''
    for key2 in counties:
        if fileNamePool[key].find(counties[key2]) != -1:
            countyName = counties[key2] + ' County'
            for key3, ele3 in enumerate(prefileNamePool): 
                if prefileNamePool[key3].find(counties[key2]) != -1:
                    preFileName = prefileNamePool[key3]
    rawData = pd.read_csv(r'%s' %(filePathForRawCaseData + fileNamePool[key] + '.csv'))
    rawDataIDAddressOnly = rawData.drop(['eventNumber','eventDate','eventName','eventDescription'], axis=1)
    rawDataIDAddressOnlyUnique = rawDataIDAddressOnly.drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)

    prerawData = pd.read_csv(r'%s' %(filePathForPreRawCaseData + preFileName + '.csv'))
    prerawDataIDAddressOnly = prerawData.drop(['eventNumber','eventDate','eventName','eventDescription'], axis=1)
    prerawDataIDAddressOnlyUnique = prerawDataIDAddressOnly.drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)

    print('Number of cases in ' + countyName +' of current/ previous: ', rawDataIDAddressOnlyUnique.shape[0],'/ ',prerawDataIDAddressOnlyUnique.shape[0],' <br> ')

    data = import_csv(r'%s' %(filePathForRawCaseData + fileNamePool[key] + '.csv')) 
    last_row5 = data[-5]
    last_row4 = data[-4]
    last_row3 = data[-3]
    last_row2 = data[-2]
    last_row = data[-1]
    print('Last 5 rows of current scrape of '+ countyName + ': ',' <br> ')
    print(last_row5,' <br> ')
    print(last_row4,' <br> ')
    print(last_row3,' <br> ')
    print(last_row2,' <br> ')
    print(last_row,' <br> <br> ')