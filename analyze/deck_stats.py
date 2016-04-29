import json
import os
import codecs
import argparse
from collections import Counter
from operator import itemgetter

class Deck:
    """Deck is defined by a name and a dictionary {'cardName': ''cardCount'}
    For example:
    >>> name = "Taka's Red Rush"
    >>> cardDict = {'Lightning Bolt': 4,
                'Goblin Guide': 4,
                'Grim Lavamancer': 4
                }
    >>> redDeck = Deck(name, cardDict)
    """
    def __init__(self, name, cardDict):
        self.name = name
        self.cardDict = cardDict

    def __str__(self):
        return str(self.name) + "\n" + str(self.cardDict)

class Archetype:
    """An archetype is a collection of similar decks.
    An archetype is defined by a name and a dictionary of cardData.
    Card data is dictionary of {'cardName': 'count'} where archetype
    count is the total number of times a card appears in the archetype.
    For example:
    >>> redDeck2 = Deck("Yoshi's Blazing Ballers", {'Lightning Bolt': 4,
        'Ball Lightning': 4})
    >>> redDeckWins = Archetype("Red Deck Wins", {})
    >>> redDeckWins.add(redDeck)
    >>> redDeckWins.add(redDeck2)
    >>> redDeckWins.cardData
    {'Lightning Bolt': 8, 'Goblin Guide': 4, 'Grim Lavamancer': 4,
     'Ball Lightning': 4}
    """
    def __init__(self, name):
        self.name = name
        self.cardData = {}
        self.totalDecks = 0

    def add(self, cardDict):
        for card in cardDict:
            if card not in self.cardData:
                self.cardData[card] = Counter()
                for copies in range(1, 5):
                    self.cardData[card][copies] = 0
            self.cardData[card][cardDict[card]] += 1
        self.totalDecks += 1

    def getPercentDict(self):
        percentDict = {}
        for card in self.cardData:
            percentDict[card] = {}
            for count in self.cardData[card].keys():
                percentDict[card][count] = float(self.cardData[card][count]) / \
                                           self.totalDecks * 100
        return percentDict

    def __getitem__(self, card):
        return self.cardData[card]

    def __str__(self):
        return self.name + "\n" + str(self.cardData)

class ArchetypeManager:
    """An ArchetypeManager is a collection of Archetypes. Since a format can be
    defined by a collection of archetypes, each ArchetypeManager instance can be
    treated as a format.
    For example:
    >>> bantCompany = Deck(...)
    >>> aggroVampires = Deck(...)
    >>> standard = ArchetypeManager({})
    >>> standard.add(bantCompany)
    >>> standard.add(aggroVampires)
    >>> print([standard.archetypes[arch].name for arch in standard.archetypes])
    ["Aggro Vampires", "Bant Company"]
    """
    def __init__(self):
        self.archetypes = {}

    def add(self, deck):
        if deck.name not in self.archetypes:
            self.archetypes[deck.name] = Archetype(deck.name)
        self.archetypes[deck.name].add(deck.cardDict)

    def __getitem__(self, archetype):
        return self.archetypes[archetype]

def constructFormat(deckJson="analyze/datadigger/items.json"):
    """ Returns an ArchetypeManager built from data in the given deckJSON file.
    The format of the JSON is defined by the code written in the Scrapy Spider
    files.
    """
    with open(deckJson) as deckData:
        decks = json.load(deckData)

    gameFormat = ArchetypeManager()
    for deck in decks:
        cardDict = {}
        for index in range(len(deck['cards'])):
            cardName = deck['cards'][index].strip('\n')
            cardCount = deck['quantities'][index].strip('\n')
            cardDict[cardName] = int(cardCount)
        name = deck['name'][0].split("  by", 1)[0]
        deckObj = Deck(name, cardDict)
        gameFormat.add(deckObj)
    return gameFormat

