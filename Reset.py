import yaml

ROUND_DATA = {"LUCK": 0 ,
              "SCORE_STRENGTH": 0 }

# 重写

with open("config/ROUND.yaml","wt") as f:
    yaml.dump(data=ROUND_DATA, stream=f, allow_unicode=True)

with open("config/PlayerList","wt") as f:
    f.write("")