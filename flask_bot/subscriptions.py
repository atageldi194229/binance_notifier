import json
import os.path

subscriptions_file = "subscriptions.json"

def get_subscriptions():
    if not os.path.isfile(subscriptions_file):
        return []
    
    with open(subscriptions_file, 'r') as openfile:
        return list(json.load(openfile))

def set_subscriptions(subscriptions):
    with open(subscriptions_file, "w") as outfile:
        json.dump(list(set(subscriptions)), outfile)
