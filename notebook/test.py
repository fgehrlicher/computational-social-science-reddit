import pandas
import json
import copy
from ipywidgets import interact

config = json.load(open("../config.json", newline='\n'))

result = pandas.read_json("../result.json")
result.head(11)

result_right = result["right"]
right_subs = config["sub_groups"]["right"]

result_right_in_right_subs = result_right[result_right.index.isin(right_subs)]
print(result_right_in_right_subs.to_string())

result_left = result["left"]
left_subs = config["sub_groups"]["left"]

result_left_in_left_subs = result_left[result_left.index.isin(left_subs)]
print(result_left_in_left_subs.to_string())

total_comments_left_in_left_subs = 0
for sub, sub_author_tuple in result_left_in_left_subs.items():
    if type(sub_author_tuple) is not list:
        continue
    total_comments_left_in_left_subs += sub_author_tuple[1]

total_comments_right_in_right_subs = 0
for sub, sub_author_tuple in result_right_in_right_subs.items():
    if type(sub_author_tuple) is not list:
        continue
    total_comments_right_in_right_subs += sub_author_tuple[1]

total_comments_right_in_other_subs = result["right"]["all"][1] - total_comments_right_in_right_subs
total_comments_left_in_other_subs = result["left"]["all"][1] - total_comments_left_in_left_subs

print(f"total left comments in left subs by relevant left authors : {total_comments_left_in_left_subs}")
print(f"total left comments in other subs by relevant left authors: {total_comments_left_in_other_subs}")

print(f"total right comments in right subs by relevant right authors: {total_comments_right_in_right_subs}")
print(f"total right comments in other subs by relevant right authors: {total_comments_right_in_other_subs}")

result_right = result["right"]
result_right_total = result_right["all"]
right_subs = config["sub_groups"]["right"]

result_left = result["left"]
result_left_total = result_left["all"]
left_subs = config["sub_groups"]["left"]

total_left_author_count = result_left_total[0]
total_left_comment_count = result_left_total[1]

raw_comments_per_sub = {
    "subreddit": [],
    "author_count": [],
    "comment_count": [],
    "author_percentage": [],
    "comment_percentage": [],
}

raw_right_comments_per_sub = copy.deepcopy(raw_comments_per_sub)

for sub, sub_author_tuple in result_right.items():
    if type(sub_author_tuple) is not list or sub == "all":
        continue
    raw_right_comments_per_sub["subreddit"].append(sub)
    raw_right_comments_per_sub["author_count"].append(sub_author_tuple[0])
    raw_right_comments_per_sub["comment_count"].append(sub_author_tuple[1])
    raw_right_comments_per_sub["author_percentage"].append(float("{:.2f}".format(sub_author_tuple[0] / total_right_author_count * 100)))
    raw_right_comments_per_sub["comment_percentage"].append(float("{:.2f}".format(sub_author_tuple[1] / total_right_comment_count * 100)))

columns = ['subreddit', 'author_percentage', 'comment_percentage', 'author_count', 'comment_count']
right_comments_per_sub = pandas.DataFrame(
    raw_right_comments_per_sub,
    columns=columns
)

@interact
def sort(column=columns, order={"ascending": True, "descending": False}, x=(5, 50, 1)):
    return right_comments_per_sub.sort_values(
        ascending=order,
        by=column
    ).head(x)


@interact
def sort(column=columns, order={"ascending": True, "descending": False}, x=(5, 50, 1)):
    right = right_comments_per_sub.sort_values(
        ascending=order,
        by=column
    ).head(x).reset_index(drop=True)
