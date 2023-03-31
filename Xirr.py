# Welcome to Workiva Scripting 
import requests
import json
import os 
import numpy as np
import pandas as pd 
import scipy 
from datetime import datetime
import streamlit as st

def xirrdemo(filename):
    data = pd.read_csv(filename)
    data['Date'] = pd.to_datetime(data['Date'], infer_datetime_format=True)
    #data['Net Cash Flow'] = data['Base Values'].astype(str).astype(int)
    data['Net Cash Flow'] = data['Net Cash Flow']
    grp_data = data.groupby(['Date'])['Net Cash Flow'].sum().reset_index()
    val=fin_xirr(grp_data['Net Cash Flow'], grp_data['Date'], daycount = 365)
    print(val)
    dataframe1=pd.DataFrame(np.zeros(1))
    col1, col2= st.columns(2)
    with col1:
        st.dataframe(data[['Date','Net Cash Flow']], use_container_width=True) 
    with col2:
        st.dataframe(grp_data, use_container_width=True) 
    dataframe1[0][0]=val
    return(dataframe1)
def xnpv(rate, values, dates , daycount = 365):
    daycount = float(daycount)
    # Why would you want to return inf if the rate <= -100%? I removed it, I don't see how it makes sense
    # if rate <= -1.0:
    #     return float('inf')
    d0 = dates[0]    # or min(dates)
    # NB: this xnpv implementation discounts the first value LIKE EXCEL
    # numpy's npv does NOT, it only starts discounting from the 2nd
    return sum([ vi / (1.0 + rate)**((di - d0).days / daycount) for vi, di in zip(values, dates)])

def fin_xirr(values, dates, daycount = 365, guess = 0, maxiters = 10000, a = -100, b =1e10):
    # a and b: lower and upper bound for the brentq algorithm
    cf = np.array(values)
    
    if np.where(cf <0,1,0).sum() ==0 | np.where(cf >0,1,0).sum() == 0:
        #if the cashflows are all positive or all negative, no point letting the algorithm
        #search forever for a solution which doesn't exist
        return np.nan
    
    try:
        output =  scipy.optimize.newton(lambda r: xnpv(r, values, dates, daycount),
                                        x0 = guess, maxiter = maxiters, full_output = True, disp = True)[0]
    except RuntimeError:
        try:

            output = scipy.optimize.brentq(lambda r: xnpv(r, values, dates, daycount),
                                      a = a , b = b, maxiter = maxiters, full_output = True, disp = True)[0]
        except:
            result = scipy.optimize.fsolve(lambda r: xnpv(r, values, dates, daycount),
                                           x0 = guess , maxfev = maxiters, full_output = True )
    
            if result[2]==1: #ie if the solution converged; if it didn't, result[0] will be the last iteration, which won't be a solution
                output = result[0][0]
            else:
                output = np.nan
                
    return output
def xirrex(postHeaders,wGuid,mGuid,downloadHeaders,header):
    # Runs an export request, and returns task metadata to 'postExport.json'
    exportData = {
      "id" : "116000000030",
      "name" : "Python - XIRR.csv",
        }
    url = (f'https://api.anaplan.com/1/3/workspaces/{wGuid}/models/{mGuid}/' +
       f'exports/{exportData["id"]}/tasks')
    postExport = requests.post(url,
                               headers=postHeaders,
                               data=json.dumps({'localeName': 'en_US'}))

    print(postExport.status_code)
    with open('postExport.json', 'wb') as f:
        f.write(postExport.text.encode('utf-8'))

    fileName = "Python - XIRR.csv"
    getFiles = requests.get(f'https://api.anaplan.com/1/3/workspaces/{wGuid}/' +
                            f'models/{mGuid}/files',
                            headers=header)

    with open('files.json', 'wb') as f:
        f.write(getFiles.text.encode('utf-8'))
        
    fObject = open("files.json")
    fjson = pd.read_json(fObject, orient ='files_details')
    fObject.close()

    fileID = fjson.loc[fjson['name'] == fileName, 'id'].values.item()
    
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


def xirrim(postHeaders,wGuid,mGuid,downloadHeaders,header):
    fileName = "xirr_sol.csv"

    getFiles = requests.get(f'https://api.anaplan.com/1/3/workspaces/{wGuid}/' +
                            f'models/{mGuid}/files',
                            headers=header)

    with open('files.json', 'wb') as f:
        f.write(getFiles.text.encode('utf-8'))
        
    fObject = open("files.json")
    fjson = pd.read_json(fObject, orient ='files_details')
    fObject.close()

    fileID = fjson.loc[fjson['name'] == fileName, 'id'].values.item()

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
    
    url2 = (f'https://api.anaplan.com/1/3/workspaces/{wGuid}/models/{mGuid}/' +f'imports/{112000000145}/tasks')
    # Runs an import request, and returns task metadata to 'postImport.json'
    postImport = requests.post(url2, headers=postHeaders, data=json.dumps({'localeName': 'en_US'}))
    print(postImport.status_code)
    with open('postImport.json', 'wb') as f:
        f.write(postImport.text.encode('utf-8'))
    return()

def xirrmain(postHeaders,wGuid,mGuid,downloadHeaders,header):
    xirrex(postHeaders,wGuid,mGuid,downloadHeaders,header)
    data = xirrdemo("Python - XIRR.csv")
    data.to_csv("xirr_sol.csv")
    xirrim(postHeaders,wGuid,mGuid,downloadHeaders,header)
    return(data)
