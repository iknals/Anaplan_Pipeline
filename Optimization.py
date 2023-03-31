import streamlit as st
from pulp import *
import pandas as pd  
import numpy as np
from tkinter import *
from functools import partial
import requests
import base64
import json
def optdemo(postHeaders,wGuid,mGuid,downloadHeaders,header):

    optex(postHeaders,wGuid,mGuid,downloadHeaders,header)
    
    data = pd.read_csv("Python_Data.csv")

    # Get a list of Concat 
    concat = list(data['Concat'])
    # Initialize Dictionaries for people, beverages , state
    people_dic = dict(zip(concat, data['People']))
    beverages_dic = dict(zip(concat, data['Beverages'])) 
    state_dic = dict(zip(concat, data['State']))  
    score_dic = dict(zip(concat, data['Appreciation Score']))
    beverages_dic= dict(zip(concat, data['Beverage Cost']))
    tax_dic= dict(zip(concat, data['Resident Tax']))
    # Set var 
    length = len(concat)
    VAR_Beverage_Allocated	= LpVariable.dicts("Allocated", concat,lowBound=0,cat='Continuous')  
    VAR_Beverage_Tax = LpVariable.dicts("Tax", concat, lowBound=0,cat='Continuous')  	
    VAR_Beverage_Cost = LpVariable.dicts("Cost", concat,lowBound=0,cat='Continuous')  	
    VAR_Appreciation_Score = LpVariable.dicts("Score", concat,lowBound=0,cat='Continuous')

    """# Min Objective"""

    cost = LpProblem("Example_1", LpMaximize)  
    #Objective  
    cost += lpSum([VAR_Beverage_Cost[i] + VAR_Beverage_Tax[i] for i in concat]) 
    #for i in concat:  
      #cost += -VAR_Appreciation_Score[i]

    people = data['People'].unique()
    for i in people:  
        df_per = data[data['People']==i]
        peop_parsed = [p for p in people_dic.keys() if people_dic[p] == i] 
        cost += lpSum([VAR_Beverage_Allocated[x] for x in peop_parsed]) >= 1  
        cost += lpSum([VAR_Beverage_Cost[x] + VAR_Beverage_Tax[x] for x in peop_parsed]) >= df_per['Min Spend'].mean()  
        cost += lpSum([VAR_Beverage_Cost[x] + VAR_Beverage_Tax[x] for x in peop_parsed]) <= df_per['Max Spend'].mean()

    cost += lpSum([VAR_Beverage_Cost[x] + VAR_Beverage_Tax[x] for x in concat]) <= data['Total Budget'].mean()

    for i in concat:
      cost += VAR_Beverage_Cost[i] - VAR_Beverage_Allocated[i] * beverages_dic[i] == 0    
      cost += VAR_Beverage_Tax[i] - VAR_Beverage_Cost[i] * tax_dic[i] == 0 
      #cost += VAR_Appreciation_Score[i] - VAR_Beverage_Allocated[i] * score_dic[i] == 0

    cost.solve() 
    #min_sol=pulp.value(cost.objective)  

    """# Final Solution"""

    lst_1 = []   
    lst_2 = []  
    lst_3 = []  
    lst_4 = []  
    counter = 1

    for v in cost.variables():   
      if counter <= length:
        lst_1.append([v.varValue])  
      elif counter <= 2 * length: 
        lst_2.append([v.varValue])  
      elif counter <= 3 * length:
        lst_3.append([v.varValue])  
      else: 
        lst_4.append([v.varValue]) 
      counter = counter + 1

    sol_df =pd.DataFrame()   
    sol_df['Concat'] =data['Concat']
    sol_df['People'] =data['People']
    sol_df['Beverages']  =data['Beverages'] 
    sol_df['State']  =data['State']
    sol_df['Allocated'] =lst_1    
    sol_df['Cost']  =lst_2   
    sol_df['Tax']  =lst_3
    #sol_df['Appreciation'] =lst_4

    sol_df.to_csv('sol_opt.csv')
    
    st.dataframe(sol_df, use_container_width=True)
    
    optim(postHeaders,wGuid,mGuid,downloadHeaders,header)
    return()
          
def optex(postHeaders,wGuid,mGuid,downloadHeaders,header):
    # Runs an export request, and returns task metadata to 'postExport.json'
    exportData = {
      "id" : "116000000001",
      "name" : "Python Key Example 1",
      "exportType" : "GRID_CURRENT_PAGE"
        }
    url = (f'https://api.anaplan.com/1/3/workspaces/{wGuid}/models/{mGuid}/' +
       f'exports/{exportData["id"]}/tasks')
    postExport = requests.post(url,
                               headers=postHeaders,
                               data=json.dumps({'localeName': 'en_US'}))

    print(postExport.status_code)
    with open('postExport.json', 'wb') as f:
        f.write(postExport.text.encode('utf-8'))

    fileID = "116000000002"
    fileName = "Python_Data.csv"
    
    url_2 = (f'https://api.anaplan.com/1/3/workspaces/{wGuid}/models/{mGuid}/' +
           f'files/{fileID}/chunks')


    getChunkData = requests.get(url_2,
                                headers=header)
    with open('downloadChunkData.json', 'wb') as f:
        f.write(getChunkData.text.encode('utf-8'))

    with open('downloadChunkData.json', 'r') as f:
        f2 = json.load(f)

    with open(f'{fileName}', 'wb') as f:
        for i in f2:
            chunkData = i
            chunkID = i['id']
            print(f'Getting chunk {chunkID}')
            getChunk = requests.get(url_2 + f'/{chunkID}',
                                    headers=downloadHeaders)
            f.write(getChunk.content)
            print('Status code: ' + str(getChunk.status_code))
    return()


def optim(postHeaders,wGuid,mGuid,downloadHeaders,header):
    fileName = "sol_opt.csv"

    fileID = "113000000007"

    url = (f'https://api.anaplan.com/1/3/workspaces/{wGuid}/models/{mGuid}/' +
       f'files/{fileID}')

    # Opens the data file (filData['name'] by default) and encodes it to utf-8
    dataFile = open(fileName, 'r').read().encode('utf-8')

    fileUpload = requests.put(url,
                              headers=downloadHeaders,
                              data= dataFile)
    if fileUpload.ok:
        print('File Upload Successful.')
    else:
        print('There was an issue with your file upload: '
              + str(fileUpload.status_code))
    
    url2 = (f'https://api.anaplan.com/1/3/workspaces/{wGuid}/models/{mGuid}/' +f'imports/{112000000007}/tasks')
    # Runs an import request, and returns task metadata to 'postImport.json'
    postImport = requests.post(url2, headers=postHeaders, data=json.dumps({'localeName': 'en_US'}))
    print(postImport.status_code)
    with open('postImport.json', 'wb') as f:
        f.write(postImport.text.encode('utf-8'))

    return()
