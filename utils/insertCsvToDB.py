
import csv
import psycopg2
from dotenv import load_dotenv, find_dotenv
import os
from pathlib import Path  # Python 3.6+ only
import datetime

def main():
	env_path = Path('../') / '.env'
	load_dotenv(dotenv_path=env_path)
	print(os.getenv("dbHost"))

def insertDataFromcsvToDB(filePathForWorkFolder, fileName):

	env_path = Path('../') / '.env'
	load_dotenv(dotenv_path=env_path)

	conn = psycopg2.connect("host="+os.getenv("dbHost")+ " port="+ os.getenv("dbPort") + " dbname=" + os.getenv("dbName") + " user=" + os.getenv("dbUser") + " password=" + os.getenv("dbPassword"))

	cur = conn.cursor()

	fileName = fileName[:-17]

	# cur.execute("""CREATE TABLE IF NOT EXISTS data.atlanta_metro_area_tract(
	# 	id integer ,
	#     FileDate text,
	#     tractID text,
	#     COUNTYFP10 text,
	#     TotalFilings integer,
	#     TotalAnsweredFilings integer,
	#     indexID text PRIMARY KEY
	# )
	# """)

	with open(filePathForWorkFolder + 'updateByTract/'+ fileName + '-generalCountByDateTract.csv', 'r') as f:
		reader = csv.reader(f)
		next(reader) # Skip the header row.
		for row in reader:
			row.append(row[1]+row[2]+row[3])
			cur.execute("SELECT EXISTS(SELECT 1 FROM data.atlanta_metro_area_tract WHERE filedate = %s AND tractid = %s AND countyfp10 = %s  )", [row[1],row[2],row[3]])
			# if exsits update else insert 
			if cur.fetchone()[0]:
				cur.execute("Update data.atlanta_metro_area_tract set  totalansweredfilings= %s WHERE filedate = %s AND tractid = %s AND countyfp10 = %s ", 
					(row[5], row[1], row[2], row[3])
				)
				# pass
			else:
				cur.execute(
					"INSERT INTO data.atlanta_metro_area_tract VALUES (%s, %s, %s, %s, %s, %s, %s)", row
				)	

	conn.commit()


def insertFultonDataFromcsvToDB(filePathForWorkFolder):
	env_path = Path('../') / '.env'
	load_dotenv(dotenv_path=env_path)

	conn = psycopg2.connect("host="+os.getenv("dbHost")+ " port="+ os.getenv("dbPort") + " dbname=" + os.getenv("dbName") + " user=" + os.getenv("dbUser") + " password=" + os.getenv("dbPassword"))
	cur = conn.cursor()
	with open(filePathForWorkFolder + 'dataByIndividual/2020FultonCountyEvictionCaseEvents--final.csv', 'r') as f:
		reader = csv.reader(f)
		next(reader) # Skip the header row.
		for row in reader:
			cur.execute("SELECT EXISTS(SELECT 1 FROM data.fulton_county_case WHERE caseid = %s )", [row[2]])
			# if exsits update else insert 
			if cur.fetchone()[0]:
				cur.execute("Update data.fulton_county_case set filedate = %s WHERE caseid = %s ", 
					(row[1], row[2])
				)
			else:
				cur.execute(
					"INSERT INTO data.fulton_county_case VALUES (%s, %s)", [row[1], row[2]]
				)	

	conn.commit()


