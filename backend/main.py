import time
import enum
import flask
import random
import requests
import datetime
import pymongo.mongo_client


class Status(enum.IntEnum):
    WRONG = 0
    WRONG_SPOT = 1
    CORRECT = 2


MAX_ATTEMPTS = 6
MAX_LEADERBOARD = 10
RESET_TIME = 3600
FROM = 6
TO = 13
DOMAIN = "domain.com"
DEBUG = __name__ == "__main__"

app = flask.Flask(__name__)
database = pymongo.mongo_client.MongoClient().wordl.users
if DEBUG:
    words = ["океан", "пилот", "шамот"]
else:
    words = open("words.txt", encoding="utf-8").read().split("\n")


def decode_jwt(jwt: str) -> dict:
    if jwt is None:
        return None
    r = requests.get(
        "https://oauth2.googleapis.com/tokeninfo", params={"id_token": jwt}
    ).json()
    if (
        "error" in r
        or int(r["exp"]) < time.time()
    ):
        return None
    if r["email"].split("@")[1] != DOMAIN and not DEBUG:
        return None
    return r


@app.route("/get")
def api_get():
    jwt = decode_jwt(flask.request.cookies.get("jwt"))
    if jwt is None:
        return flask.Response(status=400)
    user = database.find_one(jwt["sub"])
    if user is None:
        user = {
            "_id": jwt["sub"],
            "name": jwt["family_name"] + " " + jwt["given_name"],
            "totalWins": 0,
            "totalAttempts": 0,
            "totalTime": 0.0,
            "word": None,
            "attempts": list(),
            "time": 0,
            "available": True,
        }
        database.insert_one(user)

    if (
        FROM <= datetime.datetime.now(datetime.timezone.utc).hour <= TO
        and time.time() // 3600 > user["time"] // 3600
        and user["word"] is None
    ):
        database.update_one(
            {"_id": jwt["sub"]}, {"$set": {"attempts": list(), "available": True}}
        )
        user = database.find_one(jwt["sub"])

    del user["word"]
    return user


@app.route("/check")
def api_check():
    jwt = decode_jwt(flask.request.cookies.get("jwt"))
    if jwt is None:
        return flask.Response(status=400)
    user = database.find_one(jwt["sub"])
    if user is None or len(user["attempts"]) == MAX_ATTEMPTS:
        return flask.Response(status=400)

    if user["word"] is None:
        word = random.choice(words)
        database.update_one(
            {"_id": jwt["sub"]},
            {"$set": {"word": word, "time": time.time()}},
        )
        user = database.find_one(jwt["sub"])
    
    word = flask.request.args.get("word", "")
    if len(word) != 5 or word not in words:
        return flask.Response(status=400)

    status: list[Status] = []
    count = {char: user["word"].count(char) for char in set(user["word"])}
    indices = set()
    for i, char in enumerate(word):
        if char == user["word"][i]:
            status.append(Status.CORRECT)
            indices.add(i)
            count[char] -= 1
        else:
            status.append(None)
    for i, char in enumerate(word):
        if status[i] is not None:
            continue
        if char in user["word"] and count[char] > 0:
            status[i] = Status.WRONG_SPOT
            count[char] -= 1
        else:
            status[i] = Status.WRONG
    database.update_one({"_id": jwt["sub"]}, {"$push": {"attempts": (word, status)}})

    if status.count(Status.CORRECT) == len(status):
        database.update_one(
            {"_id": jwt["sub"]},
            {
                "$set": {"available": False, "word": None},
                "$inc": {
                    "totalWins": 1,
                    "totalAttempts": len(user["attempts"]),
                    "totalTime": time.time() - user["time"],
                },
            },
        )
    elif len(user["attempts"]) + 1 == MAX_ATTEMPTS:
        status.append(user["word"])
        database.update_one(
            {"_id": jwt["sub"]},
            {
                "$set": {"available": False, "word": None},
            },
        )
    return status


@app.get("/leaderboard")
def api_leaderboard():
    return list(
        database.aggregate(
            [
                {
                    "$sort": {
                        "totalWins": -1,
                        "totalAttempts": 1,
                        "totalTime": 1,
                    }
                },
                {"$limit": MAX_LEADERBOARD},
                {
                    "$project": {
                        "_id": 1,
                        "name": 1,
                        "totalAttempts": 1,
                        "totalTime": 1,
                        "totalWins": 1,
                    }
                },
            ]
        )
    )


if DEBUG:
    app.run()
