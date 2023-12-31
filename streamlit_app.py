__import__('pysqlite3')
import sys

sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import chromadb
import pandas as pd
import streamlit as st

st.title("Stuff You Should Know Episode Similarity App")
st.write(
    """
         This recomendation app was built with natural language processing
         and word embedings from the [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) 
         sentence transformer.
         Use the search bar below to find episodes around a specific topic. 
         Check out more about how this app was built
         [here](https://github.com/jmoro0408/Podcast-Episode-Recommender-Embeddings).
         """
)


search_string = st.text_input(
    "Find similar episodes - Try 'Fast Food', or 'Mystery'",
)

chroma_client = chromadb.PersistentClient(path="db")
collection = chroma_client.get_collection(name="episodes")

N_RESULTS = 5
results = collection.query(
    query_texts=[search_string], include=["metadatas", "distances"], n_results=N_RESULTS
)

titles = [results["metadatas"][0][i]["title"] for i in range(N_RESULTS)]
distances = [round(results["distances"][0][i], 4) for i in range(N_RESULTS)]
links = [results["metadatas"][0][i]["link"] for i in range(N_RESULTS)]

df = pd.DataFrame.from_dict(
    {"Title": titles, "Cosine Distance": distances, "Link": links}
)


if search_string:
    st.data_editor(
        df,
        column_config={"links": st.column_config.LinkColumn("links")},
        hide_index=True,
    )
