# app.py
import streamlit as st
from pathlib import Path
import os, time
import pandas as pd
from datetime import datetime, timedelta, timezone
import pytz
import logging
import altair as alt
from config import DATA_DIR, MODE, ENTITIES

def main():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )

    #@st.cache_resource()
    def load_entity_over_time_data():
        # Read entity_over_time.csv
        file = DATA_DIR / "entity_count_over_time.csv"
        # Read csv file and convert the columns to dictionaries
        #date_cols = ["date"]
        dtype = {
            "date": str,

        }
        df = pd.read_csv(file,
                         converters={col: eval for col in pd.read_csv(file, nrows=1).columns if col != "date"},
                         dtype=dtype,
                         index_col=0)
        
        return df
    data = load_entity_over_time_data()
    # Sidebar navigation
    st.sidebar.title("Entity over time")
    selected_entities = dict()
    for entity in ENTITIES:
        key_set = sorted(set().union(*data[entity].dropna().map(lambda x: x.keys())))
        selected_entities[entity] = st.sidebar.multiselect(entity, key_set)

    st.title("Entity Analysis")
    #st.subheader("Leopold Paris, Steven") 

    st.markdown(
        """
        In this page entities can be combined interactable. Most data was collected between 29.08.2019 and 02.03.2020
        """
    )

    # For each selected entity in the sidebar the folloing linechart should get another line.
    # line chart, x-axis datetime, y-axis count
    # def selection_changed(selected):
    #     st.write("Selected entities:")
    #     for entity in selected:
    #         st.write(entity)

    def filter_graph_data(data, selected_entities, sum_entity):
        df_return = data[["date"]].copy()
        # For each selected values in values, add a column to df_return with the occurrences of the value in the entity column at that date
        for key, value in selected_entities.items():
            if len(value) > 0:
                if not sum_entity:
                    for v in value:
                        col_name = f"{v} ({key})"
                        df_return[col_name] = data[key].map(lambda x: x.get(v, 0) if isinstance(x, dict) else 0)
                else:
                    # Sum up all values for the entity
                    col_name = f"{key}"
                    df_return[col_name] = data[key].map(lambda x: sum([x.get(v, 0) for v in value]) if isinstance(x, dict) else 0)
        return df_return
    sum_entity = st.toggle("Sum Entity", False)
    graph_data = filter_graph_data(data, selected_entities, sum_entity)
    graph_data["date"] = pd.to_datetime(graph_data["date"]).dt.date
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", value=data["date"].min(), max_value=data["date"].max())
    with col2:
        end_date = st.date_input("End date", value=data["date"].max(), min_value=data["date"].min())
    
    
    
    # Filter the data based on the selected date range
    graph_data = graph_data[(graph_data["date"] >= start_date) & (graph_data["date"] <= end_date)]
    # Convert the date column back to string format DD-MM-YYYY
    graph_data["date"] = graph_data["date"].astype(str)
    
    st.line_chart(
        graph_data,
        x="date",

        #color=entity,
        use_container_width=True,
    )

    


    

if False:#MODE == "live":
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        login()
    else:
        main()
else:
    main()