def insertCaseLevelDataFromcsvToDB(filePathForWorkFolder, fileName):

	env_path = Path('../') / '.env'
	load_dotenv(dotenv_path=env_path)

	conn = psycopg2.connect("host="+os.getenv("dbHost")+ " port="+ os.getenv("dbPort") + " dbname=" + os.getenv("dbName") + " user=" + os.getenv("dbUser") + " password=" + os.getenv("dbPassword"))

	cur = conn.cursor()

	fileName = fileName[:-17]

	with open(filePathForWorkFolder + 'dataByIndividual/'+ fileName + '-final.csv', 'r', encoding='utf-8') as f:
		reader = csv.reader(f)
		next(reader) # Skip the header row.
		for row in reader:
			#use caseid + tractID + countycode as 
			uniqueId = row[2] + row[41] + row[44]
			tractid = row[41]
			blockgroupid = row[45]
			if row[47] != "N/A":
				street = row[47].split(",")[0]
				city = row[47].split(",")[1]
				zipcode = row[47].split(",")[3]
			else:
				street = ""
				city = ""
				zipcode = ""

			if (len(row[1].split('/')[2]) == 2):
				fileDate = datetime.datetime.strptime(row[1],'%m/%d/%y').strftime('%m/%d/%Y')
			else:
				#print(row[1])
				fileDate = datetime.datetime.strptime(row[1],'%m/%d/%Y').strftime('%m/%d/%Y')
				#print(fileDate)

			if row[23] != "N/A":
				if (len(row[23].split(' ')[0].split('/')[2]) == 2):
					answerDate = datetime.datetime.strptime(row[23].split(' ')[0],'%m/%d/%y').strftime('%m/%d/%Y')
				else:
					#print(row[1])
					answerDate = datetime.datetime.strptime(row[23].split(' ')[0],'%m/%d/%Y').strftime('%m/%d/%Y')
			else:
				answerDate = "9999-12-12"

			if row[26] != "N/A":
				if (len(row[26].split(' ')[0].split('/')[2]) == 2):
					serviceDate = datetime.datetime.strptime(row[26].split(' ')[0],'%m/%d/%y').strftime('%m/%d/%Y')
				else:
					#print(row[1])
					serviceDate = datetime.datetime.strptime(row[26].split(' ')[0],'%m/%d/%Y').strftime('%m/%d/%Y')
			else:
				serviceDate = "9999-12-12"

			if row[29] != "N/A":
				if (len(row[29].split(' ')[0].split('/')[2]) == 2):
					dismissDate = datetime.datetime.strptime(row[29].split(' ')[0],'%m/%d/%y').strftime('%m/%d/%Y')
				else:
					#print(row[29])
					dismissDate = datetime.datetime.strptime(row[29].split(' ')[0],'%m/%d/%Y').strftime('%m/%d/%Y')
			else:
				dismissDate = "9999-12-12"

			if row[32] != "N/A":
				if (len(row[32].split(' ')[0].split('/')[2]) == 2):
					defaultJudgmentDate = datetime.datetime.strptime(row[32].split(' ')[0],'%m/%d/%y').strftime('%m/%d/%Y')
				else:
					#print(row[32])
					defaultJudgmentDate = datetime.datetime.strptime(row[32].split(' ')[0],'%m/%d/%Y').strftime('%m/%d/%Y')
			else:
				defaultJudgmentDate = "9999-12-12"

			if row[35] != "N/A":
				if (len(row[35].split(' ')[0].split('/')[2]) == 2):
					judgmentDate = datetime.datetime.strptime(row[35].split(' ')[0],'%m/%d/%y').strftime('%m/%d/%Y')
				else:
					#print(row[35])
					judgmentDate = datetime.datetime.strptime(row[35].split(' ')[0],'%m/%d/%Y').strftime('%m/%d/%Y')
			else:
				judgmentDate = "9999-12-12"
				
			cur.execute("SELECT EXISTS(SELECT 1 FROM data.atlanta_metro_area_case WHERE id = %s  )", [uniqueId])
			# if exsits update else insert 
			if cur.fetchone()[0]:
				cur.execute("Update data.atlanta_metro_area_case set filingdate = %s, answer = %s, latitude= %s, longitude= %s, services= %s,dismiss= %s,defaultJudgment= %s,judgment= %s,answerdate= %s,servicesdate= %s,dismissdate= %s,defaultJudgmentdate= %s,judgmentdate= %s,tractid= %s,blockgroupid= %s WHERE id = %s ", 
					(fileDate, row[24], row[40], row[39], row[27],row[30],row[33],row[36],answerDate,serviceDate,dismissDate,defaultJudgmentDate,judgmentDate,tractid,blockgroupid, uniqueId)
				)
			else:
				# id, street, city, zip, filingdate, answer, county, latitude, longitude,services,dismiss,defaultJudgment,judgment,answerdate,servicesdate,dismissdate,defaultJudgmentdate,judgmentdate,tractid,blockgroupid
				cur.execute(
					"INSERT INTO data.atlanta_metro_area_case VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s)",
					[uniqueId, street, city, zipcode, fileDate, row[24], row[44], row[40], row[39],row[27],row[30],row[33],row[36],answerDate,serviceDate,dismissDate,defaultJudgmentDate,judgmentDate,tractid,blockgroupid]
				)	

	conn.commit()

if __name__ == "__main__":
    main()