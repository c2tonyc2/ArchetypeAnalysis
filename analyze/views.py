from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext
from . import deck_stats
import json
import os

standard = ["DTK", "ORI", "BFZ", "OGW", "SOI"]

#JSON file provided by: http://mtgjson.com/
with open('analyze/assets/AllSets.json') as data_file:
    JSONdata = json.load(data_file)

def index(request):
    return render(request, 'analyze/index.html', {})

def deck(request):

    try:
        cards = pk=request.POST['cards']
        matchedArchetype = deck_stats.launcher(cards)
    except (KeyError):
        return render(request, 'analyze/index.html', {
            'error_message': "Invalid card list!",
        })
    if not matchedArchetype:
        return render(request, 'analyze/index.html', {
            'error_message': "Invalid card list!",
        })
    ids = deck_stats.getMultiverseIDDict(JSONdata, standard,
                                         matchedArchetype.cardData.keys())
    # print(repr(json.dumps(matchedArchetype.getPercentDict())))
    return render(request, 'analyze/deck.html',
                  {'cards': json.dumps(matchedArchetype.getPercentDict()),
                   'archName': matchedArchetype.name,
                   'ids': json.dumps(ids)})
