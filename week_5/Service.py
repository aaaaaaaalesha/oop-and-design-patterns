import pygame
import random
import yaml
import os
import Objects

OBJECT_TEXTURE = os.path.join("texture", "objects")
ENEMY_TEXTURE = os.path.join("texture", "enemies")
ALLY_TEXTURE = os.path.join("texture", "ally")


def create_sprite(img, sprite_size, mmp_tile):
    icon = pygame.image.load(img).convert_alpha()
    icon_mmp = pygame.transform.scale(icon, (mmp_tile, mmp_tile))
    icon = pygame.transform.scale(icon, (sprite_size, sprite_size))
    sprite = pygame.Surface((sprite_size, sprite_size), pygame.HWSURFACE)
    sprite_mmp = pygame.Surface((mmp_tile, mmp_tile), pygame.HWSURFACE)
    sprite.blit(icon, (0, 0))
    sprite_mmp.blit(icon_mmp, (0, 0))
    return sprite, sprite_mmp


def reload_game(engine, hero):
    global level_list
    level_list_max = len(level_list) - 1
    engine.level += 1
    hero.position = [1, 1]
    engine.objects = []
    generator = level_list[min(engine.level, level_list_max)]
    _map = generator['map'].get_map()
    engine.load_map(_map)
    engine.add_objects(generator['obj'].get_objects(_map))
    engine.add_hero(hero)


def restore_hp(engine, hero):
    if random.randint(1, 10) == 1:
        engine.score -= 0.05
        engine.hero = Objects.EvilEye(hero)
        engine.notify("You were cursed: unlucky")
    else:
        engine.score += 0.1
        hero.hp = hero.max_hp
        engine.notify("HP restored")


def apply_blessing(engine, hero):
    if hero.gold >= int(20 * 1.5 ** engine.level) - 2 * hero.stats["intelligence"]:
        engine.score += 0.2
        hero.gold -= int(20 * 1.5 ** engine.level) - \
                     2 * hero.stats["intelligence"]
        if random.randint(0, 1) == 0:
            engine.hero = Objects.Blessing(hero)
            engine.notify("Blessing applied")
        else:
            engine.hero = Objects.Berserk(hero)
            engine.notify("Berserk applied")
    else:
        engine.score -= 0.1
        engine.notify("Nothing happened")


def remove_effect(engine, hero):
    if hero.gold >= int(10 * 1.5 ** engine.level) - 2 * hero.stats["intelligence"] and "base" in dir(hero):
        hero.gold -= int(10 * 1.5 ** engine.level) - \
                     2 * hero.stats["intelligence"]
        engine.hero = hero.base
        engine.hero.calc_max_HP()
        engine.notify("Effect removed")
    else:
        engine.notify("Nothing happened")


def add_gold(engine, hero):
    if random.randint(1, 10) == 1:
        engine.score -= 0.05
        engine.hero = Objects.Weakness(hero)
        engine.notify("You were cursed: weak")
    else:
        engine.score += 0.1
        gold = int(random.randint(10, 1000) * (1.1 ** (engine.hero.level - 1)))
        hero.gold += gold
        engine.notify(f"{gold} gold added")


def fight(engine, enemy, hero):
    enemy_value = enemy.stats['strength'] + enemy.stats['endurance'] + \
                  enemy.stats['intelligence'] + enemy.stats['luck']
    hero_value = sum(hero.stats.values())
    while random.randint(1, enemy_value + hero_value) > hero_value and hero.hp > 0:
        hero.hp -= 1
    if hero.hp > 0:
        engine.score += 1
        hero.exp += enemy.xp
        engine.notify("Defeated enemy!")
        hero.level_up()
    else:
        engine.game_process = False
        engine.notify("Lost!")
        engine.notify("GAME OVER!!!")


def enhance(engine, hero):
    engine.score += 0.2
    engine.hero = Objects.Enhance(hero)
    hero.hp = max(hero.max_hp, hero.hp)
    engine.notify("You was enhanced!")


