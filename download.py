import os.path
import json
from riotwatcher import RiotWatcher, RateLimit, EUROPE_WEST, NORTH_AMERICA, LoLException, KOREA
from collections import defaultdict
import operator
from trueskill import Rating, TrueSkill, rate_1vs1
import time

KEY = '0d91fe97-9666-4e0b-86ff-e5c3a108db0d'
RATE_LIMITS = (RateLimit(3000, 10), RateLimit(180000, 600))
BRAWLERS = set((3611, 3612, 3613, 3614)) # Razorfin, Ironback, Plundercrab, Ocklepod
UPGRADES = set(range(3615, 3627))
NUM_GAMES = 100
ITEMS = BRAWLERS.union(UPGRADES)
REGION = "PRO"

watcher = RiotWatcher(KEY, limits = RATE_LIMITS)

	

def get_match_ids():
	x = []
	for r, s in [('KR', KOREA), ('NA', NORTH_AMERICA), ('EUW', EUROPE_WEST)]:
		with open(os.path.join("data", "pro_matches_%s.json" % r)) as infile:
			y = json.load(infile)	
		x.extend([(s, c) for c in y])	
	return x

def save_data(filename, data):
	path = os.path.join("data", filename)
	with open(path, 'wb') as outfile:
		json.dump(data, outfile)




def download_matches(match_ids, start=0, count=NUM_GAMES):
	matches = []
	i = 0
	reqs = 0
	missing_matches = 0
	start_time = time.time()
	while i < NUM_GAMES:
		try:
			reqs += 1
			region, match_id = match_ids[start + i]
			matches.append(watcher.get_match(match_id, include_timeline=True, region=region))
		except LoLException as e:
			if e.error == "Game data not found":
				missing_matches += 1
			elif e.error == "Too many requests":
				continue
		i += 1
		if i % 10 == 0:
			print start + i
	print "API Success rate: %f. Missing matches: %d. Reqs / 10 second: %f" % (NUM_GAMES / float(reqs), missing_matches, reqs / (time.time() - start_time) * 10)
	save_data("%s-%d.json" % (REGION, start), matches)


def anaylze_match(match):
	team_ids = [t['teamId'] for t in match['teams']] 
	teams = {t : set() for t in team_ids}
	upgrade_sequence = {}
	for p in match['participants']:
		upgrade_sequence[p['participantId']] = []
		teams[p['teamId']].add(p['participantId'])
 
	for frame in match['timeline']['frames']:
		
		if 'events' not in frame: continue

		for event in frame['events']:
			if event['eventType'] == 'ITEM_PURCHASED' and event['itemId'] in BRAWLERS:
				upgrade_sequence[event['participantId']].append(event['itemId'])

	teamA_id, teamB_id = team_ids
	teamA_comp = tuple(tuple(x) for x in sorted([upgrade_sequence[u] for u in teams[teamA_id]])) 
	teamB_comp = tuple(tuple(x) for x in sorted([upgrade_sequence[u] for u in teams[teamB_id]]))

	teamA_stats = match['teams'][0] if match['teams'][0]['teamId'] == teamA_id else match['teams'][1]
	teamA_won = teamA_stats['winner']

	return teamA_comp, teamB_comp, teamA_won

def get_games(start, count):
	filename = os.path.join("data", '%s-%d.json' % (REGION, start))
	with open(filename) as infile:
		x = json.load(infile)
	return x


def get_best_comp():
	env = TrueSkill(draw_probability = 0)
	comp_ratings = defaultdict(lambda: env.create_rating())
	comp_counts = defaultdict(int)
	comp_win_rate = defaultdict(lambda: [0,0])
	for i in xrange(100):
		games = get_games(i * NUM_GAMES, NUM_GAMES)
		for g in games:
			teamA_comp, teamB_comp, teamA_won = anaylze_match(g)

			if teamA_comp == teamB_comp:
				continue
			if tuple() in teamA_comp or tuple() in teamB_comp:
				continue

			teamA_rating = comp_ratings[teamA_comp]
			teamB_rating = comp_ratings[teamB_comp]

			comp_counts[teamA_comp] += 1
			comp_counts[teamB_comp] += 1

			comp_win_rate[teamA_comp][1] += 1
			comp_win_rate[teamB_comp][1] += 1
			if teamA_won:
				comp_win_rate[teamA_comp][0] += 1
				teamA_rating, teamB_rating = rate_1vs1(teamA_rating, teamB_rating)
			else:
				comp_win_rate[teamB_comp][0] += 1
				teamA_rating, teamB_rating = rate_1vs1(teamB_rating, teamA_rating)
			comp_ratings[teamA_comp] = teamA_rating
			comp_ratings[teamB_comp] = teamB_rating
		if i % 10 == 0:
			print i

	leaderboard = sorted([(comp_win_rate[k][0] / float(comp_win_rate[k][1]), v,k) for k,v in comp_ratings.items()], reverse = True)
	for l in leaderboard:
		print l, comp_counts[l[2]]
		


# sequence_counts = defaultdict(int)
# for m in matches:
# 	sequences = anaylze_match(m)
# 	for s in sequences:
# 		sequence_counts[tuple(sequences[s])] += 1

match_ids = get_match_ids()

# sorted_counts = sorted(sequence_counts.items(), key = operator.itemgetter(1), reverse=True)
# for s in sorted_counts:
# 	print s

for i in xrange(80, 120):
	print "set", i
	download_matches(match_ids, i * NUM_GAMES)


# get_best_comp()
