import shutil,os,glob,stat
import pandas as pd
import warnings
import datetime
import numpy as np

warnings.filterwarnings('ignore')

def main():
	rawDataBeforeFilingDateCheck = pd.read_csv("./data/current/rawData/2020GwinnettCountyEvictionCaseEvents-SCRAPE-02-27-2021.csv")
	rawData = checkFilingDate(rawDataBeforeFilingDateCheck)
	print(rawData)

def readIndividualFinalCSVFreqCleanedAddress(filePath,county):
	rawData = pd.read_csv(r'%s' %(filePath + 'dataByIndividual/2019'+ county + 'CountyEvictionCaseEvents--final.csv'))
	rawData['fileDate'] = rawData['fileDate'].map(lambda x: datetime.datetime.strptime(x, '%m/%d/%Y').date()
											if (len(x.split('/')[2]) > 2) 
											 else datetime.datetime.strptime(x, '%m/%d/%y').date()

											)

	today = datetime.date.today()
	# if(today == (today - datetime.timedelta(days=today.weekday()))):
	# 	latestMonday = today - datetime.timedelta(days=today.weekday(),weeks=1)
	# else:
	# #last monday
	# 	latestMonday = today - datetime.timedelta(days=today.weekday())
	latestMonday = today - datetime.timedelta(days=30)

	timeRange = (rawData['fileDate'] >= latestMonday) & (rawData['fileDate'] <= today)

	freq = rawData[timeRange].groupby('cleanedAddress').size().reset_index(name='counts').sort_values(by=['counts'], ascending=False)
	return freq

def ReadCSvAnddropDuplicationFulton (filePath, fileName,counties):
	countyName = ''
	for key in counties:
		if fileName.find(counties[key]) != -1:
			countyName = counties[key] + ' County'

	rawData = pd.read_csv(r'%s' %(filePath + 'rawData/' + fileName + '.csv'))
	rawDataIDAddressOnly = rawData.drop(['eventNumber','eventDate','eventName','eventDescription'], axis=1)
	rawDataIDAddressOnlyUnique = rawDataIDAddressOnly.drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)
	fileName = fileName[:-17]
	rawDataIDAddressOnlyUnique.to_csv(filePath + 'dataByIndividual/'+ fileName + '-final.csv')

	print('Number of cases in ' + countyName +' since 2019: ', rawDataIDAddressOnlyUnique.shape[0],' <br> ')

def ReadCSvAnddropDuplicationAddAddressFulton (rawDataIDNoAddressOnlyUnique, filePath, fileName,counties):
    # 	countyName = ''
	# for key in counties:
	# 	if fileName.find(counties[key]) != -1:
	# 		countyName = counties[key] + ' County'
	fileName = fileName[:-17]
	
	rawData = pd.read_csv(r'%s' %(filePath + 'updatedDataWithLatLongTract/' + fileName + '-LatLong-Tract.csv'))
	# rawDataIDAddressOnly = rawData[['caseID','address_x','tractID']]
	rawDataIDAddressOnlyUnique = rawData.drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)

	# rawDataIDNoAddressOnlyUnique = rawDataIDNoAddressOnlyUnique.drop(['address'], axis=1)

	#join address
	merged_df = rawDataIDNoAddressOnlyUnique.merge(rawDataIDAddressOnlyUnique, how = 'left', on = ['caseID'])

	merged_df['address'] = merged_df['address_x']

	# merged_df['COUNTYFP10'] = '121'

	# print(list(merged_df.columns))

	merged_df = merged_df.drop(['Unnamed: 0'], axis=1)

	merged_df['Longitude'].fillna(0, inplace=True)
	merged_df['Latitude'].fillna(0, inplace=True)
	merged_df['Score'].fillna(0, inplace=True)

	# merged_df.to_csv(filePath + 'dataByIndividual/'+ fileName + '-ttfinal.csv')

	return merged_df
	
	

	# print('Number of cases in ' + countyName +' of 2020: ', rawDataIDAddressOnlyUnique.shape[0],' <br> ')

