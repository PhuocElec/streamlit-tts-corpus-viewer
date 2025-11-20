# app/core/data.py
from pathlib import Path

import pandas as pd
import streamlit as st

from settings import settings


@st.cache_data(show_spinner=True)
def load_corpus_metadata() -> pd.DataFrame:
    csv_path: Path = settings.CORPUS_CSV_PATH

    if not csv_path.exists():
        raise FileNotFoundError(f"Metadata CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    if "text" not in df.columns:
        raise ValueError("CSV must contain a 'text' column.")
    if "file" not in df.columns:
        raise ValueError("CSV must contain a 'file' column (audio filename).")

    df["text"] = df["text"].astype(str)
    df["file"] = df["file"].astype(str).str.strip()

    if "id" not in df.columns:
        df.insert(0, "id", range(1, len(df) + 1))

    return df


def clear_metadata_cache() -> None:
    load_corpus_metadata.clear()


def get_valid_filenames() -> set[str]:
    df = load_corpus_metadata()
    return set(df["file"].astype(str).str.strip())
