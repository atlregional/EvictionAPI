
import os
import json
import utils.dataReader as dataReader
import utils.geocoder as geocoder
import utils.aggregater as aggregater
import utils.insertCsvToDB as insertCsvToDB
import checkCurrentDatabaseByMonthly as checkDatabase
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
	filePathForWorkFolderPreRawData = config['filePathForWorkFolderPreRawData']


	fileNamePool,countyCodePool = dataReader.findRawData(filePathForWorkFolderRawData,counties)
	#fileNamePool = ['2020ClaytonCountyEvictionCaseEvents-SCRAPE-09-25-2020','2020CobbCountyEvictionCaseEvents-SCRAPE-09-25-2020','2020DeKalbCountyEvictionCaseEvents-SCRAPE-09-25-2020','2020FultonCountyEvictionCaseEvents-SCRAPE-09-25-2020','2020GwinnettCountyEvictionCaseEvents-SCRAPE-09-25-2020'] 
	#countyCodePool = ['063','067','089','121','135']

	

	for key, ele in enumerate(fileNamePool):

		countyName = ''
		for key2 in counties:
			if fileNamePool[key].find(counties[key2]) != -1:
				countyName = counties[key2] + ' County'
		
		if ele.find('Fulton') != -1:
			rawDataIDAddressOnlyUnique = dataReader.ReadCSvAnddropDuplication(filePathForWorkFolderRawData, fileNamePool[key],counties)

			print('Number of cases in ' + countyName +' since 2020: ', rawDataIDAddressOnlyUnique.shape[0],' <br> ')
			
			# #add the address back from the previous scrape
			# rawDataIDAddressOnlyUniqueNoNull = dataReader.ReadCSvAnddropDuplicationAddAddressFulton(rawDataIDAddressOnlyUnique,filePathForWorkFolder, fileNamePool[key],counties)

			# aggregater.removeNullTractAndCount(rawDataIDAddressOnlyUniqueNoNull, fileNamePool[key],filePathForWorkFolder,countyCodePool[key])

			print('----------<br>')
		
		else:
			#read the data
			rawDataIDAddressOnlyUnique = dataReader.ReadCSvAnddropDuplication(filePathForWorkFolderRawData, fileNamePool[key],counties)

			print('Number of cases in ' + countyName +' since 2020: ', rawDataIDAddressOnlyUnique.shape[0],' <br> ')

		# 	#geocoding
		# 	#rawDataIDAddressOnlyUnique = geocoder.geocoding(rawDataIDAddressOnlyUnique)
		# 	rawDataIDAddressOnlyUnique = geocoder.updateGeoCoding(rawDataIDAddressOnlyUnique,fileNamePool[key],filePathForWorkFolder)
		# 	#spatial aggregation
		# 	# 'Cherokee':'057','Clayton':'063','Cobb':'067','DeKalb':'089','Douglas':'097','Fayette':'113',
		#  #    'Fulton':'121','Gwinnett':'135','Henry':'151','Rockdale':'247'
		# 	tractPolygons = aggregater.getTractData(countyCodePool[key])
			
		# 	#rawDataIDAddressOnlyUniqueNoNull = aggregater.removeNullAddressAndJoinTract(rawDataIDAddressOnlyUnique,tractPolygons,fileNamePool[key])
		# 	rawDataIDAddressOnlyUniqueNoNull = aggregater.removeNullAddressAndUpdateJoinTract(rawDataIDAddressOnlyUnique,tractPolygons,fileNamePool[key],filePathForWorkFolder)

		# 	# count by date and census tract
		# 	aggregater.removeNullTractAndCount(rawDataIDAddressOnlyUniqueNoNull, fileNamePool[key],filePathForWorkFolder,countyCodePool[key])


if __name__ == "__main__":
    main()