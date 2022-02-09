import pandas as pd
import warnings
import json
import utils.dataReader as dataReader


warnings.filterwarnings('ignore')

def main():

	checkMonthlyCaseCount()

	with open('./config.json') as configFile:
		config = json.load(configFile)
	#define global variables
	filePathForBackUpFolderOneLevelUp = config['filePathForBackUpFolderOneLevelUp']
	counties = config['counties']
	filePathForWorkFolder = config['filePathForWorkFolder']

	print('Top 10 Addresses by Eviction Number Snapshot',': <br> ')
	allData = {}
	
	for key in counties:
		if key != "121" and key != "051":
			# print("Top 10 addresses with eviction cases in ", counties[key], " County(Address --- Number of Cases): ",' <br> ')
			print(counties[key],': <br>')
			individualCase = dataReader.readIndividualFinalCSVFreqCleanedAddress(filePathForWorkFolder, counties[key])
			print('<table>')
			print('<tr><td>Address</td><td>Number of Evictions</td></tr>')
			for row in individualCase.head(10).values.tolist():
				print('<tr><td>')
				print(*row, sep=' </td> <td>')
				# print('<br>')
				print('</td></tr>')
			print('</table>')
			print('<br>')
			print('<br>')
			# print('<br>')
			# print('<br>')
			# allData[counties[key]]={}
			# allData[counties[key]]['df'] = individualCase

	# titleLine = '<tr><td>County</td><td>Address</td><td>Number of Evictions</td></tr>'
	# countDict = {}
	# for countyName in allData:
	# 	for row in allData[countyName]['df'].head(10).values.tolist():
	# 		if countyName in countDict:
	# 			countDict[countyName] = countDict[countyName] + row
	# 		else:
	# 			countDict[countyName] = row

	# print('<table>')
	# print(titleLine)
	# for countyName in countDict:
	# 	# newArray = [countyName] + countDict[countyName]
	# 	print('<tr><td>',countyName,'</td><')
	# 	for countIndex in range(len(countDict[countyName])):

	# 		print('<td>',countDict[countyName][countIndex],'</td>')

	# 	print('</tr>')
	# print('</table>')

def checkMonthlyCaseCount():
	with open('./config.json') as configFile:
		config = json.load(configFile)
	counties = config['counties']
	filePathForWorkFolderRawData = config['filePathForWorkFolderRawData']
	filePathForWorkFolderPreRawData = config['filePathForWorkFolderPreRawData']

	
	fileNamePool2,countyCodePool2 = dataReader.findRawData(filePathForWorkFolderPreRawData,counties)
	
	fileNamePool,countyCodePool = dataReader.findRawData(filePathForWorkFolderRawData,counties)

	allData = {}
	# print('<br>')
	# print('<br>')
	print('Scraping Snapshot',': <br> ')

	for key, ele in enumerate(fileNamePool):
		# print('Pre Scraping: ')
		rawDataIDAddressOnlyUniquePre = dataReader.ReadCSvAnddropDuplication(filePathForWorkFolderPreRawData, fileNamePool2[key],counties)

		# print('Current Scraping: ')
		rawDataIDAddressOnlyUnique = dataReader.ReadCSvAnddropDuplication(filePathForWorkFolderRawData, fileNamePool[key],counties)

		for key2 in counties:
			if fileNamePool[key].find(counties[key2]) != -1:
				countyName = counties[key2] + ' County'
		if countyName != "Cobb County":
			preSum = summarizedByMonth(rawDataIDAddressOnlyUniquePre)
			currentSum = summarizedByMonth(rawDataIDAddressOnlyUnique)

			merged_df = preSum.merge(currentSum, how = 'right', on = ['month'])
		else:
			preSum = summarizedByMonthCobb(rawDataIDAddressOnlyUniquePre)
			currentSum = summarizedByMonthCobb(rawDataIDAddressOnlyUnique)

			merged_df = preSum.merge(currentSum, how = 'right', on = ['month'])
		merged_df = merged_df.fillna(0)
	
		# print(merged_df)
		allData[countyName]={}
		allData[countyName]['preTotal'] = rawDataIDAddressOnlyUniquePre.shape[0]
		allData[countyName]['currentTotal'] = rawDataIDAddressOnlyUnique.shape[0]
		allData[countyName]['df'] = merged_df


	# print("Monthly Count for scraping ",countyName, " (month --- pre_x --- current_y):")
	titleLine = '<tr><td>Filing Month/Year</td>'
	totalCountLine = '<tr><td></td>'
	countDict = {}
	for countyName in allData:
		titleLine = titleLine + '<td colspan="2">'+ countyName + '</td>'
		totalCountLine = totalCountLine + '<td>PreScraping ('+ str(allData[countyName]['preTotal'])  +')</td><td>CurrentScraping ('+ str(allData[countyName]['currentTotal'])  +')</td>'

	# print('<br>')
	# print('<tr><td>Filing Month/Year</td><td colspan="2">',countyName,'</td></tr>')
	# print('<tr><td></td><td>PreScraping</td><td>CurrentScraping</td></tr>')
		for row in allData[countyName]['df'].values.tolist():
			if row[0] in countDict:
				countDict[row[0]] = countDict[row[0]] + row[1:]
			else:
				countDict[row[0]] = row[1:]

	titleLine = titleLine + '</tr>'
	totalCountLine = totalCountLine + '</tr>'
	print('<table>')
	print(titleLine)
	print(totalCountLine)
	for month in countDict:
		# newArray = [month] + countDict[month]
		print('<tr><td>',month,'</td>')
		for countIndex in range(len(countDict[month])):
			if countIndex % 2 == 1:
				if countDict[month][countIndex-1] > countDict[month][countIndex]:
					print('<td bgcolor="pink">',countDict[month][countIndex],'</td>')
				else:
					print('<td>',countDict[month][countIndex],'</td>')
			else:
				print('<td>',countDict[month][countIndex],'</td>')


		# print(*newArray, sep=' </td><td> ')
		print('</tr>')

				# print('<tr><td>')
				# print(*row, sep=' </td><td> ')
				# print('</td></tr>')
				# print('<br>')
		# print (merged_df)
		
	print('</table>')

	print('<br>')
	print('<br>')
		
	
		
