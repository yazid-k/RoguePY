import copy
import math
import random


# exceptions


def _find_getch():
    """Single char input, only works only on mac/linux/windows OS terminals"""
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return lambda: msvcrt.getch().decode('utf-8')

    # POSIX system. Create and return a getch that manipulates the tty.
    import sys, tty

    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch
def sign(x):
    if x > 0:
        return 1
    return -1


class Coord(object):
    """Implementation of a map coordinate"""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return '<' + str(self.x) + ',' + str(self.y) + '>'

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)

    def distance(self, other):
        """Returns the distance between two coordinates."""
        d = self - other
        return math.sqrt(d.x * d.x + d.y * d.y)

    cos45 = 1 / math.sqrt(2)
    cos180=-1
    cos0=0

    def direction(self, other):
        """Returns the direction between two coordinates."""
        d = self - other
        cos = d.x / self.distance(other)
        if cos > Coord.cos45:
            return Coord(-1, 0)
        elif cos < -Coord.cos45:
            return Coord(1, 0)
        elif d.y > 0:
            return Coord(0, -1)
        return Coord(0, 1)



class Element(object):
    """Base class for game elements. Have a name.
        Abstract class."""

    def __init__(self, name, abbrv=""):
        self.name = name
        if abbrv == "":
            abbrv = name[0]
        self.abbrv = abbrv

    def __repr__(self):
        return self.abbrv

    def description(self):
        """Description of the element"""
        return "<" + self.name + ">"

    def meet(self, hero):
        """Makes the hero meet an element. Not implemented. """
        raise NotImplementedError('Abstract Element')

class Stairs(Element):
    "Classe Escaliers"
    def __init__(self,name="Stairs",abbrv="^"):
        Element.__init__(self,name,abbrv)
        
    def meet(self,hero):
        print("Would you like to rest ? [0 : Yes, 1 : No]")
        c=getch()
        if c.isdigit():
            if int(c)==0 :
                for i in range(9):
                    theGame().floor.moveAllMonsters()
                if theGame().hero.hp+5>theGame().hero.maxhp :
                    theGame().hero.hp=theGame().hero.maxhp
                else :
                    theGame().hero.hp+=5
                curePoison(theGame().hero)
            if int(c)==1 or int(c)==0 :
                theGame().level+=1
                theGame().hero.kills=0
                theGame().buildFloor()
        
class Shop(Element):
    "Classe Boutique"
    
    def __init__(self,name="Shop",abbrv="S"):
        Element.__init__(self,name,abbrv)
        self.items=list(Game().equipments.values())
        self.actions=["Buy : 0","Sell : 1"]
        self.shop=[]


        "Construction de la boutique en fonction des equipments disponibles"
        i=0
        k=0
        while i<len(self.items):
            while k<len(self.items[i]):
                if self.items[i][k].name!="Gold":
                    self.shop.append(self.items[i][k])
                k+=1
            k=0
            i+=1

                    
    def buy(self,hero):
        "Le héros choisit l'objet qu'il veut acheter dans la boutique"
        print("What would you like to buy ? "+str([str(self.shop.index(e))+" : "+e.name +",  "+ str(e.buy)+" gold " for e in self.shop]))
        c = getch()
        if c.isdigit() and int(c) in range(len(self.shop)):
            if hero.money>=self.shop[int(c)].buy and len(hero._inventory)<10 :
                hero.money+=-self.shop[int(c)].buy
                hero.take(self.shop[int(c)])
                print("You bought "+self.shop[int(c)].name+" for "+str(self.shop[int(c)].buy)+" gold. ")
            if hero.money<self.shop[int(c)].buy :
                print("You do not have enough money. ")
            if len(hero._inventory)>=10:
                print("Your inventory is full .")
                    
    def sell(self,hero) :
        "Le héros choisit quel object vendre dans son inventaire"
        print("Which item would you like to sell ?"+str([str(hero._inventory.index(e)) + ": " + e.name+", "+str(e.sell)+" gold " for e in hero._inventory]))
        c = getch()
        if c.isdigit() and  int(c) in range(len(hero._inventory)):
            print("You sold your "+hero._inventory[int(c)].name+" for "+ str(hero._inventory[int(c)].sell)+ " gold. ")
            hero.money+=hero._inventory[int(c)].sell
            hero.Break(hero._inventory[int(c)])
        
    def selectAction(self):
        "Lorsque le héros 'meet' la boutique, il choisit quelle action prendre (acheter ou vendre)"
        c = getch()
        if c.isdigit() and int(c) in range(len(self.actions)):
            return self.actions[int(c)]
        
    def meet(self,hero):
        print("Welcome the shop ! What would you like to do ? ")        
        print(str(self.actions))
        x=self.selectAction()
        if x==self.actions[0]:
            self.buy(hero)
        if x==self.actions[1]:
            self.sell(hero)
            
            
