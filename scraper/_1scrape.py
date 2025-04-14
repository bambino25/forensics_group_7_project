import os
import pandas as pd
from tqdm import tqdm
from pathlib import Path
from src.detective import Detective

from config import DEFAULT_DIR, OVERWRITE, THREAD_DIR as target_path, TESTING
import random

if __name__ == "__main__":
    df_path = DEFAULT_DIR / "data.csv"

    # Create csv file
    cols = ['originFile', 'threadId', 'messageId', 'datetime', 'messageContent']
    df = pd.DataFrame(columns=cols)
    df.set_index('originFile', inplace=True)
    already_existing = list()
    if not Path.exists(df_path) or OVERWRITE:
        # Create folderpath
        os.makedirs(DEFAULT_DIR, exist_ok=True)
        df.to_csv(df_path)
    else: 
        already_existing = pd.read_csv(df_path)['originFile'].tolist()
    
    file_list = os.listdir(target_path)
    if TESTING: # Just keep N files
        file_list = random.sample(file_list, min(TESTING, len(file_list)))

    # Fill csv file with post data
    s_holmes = Detective()
    for file in tqdm(file_list, desc="Extract posts from files"):
        if file in already_existing:
            continue
        file_path = os.path.join(target_path, file)
        if os.path.isfile(file_path):
            report = s_holmes.report(file_path)
            if report == False: 
                print("Report is empty")
                continue
            df = pd.DataFrame(report, columns=cols)
            df['originFile'] = file
            df.to_csv(df_path, mode='a', header=False, index=False)