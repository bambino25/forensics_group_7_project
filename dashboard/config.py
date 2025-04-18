from pathlib import Path

original_data_dir = Path("../data/")
DEFAULT_PATH = original_data_dir / "data.csv"
WAR_RELATED_PATH = original_data_dir / "data_war_related.csv"
WAR_RELATED_NER_PATH = original_data_dir / "data_war_related_ner.csv"
DATA_DIR = Path("./data/")
MODE = "test"
ENTITIES = ["people", "organization", "weapon", "military_equipment", "gun_types"]


if __name__ == "__main__":
    pass