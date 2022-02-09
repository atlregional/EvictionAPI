import requests
import json
import pandas as pd    
import geopandas as gpd
from geopandas.tools import sjoin
import utils.dataClean as dataClean
import warnings
warnings.filterwarnings('ignore')



def getTractData(countyCode):
    # response = requests.get('https://opendata.arcgis.com/datasets/2e73cc4a02a441ba968e6a63a8b526f5_56.geojson')
    # responseJson = response.json()
    with open('./data/Census_2010_Blockgroups_Georgia.geojson') as fp:
        responseJson = json.load(fp)

    #sample from online tract data
    #print(responseJson["features"][0]['properties'])

    #filter the data by counties
    # stateFullList = {'Cherokee':'057','Clayton':'063','Cobb':'067','DeKalb':'089','Douglas':'097','Fayette':'113',
    #                           'Fulton':'121','Gwinnett':'135','Henry':'151','Rockdale':'247'}
    # stateFullList = {'county':countyCode}
    stateCodeList = countyCode.split(',')
    filteredArrayInJson = [feature for feature in responseJson["features"] if feature['properties']['COUNTYFP10'] in stateCodeList ]
    # validate the number of tracts 
    #print(len(filteredArrayInJson))

    tractJsonForCounties = {
    "type": "FeatureCollection",
    "name": "Census_2010_Tracts_Georgia",
    "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
    "features": filteredArrayInJson}

    # read json to dataframe
    tractPolygons = gpd.GeoDataFrame.from_features(tractJsonForCounties["features"])
    return tractPolygons
#     tractPolygons.head()


def removeNullAddressAndJoinTract(rawDataIDAddressOnlyUnique,tractPolygons,fileName,filePathForWorkFolder):
    fileName = fileName[:-17]
    # export outlines with null address 

    rawDataIDAddressOnlyUniqueNull = rawDataIDAddressOnlyUnique[rawDataIDAddressOnlyUnique['Longitude']==0].drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)
    rawDataIDAddressOnlyUniqueNull.to_csv(filePathForWorkFolder + 'outlines/noAddress/'+fileName +'-NoAddress.csv')

    # remove the case with null location
    rawDataIDAddressOnlyUniqueNoNull = rawDataIDAddressOnlyUnique[rawDataIDAddressOnlyUnique['Longitude']!=0].reset_index(drop=True)
    
    
    # build geodataframe based on long lat and dataframe for case points 
    rawDataIDAddressOnlyUniqueNoNullgeoDf = gpd.GeoDataFrame(rawDataIDAddressOnlyUniqueNoNull, geometry=gpd.points_from_xy(rawDataIDAddressOnlyUniqueNoNull.Longitude, rawDataIDAddressOnlyUniqueNoNull.Latitude))
    
    simplifiedTractPolygon = tractPolygons[['geometry','GEOID10','COUNTYFP10']]
    # spatial join 
    rawDataIDAddressOnlyUniqueNoNullJoinTract = sjoin(rawDataIDAddressOnlyUniqueNoNullgeoDf, simplifiedTractPolygon, how='left')
    rawDataIDAddressOnlyUniqueNoNullJoinTract['tractID'] = rawDataIDAddressOnlyUniqueNoNullJoinTract['GEOID10']
    rawDataIDAddressOnlyUniqueNoNullJoinTract.loc[rawDataIDAddressOnlyUniqueNoNullJoinTract['GEOID10'].isnull(), 'tractID'] = 0

    # Count the number for each tract
#     for index, row in rawDataIDAddressOnlyUniqueNoNull.iterrows():
#         transformedPoint = Point(row.Longitude,row.Latitude)
#         for indexR, rowR in tractPolygons.iterrows():