class Chest(Element):
    "Classe Coffre"
    
    def __init__(self,name="Chest",abbrv="C"):
        Element.__init__(self,name,abbrv)
        self.items= Game.equipments
        
    def meet(self,hero):
        x = 2*theGame().level
        while self.items.get(x)==None :
            x=x-1
        i=0
        while i<len(hero._inventory):
            if hero._inventory[i].name=="Key":
                hero._inventory.pop(i)
                m=self.items.get(x)[0]
                hero.take(m)
                theGame().addMessage("You found a "+m.name+" in the Chest !")
                return True
            else:
                i+=1
        else :
            theGame().addMessage("You have to find a key to open the chest")
        
            
            

class Creature(Element):
    """A creature that occupies the dungeon.
        Is an Element. Has hit points and strength."""

    def __init__(self, name, hp, abbrv="", strength=1,speed=1,poisonous=False):
        Element.__init__(self, name, abbrv)
        self.hp = hp
        self.strength = strength
        self.maxhp=hp
        self.givenXP=self.maxhp//2
        self.poisonous=poisonous
        self.speed=speed
        
    def description(self):
        """Description of the creature"""
        return Element.description(self) + "(" + str(self.hp) + ")"

    def meet(self, other):
        """The creature is encountered by an other creature.
            The other one hits the creature. Return True if the creature is dead."""
        other.invisible=False
        self.hp -= other.strength
        if isinstance(other,Hero) and other.weapon != None:
            other.weapon.armeDurability(other)
        theGame().addMessage(" The " + other.name + " hits the " + self.description()+" ")
        if self.poisonous and other.poisoned==False:
            other.poisoned=True
            theGame().addMessage("You have been poisoned. ")
        if self.hp > 0:
            return False
        if isinstance(other,Hero):
            other.kills+=1
            if other.kills==theGame().floor.keyDrop :
                other.take(Equipment("Key"))
                theGame().addMessage(" The "+self.name+" dropped you a Key !")
            if self.hp<=0:
                if other.amulet!=None:
                    other.xp+=self.givenXP+other.amulet.xpbonus
        return True


