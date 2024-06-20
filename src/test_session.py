import streamlit as st
import streamlit.components.v1 as components
from streamlit_pills import pills


st.set_page_config(page_title="Tests", page_icon="🧪")

selected_option = pills("Options", ["Option1", "Option2", "Option3"], key="sel_option" )

if selected_option:
    st.write(selected_option)
    st.write("Debug selected:",  st.session_state)



