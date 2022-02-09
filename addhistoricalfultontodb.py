
import os
import json
import utils.dataReader as dataReader
import utils.geocoder as geocoder
import utils.aggregater as aggregater
import utils.insertCsvToDB as insertCsvToDB
import shutil,os,glob,stat
import pandas as pd
import warnings
import datetime

import warnings
warnings.filterwarnings('ignore')


def main():
	with open('./config.json') as configFile:
		config = json.load(configFile)
	#define global variables
	filePathForRawCaseData = config['filePathForRawCaseData']
	filePathForPreRawCaseData = config['filePathForPreRawCaseData']
	filePathForBackUpFolderOneLevelUp = config['filePathForBackUpFolderOneLevelUp']
	counties = config['counties']
	filePathForWorkFolder = config['filePathForWorkFolder']
	filePathForWorkFolderRawData = config['filePathForWorkFolderRawData']

	fileNamePool,countyCodePool = dataReader.findRawData(filePathForWorkFolderRawData,counties)
	#fileNamePool = ['2020ClaytonCountyEvictionCaseEvents-SCRAPE-09-25-2020','2020CobbCountyEvictionCaseEvents-SCRAPE-09-25-2020','2020DeKalbCountyEvictionCaseEvents-SCRAPE-09-25-2020','2020FultonCountyEvictionCaseEvents-SCRAPE-09-25-2020','2020GwinnettCountyEvictionCaseEvents-SCRAPE-09-25-2020'] 
	#countyCodePool = ['063','067','089','121','135']
	for key, ele in enumerate(fileNamePool):
		
		if ele.find('Fulton') != -1:
			# rawDataIDNoAddressOnlyUnique = dataReader.ReadCSvAnddropDuplication(filePathForWorkFolderRawData, fileNamePool[key],counties)
			
			# #add the address back from the previous scrape
			# fileName = fileNamePool[key][:-17]
	
			# rawData = pd.read_csv(r'%s' %(filePathForWorkFolder + 'addon/' + fileName + '.csv'))
			# rawDataIDAddressOnly = rawData[['caseID','address']]
			# rawDataIDAddressOnlyUnique = rawDataIDAddressOnly.drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)

			# rawDataIDNoAddressOnlyUnique = rawDataIDNoAddressOnlyUnique.drop(['address'], axis=1)
			# #join address
			# merged_df = rawDataIDNoAddressOnlyUnique.merge(rawDataIDAddressOnlyUnique, how = 'left', on = ['caseID'])

			# #geocoding
			# #rawDataIDAddressOnlyUnique = geocoder.geocoding(rawDataIDAddressOnlyUnique)
			# merged_df = geocoder.updateGeoCoding(merged_df,fileNamePool[key],filePathForWorkFolder)
			# #spatial aggregation
			# # 'Cherokee':'057','Clayton':'063','Cobb':'067','DeKalb':'089','Douglas':'097','Fayette':'113',
			# #    'Fulton':'121','Gwinnett':'135','Henry':'151','Rockdale':'247'
			# tractPolygons = aggregater.getTractData(countyCodePool[key])

			# #rawDataIDAddressOnlyUniqueNoNull = aggregater.removeNullAddressAndJoinTract(rawDataIDAddressOnlyUnique,tractPolygons,fileNamePool[key])
			# rawDataIDAddressOnlyUniqueNoNull = aggregater.removeNullAddressAndUpdateJoinTract(merged_df,tractPolygons,fileNamePool[key],filePathForWorkFolder)

			# # count by date and census tract
			# aggregater.removeNullTractAndCount(rawDataIDAddressOnlyUniqueNoNull, fileNamePool[key],filePathForWorkFolder)

			#insertCsvToDB.insertCaseLevelDataFromcsvToDB(filePathForWorkFolder,fileNamePool[key])

			insertCsvToDB.insertDataFromcsvToDB(filePathForWorkFolder,fileNamePool[key])


if __name__ == "__main__":
    main()