def AddLonLatScoreChatham (rawDataIDNoAddressOnlyUnique):
	rawDataIDNoAddressOnlyUnique['address_x']= ''
	rawDataIDNoAddressOnlyUnique['Longitude'] = 0
	rawDataIDNoAddressOnlyUnique['Latitude']= 0
	rawDataIDNoAddressOnlyUnique['tractID']= 0
	rawDataIDNoAddressOnlyUnique['Score']= 0
	rawDataIDNoAddressOnlyUnique['Match_addr']= ''

	return rawDataIDNoAddressOnlyUnique

def checkFilingDate(rawData):
	rawData['fileDateFormatted'] = rawData['fileDate'].map(lambda x: datetime.datetime.strptime(x, '%m/%d/%Y').date()
											if (len(x.split('/')[2]) > 2) 
											 else datetime.datetime.strptime(x, '%m/%d/%y').date()

											)

	todayPlus7 = datetime.date.today() + datetime.timedelta(days=7)

	# replace the filedate by the eventDate of the first event or null if eventDate is unavailable if the filing Date is later than one week after today 
	timeRange = (rawData['fileDateFormatted'] > todayPlus7) & ((rawData['eventNumber'] == 1) | (pd.isna(rawData['eventNumber'])))
	rawDataAfterCheck = rawData.copy()
	rawDataAfterCheck['fileDate'] = np.where(timeRange,rawDataAfterCheck['eventDate'],rawDataAfterCheck['fileDate'])
	rawDataAfterCheck = rawDataAfterCheck.drop(['fileDateFormatted'], axis=1)
	# return rawDataAfterCheck[rawDataAfterCheck['caseID'] == '21-M-05366']
	return rawDataAfterCheck

