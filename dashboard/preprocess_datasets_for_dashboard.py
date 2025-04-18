from pathlib import Path
import sys
import os
import pandas as pd
import numpy as np
import ast
import streamlit as st

class Extract:
    def __init__(self, default_path, war_related_path, war_related_ner_path):
        self.default_path = default_path
        self.war_related_path = war_related_path
        self.war_related_ner_path = war_related_ner_path
        

    def load_data(self):
        """Load the data from CSV files."""
        data = pd.read_csv(self.default_path, index_col=0)
        war_related_data = pd.read_csv(self.war_related_path, index_col=0)
        war_related_ner_data = pd.read_csv(self.war_related_ner_path, index_col=0)
        
        return data, war_related_data, war_related_ner_data
    
class Preprocessor:
    def __init__(self):
        pass

    def transform_to_datetime(self, df, date_col):
        """Convert date columns to datetime format."""
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

        # NaT values with the mean of the column
        if df[date_col].isnull().any():
            mean_date = df[date_col].mean()
            df.fillna({date_col: mean_date}, inplace=True)
            
        print(f"Transformed {date_col} to datetime format.")
        return df

    def str_to_list(self, df, col: list):
        """Convert string representation of list to actual list."""
        for column in col:
            if column in df.columns:
                df[column] = df[column].apply(lambda x: [item.strip() for item in x.split(",") if item.strip()] if isinstance(x, str) else list())
            print(f"Transformed {column} to list format.")
        return df
    def show_missing_values(self, df):
        """Show missing values in the dataframe."""
        print(df.isnull().sum())

