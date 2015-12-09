import random
from utils import *

"""
A state is (dealerCard, playerTotal, hasUseableAce)

dealerCard is dealer's face-up card that player can see.

playerTotal is the total value of player's cards.

hasUseableAce is true iff playerHand's ace can be count as 11 
and playerHand's total value is less or equal to 21.


A hand is (total, hasAce)

total is the total value of the hand's cards.

hasAce is true as long as the hand has an ace.
"""

def getAllPossibleStates():
	allStates = []

	for dealerCard in range(1, 12):
		for playerTotal in range(2, 22):
			allStates.append((dealerCard, playerTotal, True))
			allStates.append((dealerCard, playerTotal, False))

	return allStates

def initializeQMap():
	
	allStates = getAllPossibleStates()
	qMap = {}

	for state in allStates:
		if state[1] < 10:
			qMap[(state, True)] = 0.1
			qMap[(state, False)] = -0.1
		else:
			qMap[(state, True)] = 0.0
			qMap[(state, False)] = 0.0

	return qMap

def initializeCounterMap():
	allStates = getAllPossibleStates()
	counterMap = {}

	for state in allStates:
		counterMap[(state, True)] = 0.0
		counterMap[(state, False)] = 0.0

	return counterMap

def getHandsFromState(state):
	dealerCard, playerTotal, hasUseableAce = state

	if hasUseableAce:
		playerTotal = playerTotal - 10

	dealerHand = (0, False)
	dealerHand = addCardToHand(dealerCard, dealerHand)
	playerHand = (playerTotal, hasUseableAce)

	return dealerHand, playerHand


def dealPlayer():
	hand = (0, False)
	card1 = drawCard()
	hand = addCardToHand(card1, hand)
	card2 = drawCard()
	hand = addCardToHand(card2, hand)
	return hand


def dealDealer():
	hand = (0, False)
	card1 = drawCard()
	hand = addCardToHand(card1, hand)
	return (card1, hand)


def addCardToHand(card, hand):
	total = hand[0] + card
	hasAce = hand[1]
	if card == 1:
		hasAce = True
	return (total, hasAce)

# To do, drawCard method is limited
def drawCard():
	card = random.randint(1, 13)
	if card > 10:
		card = 10
	return card

def getHandTotal(hand):
	total, hasAce = hand
	if handHasUseableAce(hand):
		return total + 10
	else:
		return total

def handHasUseableAce(hand):
	total, ace = hand
	return ((ace) and (total + 10 <= 21))

def getRandomState(allStates):
	randomIndex = random.randint(0, len(allStates) - 1)
	return allStates[randomIndex]

def getActionWithEpsilon(qMap, state, epsilon):
	r = random.random()
	if r < epsilon:
		if random.randint(0, 1) == 0:
			return True
		else:
			return False
	else:
		return getBestActionByQ(qMap, state)
		
def getRewardByHands(dealer_hand, player_hand):
	player_val = getHandTotal(player_hand)
	dealer_val = getHandTotal(dealer_hand)
	if (player_val > 21):
		return -1.0
	elif (dealer_val > 21):
		return 1.0
	elif (player_val < dealer_val):
		return -1.0
	elif (player_val == dealer_val):
		return 0.0
	elif (player_val > dealer_val):
		return 1.0

def dealerPlay(hand):
	while getHandTotal(hand) < 17:
		hand = addCardToHand(drawCard(), hand)
	return hand

def getNextState(dealerCard, playerHand):
	return (dealerCard, getHandTotal(playerHand), handHasUseableAce(playerHand))

def getMaxQByState(qMap, state):
	return max(qMap[(state, True)], qMap[(state, False)])

def getBestActionByQ(qMap, state):
	if qMap[(state, True)] > qMap[(state, False)]:
		return True
	else:
		return False