class Hero(Creature):
    """The hero of the game.
        Is a creature. Has an inventory of elements. """

    def __init__(self, name="Hero", hp=10, abbrv="@", strength=2,poisonous=False):
        Creature.__init__(self, name, hp, abbrv, strength)
        self._inventory = []
        self.money=0
        self.kills=0
        self.givenXP=0
        self.xp=0
        self.maxhunger=20
        self.hunger=self.maxhunger
        self.level=1
        self.maxhp=hp
        self.manamax=self.maxhp
        self.mana=self.manamax
        self._countdown=0
        self.invisible=False
        self.weapon=None
        self.poisoned=False
        self.amulet=None

    def description(self):
        """Description of the hero"""
        return Creature.description(self) + str(self._inventory)+"("+str(self.hunger)+")"+" MP: "+str(self.mana)+" "

    def fullDescription(self):
        """Complete description of the hero"""
        res = ''
        for e in self.__dict__:
            if e[0] != '_':
                res += '> ' + e + ' : ' + str(self.__dict__[e]) + '\n'
        res += '> INVENTORY : ' + str([x.name for x in self._inventory])
        return res

    def checkEquipment(self, o):
        """Check if o is an Equipment."""
        if not isinstance(o, Equipment):
            raise TypeError('Not a Equipment')

    def take(self, elem):
        """The hero takes adds the equipment to its inventory"""
        self.checkEquipment(elem)
        if len(self._inventory)<10:
            self._inventory.append(elem)
            return True
        else :
            theGame().addMessage("You don't have space in your inventory")
            return False

    def use(self, elem):
        """Use a piece of equipment"""
        if elem is None:
            return
        self.checkEquipment(elem)
        if elem not in self._inventory:
            raise ValueError('Equipment ' + elem.name + 'not in inventory')
        if elem.use(self):
            elem.durability-=1
            if elem.durability==0:
                self.Break(elem)

    def canLevelUp(self):
        "Vérifie si le héros peut passer au niveau suivant"
        necessaryXP=nextXP(self.level)
        if self.xp>=necessaryXP:
            return True
        return False

    def levelUp(self):
        "Le héros prends un niveau et a des stats améliorées"
        self.level+=1
        self.strength+=1
        self.maxhp+=3
        self.hp=self.maxhp
        curePoison(self)
        self.xp=0
        restoreMana(self)

    def lowerHunger(self):
        if self.hunger > 0:
            if theGame().hungloop==2:
                self.hunger+=-1
                theGame().hungloop=0
            else:
                theGame().hungloop+=1
        else:
            if theGame().hploop==1:
                self.hp+=-1
                theGame().hploop=0
            else:
                theGame().hploop+=1

    def Break(self,elem):
        self._inventory.remove(elem)

    def castSpell(self,spell):
        if isinstance(spell,int):
            spellChosen=theGame().spells[spell][0]
            spellCost=theGame().spells[spell][1]
            if self.mana>=spellCost:
                spellChosen(self)
                self.mana+=-spellCost
            else :
                theGame().addMessage("You don't have enough mana to cast this spell. ")

    def invisibility(self):
        if self.invisible and self._countdown <5 :
            theGame().addMessage("You are invisible ")
            self._countdown+=1
            return True
        self._countdown=0
        self.invisible=False
        return False

    def checkPoison(self):
        "Decrease in hp due to poison"
        if self.poisoned:
            if theGame().poisonloop==2:
                self.hp+=-1
                theGame().poisonloop=0
            else :
                theGame().poisonloop+=1

class Equipment(Element):
    """A piece of equipment"""

    def __init__(self, name, abbrv="",buy=2,sell=1,durability=1,usage=None):
        Element.__init__(self, name, abbrv)
        self.buy=buy #Chaque objet a un prix fixé dans la boutique
        self.sell=sell #Chaque objet a un prix de vente fixé
        self.usage = usage
        self.durability=durability

    def meet(self, hero):
        """Makes the hero meet an element. The hero takes the element."""
        if self.name=="Gold":
            hero.money+=1
        else :
            hero.take(self)
        theGame().addMessage("You pick up a " + self.name+" ")
        return True

    def use(self, creature):
        """Uses the piece of equipment. Has effect on the hero according usage.
            Return True if the object is consumed."""
        if self.usage is None:
            theGame().addMessage("The " + self.name + " is not usable ")
            return False
        else:
            theGame().addMessage("The " + creature.name + " uses the " + self.name+" ")
            return self.usage(self, creature)

class Weapon(Equipment):
    "Classe Armes"
    def __init__(self,name,strength,abbrv="",buy=2,sell=1,usage= None,durability=3):
        Equipment.__init__(self,name,abbrv,buy,sell,usage)
        self.strength=strength
        self.durability=durability

    def use(self,hero):
        "Place l'arme dans l'attribut equipement du Hero et l'enleve de l'inventaire"
        if hero.weapon!=None:
            hero.take(hero.weapon)
            hero.strength+=-hero.weapon.strength
        hero.weapon=self
        hero.Break(self)
        hero.strength+=self.strength
        theGame().addMessage("You equiped " +self.name+".")

    def armeDurability(self, hero):
        if hero.weapon is not None:
            hero.weapon.durability -= 1
            if hero.weapon.durability <= 0:
                theGame().addMessage("Your "+hero.weapon.name+" has broke. ")
                hero.strength -= hero.weapon.strength
                hero.weapon = None

