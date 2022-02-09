
import json
import pandas as pd
import requests
import warnings

warnings.filterwarnings('ignore')

def main():
	with open('./config.json') as configFile:
		config = json.load(configFile)

	counties = config['counties']

	# call the API
	r = requests.get('https://evictions.design.gatech.edu/rest/atlanta_metro_area_tracts')
	x = r.json()
	df = pd.DataFrame(x)
	print('<br>')
	print('<br>')
	print('Database Snapshot',': <br> ')

	allData = {}

	for key2 in counties:
		countyName = counties[key2] + ' County'
		if counties[key2] != "Cobb":
			
			dfCounty = df[df['countyfp10'] == key2]

			dfCounty["year"] = dfCounty['filedate'].str.split("/").str[2]

			dfCounty = dfCounty[pd.to_numeric(dfCounty.year, errors='coerce').notnull()]

			dfCounty["year"] = pd.to_numeric(dfCounty["year"])

			dfCounty = dfCounty[(dfCounty["year"] >= 2019) & (dfCounty["year"] < 2050)]

			dfCounty = dfCounty[['filedate','countyfp10','totalfilings','indexid']]

			# build the column for month 
			dfCounty['month'] = dfCounty['filedate'].str.split("/").str[0] + '-' + dfCounty['filedate'].str.split("/").str[2]
			dfCounty['month'][dfCounty['filedate'].str.split("/").str[0].str.len()>1] = dfCounty['filedate'].str.split("/").str[0] + '-'  + dfCounty['filedate'].str.split("/").str[2]
			dfCounty['month'][dfCounty['filedate'].str.split("/").str[0].str.len()<=1] = "0"+ dfCounty['filedate'].str.split("/").str[0] + '-'  + dfCounty['filedate'].str.split("/").str[2]
			# count the cases for each month
			dfCounty = dfCounty.groupby(['month']).sum().reset_index()

			# print(countyName,': <br> ')

			# for row in dfCounty.values.tolist():
			# 	print(*row, sep=' --- ')
			# 	print('<br>')
			# print('<br>')
			# print('<br>')

		else:
			dfCounty = df[df['countyfp10'] == key2]

			dfCounty["year"] = dfCounty['filedate'].str.split("/").str[2]

			dfCounty = dfCounty[pd.to_numeric(dfCounty.year, errors='coerce').notnull()]

			dfCounty["year"] = pd.to_numeric(dfCounty["year"])

			dfCounty = dfCounty[dfCounty["year"] >= 19]

			dfCounty = dfCounty[['filedate','countyfp10','totalfilings','indexid']]

			# build the column for month 
			# dfCounty['month'] = dfCounty['filedate'].str.split("/").str[0] + '-' +dfCounty['filedate'].str.split("/").str[2]
			dfCounty['month'] = dfCounty['filedate'].str.strip().str[0:2] + '-' +dfCounty['filedate'].str.strip().str[6:10]
			dfCounty['month'][dfCounty['filedate'].str.split("/").str[0].str.len()>1] = dfCounty['filedate'].str.split("/").str[0] + '-' + "20" + dfCounty['filedate'].str.split("/").str[2]
			dfCounty['month'][dfCounty['filedate'].str.split("/").str[0].str.len()<=1] = "0"+ dfCounty['filedate'].str.split("/").str[0] + '-' + "20" + dfCounty['filedate'].str.split("/").str[2]
			# count the cases for each month
			dfCounty = dfCounty.groupby(['month']).sum().reset_index()

			# print(countyName,': <br> ')

			# for row in dfCounty.values.tolist():
			# 	print(*row, sep=' --- ')
			# 	print('<br>')
			# print('<br>')
			# print('<br>')

		allData[countyName]={}
		allData[countyName]['df'] = dfCounty

	titleLine = '<tr><td>Filing Month/Year</td>'
	countDict = {}
	for countyName in allData:
		titleLine = titleLine + '<td>'+ countyName + '</td>'
		for row in allData[countyName]['df'].values.tolist():
			if row[0] in countDict:
				countDict[row[0]] = countDict[row[0]] + row[1:]
			else:
				countDict[row[0]] = row[1:]
	titleLine = titleLine + '</tr>'

	print('<table>')
	print(titleLine)
	for month in countDict:
		# newArray = [month] + countDict[month]
		print('<tr><td>',month,'</td>')
		for countIndex in range(len(countDict[month])):

			print('<td>',countDict[month][countIndex],'</td>')

		print('</tr>')
	print('</table>')
	print('<br>')
	print('<br>')


if __name__ == "__main__":
	# checkMonthlyCaseCount()
    main()