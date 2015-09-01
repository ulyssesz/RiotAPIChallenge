from analyze import *
from collections import defaultdict
import itertools

def games_by_role():
    output = defaultdict(lambda: defaultdict(int))
    for i in xrange(120):
        print i
        games = get_games(i * NUM_GAMES, NUM_GAMES)
        for g in games:
            roles = get_role_type(g)
            for p in g['participants']:
                champ_id = p['championId']
                output[champ_id][roles[p['participantId']]] += 1
                output[champ_id]['total'] += 1
    min_count = 100000000
    c_id = None
    counts = []
    for champ_id, roles_dict in output.iteritems():
        champ = CHAMPIONS[champ_id]
        
        counts.append((roles_dict['total'], champ.name, champ_id))
    
    counts.sort()
    for c, n, champ_id in counts:
        print n, c, output[champ_id]['carry'], output[champ_id]['support'], output[champ_id]['jungle']

    with open(os.path.join("output", "games_by_role.json"), 'wb') as outfile:
        json.dump(output, outfile)


def markov():
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int)))) # champ: role: chain: option: count
    # avg_pos = defaultdict(lambda: defaultdict(int))
    
    for i in xrange(120):
        print i
        games = get_games(i * NUM_GAMES, NUM_GAMES)
        for g in games:
            roles = get_role_type(g)

            
            
            items_bought = defaultdict(lambda: [None, None])
            for frame in g["timeline"]["frames"]:
                for event in frame.get("events", []):

                    if event["eventType"] == "ITEM_PURCHASED":

                        item_id = normalize_item(event["itemId"])
                        if item_id == None:
                            continue
                        items_bought[event['participantId']].append(item_id)
            
            for p in g['participants']:
                items_player_bought = items_bought[p['participantId']]

                for key_len in xrange(2, len(items_player_bought)):
                    for i in xrange(key_len, len(items_player_bought)):
                        key = tuple(items_player_bought[:i-1])
                        data[p['championId']][roles[p['participantId']]][key][items_player_bought[i]] += 1    
                    # avg_pos[items_bought[i]]["sum"] += (i - 1)
                    # avg_pos[items_bought[i]]["total"] += 1
    
    output = defaultdict(lambda: defaultdict(dict))
    for champ_id, roles_dict in data.iteritems():
        for role, chains in roles_dict.iteritems():
            seq = [None, None]
            print "Champ: %s \t Role: %s" % (CHAMPIONS[champ_id].name, role)

            # while True:
            #     l = len(seq)
            #     keys = [(seq[l-2], seq[l-1]), (seq[l-1], seq[l-2])]
            #     if l >= 4:
            #         keys.append((seq[l-3], seq[l-2]))
            #         keys.append((seq[l-2], seq[l-3]))
            #     choices = defaultdict(int)
            #     for key in keys:
            #         for item_id, count in chains.get(key, {}).iteritems():
            #             choices[item_id] += count
            #     sorted_choices = sorted([(v,k) for k,v in choices.iteritems()], reverse=True)
                
            #     if len(seq) - 2 < 6:
            #         found_item = False
            #         for count, choice in sorted_choices:
            #             if choice not in seq:
            #                 found_item = True
            #                 seq.append(choice)
            #                 break
            #         if found_item:
            #             continue
                        
            #     output[champ_id][role] = seq[2:]
            #     for item_id in seq[2:]:
            #         item = ITEMS[item_id]
            #         print item.name
            #     break

            while True:
                l = len(seq)
                choices = defaultdict(int)
                for key_len in xrange(2, l + 1):
                    key = tuple(seq[:key_len])
                    for item_id, count in chains.get(key, {}).iteritems():
                        choices[item_id] += count

                sorted_choices = sorted([(v,k) for k,v in choices.iteritems()], reverse=True)
                if len(seq) - 2 < 6:
                    found_item = False
                    for count, choice in sorted_choices:
                        if choice not in seq:
                            found_item = True
                            seq.append(choice)
                            break
                    if found_item:
                        continue
                output[champ_id][role] = seq[2:]
                for item_id in seq[2:]:
                    item = ITEMS[item_id]
                    print item.name
                break


            # sorted_pos = [(v["sum"] / float(v["total"]), item_id, v["total"]) for item_id ,v in avg_pos.iteritems()]
            # sorted_pos.sort()
            # for p, item_id, total in sorted_pos:
            #     item = ITEMS[item_id]
            #     print item.name, p, total

    with open(os.path.join("output", "new_end_items.json"), 'wb') as outfile:
        json.dump(output, outfile)


