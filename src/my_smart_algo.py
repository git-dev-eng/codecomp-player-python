import random
import math
import json
from config import _TEAM


def apply_guess(game_id, round_id, secret_length, participants, guess_tracker):

    my_guess = {"guesses": []}

    # Remove myself, I don't want to guess my secret and eventually suicide. Do I? :)
    # Also remove "dead" enemies
    dead_participants_index = []
    print(participants)
    for index in range(len("participants", [])):
        if (
            not partcipants[index]["isAlive"]
            or partcipants[index]["teamId"] == _TEAM
        ):
            dead_participants_index.append(index)

    if len(dead_participants_index) > 0:
        for index in sorted(dead_participants_index, reverse=True):
            del participants[index]

    total_participants = len(participants)

    for random_guess in range(5):
        try:
            participant = participants[
                random.randint(0, total_participants - 1)
            ]
            secret_range = math.pow(10, secret_length - 1)
            secret = random.randint(secret_range, secret_range * 10 - 1)
            guess = {}
            guess["team"] = participant["name"]
            guess["guess"] = str(secret)
            my_guess["guesses"].append(guess)

        except Exception as e:
            print(e)
            return None

    return my_guess
