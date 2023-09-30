# Podcast-Episode-Recommender-Embeddings
Using word embeddings to generate podcast episode recomendations.

An improvement on my [previous project](https://github.com/jmoro0408/Podcast_Episode_Recommender).

So you loved that Stuff You Should Know (SYSK) episode on The Dyatlov Pass Mystery, and want to know which other episodes Josh and chuck have that might be similar? Well with over 1500 episodes, it can be hard to choose.

This project uses a vector database (ChromaDB) and the all-MiniLM-L6-v2 sentence transformer to find episodes based on keyword searches. 

Full SYSK Transcripts generously provided by OSF<sup>1</sup>.

Checkout the final steamlit app [here](https://podcast-episode-recommender-embeddings-h4idhrh5swcfbzlq3dqqqj.streamlit.app/)!

Blog post on this project with details on word embeddings and ChromaDB coming soon!

### Data Stats
* Dataset consists of 2044 episodes in total
* Average length of transcript: 35,485 words
* Total of 72,531,340 words in the entire corpus


## How to use 

The search seems to work best with short phrases or single keywords, for example the search for `mystery` produces good results:

![mystery](screenshots/mystery.png)

## How I built this
### Transcript storage
I first use pandas to read the provided parquet files and subsequently write them to a local postgresql database.
Storing the files in a database allows for easy access for the rest of the project.


### Text Preprocessing

Preprocessing is generally the most important and labour intensive part of natural language processing and in broader machine learning and this project is no exception.
I used two popular NLP packages to undertake preprocessing: spacy and nltk. This involved:
1. Removing stopwords and punctuation. I append my own custom stopwords (contained in "custom_stopwords.txt") to spacy's built in stopwords. These custom stopwords generally consist of common SYSK sponsors, and Josh and Chuck's full names.
2. Lemmatization. I use NLTK's WordNetLemmatizer to reduce the words to their lemmas.

Notably the preprocessing was much less intensive than the previous LDA modelling.


### ChromaDB and word embeddings

The real magic is built into the [ChromaDB](https://www.trychroma.com/). I use this library to encode each episode into numerical representations of the text. Under the hood this uses the free and open source [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) sentence transformer. 

The embeddings are stored in a sqlite3 db file for easy retrieval and querying. 

### Streamlit App

In order for a prediction model to be useful, it has to be accessible to users.
For this I decided to use Streamlit, a simple easy to use hosting web app package which includes hosting.

The app embeds the search text, and queries the sqlite3 file to return the 5 most closely related episodes. 

I decided to use the cosine distance metric to determine similarity, therefore a lower score corresponds to a better match. 


# Bugs and Hurdles

I ran into a few issues getting running, mainly around the Streamlit deployment.

1. The ChromaDB library requires access to the sqlite3 file to query, however this file is over the github file size limits. I got around this by using git large file system (LFS) but getting the system up and working was not obvious.

2. The version of sqlite3 included with Streamlit is outdated, and ChromaDB required a newer version. This was solved by adding a `pysqlite3-binary` requirement to my `requirements.txt` file, and by following the advice in [this](https://stackoverflow.com/questions/76958817/streamlit-your-system-has-an-unsupported-version-of-sqlite3-chroma-requires-sq) stack overflow post.

3. Usual streamlit + poetry issues. Streamlit doesnt seem to work nicely with poetry's `pyproject.toml` file. By exporting the toml to "normal" `requirements.txt` seemed to get Streamlit up and running. 


---

1. Pierson, B. D. (2022, July 30). “Stuff You Should Know” Podcast Transcripts - Full Dataset with Transcript of All Episodes (SYSK_Transcripts). https://doi.org/10.17605/OSF.IO/VM9NT