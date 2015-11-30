#!/usr/bin/env python
import sys
import re
import random

# Note that this solution ignores naturals.

# A hand is represented as a pair (total, ace) where:
#  - total is the point total of cards in the hand (counting aces as 1)
#  - ace is true iff the hand contains an ace

# Return the empty hand.
def empty_hand():
   return (0, False)

# Return whether the hand has a useable ace.
# Note that a hand may contain an ace, but it might not be useable.
def hand_has_useable_ace(hand):
   total, ace = hand
   return ((ace) and ((total + 10) <= 21))

# Return the value of the hand.
# The value of the hand is either total or total + 10 (if the ace is useable)
def hand_value(hand):
   total, ace = hand
   if (hand_has_useable_ace(hand)):
      return total + 10
   else:
      return total

# Update a hand by adding a card to it.
# Return the new hand.
def hand_add_card(hand, card):
   total, ace = hand
   total = total + card
   if card == 1:
      ace = True
   return (total, ace)

# Return the reward of the game (-1, 0, or 1) given the final player and dealer
# hands.
def game_reward(player_hand, dealer_hand):
   player_val = hand_value(player_hand)
   dealer_val = hand_value(dealer_hand)
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

# Draw a card from an unbiased deck.
# Return the face value of the card (1 to 10).

def draw_card_unbiased(deck, deadDeck):
   card = deck[0][1:]
   deadDeck.append(card)
   if card == 'a':
      cardVal = 1
   elif card == 'j' or card == 'q' or card == 'k':
      cardVal = 10
   else:
      cardVal = int(card)
   return cardVal

# Deal a player hand given the function to draw cards.
# Return only the hand.
def deal_player_hand(draw):
   hand = empty_hand()
   hand = hand_add_card(hand, draw())
   hand = hand_add_card(hand, draw())
   while (hand_value(hand) < 11):
      hand = hand_add_card(hand, draw())
   return hand

# Deal the first card of a dealer hand given the function to draw cards.
# Return the hand and the shown card.
def deal_dealer_hand(draw):
   hand = empty_hand()
   card = draw()
   hand = hand_add_card(hand, card)
   return hand, card

# Play the dealer hand using the fixed strategy for the dealer.
# Return the resulting dealer hand.
def play_dealer_hand(hand, draw):
   while hand_value(hand) < 17:
      hand = hand_add_card(hand, draw())
   return hand

# States are tuples (card, val, useable) where
#  - card is the card the dealer is showing
#  - val is the current value of the player's hand
#  - useable is whether or not the player has a useable ace

# Actions are either stay (False) or hit (True)

# Select a state at random.
def select_random_state(all_states):
   n = len(all_states)
   r = random.randint(0, n-1)
   state = all_states[r]
   return state

# Select an action at random
def select_random_action():
   r = random.randint(1, 2)
   return r == 1

# Select the best action using current Q-values.
def select_best_action(Q, state):
   if Q[(state, True)] > Q[(state, False)]:
      return True
   else:
      return False

# Select an action according to the epsilon-greedy policy
def select_e_greedy_action(Q, state, epsilon):
   r = random.random()
   if r < epsilon:
      return select_random_action()
   else:
      return select_best_action(Q, state)

# Given the state, return player and dealer hand consistent with it.
def hands_from_state(state):
   card, val, useable = state
   if useable:
      val = val - 10
   player_hand = (val, useable)
   dealer_hand = empty_hand()
   dealer_hand = hand_add_card(dealer_hand, card)
   return card, dealer_hand, player_hand

# Given the dealer's card and player's hand, return the state.
def state_from_hands(card, player_hand):
   val = hand_value(player_hand)
   useable = hand_has_useable_ace(player_hand)
   return (card, val, useable)

# Return a list of the possible states.
def state_list():
   states = []
   for card in range(1, 11):
      for val in range(11, 22):
         states.append((card, val, False))
         states.append((card, val, True))
   return states

# Return a map of all (state, action) pairs -> values (initially zero)
def initialize_state_action_value_map():
   states = state_list()
   M = {}
   for state in states:
      M[(state, False)] = 0.0
      M[(state, True)] = 0.0
   return M

