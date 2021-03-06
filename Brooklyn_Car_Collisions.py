# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 08:29:29 2020

@author: mohamed
"""

#In this project we will try to identify the most risky zip codes in Brooklyn to drive, Cycle, MotorCycle, or cross the streets in there.
# we will use web scrapping to get Brooklyn Zip codes and we will use these zip codes to make requests to the NYC Open Auto Collisions API

#importing libraries
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

#1- SCarp Brooklyn ZIp Codes from https://www.zip-codes.com/city/ny-brooklyn.asp:
url="https://www.zip-codes.com/city/ny-brooklyn.asp"

html_content = requests.get(url)
soup = BeautifulSoup(html_content.content, "html.parser")

#find the table by tableID
table=soup.find(id="tblZIP")


#Create 5lists that will hold the data of the 5 columns (a list for every colum)
l1=[]
l2=[]
l3=[]
l4=[]
l5=[]


for row in table.findAll('tr'):
    cells=row.findAll('td');
    if cells[0]==row.find('td',class_='label'):
        print("Headers")
        continue
    if len(cells)==5:
        #the first column we get only the last 5 characters which are the zip code
        l1.append(cells[0].find(text=True).rstrip("\n")[-5:])
        l2.append(cells[1].find(text=True).rstrip("\n"))
        l3.append(cells[2].find(text=True).rstrip("\n"))
        l4.append(int(cells[3].find(text=True).rstrip("\n").replace(',','')))
        l5.append(cells[4].find(text=True).rstrip("\n"))
  
#Create DF1     
DF1=pd.DataFrame()
#Give DF1 columns names and intialize with the corresponding list
DF1['Zip Code']    = l1
DF1['Type']        = l2
DF1['County']      = l3
DF1['Population']  = l4
DF1['Are Code']    = l5

print("DF1 Shape",DF1.shape)   
print(DF1)

# now we will loop over zip codes and use it as a parameter to make requests to NYC AUTO collision API

#assigning endpoint to url variable
url="https://data.cityofnewyork.us/resource/h9gi-nx95.json"


#create another list that will have a dictionary with each zip code values (sum all the zipcode injuries, deaths vlaues
ZiCodesAccidents=[]
#loop pver ZipCode
for zipCode in DF1['Zip Code']:
    
    # set up the parameters,
    parameters = {
        #use zipCode from DF1 as a parameter
        "ZIP CODE":zipCode ,
        "$select":"zip_code,"+"number_of_persons_injured,"+"number_of_persons_killed,"+
                  "number_of_pedestrians_injured,"+"number_of_pedestrians_killed,"+"number_of_cyclist_injured,"+
                  "number_of_cyclist_killed,"+"number_of_motorist_injured,"+"number_of_motorist_killed",
                     
    }
    
    # send requests as long as the column has zipcodes 
    response = requests.get(url,params=parameters)
    #retrieving the json sent by the API and store in data variable
    data = response.json()
    #this variable has many records for a single zip code. we want to sum up and get one object with the total for every zip code
    
    #create another list that will have a dictionary with each zip code values (sum all the zipcode injuries, deaths vlaues
    #create a dictionary zipsum that will contain the sum of all records for the same zipcode
    ZipSum={"number_of_cyclist_injured": 0,
            "number_of_cyclist_killed": 0,
            "number_of_motorist_injured": 0,
            "number_of_motorist_killed": 0,
            "number_of_pedestrians_injured":0,
            "number_of_pedestrians_killed": 0,
            "number_of_persons_injured": 0,
            "number_of_persons_killed": 0,
            "zip_code": ""}
    for objects in data:
         # loop over every object in the zip code and sum up the values 
         # we use int() to convert a column to int before sum
        ZipSum['number_of_cyclist_injured']+=int(objects['number_of_cyclist_injured'])
        ZipSum['number_of_cyclist_killed']+=int(objects['number_of_cyclist_killed'])
        ZipSum['number_of_motorist_injured']+=int(objects['number_of_motorist_injured'])
        ZipSum['number_of_motorist_killed']+=int(objects['number_of_motorist_killed'])
        ZipSum['number_of_pedestrians_injured']+=int(objects['number_of_pedestrians_injured'])
        ZipSum['number_of_pedestrians_killed']+=int(objects['number_of_pedestrians_killed'])
        ZipSum['number_of_persons_injured']+=int(objects['number_of_persons_injured'])
        ZipSum["number_of_persons_killed"] += int(objects["number_of_persons_killed"])
        ZipSum['zip_code']=objects['zip_code']
    #After calculating totals for the zip code, append the dictionary to the list
    ZiCodesAccidents.append(ZipSum)

formatted_json = json.dumps(ZiCodesAccidents, sort_keys= True, indent= 4)

#Create DF2
DF2=pd.DataFrame(ZiCodesAccidents)

#merge DF1, and DF2 Horizontally and store in DF3
DF3=pd.concat([DF1,DF2],axis=1)

# we set opotion to display.max_columns to beable to print all the columns of the DF
pd.set_option('display.max_columns', None)
#display 
print(DF3)       
#get the describtion statistics
desc=DF3.describe()

print(desc)

#Export DF3 to a csv file 
DF3.to_csv('C:\Baruch\Fall2020\CIS 3120 Programming for analytics\Mohame_Abouregila_project2_BrooklynAccidents.csv')
#print neighborhood with the highest Cyclist injuries 87
DF3.loc[DF3['number_of_cyclist_injured'] == 87]
print(DF3.loc[DF3['number_of_cyclist_injured'] == 94])
#print neighborhood with the highest Cyclist deaths 2
print(DF3.loc[DF3['number_of_cyclist_killed'] == 2])
#print neighborhood with the highest Motorists injuries 422
print(DF3.loc[DF3['number_of_motorist_injured'] == 422])
#print neighborhood with the highest Motorists deaths 4
print(DF3.loc[DF3['number_of_motorist_killed'] == 4])
#print neighborhood with the highest number_of_pedestrians_injured 111
print(DF3.loc[DF3['number_of_pedestrians_injured'] == 111])
#print neighborhood with the highest number_of_pedestrians_killed 4
print(DF3.loc[DF3['number_of_pedestrians_killed'] == 4])
#print neighborhood with the highest number_of_personss_injured 527, or 561
print(DF3.loc[DF3['number_of_persons_injured'] == 527])
print(DF3.loc[DF3['number_of_persons_injured'] == 561])
#print neighborhood with the highest number_of_people Killed 8 or 6
print(DF3.loc[DF3['number_of_persons_killed'] == 8])
print(DF3.loc[DF3['number_of_persons_killed'] == 6])