#             if rowR.geometry.geom_type == 'MultiPolygon':
#                 print(rowR.GEOID10)
#             else:
#                 transformedTract = Polygon(rowR.geometry)
#                 if transformedTract.contains(transformedPoint):
#                     rawDataIDAddressOnlyUniqueNoNull.iloc[index,rawDataIDAddressOnlyUniqueNoNull.columns.get_loc('tractID')] = rowR.GEOID10
#                     break
    rawDataIDAddressOnlyUniqueNoNullLLCOnly = rawDataIDAddressOnlyUniqueNoNullJoinTract[['caseID','address','Longitude','Latitude','tractID','Score','Match_addr']].drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)
    rawDataIDAddressOnlyUniqueNoNullLLCOnly.to_csv(filePathForWorkFolder + 'updatedDataWithLatLongTract/'+fileName+'-LatLong-Tract.csv')
    
    return rawDataIDAddressOnlyUniqueNoNullJoinTract

def removeNullAddressAndUpdateJoinTract(rawDataIDAddressOnlyUnique,tractPolygons,fileName,filePathForWorkFolder):
    fileName = fileName[:-17]
    # export outlines with low quality address 

    rawDataIDAddressOnlyUniqueNull = rawDataIDAddressOnlyUnique[ (rawDataIDAddressOnlyUnique['Longitude'] == 0) | (rawDataIDAddressOnlyUnique['Score'] < 90)].drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)
    rawDataIDAddressOnlyUniqueNull.to_csv(filePathForWorkFolder + 'outlines/lowQualityAddress/'+fileName +'-LowQualityAddress.csv')

    # remove the case with null location
    #rawDataIDAddressOnlyUniqueNoNull = rawDataIDAddressOnlyUnique[(rawDataIDAddressOnlyUnique['Longitude'] != 0) & (rawDataIDAddressOnlyUnique['Score'] >= 90)].reset_index(drop=True)

    # get unspatial joined cases
    unSpatialJoinedRawData = rawDataIDAddressOnlyUnique

    # unSpatialJoinedRawData = rawDataIDAddressOnlyUniqueNoNull[rawDataIDAddressOnlyUniqueNoNull['tractID'].isnull()].reset_index(drop=True)
    # spatialJoinedRawData = rawDataIDAddressOnlyUniqueNoNull[rawDataIDAddressOnlyUniqueNoNull['tractID'].notnull()].reset_index(drop=True)
    
    #print(unSpatialJoinedRawData)
    # build geodataframe based on long lat and dataframe for case points 
    rawDataIDAddressOnlyUniqueNoNullgeoDf = gpd.GeoDataFrame(unSpatialJoinedRawData, geometry=gpd.points_from_xy(unSpatialJoinedRawData.Longitude, unSpatialJoinedRawData.Latitude))
#     print(tractPolygons)
    simplifiedTractPolygon = tractPolygons[['geometry','GEOID10','COUNTYFP10']]

    # spatial join 
    rawDataIDAddressOnlyUniqueNoNullJoinTract = sjoin(rawDataIDAddressOnlyUniqueNoNullgeoDf, simplifiedTractPolygon, how='left')
    rawDataIDAddressOnlyUniqueNoNullJoinTract['blockgroupID'] = rawDataIDAddressOnlyUniqueNoNullJoinTract['GEOID10']
    rawDataIDAddressOnlyUniqueNoNullJoinTract['tractID'] = rawDataIDAddressOnlyUniqueNoNullJoinTract['GEOID10'].str[:-1]
    rawDataIDAddressOnlyUniqueNoNullJoinTract.loc[rawDataIDAddressOnlyUniqueNoNullJoinTract['GEOID10'].isnull(), 'tractID'] = 0
    
    #concate
    updatedSpatialJoinedRawData = rawDataIDAddressOnlyUniqueNoNullJoinTract
    # updatedSpatialJoinedRawData = pd.concat([spatialJoinedRawData,rawDataIDAddressOnlyUniqueNoNullJoinTract])
    updatedSpatialJoinedRawData['address_x'] = updatedSpatialJoinedRawData['address']
    updatedSpatialJoinedRawDataLLCOnly = updatedSpatialJoinedRawData[['caseID','address_x','Longitude','Latitude','tractID','Score','Match_addr']].drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)
    updatedSpatialJoinedRawDataLLCOnly.to_csv(filePathForWorkFolder + 'updatedDataWithLatLongTract/'+fileName+'-LatLong-Tract.csv')

    updatedSpatialJoinedRawData = updatedSpatialJoinedRawData.drop(['geometry','index_right','GEOID10'], axis=1)
    
    return updatedSpatialJoinedRawData

