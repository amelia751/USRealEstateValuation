import requests
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import time
from datetime import datetime
import statistics
import json
import pandas as pd
from sklearn.linear_model import LinearRegression
import sklearn.metrics

def find_zipcodes(zipcode, distance):
    response = requests.request('GET', 'https://www.zipcodeapi.com/rest/ErXy4y4jfP0Gd6UPHt0cBaouadBic2Qa68wKpnP0hXPObXJarASoMmymdn8vIMOQ/radius.json/'+zipcode+'/'+distance+'/mile')
    data = json.loads(response.text)
    zipcodes = []
    for i in data['zip_codes']:
        zipcodes.append(i['distance'])
    zipcodes = sorted(zipcodes)
    distance = {}
    sorted_zipcodes = []
    for i in zipcodes:
        for b in data['zip_codes']:
            if b['distance'] == i:
                distance[b['zip_code']] = i
                sorted_zipcodes.append(b['zip_code'])
    return sorted_zipcodes

def main(zipcode, beds, baths, squarefootage, yearbuilt, mortgage_rate, hoa_fee):
    sorted_zipcodes = find_zipcodes(str(zipcode), '5')
    print(sorted_zipcodes)
    zipid = []

    addresses = []
    states = []
    city = []
    zipcode = []
    yrbuilt = []
    bedroom = []
    bathroom = []
    squareft = []
    timeonzillow = []
    values = []
    mortgagerate = []
    hoafee = []
    schools = []
    ratings = []
    cnt = 0
    global df
    for i in sorted_zipcodes:
        while True:
            url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"

            querystring = {"location":i,"home_type":"Apartments","status_type": "RecentlySold"}

            headers = {
                "x-rapidapi-key": "877053884amsh712c649858a2b59p11ac6djsnde4ade5ad458",
                "x-rapidapi-host": "zillow-com1.p.rapidapi.com"
                }


            response = requests.request("GET", url, headers=headers, params=querystring)
            prop_info = json.loads(response.text)

            try:
                if prop_info['message'] == 'You have exceeded the rate limit per second for your plan, PRO, by the API provider':
                    time.sleep(1)

                continue
            except:
                break

        try:
            for prop in prop_info["props"]:
                zipid.append(prop['zpid'])
        except:
            continue
        time.sleep(0.5)
        if len(zipid)>=200:
            break
    del zipid[200:-1]
    time.sleep(0.5)
    for i in zipid:
        while True:
            url = "https://zillow-com1.p.rapidapi.com/property"

            querystring = {'zpid':i}

            headers = {
                "x-rapidapi-key": "877053884amsh712c649858a2b59p11ac6djsnde4ade5ad458",
                "x-rapidapi-host": "zillow-com1.p.rapidapi.com"
                }


            response = requests.request("GET", url, headers=headers, params=querystring)
            prop_info = json.loads(response.text)
            try:
                if prop_info['message'] == 'You have exceeded the rate limit per second for your plan, PRO, by the API provider':
                    time.sleep(0.5)
                    continue
            except:
                break

        if prop_info['livingArea'] == None or prop_info['price']<100000:
            continue
        else:
            squareft.append(prop_info['livingArea'])
            values.append(prop_info['price'])

        addresses.append(prop_info['address']['streetAddress'])
        states.append(prop_info['address']['state'])
        city.append(prop_info['address']['city'])
        zipcode.append(prop_info['address']['zipcode'])

        if prop_info['bathrooms'] == None:
            bathroom.append(0)
        else:
            bathroom.append(prop_info['bathrooms'])
        if prop_info['bedrooms'] == None:
            bedroom.append(0)
        else:
            bedroom.append(prop_info['bedrooms'])
        if prop_info['yearBuilt'] == None:
            try:
                yrbuilt.append(statistics.mean(yrbuilt))
            except:
                yrbuilt.append(50)
        else:
            yrbuilt.append(2021 - prop_info['yearBuilt'])
        if prop_info['mortgageRates']['thirtyYearFixedRate'] == None:
            mortgagerate.append(3)
        else:
            mortgagerate.append(prop_info['mortgageRates']['thirtyYearFixedRate'])
        if prop_info['hoaFee'] == None:
            hoafee.append(0)
        else:
            hoafee.append(prop_info['hoaFee'])
        schools.append(len('schools'))
    df = pd.DataFrame({
        "Address": addresses,
        "States": states,
        "Zipcode":zipcode,
        "Age of Structure":yrbuilt,
        'Living Area (Square Feet)':squareft,
        "Value": values,
        "Number of beds": bedroom,
        "Number of baths": bathroom,
        "Thirty Year Fixed Mortgage Rate": mortgagerate,
        'HOA Fee':hoafee,
        'Number of Nearby Schools':schools})

    fig, axs = plt.subplots(2, 3, figsize=(15, 10))
    
    axs[0, 0].scatter(df['Age of Structure'], df['Value'])
    axs[0, 0].set_title('Age of Structure vs Price')
    
    axs[0, 1].scatter(df['Number of baths'], df['Value'], color='r')
    axs[0, 1].set_title('Baths vs Price')
    
    axs[0, 2].scatter(df['Number of beds'], df['Value'], color='g')
    axs[0, 2].set_title('Beds vs Price')
    
    axs[1, 0].scatter(df['HOA Fee'], df['Value'], color='y')
    axs[1, 0].set_title('HOA Fee vs Price')
    
    axs[1, 1].scatter(df['Square Footage'], df['Value'], color='c')
    axs[1, 1].set_title('Square Footage vs Price')
    
    plt.tight_layout()
    plt.show()

    print(df.head()) 

# Example usage
main('10001', 3, 2, 1500, 10, 3.5, 250)

