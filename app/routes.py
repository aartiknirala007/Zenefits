from app import application
from flask import Flask, render_template, request
import requests
import json
import os


def get_nested_children(person):
    children = []
    if person["relationship"]["children_num"] == 0:
        return children
    for child in person["children"]:
        child["children"] = get_nested_children(child)
        children.append(child)

    return children


@application.route("/")
def result():
    r = requests.get(
        os.environ.get("API_URL") + "/core/people",
        headers={"Authorization": "Bearer " + os.environ.get("TOKEN")},
    )
    response = json.loads(r.text)
    data = response["data"]["data"]
    people = {
        "1": {
            "name": "Organization",
            "title": "",
            "relationship": {"children_num": 0},
            "children": [],
        }
    }
    for person in data:
        people[person["id"]] = {
            "id": person["id"],
            "name": person["last_name"],
            "title": person["title"],
            "relationship": {"children_num": 0},
            "children": [],
        }

    for person in data:
        manager_id = "1"
        if "url" in person["manager"] and person["manager"]["url"]:
            manager_id = person["manager"]["url"].split("/")[-1]
        people[person["id"]]["relationship"]["parent_num"] = 1
        people[manager_id]["children"].append(people[person["id"]])
        people[manager_id]["relationship"]["children_num"] += 1

    people["1"]["children"] = get_nested_children(people["1"])
    tree = json.dumps(people["1"])

    return render_template("index.html", response=tree)

