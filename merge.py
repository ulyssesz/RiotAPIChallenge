import json
import os.path
from collections import namedtuple, OrderedDict

ROLES = ['support', 'carry', 'jungle']
DMG_TYPES = ['ad', 'ap']
CHAMPIONS = {}
ROLE_PERCENT_REQUIRED = 5
ROLE_COUNT_REQUIRED = 20
NUM_END_ITEMS = 8
ITEM_PERCENT_REQUIRED = 2

def convert(dictionary):
    return namedtuple('GenericDict', dictionary.keys())(**dictionary)


def load_champions():
    filename = os.path.join("BILGEWATER", 'champion.json')
    with open(filename) as infile:
        x = json.load(infile)
    
    for c in x['data']:
        CHAMPIONS[x['data'][c]['key']] = convert(x['data'][c])

def extract_champ_info():
    champ_art = {"art": {}}
    for champ_id, champ in CHAMPIONS.iteritems():
        filename = champ.image['full'].split('.')[0]
        icon_url = "http://ddragon.leagueoflegends.com/cdn/5.16.1/img/champion/%s.png" % filename
        splash_url = "http://ddragon.leagueoflegends.com/cdn/img/champion/splash/%s_0.jpg" % filename
        champ_art["art"][champ.name] = {"id": champ_id, "icon_url": icon_url, "splash_url": splash_url}
    champ_art["order"] = sorted(champ_art["art"].keys())

    with open(os.path.join("web", "data", "results", "champion_info.json"), 'wb') as outfile:
        json.dump(champ_art, outfile, sort_keys=True,
                indent=4, separators=(',', ': '))


with open(os.path.join("output", "games_by_role.json")) as infile:
    games_by_role = json.load(infile)

with open(os.path.join("output", "starting_items.json")) as infile:
    starting_items = json.load(infile)

with open(os.path.join("output", "defence_items.json")) as infile:
    defence_items = json.load(infile)

with open(os.path.join("output", "new_end_items2.json")) as infile:
    ending_items = json.load(infile)

load_champions()

extract_champ_info()

available_builds = {}
for champ_id, champ in CHAMPIONS.iteritems():
    available_builds[champ.name] = []
    total_games = float(games_by_role[champ_id]['total'])
    for role in ROLES:
        total_games_in_role = games_by_role[champ_id].get(role, 0)
        
        if total_games_in_role / float(total_games) * 100 < ROLE_PERCENT_REQUIRED or total_games_in_role < ROLE_COUNT_REQUIRED:
            continue
        if champ_id == '6' and role == "support":
            print total_games_in_role, total_games
        available_builds[champ.name].append(role)

        orderedDict = OrderedDict()
        orderedDict["title"] = "%s: %s" % (champ.name, role)
        orderedDict["type"] = "custom"
        orderedDict["map"] = "SR"
        orderedDict["mode"] = "any"
        orderedDict["blocks"] = []
            
        # Starting items
        items = [OrderedDict([("id", str(item_id)), ("count", count)]) for item_id, count in starting_items[champ_id][role][0][1]]
        items_dict = OrderedDict([("type", "Starting items"), ("items", items)])
        orderedDict['blocks'].append(items_dict)

        # Ending items
        end_items = ending_items[champ_id][role]
        # normalized_end_items = sorted([(count / total_games_in_role * 100, item_id) for item_id, count in end_items.iteritems() if item_id != 'total'], reverse=True)
        # selected_end_items = []
        # i = 0
        # while (len(selected_end_items) < NUM_END_ITEMS and i < len(normalized_end_items)):
        #     if normalized_end_items[i][0] < ITEM_PERCENT_REQUIRED:
        #         break
        #     else:
        #         end_items_dict = OrderedDict([("id", normalized_end_items[i][1]), ("count", 1)])
        #         selected_end_items.append(end_items_dict)
        #     i += 1

        selected_end_items = [OrderedDict([("id", str(item_id)), ("count", 1)]) for item_id in end_items]
        orderedDict['blocks'].append(OrderedDict([
            ("type", "Common end items"),
            ("items", selected_end_items)
        ]))

        # Defence items
        defend_items = defence_items[champ_id][role]
        for dmg_type in DMG_TYPES:
            if 'total' not in defend_items[dmg_type]:
                # No items found
                continue

            total_games_for_role_dmg_type = defend_items[dmg_type]['total']
            filtered_defence_items = sorted([(count, item_id) for item_id, count in defend_items[dmg_type].iteritems() if item_id != 'total' 
                                                and count / total_games_for_role_dmg_type * 100 > 5], reverse=True)
            selected_defence_items = [{"id": item_id, "count": 1} for _, item_id in filtered_defence_items]
            if len(selected_defence_items) > 0:
                orderedDict['blocks'].append(OrderedDict([
                    ("type", "Items against %s-heavy teams" % dmg_type),
                    ("items", selected_defence_items)
                ]))


        filename = os.path.join("web", "data", "results", "%s_%s.json" % (champ.name, role))
        with open(filename, 'wb') as outfile:
            json.dump(orderedDict, outfile, sort_keys=False,
                indent=4, separators=(',', ': '))

        with open(os.path.join("web", "data", "results", "available_builds.json"), 'wb') as outfile:
            json.dump(available_builds, outfile)


