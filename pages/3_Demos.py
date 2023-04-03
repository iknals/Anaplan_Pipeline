import streamlit as st
import sys
from pulp import *
import pandas as pd  
import numpy as np
from functools import partial
import requests
import base64
import json
sys.path.append("app_az")
from Optimization import *
from Xirr import *

def xirr():
    wGuid,mGuid = "8a81b08e575246890157b4fc78560a18","7B39E2FEB3704ECFBEF8BBA9F050E4BA"
    username = st.text_input("Enter username: ")
    password = st.text_input("Enter password: ",type="password")
    if st.button("Send"):
        if username and password:
            user = 'Basic ' + str(base64.b64encode((f'{username}:{password}').encode('utf-8')).decode('utf-8'))
            getHeaders = {'Authorization': user}
            postHeaders = {'Authorization': user,'Content-Type': 'application/json'}
            downloadHeaders = {'Authorization': user,'Accept': 'application/octet-stream'}
        
            xirrdata=xirrmain(postHeaders,wGuid,mGuid,downloadHeaders,getHeaders)
        else:
            st.write("Failed to retrieve information.")
    

def optimization():
    wGuid,mGuid = "8a81b08e575246890157b4fc78560a18","C86CC20F62C24A9894E90D6DF23C9939"
    username = st.text_input("Enter username: ")
    password = st.text_input("Enter password: ",type="password")
    if st.button("Send"):
        if username and password:
            user = 'Basic ' + str(base64.b64encode((f'{username}:{password}').encode('utf-8')).decode('utf-8'))
            getHeaders = {'Authorization': user}
            postHeaders = {'Authorization': user,'Content-Type': 'application/json'}
            downloadHeaders = {'Authorization': user,'Accept': 'application/octet-stream'}
        
            optdemo(postHeaders,wGuid,mGuid,downloadHeaders,getHeaders)
        else:
            st.write("Failed to retrieve information.")   
 

page_names_to_funcs = {
    "XIRR": xirr,
    "Optimization": optimization,
}


selected_page = st.sidebar.selectbox("Demo", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()




