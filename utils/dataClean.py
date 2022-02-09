import pandas as pd
import warnings

warnings.filterwarnings('ignore')

def cleanAddress(geocodedDataFrame, geocodedAddressField, originalAddressField):
	
	geocodedDataFrame['matchingAfterClean'] = 0
	geocodedDataFrame['cleanedAddress'] = 'N/A'

	for index, row in geocodedDataFrame.iterrows():
		if not pd.isna(row[geocodedAddressField]):
			addressArray = row[geocodedAddressField].lower().split(",")
			if len(addressArray) >= 3:
				street = addressArray[0]
				zipCode = addressArray[len(addressArray) - 1]
				state = addressArray[len(addressArray) - 2]
				city = addressArray[len(addressArray) - 3]

				cleanedAddress = street + ', ' + city + ', ' + state + ', ' + zipCode
				geocodedDataFrame.at[index,'cleanedAddress'] = cleanedAddress

				# if matching original ? 
				if not pd.isna(row[originalAddressField]):
					orginalAddressArray = row[originalAddressField].lower().split(",")
					if addressArray[0] == orginalAddressArray[0]:
						geocodedDataFrame.at[index,'matchingAfterClean'] = 1

	return geocodedDataFrame
