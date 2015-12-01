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

def shuffle(deck):
    """ Shuffles the deck using an implementation of the Fisher-Yates shuffling algorithm. n is equal to the length of the
    deck - 1 (because accessing lists starts at 0 instead of 1). While n is greater than 0, a random number k between 0
    and n is generated, and the card in the deck that is represented by the offset n is swapped with the card in the deck
    represented by the offset k. n is then decreased by 1, and the loop continues. """

    # ??? do we have better shuffle alg
    n = len(deck) - 1
    while n > 0:
        k = random.randint(0, n)
        temp = deck[k]
        deck[k] = deck[n]
        deck[n] = temp
        # deck[k], deck[n] = deck[n], deck[k]
        n -= 1

    return deck

def returnFromDead(deck, deadDeck):
    """ Appends the cards from the deadDeck to the deck that is in play. This is called when the main deck
    has been emptied. """

    for card in deadDeck:
        deck.append(card)

    del deadDeck[:]
    deck = shuffle(deck)

    return deck, deadDeck
