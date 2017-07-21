import json
import os.path

if os.path.isfile("config.json"):
    config_file = open("config.json", "r")
    config = json.load(config_file)
    TOKEN = config["TOKEN"]
    config_file.close()
else:
    TOKEN = input("Enter TOKEN: ")

print(TOKEN)
