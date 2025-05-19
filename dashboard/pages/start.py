# app.py
import streamlit as st
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta, timezone
import altair as alt
from config import DATA_DIR, MODE, ENTITIES, DEFAULT_PATH, WAR_RELATED_PATH, WAR_RELATED_NER_PATH
from preprocess_datasets_for_dashboard import Extract, Preprocessor, Transformer

def preprocess_data():
    extract = Extract(DEFAULT_PATH, WAR_RELATED_PATH, WAR_RELATED_NER_PATH)

    df, war_related_df, war_related_ner_df = extract.load_data()

    preprocessor = Preprocessor()
    df = preprocessor.transform_to_datetime(df, 'datetime')
    war_related_df = preprocessor.transform_to_datetime(war_related_df, 'datetime')
    war_related_ner_df.info()
    war_related_ner_df = preprocessor.str_to_list(war_related_ner_df, war_related_ner_df.columns)

    transformer = Transformer(df, war_related_df, war_related_ner_df)
    transformer.kpi()
    transformer.posts_by_time()
    transformer.posts_by_length()
    transformer.dist_topic()
    transformer.dist_war_related()
    transformer.dist_ner()
    transformer.top10_ner()
    transformer.entity_count_over_time()

def main():
    st.set_page_config(
        page_title="Dark Web Analysis",
        page_icon="👋",
    )
    st.title("Dark Web Analysis")
    st.subheader("Leopold Paris, Steven Verbeek")
    st.button("Update Data", on_click=preprocess_data)
    
    st.markdown(
        """
        This dashboard displays the results of the Assignment in Data Forensics. We analyzed the 8chan forum on the Dark Web. Trying to filter out the posts that are related to weapons, military equipment, and gun types. 
        We used Gemma3 Model to identify posts related to weapons, military equipment, and gun types and GLiNER to extract entity types.
        \n
        We tried to answer following researchquestion:
        """
    )
    
    st.write("_What are the most frequently mentioned weapons, military equipment, gun types, and related entities discussed on dark web forums?_")
    
    

    st.header("KPI Metrics")
    def load_kpi_data():
        # Read csv file KPI.csv 
        # KPI.csv contains the following columns:
        # ,kpi_name,value
        # 0,unique_sites_examined,3861
        # 1,non_null_posts_examined,2108638

        file = DATA_DIR / "KPI.csv"
        if not file.exists():
            st.error("KPI.csv file not found.")
            return [], []
        df = pd.read_csv(file)
        # Convert the columns to lists
        kpi_names = df["kpi_name"].tolist()
        kpis = df["value"].tolist()
        
        return kpi_names, kpis


    kpi_names, kpis = load_kpi_data()
    for i, (col, (kpi_name, kpi_value)) in enumerate(zip(st.columns(4), zip(kpi_names, kpis))):
        col.metric(label=kpi_name, value=kpi_value)


    st.header("Posts")
    # @st.cache_resource()
    def load_posts_data():
        # Read posts_by_time.csv and posts_by_length.csv
        time_df = pd.read_csv(DATA_DIR / "posts_by_time.csv", index_col=0)
        length_df = pd.read_csv(DATA_DIR / "posts_by_length.csv", index_col=0)
        return time_df, length_df

    posts_by_time, posts_by_length = load_posts_data()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Posts per day")
        st.line_chart(data=posts_by_time, x="date", y="count")
    with col2:
        st.subheader("Post Length (chars)")
        chart = alt.Chart(data=posts_by_length).mark_boxplot(extent='min-max').encode(
            y='length:Q'
        )
        st.altair_chart(chart, use_container_width=True)

    st.header("Shares")
    # @st.cache_resource()
    def load_shares_data():
        dist_topic = pd.read_csv(DATA_DIR / "dist_topic.csv", index_col=0)
        dist_war_related = pd.read_csv(DATA_DIR / "dist_war_related.csv", index_col=0)
        
        return dist_topic, dist_war_related
    topic_df, war_related_df = load_shares_data()
    
    st.subheader("Shares per Board")
    chart = alt.Chart(topic_df).mark_arc().encode(
        theta=alt.Theta(field="count", type="quantitative"),
        color=alt.Color(field="topic", type="nominal"),
        tooltip=["topic", "count"]
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Shares posts related to war")
    war_related_df['category'] = war_related_df['war_classified'].map({0: 'Non-War Related', 1: 'War Related'})
    war_related_summary = war_related_df['category'].value_counts().reset_index()
    war_related_summary.columns = ['category', 'count']

    chart = alt.Chart(war_related_summary).mark_arc().encode(
        theta=alt.Theta(field="count", type="quantitative"),
        color=alt.Color(field="category", type="nominal"),
        tooltip=["category", "count"]
    )
    st.altair_chart(chart, use_container_width=True)

    st.subheader("Found entities")

    # @st.cache_resource()
    def load_entities_data():
        # Read entities.csv
        entities_df = pd.read_csv(DATA_DIR / "dist_ner.csv", index_col=0)
        return entities_df

    entities_df = load_entities_data()
    st.bar_chart(data=entities_df, x="entity", y="count")


    st.header("Top 10")

    # @st.cache_resource()
    def load_top10(entity):
        # Read csv file top10_ner.csv and filter for the entity 
        file = DATA_DIR / f"top10_ner.csv"
        if not file.exists():
            st.error(f"{file} file not found.")
            return [], []
        df = pd.read_csv(file)
        df = df[df["entity"] == entity] # Filter for the entity
        df = df.sort_values(by="count", ascending=False) # Sort by count

        return df
    
    for entity in ENTITIES:
        st.subheader(f"{entity}")
        df = load_top10(entity)
        st.bar_chart(data=df, x="value", y="count")
if False:#MODE == "live":
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        login()
    else:
        main()
else:
    main()