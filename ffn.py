from pybrain.structure import FeedForwardNetwork
from pybrain.structure import LinearLayer, SigmoidLayer
from pybrain.structure import FullConnection
from pybrain.datasets.supervised import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer

from analyze import *

output = defaultdict(lambda: defaultdict(dict))
data = defaultdict(lambda: defaultdict(list))
for i in xrange(10):
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

            data[champ_id][roles[p['participantId']]].append(items_bought[p['participantId']])
for champ_id, roles_dict in data.iteritems():
    for role, item_seqs in roles_dict.iteritems():
        ds = SupervisedDataSet(6,1)


        for seq in item_seqs:
            for i in xrange(len(seq) - 1):
                inp = seq[:i] + [0] * (6 - i)
                print inp, seq[i]
                ds.addSample(inp, seq[i])

        net = FeedForwardNetwork() 
        inp = LinearLayer(6) 
        h1 = SigmoidLayer(6) 
        outp = LinearLayer(1)

        # add modules 
        net.addOutputModule(outp) 
        net.addInputModule(inp) 
        net.addModule(h1)

        # create connections 
        net.addConnection(FullConnection(inp, h1))  
        net.addConnection(FullConnection(h1, outp))

        # finish up 
        net.sortModules()

        # initialize the backprop trainer and train 
        trainer = BackpropTrainer(net, ds)
        trainer.trainOnDataset(ds,1000) 
        trainer.testOnData(verbose=False)

        print net.activate((0, 0, 0, 0, 0, 0))
        import pdb; pdb.set_trace()
