# pylint: disable=invalid-name, line-to-long
import tomllib
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from preprocessing import preprocess_main


def read_parquets_to_df(data_dir: Path) -> pd.DataFrame:
    """
    Reads multiple Parquet files from a directory and concatenates them into a
    single Pandas DataFrame.

    Args:
        data_dir (Path): The directory containing Parquet files to be read.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the concatenated data 
        from all Parquet files.

    Raises:
        ValueError: If no Parquet files are found in the specified directory."""

    data = list(data_dir.glob("*.parquet"))

    return pd.concat(pd.read_parquet(parquet_file) for parquet_file in data)


def get_db_params(db_toml: Path) -> dict:
    """
    Reads a TOML configuration file containing database connection parameters 
    and returns them as a dictionary.

    Args:
        db_toml (Path): The path to the TOML configuration file.

    Returns:
        dict: A dictionary containing the database connection parameters.

    Raises:
        FileNotFoundError: If the specified TOML file does not exist.
        tomllib.TomlDecodeError: If there is an issue decoding the TOML file.
    """
    with open(db_toml, "rb") as f:
        params = tomllib.load(f)
    return params


def create_db_engine(db_params: dict):
    """
    Creates a SQLAlchemy database engine for PostgreSQL using the provided database connection parameters.

    Args:
        db_params (dict): A dictionary containing the following database connection parameters:
            - 'user' (str): The username for the database.
            - 'password' (str): The password for the database user.
            - 'database' (str): The name of the database.
            - 'host' (str, optional): The database host (default is 'localhost').
            - 'port' (int, optional): The database port (default is 5432).

    Returns:
        sqlalchemy.engine.base.Engine: A SQLAlchemy database engine object.

    Example:
        >>> db_connection_params = {
        ...     'user': 'myuser',
        ...     'password': 'mypassword',
        ...     'database': 'mydatabase',
        ... }
        >>> engine = create_db_engine(db_connection_params)

    Note:
        This function assumes the use of a PostgreSQL database and constructs 
        the connection URL accordingly.
    """

    return create_engine(
        f"postgresql://{db_params['user']}:{db_params['password']}@localhost:5432/{db_params['database']}"
    )


def main():
    """
    Main function to load data from Parquet files, select specific columns, and insert 
    them into a PostgreSQL database.

    This function performs the following steps:
    1. Reads the database connection parameters from a TOML configuration file.
    2. Specifies the columns to be included in the database table.
    3. Reads transcript data from Parquet files located in a specified directory.
    4. Filters the DataFrame to retain only the selected columns.
    5. Preprocesses text as per preprocessing.py file
    6. Creates a database engine using the provided connection parameters.
    7. Inserts the filtered DataFrame into the specified database table.

    Usage:
        - Ensure that the 'db_params.toml' configuration file exists with 
        valid parameters.
        - Ensure that the Parquet files containing transcript data are located in the 
        'Data/transcript_parquets' directory.
        - Adjust the 'SQL_COLS' list to include the desired columns 
        for the database table.
        - The data will be inserted into the specified table using the provided 
        connection parameters.


    Note:
        This function assumes the use of a PostgreSQL database and 
        follows specific naming conventions.
        Make sure to customize the function and parameters as 
        needed for your specific use case.
    """

    params = get_db_params(Path("db_params.toml"))

    SQL_COLS = [
        "id",
        "title",
        "link",
        "desc",
        "summary",
        "audio_url",
        "transcript",
        "categories",
        "preprocessed"
    ]
    data_dir = Path("Data", "transcript_parquets")
    df = read_parquets_to_df(data_dir)
    df = df.dropna(subset = 'transcript', axis = 0).reset_index(drop = True)
    df['preprocessed'] = df['transcript'].apply(lambda x: preprocess_main(x))
    df = df[SQL_COLS]
    engine = create_db_engine(params)

    df.to_sql(name=params["table"], con=engine, if_exists="append")


if __name__ == "__main__":
    main()