# Print a (state, action) -> value map
def print_state_action_value_map(M):
   for useable in [True, False]:
      if useable:
         print('Usable ace')
      else:
         print('No useable ace')
      print('Values for staying:')
      for val in range(21, 10, -1):
         for card in range(1, 11):
            print('%5.2f' % M[((card, val, useable), False)], ' ',)
         print('| %d' % val)
      print('Values for hitting:')
      for val in range(21, 10, -1):
         for card in range(1, 11):
            print('%5.2f' % M[((card, val, useable), True)], ' ',)
         print('| %d' % val)
      print(' ')

# Print the state-action-value function (Q)
def print_Q(Q):
   print('---- Q(s,a) ----')
   print_state_action_value_map(Q)

# Print the state-value function (V) given the Q-values
def print_V(Q):
   print('---- V(s) ----')
   for useable in [True, False]:
      if useable:
         print('Usable ace')
      else:
         print('No useable ace')
      for val in range(21, 10, -1):
         for card in range(1, 11):
            if Q[((card, val, useable), True)] > Q[((card, val, useable), False)]:
               print('%5.2f' % Q[((card, val, useable), True)], ' ',)
            else:
               print('%5.2f' % Q[((card, val, useable), False)], ' ',)
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
      for val in range(21, 10, -1):
         for card in range(1, 11):
            if Q[((card, val, useable), True)] > Q[((card, val, useable), False)]:
               print('X'),
            else:
               print(' '),
         print('| %d' % val)
      print(' ')

# Initialize Q-values so that they produce the initial policy of sticking
# only on 20 or 21.
def initialize_Q():
   states = state_list()
   M = {}
   for state in states:
      card, val, useable = state
      if val < 20:
         M[(state, False)] = -0.001
         M[(state, True)] = 0.001   # favor hitting
      else:
         M[(state, False)] = 0.001  # favor sticking
         M[(state, True)] = -0.001
   return M

# Initialize number of times each (state,action) pair has been observed.
def initialize_count():
   count = initialize_state_action_value_map()
   return count

# Q-learning.
#
# Run Q-learning for the specified number of iterations and return the Q-values.
# In this implementation, alpha decreases over time.
def q_learning(draw, n_iter, alpha, epsilon):
   # initialize Q and count
   Q = initialize_Q()
   count = initialize_count()
   # get list of all states
   all_states = state_list()
   # iterate
   for n in range(0, n_iter):
      # initialize state
      state = select_random_state(all_states)
      dealer_card, dealer_hand, player_hand = hands_from_state(state)
      # choose actions, update Q
      while True:
         action = select_e_greedy_action(Q, state, epsilon)
         sa = (state, action)
         if action:
            # draw a card, update state
            player_hand = hand_add_card(player_hand, draw)
            # check if busted
            if hand_value(player_hand) > 21:
               # update Q-value
               count[sa] = count[sa] + 1.0
               Q[sa] = Q[sa] + alpha/count[sa] * ((-1.0) - Q[sa])
               break
            else:
               # update Q-value
               s_next = state_from_hands(dealer_card, player_hand)
               q_best = Q[(s_next, False)]
               if Q[(s_next, True)] > q_best:
                  q_best = Q[(s_next, True)]
               count[sa] = count[sa] + 1.0
               Q[sa] = Q[sa] + alpha/count[sa] * (q_best - Q[sa])
               # update state
               state = s_next
         else:
            # allow the dealer to play
            dealer_hand = play_dealer_hand(dealer_hand, draw)
            # compute return
            R = game_reward(player_hand, dealer_hand)
            # update Q value
            count[sa] = count[sa] + 1.0
            Q[sa] = Q[sa] + alpha/count[sa] * (R - Q[sa])
            break
   return Q

# Main ai function interface
def get_policy(deadDeck, playerHand, dealerHand):
   n_iter_mc = 10000000
   n_iter_q  = 10000000
   n_games = 100000
   alpha = 1
   epsilon = 0.1
   print('Q-LEARNING -- UNBIASED DECK')
   Q = q_learning(draw_card_unbiased(deck, deadDeck), n_iter_q, alpha, epsilon)
   print_Q(Q)
   print_V(Q)
   print_policy(Q)
   return Q


# Main program
if __name__ == '__main__':
   # set parameters
   n_iter_mc = 10000000
   n_iter_q  = 10000000
   n_games = 100000
   alpha = 1
   epsilon = 0.1
   # run learning algorithms
   print('Q-LEARNING -- UNBIASED DECK')
   Q = q_learning(draw_card_unbiased, n_iter_q, alpha, epsilon)
   print_Q(Q)
   print_V(Q)
   print_policy(Q)
   exit(0)