class MapFactory(yaml.YAMLObject):

    @classmethod
    def from_yaml(cls, loader, node):

        def get_end(loader, node):
            return {'map': EndMap.Map(), 'obj': EndMap.Objects()}

        def get_random(loader, node):
            return {'map': RandomMap.Map(), 'obj': RandomMap.Objects()}

        def get_special(loader, node):
            data = loader.construct_mapping(node)
            try:
                rat = data["rat"]
            except KeyError:
                rat = 0
            try:
                knight = data["knight"]
            except KeyError:
                knight = 0
            ret = {}
            _map = SpecialMap.Map()
            _obj = SpecialMap.Objects()
            _obj.config = {'rat': rat, 'knight': knight}
            ret["map"] = _map
            ret["obj"] = _obj
            return ret

        def get_empty(loader, node):
            return {'map': EmptyMap.Map(), 'obj': EmptyMap.Objects()}

        data = loader.construct_mapping(node)
        try:
            rat = data["rat"]
        except KeyError:
            rat = 0
        try:
            knight = data["knight"]
        except KeyError:
            knight = 0
        _obj = cls.create_objects()
        _obj.config = {'rat': rat, 'knight': knight}
        return {'map': cls.create_map(), 'obj': _obj}

    @classmethod
    def create_map(cls):
        return cls.Map()

    @classmethod
    def create_objects(cls):
        return cls.Objects()


class EndMap(MapFactory):
    yaml_tag = "!end_map"

    class Map:
        def __init__(self):
            self.Map = ['000000000000000000000000000000000000000',
                        '0                                     0',
                        '0                                     0',
                        '0  0   0   000   0   0  00000  0   0  0',
                        '0  0  0   0   0  0   0  0      0   0  0',
                        '0  000    0   0  00000  0000   0   0  0',
                        '0  0  0   0   0  0   0  0      0   0  0',
                        '0  0   0   000   0   0  00000  00000  0',
                        '0                                   0 0',
                        '0                                     0',
                        '000000000000000000000000000000000000000'
                        ]
            self.Map = list(map(list, self.Map))
            for i in self.Map:
                for j in range(len(i)):
                    i[j] = wall if i[j] == '0' else floor1

        def get_map(self):
            return self.Map

    class Objects:
        def __init__(self):
            self.objects = []

        def get_objects(self, _map):
            return self.objects


class RandomMap(MapFactory):
    yaml_tag = "!random_map"

    class Map:
        w, h = 39, 25

        def __init__(self):
            w = self.w
            h = self.h
            self.Map = [[0 for _ in range(w)] for _ in range(h)]
            for i in range(w):
                for j in range(h):
                    if i == 0 or j == 0 or i == w - 1 or j == h - 1:
                        self.Map[j][i] = wall
                    else:
                        self.Map[j][i] = [wall, floor1, floor2, floor3, floor1,
                                          floor2, floor3, floor1, floor2][random.randint(0, 8)]

        def get_map(self):
            return self.Map

    class Objects:

        def __init__(self):
            self.objects = []

        def get_objects(self, _map):
            w, h = 38, 24
            for obj_name in object_list_prob['objects']:
                prop = object_list_prob['objects'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = (random.randint(1, w), random.randint(1, h))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, w), random.randint(1, h))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, w), random.randint(1, h))

                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            for obj_name in object_list_prob['ally']:
                prop = object_list_prob['ally'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = (random.randint(1, w), random.randint(1, h))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, w), random.randint(1, h))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, w), random.randint(1, h))
                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            for obj_name in object_list_prob['enemies']:
                prop = object_list_prob['enemies'][obj_name]
                for i in range(random.randint(0, 5)):
                    coord = (random.randint(1, w), random.randint(1, h))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, w), random.randint(1, h))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, w), random.randint(1, h))

                    self.objects.append(Objects.Enemy(
                        prop['sprite'], prop, prop['experience'], coord))

            return self.objects


