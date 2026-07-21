import random
hit_points = 10
mhit_points = 20
attk_pwr = random.randrange(1,10)
mattk_pwr = random.randrange(1,10)
hero_name = input("Enter your Heros name: ")
monsters = {
    'mobs':
    [{
        "name": 'zombie', 
        "hp": 20,
        "attack": 5
    }
    ]
}
print(f"{hero_name} has stepped into the dungeon with {hit_points} HP and {attk_pwr} attack")

print(f"{hero_name} has appeared to find a wandering {monsters['mobs'][0]['name']}")   

def attack(monster_H,attack_H):
    monster_H -= attack_H
    return monster_H

def defend(hero_HP, mattk,defense):
    reduced = defense - mattk

    if reduced < 0:

       hero_HP += reduced
       print(f"HERO {hero_name} take {abs(reduced)} dmg by the {monsters['mobs'][0]['name']}\n")
    else:
        print("You have defended against the attk\n")

    return hero_HP

def win_status(hero_hp, Mon_HP):
    win_status = False 
    if hero_hp <= 0:
        print("YOU LOST!!!")
        win_status = True
    elif Mon_HP <= 0:
        print("YOU WON!!!")
        win_status = True

    return win_status

def show_status(mattk_pwr, hero_HP, mon_HP):

    return f"\nHero: {hero_name}\tMonster: {monsters['mobs'][0]['name']}\nHP: {hero_HP}\t\tHP: {mon_HP}\nATK: {attk_pwr}\t\tATK: {mattk_pwr}"

def monster_turn(hero_HP, mattk):

    hero_HP -= mattk

    return hero_HP

def fight(hit_points,mhit_points,attk_pwr,mattk_pwr):

    print(show_status(mattk_pwr,hit_points,mhit_points))
    user = input("CHOOSE: ATTACK or DEFEND").lower()
    if user == "attack":
        print(f"HERO {hero_name} attacks {monsters['mobs'][0]['name']} for {attk_pwr} dmg.\n")
        mhit_points = attack(mhit_points,attk_pwr)

        print(f"MONSTER {monsters['mobs'][0]['name']} attacks {hero_name} for {mattk_pwr} dmg.\n")
        hit_points = monster_turn(hit_points,mattk_pwr)

    elif user == "defend":

        hit_points = defend(hit_points,mattk_pwr,5)

    else:
        print("TRY AGAIN!\n")

    return hit_points,mhit_points

while True:

    hit_points,mhit_points = fight(hit_points,mhit_points,attk_pwr,mattk_pwr)
    game_end = win_status(hit_points,mhit_points)
    if game_end == True:
        break
    attk_pwr = random.randrange(1,10)
    mattk_pwr = random.randrange(1,10)

