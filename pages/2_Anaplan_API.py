
import requests
import base64
import streamlit as st
import pandas as pd

st.sidebar.markdown("# Anaplan API Info")

def get_all_ids(username, password,wGuid,mGuid):
    user = 'Basic ' + str(base64.b64encode((f'{username}:{password}'
                                            ).encode('utf-8')).decode('utf-8'))
    headers = {'Authorization': user}
    url1 = f'https://api.anaplan.com/1/3/workspaces/{wGuid}/' + f'models/{mGuid}/processes'
    url2 = f'https://api.anaplan.com/1/3/workspaces/{wGuid}/' + f'models/{mGuid}/imports'
    url3 = f'https://api.anaplan.com/1/3/workspaces/{wGuid}/' + f'models/{mGuid}/exports'
    url4 = f'https://api.anaplan.com/1/3/workspaces/{wGuid}/' + f'models/{mGuid}/actions'


    response1 = requests.get(url1, headers=headers)
    response2 = requests.get(url2, headers=headers)
    response3 = requests.get(url3, headers=headers)
    response4 = requests.get(url4, headers=headers)




    if response1.status_code == 200:
        data1 = response1.json()
        df1 = pd.json_normalize(data1)
        df1['Type'] = 'Process'
    else:
        return None

    if response2.status_code == 200:
        data2 = response2.json()
        df2 = pd.json_normalize(data2)
        df2['Type'] = 'Import'
    else:
        return None

    if response3.status_code == 200:
        data3 = response3.json()
        df3 = pd.json_normalize(data3)
        df3['Type'] = 'Export'
    else:
        return None

    if response4.status_code == 200:
        data4 = response4.json()
        df4 = pd.json_normalize(data4)
        df4['Type'] = 'Other Action'
    else:
        return None

    frames = [df1, df2, df3,df4]

    result = pd.concat(frames,ignore_index=True)
    # result = result.reset_index().assign(index=lambda x: x['index'].astype(int))
    st.dataframe(result)
    st.download_button("Download as CSV", result.to_csv(), file_name='Output.csv', mime='text/csv')



def main():
    st.markdown("# Anaplan API Info :blue_book:")
    #st.title('Get All IDs :blue_book:')
    username = st.text_input("Enter username: ")
    password = st.text_input("Enter password: ",type="password")
    wGuid = st.text_input("Enter Workspace ID: ")
    mGuid = st.text_input("Enter Model ID: ")
    if st.button("Send"):
        if username and password:
           get_all_ids(username, password,wGuid,mGuid)

        else:
           st.write("Failed to retrieve information.")



if __name__ == '__main__':
    main()


