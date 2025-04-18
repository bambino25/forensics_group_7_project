import pandas as pd
import spacy
from gliner_spacy.pipeline import GlinerSpacy
from pathlib import Path
from tqdm import tqdm
from config import DEFAULT_DIR, OVERWRITE, THREAD_DIR as target_path

df_path = DEFAULT_DIR / "data_war_related.csv"
cols = ['originFile', 'threadId', 'messageId', 'datetime', 'messageContent']
df = pd.read_csv(df_path, index_col=0)

# Prepare so called "memory" (because the dataset is too be processed in one go)
df_ner_path = DEFAULT_DIR / "data_war_related_ner.csv"
df_ner_cols = ["people", "organization", "weapon", "military_equipment", "gun_types"]
if not Path.exists(df_ner_path) or OVERWRITE:
    df_ner = pd.DataFrame(columns=df_ner_cols, data=None)
    df_ner.to_csv(df_ner_path, index=True)
df_ner = pd.read_csv(df_ner_path, index_col=0)
print(df.info())
# Remove rows within df that are already in df_related_path or df_not_related_path, use index
df = df[~df.index.isin(df_ner.index)]
print(df.info())


# Prepare the NER pipeline
custom_spacy_config = {
    "labels": df_ner_cols
}
nlp = spacy.load("en_core_web_sm")
nlp.add_pipe("gliner_spacy", config=custom_spacy_config)

# Loop trough each post in the dataset
for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing messages"):
    doc = nlp(row["messageContent"])
    ner_dict = {label: [] for label in df_ner_cols}
    for ent in doc.ents:
        if ent.label_ in df_ner_cols:
            ner_dict[ent.label_].append(ent.text)
    ner_dict = {label: ", ".join(ner_dict[label]) for label in df_ner_cols}

    # Append result to the dataframe
    df_temp = pd.DataFrame(ner_dict, index=[index], columns=df_ner_cols)
    df_temp.to_csv(df_ner_path, mode='a', header=False, index=True)