def removeNullTractAndCount(rawDataIDAddressOnlyUniqueNoNull, fileName, filePathForWorkFolder,countyCode):
    fileName = fileName[:-17]
    # export outlines outside the county boundary
    rawDataIDAddressOnlyUniqueNullTract = rawDataIDAddressOnlyUniqueNoNull[(rawDataIDAddressOnlyUniqueNoNull['tractID']==0)&(rawDataIDAddressOnlyUniqueNoNull['Longitude'] != 0) & (rawDataIDAddressOnlyUniqueNoNull['Score'] >= 90)].drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)
    rawDataIDAddressOnlyUniqueNullTract.to_csv(filePathForWorkFolder + 'outlines/outOfBoundary/'+ fileName + '-OutOfBoundary.csv')

    #change the tractid to 99999999999 for score less than 90 , tractid ==0 
    rawDataIDAddressOnlyUniqueNoNull.loc[rawDataIDAddressOnlyUniqueNoNull['Score'] < 90, 'tractID'] = '99999999999' 
    rawDataIDAddressOnlyUniqueNoNull.loc[rawDataIDAddressOnlyUniqueNoNull['Score'] < 90, 'blockgroupID'] = '99999999999'
    rawDataIDAddressOnlyUniqueNoNull.loc[rawDataIDAddressOnlyUniqueNoNull['tractID'] == 0, 'tractID'] = '99999999999'
    rawDataIDAddressOnlyUniqueNoNull.loc[rawDataIDAddressOnlyUniqueNoNull['blockgroupID'] == 0, 'blockgroupID'] = '99999999999'
    # for fulton specificly 
    rawDataIDAddressOnlyUniqueNoNull.loc[rawDataIDAddressOnlyUniqueNoNull['tractID'].isnull(), 'tractID'] = '99999999999'
    rawDataIDAddressOnlyUniqueNoNull.loc[rawDataIDAddressOnlyUniqueNoNull['blockgroupID'].isnull(), 'blockgroupID'] = '99999999999'

    rawDataIDAddressOnlyUniqueNoNull['tractID'] = rawDataIDAddressOnlyUniqueNoNull.tractID.astype('int64').astype(str)

    rawDataIDAddressOnlyUniqueNoNull.loc[rawDataIDAddressOnlyUniqueNoNull['tractID']== '99999999999', 'COUNTYFP10'] = countyCode

    
    # print(rawDataIDAddressOnlyUniqueNoNull['tractID'].head())

    # some cases are out of boundary thus the case id is 0 ? Todo
    #rawDataIDAddressOnlyUniqueNoNullTract = rawDataIDAddressOnlyUniqueNoNull[(rawDataIDAddressOnlyUniqueNoNull['tractID']!=0)&(rawDataIDAddressOnlyUniqueNoNull['Longitude'] != 0) & (rawDataIDAddressOnlyUniqueNoNull['Score'] >= 90)].reset_index(drop=True)
    rawDataIDAddressOnlyUniqueNoNullTract = rawDataIDAddressOnlyUniqueNoNull
    rawDataIDAddressOnlyUniqueNoNullTract = dataClean.cleanAddress(rawDataIDAddressOnlyUniqueNoNullTract,"Match_addr","address_x").drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)
    rawDataIDAddressOnlyUniqueNoNullTract.to_csv(filePathForWorkFolder + 'dataByIndividual/'+fileName+'-final.csv')

    #cleaned data only have address caseID longitude and latitude
    rawDataIDAddressOnlyUniqueNoNullTractCleaned = rawDataIDAddressOnlyUniqueNoNullTract[['caseID','address','Longitude','Latitude']].drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)
    rawDataIDAddressOnlyUniqueNoNullTractCleaned.to_csv(filePathForWorkFolder + 'cleanedGeocodedCases/'+fileName+'-cleaned.csv')
    
    # #leave the data for additional 
    # rawDataIDAddressOnlyUniqueNoNullCaseStatusOnly = rawDataIDAddressOnlyUniqueNoNullTract[['caseID','fileDate','Case.Status','Address','Longitude','Latitude','tractID','COUNTYFP10']]
    # rawDataIDAddressOnlyUniqueNoNullCaseStatusOnly.to_csv('../../data/caseStatus/'+fileName+'-caseStatus.csv')

    #count the cases by filling time and census tract 
    rawDataIDAddressOnlyUniqueNoNullGrouped = rawDataIDAddressOnlyUniqueNoNullTract.groupby(['fileDate','tractID','COUNTYFP10'], sort=False).size().reset_index(name='Total Filings')
    rawDataIDAddressOnlyUniqueNoNullGrouped.to_csv(filePathForWorkFolder + 'updateByTractSeperate/'+ fileName +'-generalCountByDateTract.csv')
    rawDataIDAddressOnlyUniqueNoNullGrouped['joinID'] = rawDataIDAddressOnlyUniqueNoNullGrouped['fileDate'] + rawDataIDAddressOnlyUniqueNoNullGrouped['tractID']


    rawDataIDAddressOnlyUniqueNoNullGroupedAnswered = rawDataIDAddressOnlyUniqueNoNullTract.groupby(['fileDate','tractID','COUNTYFP10','ifAnswered'], sort=False).size().reset_index(name='Total Filings')
    rawDataIDAddressOnlyUniqueNoNullGroupedAnswered.to_csv(filePathForWorkFolder + 'updateByTractSeperate/'+ fileName +'-AnswerCountByDateTract.csv')

    rawDataIDAddressOnlyUniqueNoNullGroupedAnswered = rawDataIDAddressOnlyUniqueNoNullGroupedAnswered[rawDataIDAddressOnlyUniqueNoNullGroupedAnswered['ifAnswered'] == 1]
    rawDataIDAddressOnlyUniqueNoNullGroupedAnswered['Total Answered Filings'] = rawDataIDAddressOnlyUniqueNoNullGroupedAnswered['Total Filings']
    
    rawDataIDAddressOnlyUniqueNoNullGroupedAnswered['joinID'] = rawDataIDAddressOnlyUniqueNoNullGroupedAnswered['fileDate'] + rawDataIDAddressOnlyUniqueNoNullGroupedAnswered['tractID']
    rawDataIDAddressOnlyUniqueNoNullGroupedAnswered = rawDataIDAddressOnlyUniqueNoNullGroupedAnswered.drop(['Total Filings','fileDate','tractID','COUNTYFP10','ifAnswered'], axis=1)

    rawDataIDAddressOnlyUniqueNoNullGroupedAll = pd.merge(rawDataIDAddressOnlyUniqueNoNullGrouped, rawDataIDAddressOnlyUniqueNoNullGroupedAnswered, on='joinID', how='left')
    rawDataIDAddressOnlyUniqueNoNullGroupedAll = rawDataIDAddressOnlyUniqueNoNullGroupedAll.drop(['joinID'], axis=1)
    rawDataIDAddressOnlyUniqueNoNullGroupedAll['Total Answered Filings'].fillna(0, inplace=True)

    rawDataIDAddressOnlyUniqueNoNullGroupedAll['Total Answered Filings'] = rawDataIDAddressOnlyUniqueNoNullGroupedAll['Total Answered Filings'].astype(int)

    rawDataIDAddressOnlyUniqueNoNullGroupedAll.to_csv(filePathForWorkFolder + 'updateByTract/'+ fileName +'-generalCountByDateTract.csv')
    #rawDataIDAddressOnlyUniqueNoNullGrouped.head()