def summarizedByMonth (dfCounty):

	dfCounty["year"] = dfCounty['fileDate'].str.split("/").str[2]

	dfCounty = dfCounty[pd.to_numeric(dfCounty.year, errors='coerce').notnull()]

	dfCounty["year"] = pd.to_numeric(dfCounty["year"])

	# dfCounty = dfCounty[dfCounty["year"] >= 2020]
	dfCounty = dfCounty[(dfCounty["year"] >= 2019) & (dfCounty["year"] < 2050)]

	# build the column for month 
	dfCounty['month'] = dfCounty['fileDate'].str.split("/").str[0] + '-' + dfCounty['fileDate'].str.split("/").str[2]
	dfCounty['month'][dfCounty['fileDate'].str.split("/").str[0].str.len()>1] = dfCounty['fileDate'].str.split("/").str[0] + '-' + dfCounty['fileDate'].str.split("/").str[2]
	dfCounty['month'][dfCounty['fileDate'].str.split("/").str[0].str.len()<=1] = "0"+ dfCounty['fileDate'].str.split("/").str[0] + '-' + dfCounty['fileDate'].str.split("/").str[2]
	# count the cases for each month
	dfCounty = dfCounty.groupby(['month']).size().reset_index(name = "count")

	# # only take rows for year 2020 
	# df = df[df['fileDate'].str.strip().str[6:10] == '2020']

	# # build the column for month 
	# df['month'] = df['fileDate'].str.strip().str[0:2]

	# # count the cases for each month
	# df = df.groupby(['month']).size().reset_index(name = "count")

	return dfCounty

def summarizedByMonthCobb (dfCounty):

	dfCounty["year"] = dfCounty['fileDate'].str.split("/").str[2]

	dfCounty = dfCounty[pd.to_numeric(dfCounty.year, errors='coerce').notnull()]

	dfCounty["year"] = pd.to_numeric(dfCounty["year"])

	dfCounty = dfCounty[dfCounty["year"] >= 19]

	# build the column for month 
	dfCounty['month'] = dfCounty['fileDate'].str.split("/").str[0] + '-' + "20" + dfCounty['fileDate'].str.split("/").str[2]
	dfCounty['month'][dfCounty['fileDate'].str.split("/").str[0].str.len()>1] = dfCounty['fileDate'].str.split("/").str[0] + '-' + "20" + dfCounty['fileDate'].str.split("/").str[2]
	dfCounty['month'][dfCounty['fileDate'].str.split("/").str[0].str.len()<=1] = "0"+ dfCounty['fileDate'].str.split("/").str[0] + '-' + "20" + dfCounty['fileDate'].str.split("/").str[2]
	# count the cases for each month

	# # only take rows for year 2020 
	# df = df[df['fileDate'].str.strip().str[-2:] == '20']

	# # build the column for month 

	
	# df['month'] = df['fileDate'].str.split("/").str[0]
	

	# count the cases for each month
	dfCounty = dfCounty.groupby(['month']).size().reset_index(name = "count")

	return dfCounty

if __name__ == "__main__":
	# checkMonthlyCaseCount()
    main()