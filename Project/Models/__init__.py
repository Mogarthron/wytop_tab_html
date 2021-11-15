import json


with open("./Project/Data/scierzki_do_plikow.json") as p:
    scierzki_do_plikow = json.load(p)["paths"]