class SpecialMap(MapFactory):
    yaml_tag = "!special_map"

    class Map:
        def __init__(self):
            self.Map = ['000000000000000000000000000000000000000',
                        '0                                     0',
                        '0                                  0  0',
                        '0  0   0  0000   0     0  00  00    0 0',
                        '0  0  0   0   0  0     0  0 00 0  0  00',
                        '0  000    0000   0000  0  0    0     00',
                        '0  0  0   0      0   0 0  0    0  0  00',
                        '0  0   0  0      0000  0  0    0    0 0',
                        '0                                  0  0',
                        '0                                     0',
                        '000000000000000000000000000000000000000'
                        ]
            self.Map = list(map(list, self.Map))
            for i in self.Map:
                for j in range(len(i)):
                    i[j] = wall if i[j] == '0' else floor1

        def get_map(self):
            return self.Map

    class Objects:

        def __init__(self):
            self.objects = []
            self.config = {}

        def get_objects(self, _map):
            w, h = 10, 38
            for obj_name in object_list_prob['objects']:
                prop = object_list_prob['objects'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = (random.randint(1, h), random.randint(1, w))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, h),
                                     random.randint(1, w))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, h),
                                         random.randint(1, w))

                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            for obj_name in object_list_prob['ally']:
                prop = object_list_prob['ally'][obj_name]
                for i in range(random.randint(prop['min-count'], prop['max-count'])):
                    coord = (random.randint(1, h), random.randint(1, w))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, h),
                                     random.randint(1, w))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, h),
                                         random.randint(1, w))
                    self.objects.append(Objects.Ally(
                        prop['sprite'], prop['action'], coord))

            for enemy, count in self.config.items():
                prop = object_list_prob['enemies'][enemy]
                for i in range(random.randint(0, count)):
                    coord = (random.randint(1, h), random.randint(1, w))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == wall:
                            intersect = True
                            coord = (random.randint(1, h),
                                     random.randint(1, w))
                            continue
                        for obj in self.objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, h),
                                         random.randint(1, w))

                    self.objects.append(Objects.Enemy(
                        prop['sprite'], prop, prop['experience'], coord))

            return self.objects


class EmptyMap(MapFactory):
    yaml_tag = "!empty_map"

    @classmethod
    def from_yaml(cls, loader, node):
        return {'map': EmptyMap.Map(), 'obj': EmptyMap.Objects()}

    class Map:
        def __init__(self):
            self.Map = [[]]

        def get_map(self):
            return self.Map

    class Objects:

        def __init__(self):
            self.objects = []

        def get_objects(self, _map):
            return self.objects


wall = [0]
floor1 = [0]
floor2 = [0]
floor3 = [0]


def service_init(sprite_size, tile, full=True):
    global object_list_prob, level_list

    global wall
    global floor1
    global floor2
    global floor3

    wall[0] = create_sprite(os.path.join("texture", "wall.png"), sprite_size, tile)
    floor1[0] = create_sprite(os.path.join("texture", "Ground_1.png"), sprite_size, tile)
    floor2[0] = create_sprite(os.path.join("texture", "Ground_2.png"), sprite_size, tile)
    floor3[0] = create_sprite(os.path.join("texture", "Ground_3.png"), sprite_size, tile)

    file = open("objects.yml", "r")

    object_list_tmp = yaml.load(file.read(), Loader=yaml.Loader)
    if full:
        object_list_prob = object_list_tmp

    object_list_actions = {'reload_game': reload_game,
                           'add_gold': add_gold,
                           'apply_blessing': apply_blessing,
                           'remove_effect': remove_effect,
                           'restore_hp': restore_hp,
                           'fight': fight,
                           'enhance': enhance}

    for obj in object_list_prob['objects']:
        prop = object_list_prob['objects'][obj]
        prop_tmp = object_list_tmp['objects'][obj]
        prop['sprite'][0] = create_sprite(
            os.path.join(OBJECT_TEXTURE, prop_tmp['sprite'][0]), sprite_size, tile)
        prop['action'] = object_list_actions[prop_tmp['action']]

    for ally in object_list_prob['ally']:
        prop = object_list_prob['ally'][ally]
        prop_tmp = object_list_tmp['ally'][ally]
        prop['sprite'][0] = create_sprite(
            os.path.join(ALLY_TEXTURE, prop_tmp['sprite'][0]), sprite_size, tile)
        prop['action'] = object_list_actions[prop_tmp['action']]

    for enemy in object_list_prob['enemies']:
        prop = object_list_prob['enemies'][enemy]
        prop_tmp = object_list_tmp['enemies'][enemy]
        prop['sprite'][0] = create_sprite(
            os.path.join(ENEMY_TEXTURE, prop_tmp['sprite'][0]), sprite_size, tile)
        prop['action'] = object_list_actions['fight']

    file.close()

    if full:
        file = open("levels.yml", "r")
        level_list = yaml.load(file.read(), Loader=yaml.Loader)['levels']
        level_list.append({'map': EndMap.Map(), 'obj': EndMap.Objects()})
        file.close()