def analyzeArchetype(archetype):
    """Returns a list with the following format:
    'Archetype Name'
    'Card Name'
    'Number of Copies Used': 'Percent of Decks that use this count'
    For example:
    >>> bantCompany = Archetype(...)
    >>> print(analyzeArchetype(bantCompany))
    [
    'Bant Company',
    'Collected Company',
    '1: 0%',
    '2: 0%',
    '3: 0%',
    '4: 100%',
    'Declaration in Stone'
    '1: 0%',
    '2: 22.5%',
    '3: 55.0%',
    '4: 22.5%',
    ]
    """
    data = []
    data.append(archetype.name)
    percentDict = archetype.getPercentDict()
    for card in percentDict:
        data.append(card)
        for count in percentDict[card]:
            data.append("{0}:{1:.2f}%".format(count, percentDict[card][count]))
    return data

def decReader(decFile):
    """Parser designed to take in a path to a deck file, read the file, and
    return a deck object built from that file.
    The file must be in .dec format.
    #TODO: Error Handling for bad format.
    """
    deckCards = {}
    with codecs.open(decFile, "r",encoding='utf-8', errors='ignore') as deck:
        for line in deck.readlines():
            deckAdder(deckCards, line)
    return Deck(decFile.split(".dec")[0], deckCards)

def stringReader(deckString):
    """Parser designed to take in a large string representing a list of cards in
    a deck delimited by new line characters, and return a deck object built from
    that list of cards.
    String must be in .dec format.
    #TODO: Error Handling for bad format.
    """
    deckCards = {}
    for line in deckString.splitlines():
        deckAdder(deckCards, line)
    return Deck("userDeck", deckCards)

def deckAdder(deckDict, line):
    """Helper function for decReader and stringReader, to add a given card
    string to a given card dictionary.
    """
    card = line.split()
    if len(card) and (card[0].isdigit() or card[0] == "SB:"):
        i = 0
        if card[0] == "SB:":
            i = 1
        deckDict[" ".join(card[i + 1:])] = int(card[i])
    return

def deckCompare(archetype, deck):
    """Compares a deck to a archetype for similarity.  Returns a number
    proportional to similarity.  If the number is higher the deck is more
    similar to the archetype.  To test make sure that the function returns the
    following values when given these decks.  Currently using naive implemention
    to count number of duplcate cards.
    #TODO: Improve deck compare algorithm, number of duplicate card names is
    naive.
    """
    matches = 0
    duplicates = deck.cardDict.keys()
    archetypeKeys = archetype.cardData.keys()
    for key in duplicates:
        if key in archetypeKeys:
            matches += 1
    return matches

def getMultiverseIDDict(JSONdata, allowedSets, cards):
    """Function that takes in a json object built from an MTG JSON object using
    json.load(), a list of allowed sets for a format, and a list of cards to
    find their corresponding multiverseid.
    Returns a dictionary formatted as {'cardName': 'multiverseid'} .
    """
    IDDict = {}
    for cardName in cards:
        for setName in allowedSets:
            for cardDict in JSONdata[setName]["cards"]:
                if cardName == cardDict["name"]:
                    IDDict[cardName] = cardDict["multiverseid"]
    return IDDict

def launcher(args, fileDeck=False):
    """Launcher function to build the standard format, and take in either a deck
    file or a deck string.  Returns the archetype from the format that best
    matches the given deck.
    """
    standard = constructFormat()
    if fileDeck:
        myDeck = decReader(args.deck)
    else:
        myDeck = stringReader(args)
    bestValue = 0
    bestMatch = None
    for archetype in standard.archetypes:
        similarity = deckCompare(standard[archetype], myDeck)
        if similarity > bestValue:
            bestMatch = standard[archetype]
            bestValue = similarity
    return bestMatch

if __name__ == '__main__':
    """
    CLI for testing and debugging.
    Currently set to only analyze deck files.
    #TODO: Build an automatic testing framework.
    """
    parser = argparse.ArgumentParser(description='Deck Suggester options.')
    parser.add_argument('deck', metavar='deck', type=str,
                        default="", help="deck file to analyze")
    args = parser.parse_args()
    launcher(args, True)
