from arcgis.gis import GIS
from arcgis.geocoding import geocode
import pandas as pd
import warnings
import time
from os.path import exists
import numpy as np

warnings.filterwarnings('ignore')

def geocoding(rawDataIDAddressOnlyUnique):
    gis = GIS()
    rawDataIDAddressOnlyUnique['Longitude'] = 0
    rawDataIDAddressOnlyUnique['Latitude'] = 0
    rawDataIDAddressOnlyUnique['Score'] = 0
    rawDataIDAddressOnlyUnique['Match_addr'] = ''
    for index, row in rawDataIDAddressOnlyUnique.iterrows():
        # if index != 0 and index % 500 == 0:
        #     print(index)
        #     time.sleep(60)
        geoAddress = geocode(row.address)
        if(geoAddress):
            location = geoAddress[0]['location']
            rawDataIDAddressOnlyUnique.iloc[index, rawDataIDAddressOnlyUnique.columns.get_loc('Longitude')] = location['x']
            rawDataIDAddressOnlyUnique.iloc[index, rawDataIDAddressOnlyUnique.columns.get_loc('Latitude')] = location['y']
            rawDataIDAddressOnlyUnique.iloc[index, rawDataIDAddressOnlyUnique.columns.get_loc('Score')] = geoAddress[0]['score']
            rawDataIDAddressOnlyUnique.iloc[index, rawDataIDAddressOnlyUnique.columns.get_loc('Match_addr')] = geoAddress[0]['attributes']['Match_addr']

    #rawDataIDAddressOnlyUniqueLLOnly = rawDataIDAddressOnlyUnique[['Case.ID','Longitude','Latitude']]
    #rawDataIDAddressOnlyUniqueLLOnly.to_csv('./data/DataWithLatLong/'+ fileName + '-LatLong.csv')
    return rawDataIDAddressOnlyUnique
    # rawDataIDAddressOnlyUnique.head()


#join the data already geocoded, do the rest 
def updateGeoCoding(rawDataIDAddressOnlyUnique,fileName,filePathForWorkFolder):
    
    fileName = fileName[:-17]
    #read the geocoded data
    if exists(filePathForWorkFolder +'updatedDataWithLatLongTract/' + fileName + '-LatLong-Tract.csv'):
        geocodedData = pd.read_csv(r'%s' %(filePathForWorkFolder +'updatedDataWithLatLongTract/' + fileName + '-LatLong-Tract.csv')).drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)
        
        #join the spatial info
        joinedRawData = pd.merge(rawDataIDAddressOnlyUnique, geocodedData, on='caseID', how='left')
        
        cleanedJoinedRawData = joinedRawData.drop(['Unnamed: 0'], axis=1)
    else:
        cleanedJoinedRawData = rawDataIDAddressOnlyUnique
        cleanedJoinedRawData['address_x']= np.nan
        cleanedJoinedRawData['Longitude'] = np.nan
        cleanedJoinedRawData['Latitude']= np.nan
        cleanedJoinedRawData['tractID']= np.nan
        cleanedJoinedRawData['Score']= np.nan
        cleanedJoinedRawData['Match_addr']= np.nan
    
    ungeocodedRawData = cleanedJoinedRawData[cleanedJoinedRawData['Longitude'].isnull()].drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)
    geocodedRawData = cleanedJoinedRawData[cleanedJoinedRawData['Longitude'].notnull()].drop_duplicates(subset='caseID', keep="first").reset_index(drop=True)
    
    # gis = GIS()
    # for index, row in ungeocodedRawData.iterrows():

    #     geoAddress = geocode(row.Address)
    #     if(geoAddress):
    #         location = geoAddress[0]['location']
    #         ungeocodedRawData.iloc[index, ungeocodedRawData.columns.get_loc('Longitude')] = location['x']
    #         ungeocodedRawData.iloc[index, ungeocodedRawData.columns.get_loc('Latitude')] = location['y']

    print('Number of new cases of the last week' +': ', ungeocodedRawData.shape[0],' <br> ')
    print('----------<br>')
    
    ungeocodedRawData.to_csv(filePathForWorkFolder + 'dataByIndividual/'+ fileName + '-ungeocoded.csv')

    ungeocodedRawData = geocoding(ungeocodedRawData)
    
    updatedGeocodedRawData = pd.concat([geocodedRawData,ungeocodedRawData])
    
    # updatedGeocodedRawData.to_csv(fileName + '.csv')
    
    return updatedGeocodedRawData