def ReadCSvAnddropDuplication (filePath, fileName,counties):

	countyName = ''
	for key in counties:
		if fileName.find(counties[key]) != -1:
			countyName = counties[key] + ' County'

	rawDataBeforeFilingDateCheck = pd.read_csv(r'%s' %(filePath + fileName + '.csv'))
	rawData = checkFilingDate(rawDataBeforeFilingDateCheck)
	#create dict  {caseid:[{date: , name: }]}
	answerDict = {}
	answerTerm= {'answer'}
	serviceDict = {}
	serviceTerm= {'service'}
	dismissedDict = {}
	dismissedTerm= {'dismiss'}
	defaultJudgmentDict = {}
	defaultJudgmentTerm= {'default','dispossessory 4'}
	judgmentDict = {}
	judgmentTerm= {'writ','eject','judgment','tenant'}

	for index, row in rawData.iterrows():

		if row['caseID'] not in answerDict:
			answerDict[row['caseID']] = []
			serviceDict[row['caseID']] = []
			dismissedDict[row['caseID']] = []
			defaultJudgmentDict[row['caseID']] = []
			judgmentDict[row['caseID']] = []
	
		if not pd.isna(row['eventName']) and len(row['eventDate'].split('/'))>1:
			for term in answerTerm:
				if row['eventName'].lower().find(term) != -1:
					answerDict[row['caseID']].append({'date': row['eventDate'],'name':row['eventName']})
					break

			for term in serviceTerm:
				if row['eventName'].lower().find(term) != -1:
					serviceDict[row['caseID']].append({'date': row['eventDate'],'name':row['eventName']})
					break

			for term in dismissedTerm:
				if row['eventName'].lower().find(term) != -1:
					dismissedDict[row['caseID']].append({'date': row['eventDate'],'name':row['eventName']})
					break

			for term in defaultJudgmentTerm:
				if row['eventName'].lower().find(term) != -1:
					defaultJudgmentDict[row['caseID']].append({'date': row['eventDate'],'name':row['eventName']})
					break

			for term in judgmentTerm:
				if row['eventName'].lower().find(term) != -1:
					judgmentDict[row['caseID']].append({'date': row['eventDate'],'name':row['eventName']})
					break

	# catch the cases with answer 
	validAnswerDict = {key:answerDict[key] for key in answerDict if len(answerDict[key]) > 0}
	validServiceDict = {key:serviceDict[key] for key in serviceDict if len(serviceDict[key]) > 0}
	validdismissedDict = {key:dismissedDict[key] for key in dismissedDict if len(dismissedDict[key]) > 0}
	validdefaultJudgmentDict = {key:defaultJudgmentDict[key] for key in defaultJudgmentDict if len(defaultJudgmentDict[key]) > 0}
	validjudgmentDict = {key:judgmentDict[key] for key in judgmentDict if len(judgmentDict[key]) > 0}
	
	# print(validAnswerDict)
	rawDataIDAddressOnly = rawData.drop(['eventNumber','eventDate','eventName','eventDescription'], axis=1)
	# rawDataIDAddressOnly = rawData.drop(['caseStatus','eventNumber','eventDate','eventName'], axis=1)
	# rawDataIDAddressOnly.head()
	# drop the events to get unique record for each case 
	rawDataIDAddressOnlyUnique = rawDataIDAddressOnly.drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)

	# print(rawDataIDAddressOnlyUnique.head(30))

	rawDataIDAddressOnlyUnique = sortCasesByDateThenMostRecentCase(rawDataIDAddressOnlyUnique,validAnswerDict,'answerDate','ifAnswered','answerEventName')
	rawDataIDAddressOnlyUnique = sortCasesByDateThenMostRecentCase(rawDataIDAddressOnlyUnique,validServiceDict,'serviceDate','ifServiced','serviceEventName')
	rawDataIDAddressOnlyUnique = sortCasesByDateThenMostRecentCase(rawDataIDAddressOnlyUnique,validdismissedDict,'dismissDate','ifDismissed','dismissEventName')
	rawDataIDAddressOnlyUnique = sortCasesByDateThenMostRecentCase(rawDataIDAddressOnlyUnique,validdefaultJudgmentDict,'defaultJudgmentDate','ifdefaultJudgment','defaultJudgmentEventName')
	rawDataIDAddressOnlyUnique = sortCasesByDateThenMostRecentCase(rawDataIDAddressOnlyUnique,validjudgmentDict,'judgmentDate','ifjudgmented','judgmentEventName')

	# print('Number of cases in ' + countyName +' of 2020: ', rawDataIDAddressOnlyUnique.shape[0],' <br> ')

	
	return rawDataIDAddressOnlyUnique
    #rawDataIDAddressOnlyUnique.head()

def sortCasesByDateThenMostRecentCase(rawDataIDAddressOnlyUnique,validAnswerDict,answerDate,ifAnswered,answerEventName):
	# sort each valid answer case by date
	for key in validAnswerDict:
		# for ele in validAnswerDict[key]:
		# 	#08/24/2020
		# 	if(len(ele['date'].split(' ')[0].split('/')[2]) > 2):
		# 		print(datetime.datetime.strptime(ele['date'].split(' ')[0],'%m/%d/%Y'))
		# 	else:
		# 		#8/24/20
		# 		print(datetime.datetime.strptime(ele['date'].split(' ')[0],'%m/%d/%y'))

		validAnswerDict[key].sort(key=lambda x: datetime.datetime.strptime(x['date'].split(' ')[0],'%m/%d/%Y')
		 if (len(x['date'].split(' ')[0].split('/')[2]) > 2) 
		 else datetime.datetime.strptime(x['date'].split(' ')[0],'%m/%d/%y'),reverse = False)

	#add answer info to the raw data
	rawDataIDAddressOnlyUnique[answerDate] = 'N/A'
	rawDataIDAddressOnlyUnique[ifAnswered] = 0
	rawDataIDAddressOnlyUnique[answerEventName] = 'N/A'

	for index, row in rawDataIDAddressOnlyUnique.iterrows():

		if row['caseID'] in validAnswerDict:
			rawDataIDAddressOnlyUnique.at[index,answerDate] = validAnswerDict[row['caseID']][0]['date']
			rawDataIDAddressOnlyUnique.at[index,ifAnswered] = 1
			rawDataIDAddressOnlyUnique.at[index,answerEventName] = validAnswerDict[row['caseID']][0]['name']

	return rawDataIDAddressOnlyUnique

