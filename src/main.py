import os
import time
import json
import google.cloud.logging
import logging
from config import _TEAM
from game_api import get_game_status, join_game, make_guess
from my_smart_algo import apply_guess
from colorama import init, Fore, Style

_MY_GUESS_TRACKER = {}
_TEAM_NOT_PROVIDED = (
    "Please put your team name and password into config.py and start again."
)
client = google.cloud.logging.Client()
client.get_default_handler()
client.setup_logging()

team = _TEAM
if team is None or _TEAM.strip() == "":
    print(_TEAM_NOT_PROVIDED)
    exit()

logging.info()
logging.info("Game Started")
logging.info("I am playing as {}".format(_TEAM))

def game_status_received(err, data):
    if err is not None:
        print(err)
        print("Get Game Status Failed")
    else:
        
        print(
            "GameId: {}\nRoundId: {}\nStatus: {}\n#Participants: {}".format(
                data["gameId"],
                data["roundId"],
                data["status"],
                len(data["participants"]),
            )
        )
        print(
            "------------------------------------------------------------------------------------------\n"
        )
        status = data["status"].lower()
        key = str(data["gameId"]) + "-" + str(data["roundId"])
        joined_status = False
        alive_status = False
        team_name = _TEAM.upper()
        for participant in data["participants"]:
            if (
                "name" in participant
                and participant["name"] == team_name
                and participant["joinedInThisRound"] == True
            ):
                joined_status = True
                alive_status = participant["isAlive"]

        if status == "joining":

            if not joined_status:
                err_join, data_join = join_game()
                if err_join is not None:
                    print("Join Failed")
                    print(err_join)
                else:
                    print("Join Successful")
                    print(data_join["message"])

            else:
                print("Already joined, waiting to play...")

        elif status == "running":
            if not joined_status:
                print(
                    "Oho, I have missed the joining phase, let me wait till the next round starts"
                )
            elif not alive_status:
                print("I am dead, waiting to respawn in next round...:(")
            else:
                my_next_guess = apply_guess(
                    data["gameId"],
                    data["roundId"],
                    data["secretLength"],
                    data["participants"],
                    _MY_GUESS_TRACKER,
                )
                if my_next_guess is not None and len(my_next_guess["guesses"]) > 0:
                    print("My guess: {}".format(my_next_guess), "\n")
                    json_object = json.dumps(my_next_guess)
                    err_guess, data_guess = make_guess(json_object)

                    if err_guess is not None:
                        print("Guess Failed\n")
                        print(err_guess, "\n")

                    else:
                        total_score_current_guess = 0
                        if (
                            "guesses" in data_guess
                            and data_guess["guesses"] is not None
                        ):
                            for item in data_guess["guesses"]:
                                if "score" in item:
                                    total_score_current_guess += item["score"]
                        print(
                            "Guess Successful : Score {}\n".format(
                                total_score_current_guess
                            )
                        )
                        print("Result : {}".format(data_guess))

                        guess_key = "Round-" + str(data["roundId"])

                        if key not in _MY_GUESS_TRACKER:
                            _MY_GUESS_TRACKER[key] = []

                        _MY_GUESS_TRACKER[key].append(data_guess)


while True:
    error, data = get_game_status()
    game_status_received(error, data)
    time.sleep(5)