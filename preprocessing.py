import string
from pathlib import Path
from typing import Optional, Union

import numpy as np
import spacy
from nltk.stem.wordnet import WordNetLemmatizer
from spacy.lang.en.stop_words import STOP_WORDS


def remove_if_substring(doc: list[str], substring: Union[list, str]) -> list[str]:
    """Removes word from a list if the substring appears in the list.
    i.e: with substring = "tring"
    ["this", "is", "a", "test", "string"]
    becomes -> ["this", "is", "a", "test"]
    Args:
        doc (list[str]): list of strings
        substring (str): substring to check for

    Returns:
        doc[str]: filtered list
    """
    if isinstance(substring, str):
        substring = list(substring)
    for word in doc:
        for subword in substring:
            if subword in word:
                doc.remove(word)
    return doc


def list_from_text(filepath: Union[Path, str]) -> list[str]:
    """Reads a .txt file into a list.

    Args:
        filepath (Union[Path, str]): .txt filepath.

    Returns:
        list[str]: list of words in .txt file.
    """
    loaded_text = np.loadtxt(filepath, dtype="str", delimiter=",").tolist()
    return [x.strip() for x in loaded_text]


def clean_text(
    input_text: str,
    custom_stopwords: Optional[list[str]] = None,
    nouns_only: bool = False,
) -> str:
    """cleans input text by:
    1. removing punctuation
    2. removing stopwords, including any custom stopwords passed as an argument
    3. lemmanizing words
    4. Optionally excluding all words that are not nouns. Warning: this can significantly
    increase processing time


    Args:
        input_text (str): text to be cleaned
        custom_stopwords (Optional[list], optional): Custom stopwordst to be removoved, if any.
        Should be a list of string. Defaults to None.
        nouns_only (bool): Returns only nouns. Defaults to False.

    Returns:
        str: cleaned text
    """
    if custom_stopwords is not None:
        STOP_WORDS.update(set(custom_stopwords))
    lemma = WordNetLemmatizer()
    punc_free = input_text.translate(str.maketrans("", "", string.punctuation))
    stop_free = " ".join(
        [i for i in punc_free.lower().split(" ") if i not in STOP_WORDS]
    )
    if nouns_only:
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(stop_free)
        tokens = list(doc)
        noun_tokens = [token for token in tokens if token.tag_ in ("NN", "NNP", "NNS")]
        nouns_joined = " ".join([str(i) for i in noun_tokens])
        normalized = " ".join(lemma.lemmatize(word) for word in nouns_joined.split())
        return normalized

    normalized = " ".join(lemma.lemmatize(word) for word in stop_free.split())
    return normalized


def prepare_custom_stopwords(
    stopwords_to_add: Optional[Union[list[str], str]] = None,
) -> list[str]:
    """Prepares custom stopwords from the full corpus.
        Custom stopwords should be provided either as a list of words,
        or a string with commas separating.
        Standard filler words can be added to the list with the add_word_fillers arg.
        The list is then written to a custom_stopwords.txt file for later use.

    Args:
        stopwords_to_add (Union[list[str],str]): custom stopwords to be included.
        add_word_fillers (bool, optional): Add frequent filler words to stopwords list. Defaults to True.
        **kwargs: Optional keyword arguments for the append_to_txt_file function.

    Returns:
        list[str]: List of custom stopwords to be passed to the algorithm.
    """
    if stopwords_to_add is None:
        stopwords_to_add = []
    if isinstance(stopwords_to_add, str):
        stopwords_to_add = stopwords_to_add.split(",")
    from_txt_file = list_from_text("custom_stopwords.txt")
    stopwords_to_add = stopwords_to_add + from_txt_file
    return stopwords_to_add


def preprocess_main(text_to_clean: str) -> str:
    """
    Function to run through all text preprocessing steps.
    1. creates a list of custom stopwords
    2. cleans text by removing punctuation, stopwords, and lemmatizing

    Args:
        text_to_clean: string to be cleaned
    Returns:
        str: cleaned text
    """

    custom_stopwords = prepare_custom_stopwords()
    clean_transcript = clean_text(
        text_to_clean, custom_stopwords=custom_stopwords, nouns_only=False
    )
    substrings_to_remove = ["com"]
    clean_transcript = remove_if_substring(clean_transcript, substrings_to_remove)
    return clean_transcript
