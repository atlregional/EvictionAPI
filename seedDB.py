import json
import utils.dataReader as dataReader
import utils.insertCsvToDB as insertCsvToDB
import warnings

warnings.filterwarnings('ignore')


def main():
    with open('./config.json') as configFile:
        config = json.load(configFile)

    filePathForWorkFolder = config['filePathForWorkFolder']
    filePathForWorkFolderRawData = config['filePathForWorkFolderRawData']
    counties = config['counties']

    fileNamePool, countyCodePool = dataReader.findRawData(
        filePathForWorkFolderRawData, counties)

    print('')
    for filename in fileNamePool:
        print('Updating DB with:', filename)

        insertCsvToDB.insertDataFromcsvToDB(
            filePathForWorkFolder, filename)

        insertCsvToDB.insertCaseLevelDataFromcsvToDB(
            filePathForWorkFolder, filename)


if __name__ == "__main__":
    main()
