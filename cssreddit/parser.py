import time
import pandas
from pandas.io.parsers import TextFileReader
from cssreddit.config import Config

subreddit_column = 'subreddit'
author_column = 'author'


def get_author_and_comment_count_per_sub(config: Config, sanitized_authors: dict):
    """
    returns list containing subgroups comment and author count

    :param sanitized_authors:
    :param config:
    :return: result dict. e.g:
    {
        "right": {
            "all": [
                # unique author count
                54,
                # total comment count
                67
            ],
            "art": [
                20,
                31
            ],
            ...
        },

        "left": {
            "all": [
                ...
            ],
            "art": [
                ...
            ],
            ...
        }
    }
    """

    start = time.time()
    raw_result = get_raw_author_and_comment_count_per_sub(config, sanitized_authors)
    end = time.time()
    print(f"get_raw_author_and_comment_count_per_sub took {end - start} seconds")

    start = time.time()
    sanitized_result = sanitize_author_and_comment_count_per_sub(raw_result)
    end = time.time()
    print(f"sanitize_author_and_comment_count_per_sub took {end - start} seconds")

    return sanitized_result


def get_raw_author_and_comment_count_per_sub(config: Config, sanitized_authors: dict) -> dict:
    file_handle = load_csv_file(config.input)
    processed_chunks = 0

    result = {}
    for sub_group in sanitized_authors:
        result[sub_group] = {
            "all": [len(sanitized_authors[sub_group]), 0]
        }

    for chunk in file_handle:
        start = time.time()

        for sub_group, sub_group_authors in sanitized_authors.items():
            authors = chunk[chunk[author_column].isin(sub_group_authors)]

            author_comment_count_per_sub = authors.groupby([subreddit_column, author_column]).size()

            for sub_author_tuple, comment_count in author_comment_count_per_sub.items():
                sub = sub_author_tuple[0]
                author = sub_author_tuple[1]

                if sub not in result[sub_group]:
                    result[sub_group][sub] = [{author}, comment_count]
                else:
                    result[sub_group][sub][0].add(author)
                    result[sub_group][sub][1] += comment_count

                result[sub_group]["all"][1] += comment_count

        end = time.time()
        processed_chunks += 1
        print(f" chunk {processed_chunks} took {int(round(end - start))} s")

    return result


def get_author_sub_group(sanitized_authors: dict, author_name: str) -> str:
    for subgroup, authors in sanitized_authors.items():
        if author_name in authors:
            return subgroup

    return ""


def sanitize_author_and_comment_count_per_sub(result: dict) -> dict:
    for sub_group, subs in result.items():
        for sub_name, sub_data in subs.items():
            try:
                sub_data[0] = len(sub_data[0])
            except TypeError:
                pass

    return result


def get_authors(config: Config) -> dict:
    """
    returns list containing all relevant authors

    :param config:
    :return: result dict. e.g:
        {
        "right": [
            'DavidlikesPeace',
            'grewapair'
            ...
        ]
        "left": [
            'DavidlikesPeace',
            'grewapair'
            ...
        ]
    }
    """

    file_handle = load_csv_file(config.input)

    start = time.time()
    raw_authors = get_raw_authors(config, file_handle)
    end = time.time()
    print(f"get_raw_authors took {end - start} seconds")

    start = time.time()
    sanitized_authors = sanitize_authors(config, raw_authors)
    end = time.time()
    print(f"sanitize_authors took {end - start} seconds")

    return sanitized_authors


def load_csv_file(file_path: str) -> TextFileReader:
    return pandas.read_csv(
        file_path,
        usecols=[subreddit_column, author_column],
        chunksize=10000000,  # in rows
        header=0
    )


def get_raw_authors(config: Config, csv_reader: TextFileReader) -> dict:
    result_authors = {}
    for sub_group, sub_list in config.sub_groups.items():
        result_authors[sub_group] = {}

    for chunk in csv_reader:
        for sub_group, sub_list in config.sub_groups.items():
            sub_group_items = chunk[chunk[subreddit_column].isin(sub_list)]

            author_count = sub_group_items[author_column].value_counts()
            for author, count in author_count.items():
                result_authors[sub_group][author] = result_authors[sub_group].get(author, 0) + count

    return result_authors


def sanitize_authors(config: Config, raw_authors: dict) -> dict:
    """
    :param config:
    :param raw_authors:
    :return: sanitized list of authors.
    """
    result = {}

    for sub_group, authors in raw_authors.items():

        sub_group_authors = []
        for key, value in authors.items():
            if value > config.filter["do_not_consider_author_under_comment_count"] and key != "[deleted]":
                sub_group_authors.append(key)

        result[sub_group] = sub_group_authors

    return result
