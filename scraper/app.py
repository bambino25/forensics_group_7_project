import pandas as pd
import numpy as np
import os
import sys
import bs4
from tqdm import tqdm
from pathlib import Path
import shutil
import filecmp
from collections import Counter
import json
import requests
from bs4 import BeautifulSoup, Comment
import re
import datetime as dt




if __name__ == "__main__":
    
    DEFAULT_DIR = Path("../data/")
    OVERWRITE = False
    target_path = DEFAULT_DIR / "threads"
    df_path = DEFAULT_DIR / "data.csv"

    # Create csv file
    cols = ['originFile', 'threadId', 'messageId', 'datetime', 'messageContent']
    # df = pd.DataFrame(columns=cols)
    # df.set_index('originFile', inplace=True)
    # if not Path.exists(df_path) or #OVERWRITE:
    #     df.to_csv(df_path)
    # else: 
    #     already_existing = pd.read_csv(df_path)['originFile'].tolist()
    
    # Fill csv file with post data
    # s_holmes = Detective()
    # for file in tqdm(os.listdir(target_path), desc="Processing files"):
    #     if file in already_existing:
    #         continue
    #     file_path = os.path.join(target_path, file)
    #     if os.path.isfile(file_path):
    #         report = s_holmes.report(file_path)
    #         if report == False: 
    #             print("Report is empty")
    #             continue
    #         df = pd.DataFrame(report, columns=cols)
    #         df['originFile'] = file
    #         df.to_csv(df_path, mode='a', header=False, index=False)

    # Use LLM to check if the message is war related

    body = {
        "model": "gemma3:4b",
        "prompt": "Is the following text weapons, military equipment or gun types related? If it is - answer 'yes' if it is not - then answer 'no'",
        "stream": False,
        #"context": [1,2, random.randint(1, 100)],
    }
    ambassador = AmbassadorLLM(body)
    # ['originFile', 'threadId', 'messageId', 'datetime', 'messageContent']
    df = pd.read_csv(df_path, index_col=0)
    # Drop all rows with empty messageContent
    df = df[df['messageContent'].notna()]
    df = df[df['messageContent'] != ""]
    df.info()
    # Prepare so called "memory" (because the dataset is too be processed in one go)
    df_related_path = DEFAULT_DIR / "data_war_related.csv"
    df_not_related_path = DEFAULT_DIR / "data_not_war_related.csv"
    if not Path.exists(df_related_path) or OVERWRITE:
        df_related = pd.DataFrame(columns=cols)
        df_related.to_csv(df_related_path, index=True)
    if not Path.exists(df_not_related_path) or OVERWRITE:
        df_not_related = pd.DataFrame(columns=cols)
        df_not_related.to_csv(df_not_related_path, index=True)
    
    df_related = pd.read_csv(df_related_path, index_col=0)
    df_related.info()
    df_not_related = pd.read_csv(df_not_related_path, index_col=0)
    # Remove rows within df that are already in df_related_path or df_not_related_path, use index
    df = df[~df.index.isin(df_related.index)]
    df = df[~df.index.isin(df_not_related.index)]

    df.info()
    # df = df.sample(frac=0.00001, random_state=1) # TESTING: Just keep 1% of the data
    unexpected_llm_response = list()
    #exit()
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing messages"):
        if row['messageContent'] != "": # Skip empty messages
            answer = ambassador.ask(row['messageContent']).strip()
        else:
            answer = ""
        # create a temporary dataframe with the row
        df_temp = pd.DataFrame([row], columns=cols, index=[index])
        if "yes" in answer.lower():
            df_temp.to_csv(df_related_path, mode='a', header=False, index=True)
        else:
            df_temp.to_csv(df_not_related_path, mode='a', header=False, index=True)
        
        if "no" not in answer.lower():
            unexpected_llm_response.append({
                'messageContent': row['messageContent'],
                'llm_answer': answer
            })




    # with Profile() as profile:
    #     for file in tqdm(os.listdir(target_path), desc="Processing files"):
    #         file_path = os.path.join(target_path, file)
    #         if os.path.isfile(file_path):
    #             report = s_holmes.report(file_path)
    #             if report == False: 
    #                 print("Report is empty")
    #                 continue
    #             df = pd.DataFrame(report, columns=cols)
    #             df['originFile'] = file
    #             df.to_csv(df_path, mode='a', header=False, index=False)
    #             break
    #     (
    #         Stats(profile)
    #         .strip_dirs()
    #         .sort_stats(SortKey.CALLS)
    #         .print_stats()
    #     )