class Transformer:
    def __init__(self, df, war_related_df, war_related_ner_df, target_dir = Path("./data/")):
        self.df = df
        self.war_related_df = war_related_df
        self.war_related_ner_df = war_related_ner_df
        self.target_dir = target_dir

    def kpi(self, name="KPI"):
        """Calculate KPIs and return a dataframe with kpi_name and value."""
        # Calculate the number of unique sites examined
        unique_sites = self.df["originFile"].nunique()
        
        # Calculate the number of non-null posts
        non_null_posts = self.df["messageContent"].notnull().sum()
        
        # Create a dataframe with the results
        result_df = pd.DataFrame({
            "kpi_name": ["Sites", "Posts"],
            "value": [unique_sites, non_null_posts]
        })
        
        # Save the result to a CSV file
        self.save(result_df, name)

    def posts_by_time(self, name="posts_by_time"):
        """Calculate a dataframe from df with the number of posts (colname = count) by time (colname = date)."""
        self.df['date'] = pd.to_datetime(self.df['datetime']).dt.date
        posts_by_time = self.df.groupby('date').size().reset_index(name='count')
        posts_by_time['date'] = pd.to_datetime(posts_by_time['date'])
        posts_by_time.sort_values('date', inplace=True)
        
        # Fill gaps between the first and last date with 0
        all_dates = pd.date_range(start=posts_by_time['date'].min(), 
                      end=posts_by_time['date'].max(), 
                      freq='D')
        all_dates_df = pd.DataFrame({'date': all_dates})
        posts_by_time = pd.merge(all_dates_df, posts_by_time, on='date', how='left').fillna(0)
        posts_by_time['count'] = posts_by_time['count'].astype(int)
        
        # Save the result to a CSV file
        self.save(posts_by_time, name)


    def posts_by_length(self, name="posts_by_length"):
        """Calculate the number chars per post"""
        self.df['length'] = self.df['messageContent'].str.len()
        
        # Save the result to a CSV file
        self.save(self.df['length'], name)

    def dist_topic(self, name="dist_topic"):
        """Calculate the distribution of topics in the dataframe."""
        # Assuming 'topic' is a column in df called threadId
        topic_distribution = self.df['threadId'].value_counts().reset_index()
        topic_distribution.columns = ['topic', 'count']
        # Order the topics by count
        topic_distribution.sort_values(by='count', ascending=False, inplace=True)
        
        # Save the result to a CSV file
        self.save(topic_distribution, name)
    
    def dist_war_related(self, name="dist_war_related"):
        """Create a DataFrame containing all indexes with a column 'war_classified' (0 or 1)."""
        # Create a set of indexes classified as war-related
        war_related_indexes = set(self.war_related_df.index)
        
        # Add a column 'war_classified' to the main DataFrame
        self.df['war_classified'] = self.df.index.map(lambda idx: 1 if idx in war_related_indexes else 0)
        
        # Save the result to a CSV file
        self.save(self.df[['war_classified']], name)

    def dist_ner(self, name="dist_ner"):
        """ From all the not null values in the war_related_ner_df, create a DataFrame with the columns 'entity' and 'count'."""
        # Count the number of not null values in for each col in war_related_ner_df 
        non_null_counts = self.war_related_ner_df.notnull().sum()
        null_counts = self.war_related_ner_df.isnull().sum()
        
        # Create a DataFrame with the results
        result_df = pd.DataFrame({
            'entity': non_null_counts.index,
            'count': non_null_counts.values
        })
    
        # Save the result to a CSV file
        self.save(result_df, name)

    def top10_ner(self, name="top10_ner"):
        """Calculate the top 10 entities in the war_related_ner_df for each column. Careful the cell values are lists."""
        result_df = pd.DataFrame(data=[], columns=['entity', 'value', 'count'])

        for column in self.war_related_ner_df.columns:
            entity = column
            # Count the number of occurrences of each entity in the column and keep top 10
            counts = self.war_related_ner_df[column].explode().value_counts().sort_values(ascending=False).head(10)
            # Create a DataFrame for the top 10 entities
            top_10_df = pd.DataFrame({
                'entity': entity,
                'value': counts.index,
                'count': counts.values
            })
            # Append the top 10 DataFrame to the result DataFrame
            result_df = pd.concat([result_df, top_10_df], ignore_index=True)
        # Save the result to a CSV file
        self.save(result_df, name)

    def entity_count_over_time(self, name="entity_count_over_time"):
        """Merge the col datetime from war_related_df with the entity count from war_related_ner_df.
        Then for each day list the entities as json strings with entity: count for each column in war_related_ner_df.
        For days without any entity, give an empty json string.
        """
        # Merge the "datetime" column from war_related_df to the war_related_ner_df using the index
        merged_df = pd.merge(self.war_related_ner_df, self.war_related_df[['datetime']], left_index=True, right_index=True)
        
        # Convert datetime to date
        merged_df['date'] = pd.to_datetime(merged_df['datetime']).dt.date
        
        # Initialize the result DataFrame with the date column
        result_df = pd.DataFrame({'date': merged_df['date'].unique()})
        result_df.sort_values('date', inplace=True)
        
        # Process each column in war_related_ner_df
        for column in self.war_related_ner_df.columns:
            # Group by date and count the occurrences of each entity
            entity_counts = merged_df.groupby('date')[column].agg(
                lambda x: x.explode().str.strip().value_counts().to_dict()
            ).reset_index(name=column)
            
            # Merge the counts into the result DataFrame
            result_df = pd.merge(result_df, entity_counts, on='date', how='left')
        
        # Fill missing dates with empty dictionaries
        for column in self.war_related_ner_df.columns:
            result_df[column] = result_df[column].apply(lambda x: x if isinstance(x, dict) else {})
        
        # Save the result to a CSV file
        self.save(result_df, name)


    def save(self, df, name):
        """Save the DataFrame to a CSV file."""
        if not self.target_dir.exists(): # Check if the target directory exists, if not create it
            os.makedirs(self.target_dir)
        name = name + ".csv"
        df.to_csv(self.target_dir / name  , index=True)
        print("Data saved to ", name)


# DATA_DIR = Path("../data")
# default_path = DATA_DIR / "data.csv"
# war_related_path = DATA_DIR / "data_war_related.csv"
# war_related_ner_path = DATA_DIR / "data_war_related_ner.csv"

# extract = Extract(default_path, war_related_path, war_related_ner_path)
# df, war_related_df, war_related_ner_df = extract.load_data()

# preprocessor = Preprocessor()
# df = preprocessor.transform_to_datetime(df, 'datetime')
# war_related_df = preprocessor.transform_to_datetime(war_related_df, 'datetime')
# war_related_ner_df.info()
# war_related_ner_df = preprocessor.str_to_list(war_related_ner_df, war_related_ner_df.columns)

# transformer = Transformer(df, war_related_df, war_related_ner_df)
#transformer.kpi()
#transformer.posts_by_time()
#transformer.posts_by_length()
#transformer.dist_topic()
#transformer.dist_war_related()
#transformer.dist_ner()
#transformer.top10_ner()
#transformer.entity_count_over_time()