class Amulet(Equipment):
    "Classe amulettes"
    def __init__(self,name,abbrv="",buy=2,sell=1,usage=None,strength=1,regen=1,xpbonus=1):
        Equipment.__init__(self,name,abbrv,buy,sell,usage)
        self.strength=strength
        self.regen=regen
        self.xpbonus=xpbonus

    def use(self,hero):
        "Place l'amulette dans l'attribut amulette de l'héro"
        if hero.amulet!=None:
            hero.take(hero.amulet)
            hero.strength+=-hero.amulet.strength
        hero.amulet=self
        hero.Break(self)
        hero.strength+=self.strength
        theGame().addMessage("You equiped "+ self.name+". ")

    def regeneration(self,hero):
        if theGame().regenloop<3:
            theGame().regenloop+=1
        if theGame().regenloop==3:
            if hero.hp+self.regen<hero.maxhp:
                hero.hp+=self.regen
            else :
                hero.hp=hero.maxhp
            theGame().regenloop=0

        
class Room(object):
    """A rectangular room in the map"""

    def __init__(self, c1, c2):
        self.c1 = c1
        self.c2 = c2

    def __repr__(self):
        return "[" + str(self.c1) + ", " + str(self.c2) + "]"

    def __contains__(self, coord):
        return self.c1.x <= coord.x <= self.c2.x and self.c1.y <= coord.y <= self.c2.y

    def intersect(self, other):
        """Test if the room has an intersection with another room"""
        sc3 = Coord(self.c2.x, self.c1.y)
        sc4 = Coord(self.c1.x, self.c2.y)
        return self.c1 in other or self.c2 in other or sc3 in other or sc4 in other or other.c1 in self

    def center(self):
        """Returns the coordinates of the room center"""
        return Coord((self.c1.x + self.c2.x) // 2, (self.c1.y + self.c2.y) // 2)

    def randCoord(self):
        """A random coordinate inside the room"""
        return Coord(random.randint(self.c1.x, self.c2.x), random.randint(self.c1.y, self.c2.y))

    def randEmptyCoord(self, map):
        """A random coordinate inside the room which is free on the map."""
        c = self.randCoord()
        while map.get(c) != Map.ground or c == self.center():
            c = self.randCoord()
        return c

    def decorate(self, map):
        """Decorates the room by adding a random equipment and monster."""
        map.put(self.randEmptyCoord(map), theGame().randEquipment())
        map.put(self.randEmptyCoord(map), theGame().randMonster())


class Map(object):
    """A map of a game floor.
        Contains game elements."""

    ground = '.'  # A walkable ground cell
    dir = {'z': Coord(0, -1), 's': Coord(0, 1), 'd': Coord(1, 0), 'q': Coord(-1, 0)}  # four direction user keys
    empty = ' '  # A non walkable cell

    def __init__(self, size=20, hero=None):
        self._mat = []
        self._elem = {}
        self._rooms = []
        self._roomsToReach = []

        for i in range(size):
            self._mat.append([Map.empty] * size)
        if hero is None:
            hero = Hero()
        self.hero = hero
        self.generateRooms(15)
        self.reachAllRooms()
        self.put(self._rooms[0].center(), hero)
        self.addStairs()
        self.addShop()
        self.addChest()
        for r in self._rooms:
            r.decorate(self)
        self.keyDrop=random.randint(1,self.monstersCount())

    def addRoom(self, room):
        """Adds a room in the map."""
        self._roomsToReach.append(room)
        for y in range(room.c1.y, room.c2.y + 1):
            for x in range(room.c1.x, room.c2.x + 1):
                self._mat[y][x] = Map.ground

    def findRoom(self, coord):
        """If the coord belongs to a room, returns the room elsewhere returns None"""
        for r in self._roomsToReach:
            if coord in r:
                return r
        return None

    def intersectNone(self, room):
        """Tests if the room shall intersect any room already in the map."""
        for r in self._roomsToReach:
            if room.intersect(r):
                return False
        return True

    def dig(self, coord):
        """Puts a ground cell at the given coord.
            If the coord corresponds to a room, considers the room reached."""
        self._mat[coord.y][coord.x] = Map.ground
        r = self.findRoom(coord)
        if r:
            self._roomsToReach.remove(r)
            self._rooms.append(r)

    def corridor(self, cursor, end):
        """Digs a corridors from the coordinates cursor to the end, first vertically, then horizontally."""
        d = end - cursor
        self.dig(cursor)
        while cursor.y != end.y:
            cursor = cursor + Coord(0, sign(d.y))
            self.dig(cursor)
        while cursor.x != end.x:
            cursor = cursor + Coord(sign(d.x), 0)
            self.dig(cursor)

    def reach(self):
        """Makes more rooms reachable.
            Start from one random reached room, and dig a corridor to an unreached room."""
        roomA = random.choice(self._rooms)
        roomB = random.choice(self._roomsToReach)

        self.corridor(roomA.center(), roomB.center())

    def reachAllRooms(self):
        """Makes all rooms reachable.
            Start from the first room, repeats @reach until all rooms are reached."""
        self._rooms.append(self._roomsToReach.pop(0))
        while len(self._roomsToReach) > 0:
            self.reach()

    def randRoom(self):
        """A random room to be put on the map."""
        c1 = Coord(random.randint(0, len(self) - 3), random.randint(0, len(self) - 3))
        c2 = Coord(min(c1.x + random.randint(3, 8), len(self) - 1), min(c1.y + random.randint(3, 8), len(self) - 1))
        return Room(c1, c2)

    def generateRooms(self, n):
        """Generates n random rooms and adds them if non-intersecting."""
        for i in range(n):
            r = self.randRoom()
            if self.intersectNone(r):
                self.addRoom(r)

    def addStairs(self):
        "Rajoute des ecaliers au centre d'une salle choisie au hasard"
        room=random.choice(self._rooms)
        center=Room.center(room)
        while self.get(center)!=self.ground :
            room=random.choice(self._rooms)
            center=Room.center(room)
        self.put(center,Stairs())

    def addShop(self):
        "Rajoute une boutique au centre d'une salle choisie au hasard"
        room=random.choice(self._rooms)
        center=Room.center(room)
        while self.get(center)!=self.ground :
            room=random.choice(self._rooms)
            center=Room.center(room)
        self.put(center,Shop())

    def addChest(self):
        "Rajoute un coffre au centre d'une salle choisie au hasard"
        room=random.choice(self._rooms)
        center=Room.center(room)
        while self.get(center)!=self.ground :
            room=random.choice(self._rooms)
            center=Room.center(room)
        self.put(center,Chest())
        
    def __len__(self):
        return len(self._mat)

    def __contains__(self, item):
        if isinstance(item, Coord):
            return 0 <= item.x < len(self) and 0 <= item.y < len(self)
        return item in self._elem

    def __repr__(self):
        s = ""
        for i in self._mat:
            for j in i:
                s += str(j)
            s += '\n'
        return s

    def checkCoord(self, c):
        """Check if the coordinates c is valid in the map."""
        if not isinstance(c, Coord):
            raise TypeError('Not a Coord')
        if not c in self:
            raise IndexError('Out of map coord')

    def checkElement(self, o):
        """Check if o is an Element."""
        if not isinstance(o, Element):
            raise TypeError('Not a Element')

    def put(self, c, o):
        """Puts an element o on the cell c"""
        self.checkCoord(c)
        self.checkElement(o)
        if self._mat[c.y][c.x] != Map.ground:
            raise ValueError('Incorrect cell')
        if o in self._elem:
            raise KeyError('Already placed')
        self._mat[c.y][c.x] = o
        self._elem[o] = c

    def get(self, c):
        """Returns the object present on the cell c"""
        self.checkCoord(c)
        return self._mat[c.y][c.x]

    def pos(self, o):
        """Returns the coordinates of an element in the map """
        self.checkElement(o)
        return self._elem[o]

    def rm(self, c):
        """Removes the element at the coordinates c"""
        self.checkCoord(c)
        del self._elem[self._mat[c.y][c.x]]
        self._mat[c.y][c.x] = Map.ground

    def move(self, e, way):
        """Moves the element e in the direction way."""
        orig = self.pos(e)
        dest = orig + way
        if dest in self:
            if self.get(dest) == Map.ground:
                self._mat[orig.y][orig.x] = Map.ground
                self._mat[dest.y][dest.x] = e
                self._elem[e] = dest
            elif self.get(dest) != Map.empty and self.get(dest).meet(e) and self.get(dest) != self.hero:
                self.rm(dest)

    def moveAllMonsters(self):
        """Moves all monsters in the map.
            If a monster is at distance lower than 6 from the hero, the monster advances."""
        h = self.pos(self.hero)
        for e in self._elem:
            c = self.pos(e)
            if isinstance(e, Creature) and e != self.hero and c.distance(h) < 6:
                for i in range(0,e.speed):
                    d = c.direction(h)
                    if self.get(c + d) in [Map.ground, self.hero]:
                        self.move(e, d)

    def monstersCount(self):
        "Compte le nombre de monstre sur la map"
        l=len(self._elem)
        i=0
        m=-1
        while i<l:
            if isinstance(list(self._elem)[i],Creature):
                m+=1
            i+=1
        return m


def heal(creature):
    """Heal the creature"""
    if creature.hp+ 3 < creature.maxhp:
        creature.hp+=3
    else :
        creature.hp=creature.maxhp
    curePoison(creature)
    return True

def nextXP(n):
    "Donne le nombre d'XP nécessaire pour passer au niveau suivant en fonction du niveau du héro"
    if n==1:
        return 10
    return 5+nextXP(n-1)

def eat(hero,feed):
    "Rajoute la quantité feed a la barre de faim du héro sans dépasser le maximum"
    if hero.hunger+feed<=hero.maxhunger:
        hero.hunger+=feed
    else :
        hero.hunger=hero.maxhunger
    return True


def teleport(creature, unique):
    """Teleport the creature"""
    r = random.choice(theGame().floor._rooms)
    c = r.randCoord()
    while not theGame().floor.get(c) == Map.ground:
        c = r.randCoord()
    theGame().floor.rm(theGame().floor.pos(creature))
    theGame().floor.put(c, creature)
    return unique

def restoreMana(hero):
    if hero.mana+3<=hero.manamax:
        hero.mana+=3
    else :
        return True

def curePoison(hero):
    "Cure the hero from poison"
    if isinstance(hero,Hero) and hero.poisoned :
        hero.poisoned=False
        theGame().addMessage("You are no longer poisoned. ")
    return True

    
class Game(object):
    """ Class representing game state """
    """ available equipments """
    equipments = {0: [Equipment("Heal potion", "!", usage=lambda self, hero: heal(hero)), \
                      Equipment("Gold", "o")], \
                  1: [Equipment("Teleport potion", "?", usage=lambda self, hero: teleport(hero, True)),Weapon("Sword",2,"s")], \
                  2: [Weapon("Axe",4,"a",4,2),Amulet("Water Amulet","£",4,2,None,1,3,1),Amulet("Fire Amulet","£",4,2,None,3,1,1),Amulet("Air Amulet","€",4,2,None,1,1,3)], \
                  3: [Equipment("Portoloin", "w",6,2,3, usage=lambda self, hero: teleport(hero, False)),Equipment("Chicken","m",6,2,usage= lambda item,hero: eat(hero,16))], \
                  }
    
    """ available monsters """
    monsters = {0: [Creature("Goblin", 4), Creature("Bat", 2, "W")],
                1: [Creature("Ork", 6, strength=2),Creature("Spider",4,"X",poisonous=True), Creature("Blob", 10)], 5: [Creature("Dragon", 20, strength=3)]}

    """ available actions """
    _actions = {'z': lambda h: theGame().floor.move(h, Coord(0, -1)), \
                'q': lambda h: theGame().floor.move(h, Coord(-1, 0)), \
                's': lambda h: theGame().floor.move(h, Coord(0, 1)), \
                'd': lambda h: theGame().floor.move(h, Coord(1, 0)), \
                'i': lambda h: theGame().addMessage(h.fullDescription()), \
                'k': lambda h: h.__setattr__('hp', 0), \
                'u': lambda h: h.use(theGame().select(h._inventory)), \
                ' ': lambda h: None, \
                'h': lambda hero: theGame().addMessage("Actions disponibles : " + str(list(Game._actions.keys()))), \
                'b': lambda hero: theGame().addMessage("I am " + hero.name), \
                'v': lambda hero: theGame().hero.Break(theGame().select(hero._inventory)), \
                'w': lambda hero: hero.castSpell(theGame().selectSpell()), \
                }

    spells = { "teleportation": [lambda self: teleport(self,True),5], \
    	       "heal": [lambda self: heal(self),3], \
    	       "invisibility" : [lambda self: self.__setattr__("invisible",True),8]}

    def __init__(self, level=1, hero=None):
        self.level = level
        self._message = []
        if hero == None:
            hero = Hero()
        self.hero = hero
        self.floor = None
        self.hungloop=0
        self.hploop=0
        self.poisonloop=0
        self.regenloop=0

    def buildFloor(self):
        """Creates a map for the current floor."""
        self.floor = Map(hero=self.hero)

    def addMessage(self, msg):
        """Adds a message in the message list."""
        self._message.append(msg)

    def readMessages(self):
        """Returns the message list and clears it."""
        s = ''
        for m in self._message:
            s += m
        self._message.clear()
        return s

    def randElement(self, collect):
        """Returns a clone of random element from a collection using exponential random law."""
        x = random.expovariate(1 / self.level)
        for k in collect.keys():
            if k <= x:
                l = collect[k]
        return copy.copy(random.choice(l))

    def randEquipment(self):
        """Returns a random equipment."""
        return self.randElement(Game.equipments)

    def randMonster(self):
        """Returns a random monster."""
        return self.randElement(Game.monsters)
    
    def select(self, l):
        print("Choose item> " + str([str(l.index(e)) + ": " + e.name for e in l])+" You have "+str(self.hero.money)+" gold.")
        c = getch()
        if c.isdigit() and int(c) in range(len(l)):
            return l[int(c)]

    def selectSpell(self):
        l=list(self.spells.keys())
        s=[str(l.index(x))+": "+x for x in l]
        print("Choose a spell to cast> "+str(s))
        c=getch()
        if c.isdigit() and int(c) in range(len(s)):
            return l[int(c)]

    def play(self):
        """Main game loop"""
        self.buildFloor()
        print("--- Welcome Hero! ---")
        while self.hero.hp > -999 :
            print()
            print(self.floor)
            print(self.hero.description())
            print(self.readMessages())
            c = getch()
            if c in Game._actions:
                Game._actions[c](self.hero)
            if not self.hero.invisibility() :
                self.floor.moveAllMonsters()
            self.hero.lowerHunger()
            if self.hero.amulet!=None:
                self.hero.amulet.regeneration(self.hero)
            self.hero.checkPoison()
            if self.hero.canLevelUp():
                self.hero.levelUp()
                theGame().addMessage("Level Up !")
        print("--- Game Over ---")

def theGame(game=Game()):
    """Game singleton"""
    return game


getch = _find_getch()
theGame().play()