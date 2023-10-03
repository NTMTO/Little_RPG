import random
import time


testing = False



def trance(fn):
    def wrapper(self, *args, **kwargs):
        if self.tranced:
            printout(f"{self.name} is in a trance and does nothing this turn.")
            self.tranced = None
        else:
            return fn(self, *args, **kwargs)
    return wrapper


def terror(fn):
    def wrapper(self, *args, **kwargs):
        if self.terrified:
            printout(f"{self.name} is terrified! They try to run away instead.")
            self.run(*args, **kwargs)
            self.terrified = None
        else:
            return fn(self, *args, **kwargs)
    return wrapper


def printout(string):
    string = string + " (Press Enter)"
    if testing:
        print(string)
    else:
        input(string)


class Char():
    def __init__(self, name, hp, armor):
        self.name = name
        self.hitpoints = hp
        self.armor = armor
        self.strength = self.hitpoints + self.armor
        self.damage = (self.hitpoints - self.armor / 4) + self.strength
        self.charisma = 20 - self.hitpoints
        self.speed = 20 - self.armor
        self.tranced = None
        self.terrified = None
        self.defeated = None


    def __repr__(self):
        return self.__doc__

    @terror
    @trance
    def attack(self, opponent):
        winner, diff = self.test('damage', 'strength', opponent)
        if self == winner:
            attack_val = self.damage - opponent.armor
            result = opponent.hitpoints - attack_val
            printout(f"{self.name} attacked {opponent.name} for {attack_val} hit points")
            opponent.deal_damage(diff)
            opponent.hitpoints = result
        else:
            printout(f"{self.name}'s attack narrowly missed its mark!")

    @terror
    @trance
    def charm(self, opponent):
        printout(f"{self.name} is trying to charm {opponent.name}")
        winner, diff = self.test('charisma', 'charisma', opponent)
        if self == winner:
            printout("Success!")
            result = random.choice(['trance', 'terrify'])
            if result == 'trance' or type(opponent) == Hero:
                printout(f"{self.name} has put {opponent.name} into a trance. They will do nothing on their next turn!")
                opponent.tranced = True
            elif result == 'terrify':
                printout(f"{opponent.name} has been terrified")
                opponent.terrified = True
        else:
            printout(f"{opponent.name} resisted the charm!")

    def defeat(self):
        printout(f"{self.name} has been defeated!")
        self.defeated = True

    def spawn(self):
        printout(f"a {self.name} has appeared!")

    @trance
    def run(self, opponent):
        printout(f"{self.name} is trying to run away!")
        winner, diff = self.test('speed', 'strength', opponent)
        # if testing:
        #     winner = opponent
        if self == winner:
            printout(f"{opponent.name} couldn't stop {self.name} from running away!")
            if type(self) == Hero:
                opponent.defeated = True
            else:
                self.defeated = True
        else:
            printout(f"{opponent.name} stopped {self.name} from running away!")

    def test(self, off_trait, def_trait, opponent):
        params = {self: off_trait, opponent: def_trait}
        result = ""
        totals = {self: '', opponent: ''}
        for character, trait in params.items():
            roll = random.choice(range(21))
            trait_str = trait
            trait = character.__dict__[trait]
            total = roll + trait
            totals[character] = total
            printout(f"{character.name} rolled a {str(roll)} plus {str(trait)} for a total of {str(total)} {trait_str}")
        winner = [character for character, total in totals.items() if total == max([total for total in totals.values()])][0]
        diff = totals[winner] - [totals[character] for character in totals.keys() if character != winner][0]
        return winner, diff

    def deal_damage(self, hps):
        self.hitpoints -= hps
        if self.hitpoints <= 0:
            self.defeat()
        else:
            printout(f'{self.name} has suffered {str(hps)} damage and has {self.hitpoints} remaining.')



class Hero(Char):
    """
    This is you. An intrepid adventurer venturing into the unknown in search of treasure, power, and glory!
    """

    def __init__(self, Char):
        if testing:
            name = 'Albert'
        else:
            name = input("Please enter your hero's name:  ")
        properties = {
            'hitpoints': range(21), 'armor': range(6)
        }
        for key, value in properties.items():
            while True:
                try:
                    maximum = max(value)
                    minimum = min(value)
                    err_msg = f"Value must been between {str(minimum)} and {str(maximum)}"
                    if testing:
                        properties[key] = 5
                    else:
                        properties[key] = int(input(f"Choose your maximum {key} from 1-{str(maximum)}:  "))
                    if maximum < properties[key] > minimum:
                        printout(err_msg)
                        continue
                    break
                except ValueError:
                    printout(err_msg)
        Char.__init__(self, name, properties['hitpoints'], properties['armor'])


class Enemy(Char):
    """
    A randomly generated enemy guarding the way. It is irrationally afraid of doorways!
    """

    def __init__(self, Char):
        name = random.choice([
            "dragon",
            "henchman",
            "wizard"
        ])
        hp = random.choice(range(5, 20))
        armor = random.choice(range(6))
        Char.__init__(self, name, hp, armor)


def generate_enemies():
    enemies = []
    num_enemies = random.choice(range(1,4))
    while num_enemies > 0:
        enemies.append(Enemy(Char))
        num_enemies -= 1
    return enemies


def choice(char, enemy, command):
    command = command.lower().strip()
    method = getattr(char, command)
    method(enemy)


def check_enemy_def(enemies, enemy):
    if enemy and enemy.defeated:
        enemies.remove(enemy)
        if len(enemies) > 0:
            enemy = enemies[0]
            enemy.spawn()
        else:
            enemy = None
    return enemies, enemy


def start():
    hero = Hero(Char)
    prinout(hero.__repr__())
    enemies = generate_enemies()
    enemies[0].spawn()
    while len(enemies) > 0:
        enemy = enemies[0]
        if testing:
            command = 'run'
        else:
            command = input("What would you like to do? You can try to attack, charm, or run:  ")
        try:
            choice(hero, enemy, command)
        except:
            printout("Sorry, that is not a valid command. Please try again.")
            continue
        enemies, enemy = check_enemy_def(enemies, enemy)
        enemy_action = random.choice(['attack', 'charm', 'run'])
        if testing:
            enemy_action = 'run'
        if enemy:
            choice(enemy, hero, enemy_action)
        enemies, enemy = check_enemy_def(enemies, enemy)
        if hero.defeated:
            print(f"{hero.name} has been defeated! Better luck next time.\n-Game Over-\n")
            return
    print("All enemies have been defeated!\n-You Win!-\n")

# testing = True
start()