# Q learning.
def q_learning(learningTimes, alpha, discount, epsilon):
	# initialize
	qMap = initializeQMap()
	counterMap = initializeCounterMap()
	allStates = getAllPossibleStates()
	for n in range(0, learningTimes):
		# select a start state randomly 
		state = getRandomState(allStates)
		dealerHand, playerHand = getHandsFromState(state)
		dealerCard = state[0]
		while True:
			action = getActionWithEpsilon(qMap, state, epsilon)
			stateActionPair = (state, action)
			counterMap[stateActionPair] = counterMap[stateActionPair] + 1.0
			# Player hits
			if action:
				playerHand = addCardToHand(drawCard(), playerHand)
				# Player does not bust
				if getHandTotal(playerHand) <= 21:
					# Update qMap
					nextState = getNextState(dealerCard, playerHand)
					maxQ = getMaxQByState(qMap, nextState)
					diff = (discount * maxQ) - qMap[stateActionPair]
					qMap[stateActionPair] = qMap[stateActionPair] + (alpha / counterMap[stateActionPair] * diff)
					state = nextState
				# Player busts
				else:
					# Update qMap
					diff = (-1) - qMap[stateActionPair]
					qMap[stateActionPair] = qMap[stateActionPair] + (alpha / counterMap[stateActionPair] * diff)
					break;
			# Player stands
			else:
				# Dealer play
				dealerHand = dealerPlay(dealerHand)
				# Update qMap
				diff = getRewardByHands(dealerHand, playerHand) - qMap[stateActionPair]
				qMap[stateActionPair] = qMap[stateActionPair] + (alpha / counterMap[stateActionPair] * diff)
				break;

		#epsilon = epsilon * ((learningTimes - n) / learningTimes)
	return qMap

# Q learning.
def q_learning_test_print_average(Q, n_times):
	# initialize
	qMap = Q
	gain = 0.0
	for n in range(0, n_times):
		playerHand = dealPlayer()
		dealerCard, dealerHand = dealDealer()
		state = getNextState(dealerCard, playerHand)
		while True:
			action = getBestActionByQ(qMap, state)
			stateActionPair = (state, action)
			# Player hits
			if action:
				playerHand = addCardToHand(drawCard(), playerHand)
				# Player does not bust
				if getHandTotal(playerHand) <= 21:
					nextState = getNextState(dealerCard, playerHand)
					state = nextState
				# Player busts
				else:
					gain = gain - 1
					break;
			# Player stands
			else:
				# Dealer play
				dealerHand = dealerPlay(dealerHand)
				gain = gain + getRewardByHands(dealerHand, playerHand)
				break;

		#epsilon = epsilon * ((learningTimes - n) / learningTimes)
	print ('AverageGain: %6.3f' % (gain / n_times))


def print_Q(Q):
	print('------------ Q MAP -----------')
	for useable in [True, False]:
		if useable:
			print('Usable ace')
		else:
			print('No useable ace')
		print('Values for staying:')
		for val in range(21,10,-1):
			for card in range(1,11):
				print('%5.2f' % M[((card, val, useable), False)], end = ' ')
			print('| %d' % val)
		print('Values for hitting:')
		for val in range(21,10,-1):
			for card in range(1,11):
				print('%5.2f' % M[((card,val,useable), True)], end = ' ')
			print('| %d' % val)
		print(' ')

# Print a policy given the Q-values
def print_policy(Q):
	print('---- Policy ----')
	for useable in [True, False]:
		if useable:
			print('Usable ace')
		else:
			print('No useable ace')
		for val in range(21, 1, -1):
			for card in range(1, 11):
				if Q[((card, val, useable), True)] > Q[((card, val, useable), False)]:
					print('X', end = ' '),
				else:
					print(' ', end = ' '),
			print('| %d' % val)
		print(' ')

# Main ai function interface
def policyHelper(Q):
    policySet = []
    policy0 = {}
    policy1 = {}
    for val in range(21, 1, -1):
        for card in range(1, 11):
            item = (card, val)
            stateWithUseableAce = (card, val, True)
            policy0.setdefault(item, getBestActionByQ(Q, stateWithUseableAce))
            stateWithoutUseableAce = (card, val, False)
            policy1.setdefault(item, getBestActionByQ(Q, stateWithoutUseableAce))

    policySet.append(policy0)
    policySet.append(policy1)
    return policySet

def getPolicySet():
    # set parameters
    n_iter_q = 3500000
    alpha = 1
    epsilon = 0.1
    discount = 1
    # run learning algorithms
    print('Q-LEARNING -- UNBIASED DECK')
    Q = q_learning(n_iter_q, alpha, discount, epsilon)
    # print_Q(Q)
    # print_V(Q)
    print_policy(Q)
    return policyHelper(Q)

def test():
    # set parameters
    n_iter_q = 125
    alpha = 1
    epsilon = 0.2
    discount = 1
    n_iter = 100000
    while (n_iter_q <= 5120000):
    	Q = q_learning(n_iter_q, alpha, discount, epsilon)
    	print('q_learning times %d' % n_iter_q, end = ' ')
    	q_learning_test_print_average(Q, n_iter)
    	n_iter_q = n_iter_q * 2

if __name__ == '__main__':
	test()





























