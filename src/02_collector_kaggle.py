"""
Kaggle Data Collector & Processor for K-Pop / Global Music Charts
Uses kagglehub to download public datasets and filter relevant global streaming and charting benchmarks.
"""
import os
import shutil
import pandas as pd
from pathlib import Path
import kagglehub

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw_kaggle"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def collect_kaggle_data():
    print("[Kaggle] Downloading global music & Spotify benchmark datasets...")
    
    # 1. Download top spotify songs
    spotify_path = kagglehub.dataset_download('nelgiriyewithana/top-spotify-songs-2023')
    print(f"[Kaggle] Spotify dataset downloaded to: {spotify_path}")
    
    # Copy files to our local data directory
    for item in Path(spotify_path).glob("*.csv"):
        dest = DATA_DIR / item.name
        shutil.copy(item, dest)
        print(f" -> Copied {item.name} to {dest}")
        
        # Quick inspection
        df = pd.read_csv(dest, encoding="latin-1")
        print(f"    Loaded {len(df)} rows, columns: {list(df.columns[:6])}")
        
        # Filter K-pop artists if present
        kpop_artists = ["BTS", "Jung Kook", "Jimin", "BLACKPINK", "NewJeans", "IVE", "Stray Kids", "SEVENTEEN", "TWICE", "FIFTY FIFTY"]
        pattern = "|".join(kpop_artists)
        kpop_df = df[df["artist(s)_name"].str.contains(pattern, case=False, na=False)]
        print(f"    Found {len(kpop_df)} K-Pop chart entries in global dataset")
        kpop_df.to_csv(PROCESSED_DIR / "kaggle_kpop_spotify_benchmarks.csv", index=False, encoding="utf-8-sig")

    print("[Kaggle Collection Completed Successfully!]")

if __name__ == "__main__":
    collect_kaggle_data()
