from flask import Flask ,jsonify,request
from dungeon import Hero,Monster
import json
import uuid
app = Flask(__name__)
games = {}

@app.route("/new_game", methods = ["POST"])

def new_game():
    game_id = str(uuid.uuid4())
    with open("hero.json", mode="r", encoding="utf-8") as file:
        hero_data = json.load(file)
    hero = Hero(hero_data["name"],hero_data["hp"],hero_data["attack"])

    with open("monster.json", mode="r", encoding="utf-8") as file:
        monster_data = json.load(file)    

    monsters = []

    for data in monster_data:
        monsters.append(
            Monster(data["name"],
                    data["hp"],
                    data["attack"]
                )
            )
    games[game_id] = {"hero": hero, "monsters": monsters}
    response = {
        "game_id": game_id,
        "hero": {"name": hero_data["name"],"hp":hero_data["hp"],"attack":hero_data["attack"]},
        "monster": {"name": monsters["name"],"hp":monsters["hp"],"attack":monsters["attack"]}
    }
    return jsonify(response)

@app.route("/action", methods = ["POST"])

def action():
    pass

if __name__ == "__main__":
    app.run(debug=True)