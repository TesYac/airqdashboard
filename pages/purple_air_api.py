import streamlit as st
import requests

st.title("Download Purple Air Data using an API")

#Get API Key from the user 
api_key = st.text_input(
    "Enter your API Key",
    type="password"
)

if api_key:
    st.success("API key received!")
