import streamlit as st
from PIL import Image

title_container = st.container()
col1, col2,col3, col4= st.columns(4)

logo = Image.open('lionpointlogo.png')

with title_container:
    with col1:
        st.image(logo, width=100)
    with col2:
        st.markdown("# Home")

st.sidebar.markdown("# Home")


