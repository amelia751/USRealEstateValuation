

!pip install -q streamlit
!pip install -q pyngrok

%%writefile app.py
import streamlit as st
from sklearn.linear_model import LinearRegression
import requests
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from array import *
import time
from datetime import datetime
import statistics
import requests
import json
import pandas as pd
import sklearn.metrics

PAGE_CONFIG = {"page_title":"US Real Estate Valuation","page_icon":":smiley:","layout":"centered"}
st.set_page_config(**PAGE_CONFIG)
def main():
    st.title("Estimating Home Prices Using Regression and Machine Learning")
    menu = ["Home","Creators"]
    choice = st.sidebar.selectbox('Menu',menu)
    if choice == 'Home':
      st.subheader("Please Enter Your Parameters")
      zipcode = st.text_input('Enter the Zipcode', value = '0', max_chars=5)
      beds = st.slider('Enter Number of Beds', 0, 10, 0, 1)
      baths = st.slider('Enter Number of Baths', 0.0, 10.0, 0.0, 0.5, format='%f')
      squarefootage = st.number_input('Enter the Square Footage of Home', value = 0,format = '%d')
      yearbuilt = st.number_input('Enter the Age of Your Home (2021-Year Built)', value = 0,format = '%d')
      mortgage_rate = st.number_input('Enter the 30 Year Fixed Mortgage Rate(3% = 3)')
      hoa_fee = st.number_input('Enter in the HOA Fees of the Home (If None Enter 0)')
      if st.button('Give Me Predicted Price'):
        import requests
        import json
        import pandas as pd
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
        sorted_zipcodes = find_zipcodes(str(zipcode), '5')
        st.write(sorted_zipcodes)
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
              yrbuilt.sppend(50)
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



        z = np.abs(stats.zscore(df['Value']))
        arr = np.where(z>3)
        list1 = list(arr)
        for i in list1:
          list2 = list(i)
        df = df.drop(index = list2)
        z = np.abs(stats.zscore(df['Value']))
        arr = np.where(z>3)
        list1 = list(arr)
        for i in list1:
          list2 = list(i)
        df = df.drop(index = list2)
        st.dataframe(df)
        lr = LinearRegression()

        da = df.drop(labels = ['Value', 'Address', 'States', 'Zipcode'], axis = 1)

        X = df.drop(labels = ['Value', 'Address', 'States', 'Zipcode'], axis = 1)
        Y = df['Value']
        lr.fit(X,Y)

        intercept = lr.intercept_

        yo = pd.DataFrame(zip(da.columns, lr.coef_), columns = ["features", "coefficients"])

        bedco = yo['coefficients'][2]
        bathco = yo['coefficients'][3]
        sqftco = yo['coefficients'][1]
        yrbuiltco = yo['coefficients'][0]
        mortgageco = yo['coefficients'][4]
        hoaco = yo['coefficients'][5]

        predictedprice = (beds*bedco+baths*bathco+squarefootage*sqftco+yearbuilt*yrbuiltco+mortgage_rate*mortgageco+hoa_fee*hoaco+intercept)
        st.write('Your Predicted Price Is: $'+ format(predictedprice, ',.2f'))
        st.write('The Aggregate Price Per Square Foot of Recently Sold Properties In Your Area Is', '$'+str(format(sum(df['Value'])/sum(df['Living Area (Square Feet)']),',.2f')),'Per Square Foot')
        st.write('There Are', statistics.mean(schools), 'Nearby Schools In Your Area')
        lr = LinearRegression()

        da = df.drop(labels = ['Value', 'Address', 'States', 'Zipcode'], axis = 1)

        X = df.drop(labels = ['Value', 'Address', 'States', 'Zipcode'], axis = 1)
        Y = df['Value']
        lr.fit(X,Y)

        intercept = lr.intercept_

        yo = pd.DataFrame(zip(da.columns, lr.coef_), columns = ["features", "coefficients"])
        st.dataframe(yo)




        fig,ax = plt.subplots()
        ax.scatter(df['Age of Structure'],df['Value'])
        plt.xlabel("Age of Structure")
        plt.ylabel("Price")
        plt.title("Relationship between Age of Structure and Price")
        st.pyplot(fig)


        fig,ax = plt.subplots()
        ax.scatter(df['Number of baths'], df['Value'], color='r')
        plt.xlabel("Baths")
        plt.ylabel("Price")
        plt.title("Relationship between Baths and Price")
        st.pyplot(fig)


        fig,ax = plt.subplots()
        ax.scatter(df['Number of beds'], df['Value'], color = 'g')
        plt.xlabel("Beds")
        plt.ylabel("Price")
        plt.title("Relationship between Beds and Price")
        st.pyplot(fig)


        fig,ax = plt.subplots()
        ax.scatter(df['HOA Fee'], df['Value'], color = 'y')
        plt.xlabel("HOA Fee")
        plt.ylabel("Price")
        plt.title("Relationship between HOA Fee and Price")
        st.pyplot(fig)



        fig,ax = plt.subplots()
        ax.scatter(df['Living Area (Square Feet)'], df['Value'], color = 'c')
        plt.xlabel('Square Footage')
        plt.ylabel('Price')
        plt.title('Relationship between Square Footage and Price')
        st.pyplot(fig)





        Y_p = lr.predict(X)
        fig,ax = plt.subplots()
        ax.scatter(Y, Y_p, color='r', label='predicted data', alpha=0.6)
        ax.scatter(Y, Y, color='b', label='true data', alpha=0.7)
        plt.xlabel("True prices")
        plt.ylabel("Predicted prices")
        plt.title("Relationship between true prices and predicted prices")
        st.pyplot(fig)
        st.write("R2:", sklearn.metrics.r2_score(Y, Y_p))


if __name__ == '__main__':
    main()

!streamlit run app.py &>/dev/null &
from pyngrok import ngrok
public_url = ngrok.connect(8501)
public_url

!pgrep streamlit
ngrok.kill()
