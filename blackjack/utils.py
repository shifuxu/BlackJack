import random
import sys
from settings import *


def createDeck():
    """ Creates a default deck which contains all 52 cards and returns it. """

    deck = ['sj', 'sq', 'sk', 'sa', 'hj', 'hq', 'hk', 'ha', 'cj', 'cq', 'ck', 'ca', 'dj', 'dq', 'dk', 'da']
    values = range(2, 11)
    for x in values:
        spades = "s" + str(x)
        hearts = "h" + str(x)
        clubs = "c" + str(x)
        diamonds = "d" + str(x)
        deck.append(spades)
        deck.append(hearts)
        deck.append(clubs)
        deck.append(diamonds)

    return deck