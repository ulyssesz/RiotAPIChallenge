import os.path
import json
from riotwatcher import RiotWatcher, RateLimit, EUROPE_WEST, NORTH_AMERICA
from collections import defaultdict
import operator
from trueskill import Rating, TrueSkill, rate_1vs1
import time
import itertools

KEY = '0d91fe97-9666-4e0b-86ff-e5c3a108db0d'
ACCEPTED_QUEUE_TYPES = set(['RANKED_TEAM_5x5', 'RANKED_SOLO_5x5', 'NORMAL_5x5_BLIND'])
RATE_LIMITS = (RateLimit(3000, 10), RateLimit(180000, 600))
NUM_GAMES = 100

REGION = "PRO"

watcher = RiotWatcher(KEY, limits = RATE_LIMITS, default_region=EUROPE_WEST)

def get_chunk(iterable, chunk_size):
    result = []
    for item in iterable:
        result.append(item)
        if len(result) == chunk_size:
            yield tuple(result)
            result = []
    if len(result) > 0:
        yield tuple(result)

def get_player_ids():
	player_ids = []

	challengers = watcher.get_challenger()
	for c in challengers['entries']:
		player_ids.append(c['playerOrTeamId'])
	
	path = os.path.join("data", "master_%s.json" % REGION)
	with open(path) as infile:
		master = json.load(infile)
	
	for m in master['entries']:
		player_ids.append(m['playerOrTeamId'])

	with open(os.path.join("data", "player_%s.json" % REGION), 'wb') as outfile:
		json.dump(player_ids, outfile)


def get_match_ids():
	with open(os.path.join("data", "player_%s.json" % REGION)) as infile:
		player_ids = json.load(infile)
	
	match_ids = set([])
	i = 0
	for chunk in get_chunk(player_ids, 10):
		i += 1
		print "Players checked: %d" % (i * 10)
		for p_id in chunk:
			success = False
			while not success:
				try:
					games = watcher.get_match_history(p_id, begin_index=0, end_index=15)
					success = True
				except:
					print "Fail"
					time.sleep(0.25)
					

			for g in games['matches']:
				if not g['matchVersion'].startswith('5.15'):
					continue
				match_ids.add(g['matchId'])
		print len(match_ids)

	with open(os.path.join("data", "pro_matches_%s.json" % REGION), 'wb') as outfile:
		json.dump(list(match_ids), outfile)

def get_games(start, count):
	filename = os.path.join("data", '%s-%d.json' % (REGION, start))
	with open(filename) as infile:
		x = json.load(infile)
	return x


def filter_matches():
	t = defaultdict(int)
	ft = defaultdict(int)
	for i in xrange(100):
		print i
		games = get_games(i * NUM_GAMES, NUM_GAMES)

		filtered = [g for g in games if g['queueType'] in ACCEPTED_QUEUE_TYPES]
		for g in games:
			t[g['queueType']] += 1

		for f in filtered:
			ft[f['queueType']] += 1

		# filename = os.path.join("data2", '%s-%d.json' % (REGION, i * 100))
		# with open(filename, 'wb') as outfile:
		# 	json.dump(filtered, outfile)

	print t
	print ft

# get_player_ids()
# get_match_ids()
filter_matches()