def createFoldersBasedOnDate (directory):
	PathForDataRootFolder = directory + datetime.datetime.now().strftime("%Y%m%d")
	if not os.path.exists(PathForDataRootFolder):
		os.makedirs(PathForDataRootFolder)
		# os.makedirs(PathForDataRootFolder +"/dataByIndividual")
		# os.makedirs(PathForDataRootFolder +"/outlines")
		# os.makedirs(PathForDataRootFolder +"/outlines/lowQualityAddress")
		# os.makedirs(PathForDataRootFolder +"/outlines/outOfBoundary")
		# os.makedirs(PathForDataRootFolder +"/updateByTract")
		# os.makedirs(PathForDataRootFolder +"/updateByTractSeperate")
		# os.makedirs(PathForDataRootFolder +"/rawData")
		# os.makedirs(PathForDataRootFolder +"/updatedDataWithLatLongTract")


def findRawData (filePathForRawCaseData,counties):
	countyCodePool = [ ]
	fileNamePool = [ ]
	directory = os.fsencode(filePathForRawCaseData)
	for file in os.listdir(directory):
		fileName = os.fsdecode(file)
		for key in counties:
			if fileName.find(counties[key]) != -1:
				countyCodePool.append(key)
				fileNamePool.append(fileName[:-4])
	# print(fileNamePool)
	# print(countyCodePool)
	return fileNamePool,countyCodePool

def backUpResults ( filePathForWorkFolder, filePathForBackUpFolderOneLevelUp):
	PathForDataRootFolder = filePathForBackUpFolderOneLevelUp + datetime.datetime.now().strftime("%Y%m%d")
	if not os.path.exists(PathForDataRootFolder):
		shutil.copytree(filePathForWorkFolder, filePathForBackUpFolderOneLevelUp + datetime.datetime.now().strftime("%Y%m%d"))
		

def copyRawDataToWorkFolderFromScraper (filePathForRawCaseData,filePathForWorkFolderRawData):
	# clear the raw data folder for new data
	if os.path.exists(filePathForWorkFolderRawData):
		shutil.rmtree(filePathForWorkFolderRawData)
	os.makedirs(filePathForWorkFolderRawData)
	# copy the data from scraper
	directory = os.fsencode(filePathForRawCaseData)
	for file in os.listdir(directory):
		fileName = os.fsdecode(file)
		shutil.copy(filePathForRawCaseData + fileName, filePathForWorkFolderRawData)


def reloadDataforNextScrape (filePathForCurrentRawCaseData,filePathForPreRawCaseData):
	# clear the pre folder for new load
	if os.path.exists(filePathForPreRawCaseData):
		shutil.rmtree(filePathForPreRawCaseData)
	os.makedirs(filePathForPreRawCaseData)
	# copy the data from scraper current folder to pre folder
	directory = os.fsencode(filePathForCurrentRawCaseData)
	for file in os.listdir(directory):
		fileName = os.fsdecode(file)
		shutil.copy(filePathForCurrentRawCaseData + fileName, filePathForPreRawCaseData)
	# empty current folder
	if os.path.exists(filePathForCurrentRawCaseData):
		shutil.rmtree(filePathForCurrentRawCaseData)
	os.makedirs(filePathForCurrentRawCaseData)
	# print("Data reloaded for the next round.")


if __name__ == "__main__":
    main()