#!/usr/bin/python
import random
import sys
from ai import *
from settings import *
import pygame
from pygame.locals import *
from utils import *
import _thread
import time

# init the pygame state
pygame.font.init()
pygame.mixer.init()

screen = pygame.display.set_mode((820, 540))
clock = pygame.time.Clock()

# main game function begins
def mainGame():
    """ Function that contains all the game logic. """
    
    def gameOver(funds):
        """ Displays a game over screen in its own little loop. It is called when it has been determined that the player's funds have
        run out. All the player can do from this screen is exit the game."""
        
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    sys.exit()

            # Fill the screen with black screen
            screen.fill((0, 0, 0))
            
            # Render "Game Over" sentence on the screen
            oFont = pygame.font.Font(None, 50)
            if funds <= 0:
                displayFont = pygame.font.Font.render(oFont, "Game over! You lose!", 1, (255, 255, 255), (0, 0, 0))
            elif funds >= 200:
                displayFont = pygame.font.Font.render(oFont, "Game over! You win", 1, (255, 255, 255), (0, 0, 0))
            screen.blit(displayFont, (125, 220))
            
            # Update the display
            pygame.display.flip()

    def showProgressBar(pbar, continueFlag):
        """Display the progress bar before we enter into the formal game, at the same time, the ai alg will
        run behind and get the policy when loading is finished"""

        while continueFlag[0]:
            for event in pygame.event.get():
                if event.type == QUIT:
                    sys.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    sys.exit()

            screen.fill((0, 0, 0))
            time.sleep(0.7)
            pbar.update()
            
    ######## DECK FUNCTIONS BEGIN ########
    def deckDeal(deck, deadDeck):
        """ Shuffles the deck, takes the top 4 cards off the deck, appends them to the player's and dealer's hands, and
        returns the player's and dealer's hands. """

        deck = shuffle(deck)
        dealerHand, playerHand = [], []

        cardsToDeal = 4

        while cardsToDeal > 0:
            if len(deck) == 0:
                deck, deadDeck = returnFromDead(deck, deadDeck)

            # deal the first card to the player, second to dealer, 3rd to player, 4th to dealer,
            # based on divisibility
            if cardsToDeal % 2 == 0:
                playerHand.append(deck[0])
            else:
                dealerHand.append(deck[0])
            
            del deck[0]
            cardsToDeal -= 1
            
        return deck, deadDeck, playerHand, dealerHand

    def hit(deck, deadDeck, hand):
        """ Checks to see if the deck is gone, in which case it takes the cards from
        the dead deck (cards that have been played and discarded)
        and shuffles them in. Then if the player is hitting, it gives
        a card to the player, or if the dealer is hitting, gives one to the dealer."""

        # if the deck is empty, shuffle in the dead deck
        if len(deck) == 0:
            deck, deadDeck = returnFromDead(deck, deadDeck)

        hand.append(deck[0])
        del deck[0]

        return deck, deadDeck, hand

    def checkValue(hand):
        """ Checks the value of the cards in the player's or dealer's hand. """

        totalValue = 0
        aceCount = 0
        aceFlag = True

        for card in hand:
            value = card[1:]

            # Jacks, kings and queens are all worth 10, and ace is worth 11    
            if value == 'j' or value == 'q' or value == 'k':
                value = 10
            elif value == 'a':
                value = 11
                aceCount += 1
            else:
                value = int(value)

            totalValue += value
            
        # check the special case where ace represents 1
        if totalValue > 21:
            for card in hand:
                # If the player would bust and he has an ace in his hand, the ace's value is diminished by 10    
                # In situations where there are multiple aces in the hand, this checks to see if the total value
                # would still be over 21 if the second ace wasn't changed to a value of one. If it's under 21, there's no need 
                # to change the value of the second ace, so the loop breaks. 
                if card[1] == 'a':
                    totalValue -= 10
                    aceCount -= 1

                if totalValue <= 21:
                    if aceCount == 0:
                        aceFlag = False
                    else:
                        aceFlag = True
                    break
                else:
                    continue

        return totalValue, aceFlag
        
    def blackJack(deck, deadDeck, playerHand, dealerHand, funds, bet, cards, cardSprite):
        """ Called when the player or the dealer is determined to have blackjack. Hands are compared to determine the outcome. """

        textFont = pygame.font.Font(None, 28)

        playerValue, playerAceFlag = checkValue(playerHand)
        dealerValue, dealerAceFlag = checkValue(dealerHand)
        
        if playerValue == 21 and dealerValue == 21:
            # The opposing player ties the original blackjack getter because he also has blackjack
            # No money will be lost, and a new hand will be dealt
            displayFont = display(textFont, "Blackjack! The dealer also has blackjack, another round")
            deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, 0, bet, cards, cardSprite)
        elif playerValue == 21 and dealerValue != 21:
            # Dealer loses
            displayFont = display(textFont, "Blackjack! You won $%.2f." % (bet * 1.5))
            deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, bet, 0, cards, cardSprite)
        elif dealerValue == 21 and playerValue != 21:
            # Player loses, money is lost, and new hand will be dealt
            deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, 0, bet, cards, cardSprite)
            displayFont = display(textFont, "Dealer has blackjack! You lose $%.2f." % bet)
            
        return displayFont, playerHand, dealerHand, deadDeck, funds, roundEnd

    def bust(deck, playerHand, dealerHand, deadDeck, funds, moneyGained, moneyLost, cards, cardSprite):
        """ This is only called when player busts by drawing too many cards. """
        
        font = pygame.font.Font(None, 28)
        displayFont = display(font, "You bust! You lost $%.2f." % moneyLost)
        
        deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, moneyGained, moneyLost, cards, cardSprite)
        
        return deck, playerHand, dealerHand, deadDeck, funds, roundEnd, displayFont

    def endRound(deck, playerHand, dealerHand, deadDeck, funds, moneyGained, moneyLost, cards, cardSprite):
        """ Called at the end of a round to determine what happens to the cards, the money gained or lost,
        and such. It also shows the dealer's hand to the player, by deleting the old sprites and showing
        all the cards. """
    
        if len(playerHand) == 2 and "a" in playerHand[0] or "a" in playerHand[1]:
            # If the player has blackjack, pay his bet back 3:2
            moneyGained += moneyGained / 2.0
            
        # Remove old dealer's cards
        cards.empty()
        
        dCardPos = (50, 70)
                   
        for x in dealerHand:
            card = cardSprite(x, dCardPos)
            dCardPos = (dCardPos[0] + 80, dCardPos[1])
            cards.add(card)

        # Remove the cards from the player's and dealer's hands
        for card in playerHand:
            deadDeck.append(card)
        for card in dealerHand:
            deadDeck.append(card)

        del playerHand[:]
        del dealerHand[:]

        funds += moneyGained
        funds -= moneyLost
        
        textFont = pygame.font.Font(None, 28)
        
        if funds <= 0 or funds >= 200:
            gameOver(funds)
        
        roundEnd = 1

        return deck, playerHand, dealerHand, deadDeck, funds, roundEnd 
        
    def compareHands(deck, deadDeck, playerHand, dealerHand, funds, bet, cards, cardSprite):
        """ Called at the end of a round (after the player stands), or at the beginning of a round
        if the player or dealer has blackjack. This function compares the values of the respective hands of
        the player and the dealer and determines who wins the round based on the rules of blacjack. """

        textFont = pygame.font.Font(None, 28)

        dealerValue, dealerAceFlag = checkValue(dealerHand)
        playerValue, playerAceFlag = checkValue(playerHand)
            
        # Dealer hits until he has 17 or over        
        while True:
            if dealerValue < 17:
                # dealer hits when he has less than 17, and stands if he has 17 or above
                deck, deadDeck, dealerHand = hit(deck, deadDeck, dealerHand)
                dealerValue, dealerAceFlag = checkValue(dealerHand)
            else:   
                # dealer stands
                break
            
        if playerValue > dealerValue and playerValue <= 21:
            # Player has beaten the dealer, and hasn't busted, therefore WINS
            deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, bet, 0, cards, cardSprite)
            displayFont = display(textFont, "You won $%.2f." % bet)
        elif playerValue == dealerValue and playerValue <= 21:
            # Tie
            deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, 0, 0, cards, cardSprite)
            displayFont = display(textFont, "It's a tie, another round!")
        elif dealerValue > 21 and playerValue <= 21:
            # Dealer has busted and player hasn't
            deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, bet, 0, cards, cardSprite)
            displayFont = display(textFont, "Dealer busts! You won $%.2f." % bet)
        else:
            # Dealer wins in every other siutation taht i can think of
            deck, playerHand, dealerHand, deadDeck, funds, roundEnd = endRound(deck, playerHand, dealerHand, deadDeck, funds, 0, bet, cards, cardSprite)
            displayFont = display(textFont, "Dealer wins! You lost $%.2f." % bet)
            
        return deck, deadDeck, roundEnd, funds, displayFont
    ######## DECK FUNCTIONS END ########  

    ######## SPRITE FUNCTIONS BEGIN ##########
    class cardSprite(pygame.sprite.Sprite):
        """ Sprite that displays a specific card. """
        
        def __init__(self, card, position):
            pygame.sprite.Sprite.__init__(self)
            cardImage = card + ".png"
            self.image, self.rect = imageLoad(cardImage, 1)
            self.position = position
        def update(self):
            self.rect.center = self.position
            
    class hitButton(pygame.sprite.Sprite):
        """ Button that allows player to hit (take another card from the deck). """
        
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = imageLoad("hit-grey.png", 0)
            self.position = (735, 400)
            
        def update(self, mX, mY, deck, deadDeck, playerHand, cards, pCardPos, roundEnd, cardSprite, click):
            """ If the button is clicked and the round is NOT over, Hits the player with a new card from the deck. It then creates a sprite
            for the card and displays it. """
            
            if roundEnd == 0:
                self.image, self.rect = imageLoad("hit.png", 0)
            else:
                self.image, self.rect = imageLoad("hit-grey.png", 0)
            
            self.position = (735, 400)
            self.rect.center = self.position
            
            if self.rect.collidepoint(mX, mY) == 1 and click == 1:
                if roundEnd == 0: 
                    playClick()
                    deck, deadDeck, playerHand = hit(deck, deadDeck, playerHand)

                    currentCard = len(playerHand) - 1
                    card = cardSprite(playerHand[currentCard], pCardPos)
                    cards.add(card)
                    pCardPos = (pCardPos[0] - 80, pCardPos[1])
                
                    click = 0
                
            return deck, deadDeck, playerHand, pCardPos, click
            
    class standButton(pygame.sprite.Sprite):
        """ Button that allows the player to stand (not take any more cards). """
        
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = imageLoad("stand-grey.png", 0)
            self.position = (735, 365)
            
        def update(self, mX, mY, deck, deadDeck, playerHand, dealerHand, cards, pCardPos, roundEnd, cardSprite, funds, bet, displayFont):
            """ If the button is clicked and the round is NOT over, let the player stand (take no more cards). """
            
            if roundEnd == 0:
                self.image, self.rect = imageLoad("stand.png", 0)
            else:
                self.image, self.rect = imageLoad("stand-grey.png", 0)
            
            self.position = (735, 365)
            self.rect.center = self.position
            
            if self.rect.collidepoint(mX, mY) == 1:
                if roundEnd == 0: 
                    playClick()
                    deck, deadDeck, roundEnd, funds, displayFont = compareHands(deck, deadDeck, playerHand, dealerHand, funds, bet, cards, cardSprite)
                
            return deck, deadDeck, roundEnd, funds, playerHand, deadDeck, pCardPos, displayFont 
            
    class doubleButton(pygame.sprite.Sprite):
        """ Button that allows player to double (double the bet, take one more card, then stand)."""
        
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = imageLoad("double-grey.png", 0)
            self.position = (735, 330)
            
        def update(self, mX, mY, deck, deadDeck, playerHand, dealerHand, playerCards, cards, pCardPos, roundEnd, cardSprite, funds, bet, displayFont):
            """ If the button is clicked and the round is NOT over, let the player stand (take no more cards). """
            
            if roundEnd == 0 and funds >= bet * 2 and len(playerHand) == 2:
                self.image, self.rect = imageLoad("double.png", 0)
            else:
                self.image, self.rect = imageLoad("double-grey.png", 0)
                
            self.position = (735, 330)
            self.rect.center = self.position
                
            if self.rect.collidepoint(mX, mY) == 1:
                if roundEnd == 0 and funds >= bet * 2 and len(playerHand) == 2: 
                    bet = bet * 2
                    
                    playClick()
                    deck, deadDeck, playerHand = hit(deck, deadDeck, playerHand)

                    currentCard = len(playerHand) - 1
                    card = cardSprite(playerHand[currentCard], pCardPos)
                    playerCards.add(card)
                    pCardPos = (pCardPos[0] - 80, pCardPos[1])
        
                    deck, deadDeck, roundEnd, funds, displayFont = compareHands(deck, deadDeck, playerHand, dealerHand, funds, bet, cards, cardSprite)
                    
                    bet = bet / 2

            return deck, deadDeck, roundEnd, funds, playerHand, deadDeck, pCardPos, displayFont, bet

    class aiButton(pygame.sprite.Sprite):
        """ Button for ai to deal with the game, it will help the player to determine hit or stand during the game"""
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = imageLoad("ai.png", 0)
            self.position = (735, 435)
            self.policySet = None
            self.continueFlag = [True]
            _thread.start_new_thread(self.setPolicy, ())
            # print(self.policySet[0])
            # print(self.policySet[1])

        def setPolicy(self):
            self.policySet = getPolicySet()
            self.continueFlag.remove(True)
            self.continueFlag.append(False)

        def choseAction(self, playerAceFlag, dealerVal, playerVal):
            if playerAceFlag:
                return self.policySet[0][(dealerVal, playerVal)]
            else:
                return self.policySet[1][(dealerVal, playerVal)]

        def update(self, mX, mY, deck, deadDeck, roundEnd, cardSprite, playerCards ,cards, playerHand, dealerHand, pCardPos, funds, bet, displayFont):
            """If the mouse position is on the ai button, and the mouse is clicking and roundEnd is 0, then ai will be
            triggered to handle the hit or action according to the policy table"""

            if roundEnd == 0:
                self.image, self.rect = imageLoad("ai.png", 0)
            else:
                self.image, self.rect = imageLoad("ai-grey.png", 0)

            self.position = (735, 435)
            self.rect.center = self.position

            if self.rect.collidepoint(mX, mY) == 1:
                if roundEnd == 0:
                    playClick()
                    # check the current player hand and dealer hand
                    # according to the policy table to find the action
                    playerVal, playerAceFlag = checkValue(playerHand)
                    dealerVal, dealerAceFlag = checkValue(dealerHand[0:1])
                    if dealerVal == 11:
                        dealerVal -= 10

                    print("---start----")
                    print("player" + str(playerVal))
                    print(playerAceFlag)
                    # print("total dealer" + str(checkValue(dealerHand)))
                    print("current dealer" + str(dealerVal))
                    print("---end----")

                    # hit
                    while playerVal <= 21 and self.choseAction(playerAceFlag, dealerVal, playerVal):
                        deck, deadDeck, playerHand = hit(deck, deadDeck, playerHand)
                        currentCard = len(playerHand) - 1
                        card = cardSprite(playerHand[currentCard], pCardPos)
                        playerCards.add(card)
                        pCardPos = (pCardPos[0] - 80, pCardPos[1])
                        playerVal, playerAceFlag = checkValue(playerHand)
                        print("---")
                        print(playerAceFlag)
                        print("updated player" + str(playerVal))
                        print("---")

                    # stand
                    if playerVal <= 21 and self.choseAction(playerAceFlag, dealerVal, playerVal) is False:
                        deck, deadDeck, roundEnd, funds, displayFont = compareHands(deck, deadDeck, playerHand, dealerHand, funds, bet, cards, cardSprite)


            return deck, deadDeck, roundEnd, playerHand, pCardPos, funds, bet, displayFont


    class dealButton(pygame.sprite.Sprite):
        """ A button on the right hand side of the screen that can be clicked at the end of a round to deal a
        new hand of cards and continue the game. """
        
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = imageLoad("deal.png", 0)
            self.position = (735, 485)

        def update(self, mX, mY, deck, deadDeck, roundEnd, cardSprite, cards, playerHand, dealerHand, dCardPos, pCardPos, displayFont, playerCards, click, handsPlayed):
            """ If the mouse position collides with the button, and the mouse is clicking, and roundEnd does not = 0,
            then Calls deckDeal to deal a hand to the player and a hand to the dealer. It then
            takes the cards from the player's hand and the dealer's hand and creates sprites for them,
            placing them on the visible table. The deal button can only be pushed after the round has ended
            and a winner has been declared. """
            
            # Get rid of the in between-hands chatter
            textFont = pygame.font.Font(None, 28)
            
            if roundEnd == 1:
                self.image, self.rect = imageLoad("deal.png", 0)
            else:
                self.image, self.rect = imageLoad("deal-grey.png", 0)
            
            self.position = (735, 485)
            self.rect.center = self.position
            
                
            if self.rect.collidepoint(mX, mY) == 1:
                if roundEnd == 1 and click == 1:
                    playClick()
                    displayFont = display(textFont, "")
                    
                    cards.empty()
                    playerCards.empty()
                    
                    deck, deadDeck, playerHand, dealerHand = deckDeal(deck, deadDeck)

                    dCardPos = (50, 70)
                    pCardPos = (540, 370)

                    # Create player's card sprites
                    for x in playerHand:
                        card = cardSprite(x, pCardPos)
                        pCardPos = (pCardPos[0] - 80, pCardPos[1])
                        playerCards.add(card)
                    
                    # Create dealer's card sprites  
                    faceDownCard = cardSprite("back", dCardPos)
                    dCardPos = (dCardPos[0] + 80, dCardPos[1])
                    cards.add(faceDownCard)

                    card = cardSprite(dealerHand [0], dCardPos)
                    cards.add(card)
                    roundEnd = 0
                    click = 0
                    handsPlayed += 1


                    
            return deck, deadDeck, playerHand, dealerHand, dCardPos, pCardPos, roundEnd, displayFont, click, handsPlayed
            
    class betButtonUp(pygame.sprite.Sprite):
        """ Button that allows player to increase his bet (in between hands only). """
        
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = imageLoad("up.png", 0)
            self.position = (710, 255)
            
        def update(self, mX, mY, bet, funds, click, roundEnd):
            if roundEnd == 1:
                self.image, self.rect = imageLoad("up.png", 0)
            else:
                self.image, self.rect = imageLoad("up-grey.png", 0)
            
            self.position = (710, 255)
            self.rect.center = self.position
            
            if self.rect.collidepoint(mX, mY) == 1 and click == 1 and roundEnd == 1:
                playClick()
                    
                if bet < funds:
                    bet += 5.0
                    # If the bet is not a multiple of 5, turn it into a multiple of 5
                    # This can only happen when the player has gotten blackjack, and has funds that are not divisible by 5,
                    # then loses money, and has a bet higher than his funds, so the bet is pulled down to the funds,
                    # which are uneven.
                    if bet % 5 != 0:
                        while bet % 5 != 0:
                            bet -= 1

                click = 0
            
            return bet, click
            
    class betButtonDown(pygame.sprite.Sprite):
        """ Button that allows player to decrease his bet (in between hands only). """
        
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)
            self.image, self.rect = imageLoad("down.png", 0)
            self.position = (710, 255)
            
        def update(self, mX, mY, bet, click, roundEnd):  
            if roundEnd == 1:
                self.image, self.rect = imageLoad("down.png", 0)
            else:
                self.image, self.rect = imageLoad("down-grey.png", 0)
        
            self.position = (760, 255)
            self.rect.center = self.position
            
            if self.rect.collidepoint(mX, mY) == 1 and click == 1 and roundEnd == 1:
                playClick()
                if bet > 5:
                    bet -= 5.0
                    if bet % 5 != 0:
                        while bet % 5 != 0:
                            bet += 1
                    
                click = 0
            
            return bet, click

    class progressBar():
        def __init__(self):
            self.color = (102, 170, 255)
            self.y1 = screen.get_height()/2
            self.y2 = self.y1 + 20
            self.max_width = 800 - 40
            self.font = pygame.font.Font(None, 64)
            self.loading = self.font.render("LOADING", True, self.color)
            self.textHeight = self.y1 - 80
            self.percent = 0

        def update(self):
            screen.fill((0, 0, 0))
            screen.blit(self.loading, (300, self.textHeight))
            pygame.draw.rect(screen, self.color, (20, self.y1, self.max_width, 20), 2)
            self.percent += 1
            pygame.draw.rect(screen, self.color, (20, self.y1, (self.percent*self.max_width)/100, 20), 0)
            pygame.display.flip()

            (r, g, b) = self.color
            r = min(r + 2, 255)
            g = max(g - 2, 0)
            b = max(b - 2, 0)
            self.color = (r, g, b)
            self.loading = self.font.render("LOADING", True, self.color)

    ###### SPRITE FUNCTIONS END ######

    ###### INITIALIZATION BEGINS ######
    # This font is used to display text on the right-hand side of the screen
    textFont = pygame.font.Font(None, 28)

    # This sets up the background image, and its container rect
    background, backgroundRect = imageLoad("bjs.png", 0)
    
    # cards is the sprite group that will contain sprites for the dealer's cards
    cards = pygame.sprite.Group()
    # playerCards will serve the same purpose, but for the player
    playerCards = pygame.sprite.Group()

    # This creates instances of all the button sprites
    bbU = betButtonUp()
    bbD = betButtonDown()
    standButton = standButton()
    dealButton = dealButton()
    hitButton = hitButton()
    doubleButton = doubleButton()
    aiButton = aiButton()
    pbar = progressBar()
    
    # This group contains the button sprites
    buttons = pygame.sprite.Group(bbU, bbD, hitButton, standButton, dealButton, doubleButton, aiButton)

    # The 52 card deck is created
    deck = createDeck()
    # The dead deck will contain cards that have been discarded
    deadDeck = []

    # These are default values that will be changed later, but are required to be declared now
    # so that Python doesn't get confused
    playerHand, dealerHand, dCardPos, pCardPos = [], [], (), ()
    mX, mY = 0, 0
    click = 0

    # The default funds start at $100.00, and the initial bet defaults to $10.00
    funds = 100.00
    bet = 10.00

    # This is a counter that counts the number of rounds played in a given session
    handsPlayed = 0

    # When the cards have been dealt, roundEnd is zero.
    # In between rounds, it is equal to one
    roundEnd = 1
    
    # firstTime is a variable that is only used once, to display the initial
    # message at the bottom, then it is set to zero for the duration of the program.
    firstTime = 1

    showProgressBar(pbar, aiButton.continueFlag)
    ###### INITILIZATION ENDS ########
    
    ###### MAIN GAME LOOP BEGINS #######
    while True:
        screen.blit(background, backgroundRect)

        if bet > funds:
            # If you lost money, and your bet is greater than your funds, make the bet equal to the funds
            bet = funds

        # When the player hasn't started. Will only be displayed the first time.
        if roundEnd == 1 and firstTime == 1:
            displayFont = display(textFont, "Click on the arrows to declare your bet, then deal to start the game.")
            firstTime = 0

        # When a new round start, put the card in the dead deck into the original deck
        if roundEnd == 1:
            returnFromDead(deck, deadDeck)

        # Show the blurb at the bottom of the screen, how much money left, and current bet
        screen.blit(displayFont, (10, 444))
        fundsFont = pygame.font.Font.render(textFont, "Funds: $%.2f" % funds, 1, (255, 255, 255), (0, 0, 0))
        screen.blit(fundsFont, (663, 205))
        betFont = pygame.font.Font.render(textFont, "Bet: $%.2f" % bet, 1, (255, 255, 255), (0, 0, 0))
        screen.blit(betFont, (680, 285))
        hpFont = pygame.font.Font.render(textFont, "Round: %i " % handsPlayed, 1, (255, 255, 255), (0, 0, 0))
        screen.blit(hpFont, (663, 180))

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mX, mY = pygame.mouse.get_pos()
                    click = 1
            elif event.type == MOUSEBUTTONUP:
                mX, mY = 0, 0
                click = 0

        # Initial check for the value of the player's hand, so that his hand can be displayed and it can be determined
        # if the player busts or has blackjack or not
        if roundEnd == 0:
            # Stuff to do when the game is happening
            playerValue, playerAceFlag = checkValue(playerHand)
            # print(playerValue)
            dealerValue, dealerAceFlag = checkValue(dealerHand)
            # print(dealerValue)

            if playerValue == 21 and len(playerHand) == 2:
                # If the player gets blackjack
                displayFont, playerHand, dealerHand, deadDeck, funds, roundEnd = \
                    blackJack(deck, deadDeck, playerHand, dealerHand, funds,  bet, cards, cardSprite)

            if dealerValue == 21 and len(dealerHand) == 2:
                # If the dealer has blackjack
                displayFont, playerHand, dealerHand, deadDeck, funds, roundEnd = \
                    blackJack(deck, deadDeck, playerHand, dealerHand, funds,  bet, cards, cardSprite)

            if playerValue > 21:
                # If player busts
                deck, playerHand, dealerHand, deadDeck, funds, roundEnd, displayFont = \
                    bust(deck, playerHand, dealerHand, deadDeck, funds, 0, bet, cards, cardSprite)

        # Update the buttons
        # deal
        deck, deadDeck, playerHand, dealerHand, dCardPos, pCardPos, roundEnd, displayFont, click, handsPlayed = \
            dealButton.update(mX, mY, deck, deadDeck, roundEnd, cardSprite, cards, playerHand, dealerHand, dCardPos,
                              pCardPos, displayFont, playerCards, click, handsPlayed)
        # ai
        deck, deadDeck, roundEnd, playerHand, pCardPos, funds, bet, displayFont = \
            aiButton.update(mX, mY, deck, deadDeck, roundEnd, cardSprite, playerCards, cards, playerHand, dealerHand,
                            pCardPos,funds, bet, displayFont)
        # hit
        deck, deadDeck, playerHand, pCardPos, click = \
            hitButton.update(mX, mY, deck, deadDeck, playerHand, playerCards, pCardPos, roundEnd, cardSprite, click)
        # stand
        deck, deadDeck, roundEnd, funds, playerHand, deadDeck, pCardPos,  displayFont = \
            standButton.update(mX, mY, deck, deadDeck, playerHand, dealerHand, cards, pCardPos, roundEnd, cardSprite,
                               funds, bet, displayFont)
        # double
        deck, deadDeck, roundEnd, funds, playerHand, deadDeck, pCardPos, displayFont, bet = \
            doubleButton.update(mX, mY, deck, deadDeck, playerHand, dealerHand, playerCards, cards, pCardPos, roundEnd,
                                cardSprite, funds, bet, displayFont)
        # Bet buttons
        bet, click = bbU.update(mX, mY, bet, funds, click, roundEnd)
        bet, click = bbD.update(mX, mY, bet, click, roundEnd)
        # draw them to the screen
        buttons.draw(screen)

        # If there are cards on the screen, draw them
        if len(cards) is not 0:
            playerCards.update()
            playerCards.draw(screen)
            cards.update()
            cards.draw(screen)

        # Updates the contents of the display
        pygame.display.flip()

    ###### MAIN GAME LOOP ENDS ######

###### MAIN GAME FUNCTION ENDS ######


# start the game
if __name__ == "__main__":
    mainGame()
