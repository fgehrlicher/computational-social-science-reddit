import json

from cssreddit.config import Config
from cssreddit.parser import get_authors, get_author_and_comment_count_per_sub


if __name__ == '__main__':
    config = Config("config.json")

    authors = get_authors(config)

    result = get_author_and_comment_count_per_sub(config, authors)

    with open(config.output, 'w') as outfile:
        json.dump(result, outfile)
