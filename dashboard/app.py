import streamlit as st

pages = [
        st.Page("./pages/start.py", title="Intro"),
        st.Page("./pages/entity.py", title="Entities over Time"),
]

pg = st.navigation(pages)
#pg = st.navigation(["page_1.py", page_2])
pg.run()