def hash_by_index(text):
    return {text[i]: i for i in xrange(len(text))}


def get_build_orders():
    
    data = defaultdict(lambda: defaultdict(list))
    allowed = set([])
    for i in xrange(120):
        print i
        games = get_games(i * NUM_GAMES, NUM_GAMES)
        for g in games:
            roles = get_role_type(g)

            
            items_bought = defaultdict(list)
            for frame in g["timeline"]["frames"]:
                for event in frame.get("events", []):

                    if event["eventType"] == "ITEM_PURCHASED":

                        item_id = normalize_item(event["itemId"])
                        if item_id == None:
                            continue
                        items_bought[event['participantId']].append(item_id)
                    elif event['eventType'] == 'ITEM_UNDO':
                        item_id = event["itemBefore"]
                        if item_id in items_bought[event['participantId']]:
                            items_bought[event['participantId']].remove(item_id)
                    elif event['eventType'] == 'ITEM_SOLD':
                        item_id = event["itemId"]
                        if item_id in items_bought[event['participantId']]:
                            items_bought[event['participantId']].remove(item_id)

            for p in g['participants']:
                champ_id = p['championId']

                items_player_bought = items_bought[p['participantId']]
                for comb in itertools.combinations(items_player_bought, 2):
                    allowed.add(tuple(sorted(comb)))

                data[champ_id][roles[p['participantId']]].append(items_bought[p['participantId']])

    with open(os.path.join("output", "build_orders.json"), 'wb') as outfile:
        json.dump(data, outfile)

def end_items():
    output = defaultdict(lambda: defaultdict(dict))
    with open(os.path.join("output", "build_orders.json")) as infile:
        data = json.load(infile)

    for champ_id, roles_dict in data.iteritems():
        champ_id = int(champ_id)
        for role, item_seqs in roles_dict.iteritems():
            curr_seq = []
            remaining_seqs = item_seqs[:]
            while len(curr_seq) < 6 and len(remaining_seqs) > 0:
                new_remaining_seqs = []
                next_item = defaultdict(int)
                for seq in remaining_seqs:
                    x = set(curr_seq)
                    y = set(seq)
                    new_remaining_seqs.append(seq)

                    x_hash = hash_by_index(curr_seq)
                    y_hash = hash_by_index(seq)

                    missing = list(x.difference(y))
                    for i in xrange(len(missing)):
                        y_hash[missing[i]] = len(seq) + i

                    last_index = -1 # Find index of the rightmost char in seq that is part of curr_seq
                    for c in x_hash:
                        if y_hash[c] > last_index:
                            last_index = y_hash[c]

                    
                    
                    for item_id in y.difference(x):
                        weight = 1.0
                        if y_hash[item_id] > last_index:
                            # Item occurs after
                            weight /= (2 ** (y_hash[item_id] - last_index - 1))
                        else:
                            # Item purchase occurs before at least one
                            for c in x_hash:
                                if y_hash[item_id] < y_hash[c]:
                                    weight /= 2
                        next_item[item_id] += weight
                sorted_items = sorted([(count, item_id) for item_id, count in next_item.iteritems()], reverse=True)
                if len(sorted_items) == 0:
                    break

                found_item = False
                for count, item_id in sorted_items:
                    if item_id in BOOTS and len(set(curr_seq).intersection(BOOTS)) >= 1:
                        continue # Can't have > 1 boots
                    else:
                        curr_seq.append(item_id)
                        found_item = True
                        break
                if not found_item:
                    break
                
                remaining_seqs = new_remaining_seqs
            print "Champ: %s \t Role: %s" % (CHAMPIONS[champ_id].name, role)
            print curr_seq

            for item_id in curr_seq:
                item = ITEMS[item_id]
                print item.name, ",",
            print
            print
            output[champ_id][role] = curr_seq


    with open(os.path.join("output", "new_end_items2.json"), 'wb') as outfile:
        json.dump(output, outfile)





if __name__ == "__main__":
    # games_by_role()
    # markov()
    get_build_orders()
    end_items()