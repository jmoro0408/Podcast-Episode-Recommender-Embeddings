from pathlib import Path

import chromadb
import pandas as pd

from write_to_db import create_db_engine, get_db_params


def get_episode_metadata(episode_df: pd.DataFrame, episode_index: int) -> dict:
    """
    Retrieves metadata for a specific episode from a DataFrame.

    Args:
        episode_df (pd.DataFrame): The DataFrame containing episode data.
        episode_index (int): The index of the episode to retrieve metadata for.

    Returns:
        dict: A dictionary containing episode metadata with the following keys:
            - 'title' (str): The title of the episode.
            - 'link' (str): The link to the episode.
            - 'desc' (str): A short description of the episode.
            - 'summary' (str): A summary of the episode content.
            - 'audio_url' (str): The URL to the audio file of the episode.
            - 'categories' (str): Categories or tags associated with the episode.

    Raises:
        IndexError: If the provided episode_index is out of bounds.
    """
    metadata_cols = ["title", "link", "desc", "summary", "audio_url", "categories"]
    _temp = episode_df[episode_df["index"] == episode_index][metadata_cols].values[0]
    return dict(zip(metadata_cols, _temp))


def get_episode_transcript(episode_df: pd.DataFrame, episode_index: int) -> str:
    """
    Retrieves the transcript of a specific episode from a DataFrame.

    Parameters:
    - episode_df (pd.DataFrame): A DataFrame containing episode data, including an "index" column.
    - episode_index (int): The index of the episode whose transcript is to be retrieved.

    Returns:
    - str: The transcript of the specified episode as a string.
    """
    return episode_df[episode_df["index"] == episode_index]["transcript"].values[0]


def get_episode_preprocessed_text(episode_df: pd.DataFrame, episode_index: int) -> str:
    """
    Retrieves the preprocessed text of a specific episode from a DataFrame.

    Args:
        episode_df (pd.DataFrame): A DataFrame containing episode data.
        episode_index (int): The index of the episode to retrieve.

    Returns:
        str: The preprocessed text of the specified episode.
    """
    return episode_df[episode_df["index"] == episode_index]["preprocessed"].values[0]


def add_to_chroma(documents: list[str], metadata: list[dict], ids: list[str]) -> None:
    """
    Adds documents and their associated metadata to a Chroma collection.

    Args:
        documents (list[str]): A list of strings representing the documents to be added to the collection.
        metadata (list[dict]): A list of dictionaries containing metadata for each document.
        ids (list[str]): A list of unique identifiers corresponding to each document.

    Returns:
        None
    """
    chroma_client = chromadb.PersistentClient(path="db")
    try:
        chroma_client.delete_collection(name="episodes")
    except ValueError:
        chroma_client.create_collection(
            name="episodes", metadata={"hnsw:space": "cosine"}  # l2 is the default
        )

    collection = chroma_client.get_collection(name="episodes")
    collection.add(documents=documents, metadatas=metadata, ids=ids)


def main():
    QUERY = """ select * from episodes;"""
    params = get_db_params(Path("db_params.toml"))
    engine = create_db_engine(params)
    df = pd.read_sql(QUERY, engine).dropna(how = 'any', subset = ["title", "link", "desc", "summary", "audio_url", "categories"])
    ids_to_process = df["index"].to_list()
    episode_preprocessed = [
        get_episode_preprocessed_text(df, i) for i in ids_to_process
    ]
    episodes_metadatas = [get_episode_metadata(df, i) for i in ids_to_process]
    chroma_ids = [str(i) for i in ids_to_process]
    add_to_chroma(episode_preprocessed, episodes_metadatas, chroma_ids)


if __name__ == "__main__":
    main()
