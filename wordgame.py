# The 6.00 Word Game

import random
from randomdict import RandomDict
import threading
import queue
import textwrap



VOWELS = 'aeiou'
CONSONANTS = 'bcdfghjklmnpqrstvwxyz'
HAND_SIZE = 7

SCRABBLE_LETTER_VALUES = {
    'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4, 'g': 2, 'h': 4, 'i': 1, 'j': 8, 'k': 5, 'l': 1, 'm': 3, 'n': 1, 'o': 1, 'p': 3, 'q': 10, 'r': 1, 's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8, 'y': 4, 'z': 10
}

# -----------------------------------
# Helper code
# (you don't need to understand this helper code)

WORDLIST_FILENAME = "words.txt"

def loadWords_thread(in_queue):
    """ Worker queue processing function
    """
    while True:
        item = in_queue.get()
        # wordList is a dict. str -> list
        # keys are words, list[0] is the score list[1] is the word len
        wordList[item] = [ getWordScore_init(item), len(item) ]
        in_queue.task_done()
        
def loadWords(n):
    """
    Returns a list of valid words based on maximum word size n. 
    Words are strings of lowercase letters. n assumed to be integer
    
    n: int representing maximum word size
    Depending on the size of the word list, this function may
    take a while to finish.
    
    """
    print("Loading word list from file...")
    global wordList
    wordList = {}
    work = queue.Queue()
    
    # Create 4 threads to process the words from the file into a dict
    for i in range(4):
        t = threading.Thread(target=loadWords_thread, args=(work,))
        t.daemon = True
        t.start()

    # Use with open for guaranteed file closing
    with open(WORDLIST_FILENAME, 'r') as inFile:  
        for line in inFile:
            # First, check if the word has less or equal # of letters as n
            if len(line.strip().lower()) <= n:
                #If true, put the work in the worker queue
                work.put(line.strip().lower())

    # work.join() makes sure all processing is completed by threads before
    # continuing with the program
    work.join()

    print("  ", len(wordList), "words loaded.")
    return wordList

def getFrequencyDict(sequence):
    """
    Returns a dictionary where the keys are elements of the sequence
    and the values are integer counts, for the number of times that
    an element is repeated in the sequence.

    sequence: string or list
    return: dictionary
    """
    # freqs: dictionary (element_type -> int)
    freq = {}
    for x in sequence:
        freq[x] = freq.get(x,0) + 1
    return freq
	

# (end of helper code)
# -----------------------------------

#
# Problem #1: Scoring a word
#
def getWordScore_init(word):
    """
    Returns the score for a word. Assumes the word is a valid word.
    
    This is a helper function for initializing the dictionary that will
    contain the word score for the remainder of the game.

    The score for a word is the sum of the points for letters in the
    word, multiplied by the length of the word, PLUS 50 points if all n
    letters are used on the first turn.

    Letters are scored as in Scrabble; A is worth 1, B is worth 3, C is
    worth 3, D is worth 2, E is worth 1, and so on (see SCRABBLE_LETTER_VALUES)

    word: string (lowercase letters)
    n: integer (HAND_SIZE; i.e., hand size required for additional points)
    returns: int >= 0
    """
    score = 0

    for ltr in word:
        score += SCRABBLE_LETTER_VALUES.get(ltr,0)
    
    score *= len(word)

    return score
    
def getWordScore(word, n):
    """
    Returns the score for a word. Assumes the word is a valid word.
    
    Achieved by retrieving the score from the dictionary containing all
    words and word scores

    """
    score = wordList[word][0]
    if len(word) == n:
        score += 50
    return score
    
        


#
# Problem #2: Make sure you understand how this function works and what it does!
#

def flatten(aList):
    ''' 
    aList: a list 
    Returns a copy of aList, which is a flattened version of aList 
    '''            
    if type(aList) != list:
        return [aList]
    else:
        if len(aList) == 0:
            return []
        else:
            return flatten(aList[0]) + flatten(aList[1:])
        
def displayHand(hand):
    """
    Displays the letters currently in the hand.

    For example:
    >>> displayHand({'a':1, 'x':2, 'l':3, 'e':1})
    Should print out something like:
       a x x l l l e
    The order of the letters is unimportant.

    hand: dictionary (string -> int)
    """
    for letter in hand.keys():
        for j in range(hand[letter]):
             print(letter,end=" ")       # print all on the same line
    print()                             # print an empty line

def shuffleHand(hand):
    """
    Displays hand in randomized order
    
    hand: dictionary (string -> int)
    """
    randHand = [ [e]*hand[e] for e in hand ]
    randHand = flatten(randHand)
    random.shuffle(randHand)
    for ltr in randHand:
        print(ltr, end=" ")
    print()
    

#
# Problem #2: Make sure you understand how this function works and what it does!
#
def dealHand(wordList, n):
    """
    Generates a 'hand' from letters of a word in the wordlist with
    letters = n
    
    Takes wordList and filters it to only contain words of length n,
    then randomly chooses one of these words using RandomDict

    n: int >= 4
    returns: dictionary (string -> int)
    """
#    hand={}
#    numVowels = n // 3
#    

    # First create a dictionary of words that match the word length selected
    # at the beginning of the game
    wordMatch = { x:y[0] for x, y in wordList.items() if y[1] == n }
    wordMatchRand = RandomDict(wordMatch)
        
    myRandHand = wordMatchRand.random_key()
    hand = getFrequencyDict(myRandHand)
    
        
    return hand

#
# Problem #2: Update a hand by removing letters
#
def updateHand(hand, word):
    """
    Assumes that 'hand' has all the letters in word.
    In other words, this assumes that however many times
    a letter appears in 'word', 'hand' has at least as
    many of that letter in it. 

    Updates the hand: uses up the letters in the given word
    and returns the new hand, without those letters in it.

    Has no side effects: does not modify hand.

    word: string
    hand: dictionary (string -> int)    
    returns: dictionary (string -> int)
    """

    return { x: hand[x] - word.count(x) if x in word else hand[x]
        for x in hand if (hand.get(x,0) - word.count(x)) > 0 }    
 

#
# Problem #3: Test word validity
#
def isValidWord(word, hand, wordList):
    """
    Returns True if word is in the wordList and is entirely
    composed of letters in the hand. Otherwise, returns False.

    Does not mutate hand or wordList.
   
    word: string
    hand: dictionary (string -> int)
    wordList: list of lowercase strings
    """
    if word in wordList:
        valWord = True
    else:
        return False
    for ltr in word:
        if hand.get(ltr,0) - word.count(ltr) >= 0:
            valWord = True
        else: 
            valWord = False
            break
    return valWord
        

#
# Problem #4: Playing a hand
#

def calculateHandlen(hand):
    """ 
    Returns the length (number of letters) in the current hand.
    
    hand: dictionary (string-> int)
    returns: integer
    """
    return sum(hand.values())



def playHand(hand, wordList, n):
    """
    Allows the user to play the given hand, as follows:

    * The hand is displayed.
    * The user may input a word or a single period (the string ".") 
      to indicate they're done playing
    * Invalid words are rejected, and a message is displayed asking
      the user to choose another word until they enter a valid word or "."
    * When a valid word is entered, it uses up letters from the hand.
    * After every valid word: the score for that word is displayed,
      the remaining letters in the hand are displayed, and the user
      is asked to input another word.
    * The sum of the word scores is displayed when the hand finishes.
    * The hand finishes when there are no more unused letters or the user
      inputs a "."

      hand: dictionary (string -> int)
      wordList: list of lowercase strings
      n: integer (HAND_SIZE; i.e., hand size required for additional points)
      
    """
    # Keep track of the total score
    score = 0
    # As long as there are still letters left in the hand:
    userSelect = 'n'
    while calculateHandlen(hand) > 0:    
        # Display the hand
        if userSelect != "r":
            print()
            print("Current hand: ", end=" ")
            displayHand(hand)
        # Ask user for input
        userSelect = input("Enter word, a 'r' to shuffle the letters, or a '.' to indicate that you are finished: ")
        print()
        # If the input is a single period:
        if userSelect == ".":
            # End the game (break out of the loop)
            break
        # Otherwise (the input is not a single period):
        elif userSelect == "r":
            print("Current hand: ", end=" ")
            shuffleHand(hand)
        else:
            # If the word is not valid:
            if not isValidWord(userSelect, hand, wordList):    
                # Reject invalid word (print a message followed by a blank line)
                print("Invalid word, please try again.")
            # Otherwise (the word is valid):
            else:
                # Tell the user how many points the word earned, and the updated total score, in one line followed by a blank line
                score += getWordScore(userSelect,calculateHandlen(hand))
                print("Congratulations, your word '" + userSelect + "' has earned you " + 
                    str(getWordScore(userSelect,calculateHandlen(hand))) + " points. Your new score is: " + str(score) + ".")
                # Update the hand 
                hand = updateHand(hand, userSelect)

    # Game is over (user entered a '.' or ran out of letters), so tell user the total score
    print("Game over. You scored " + str(score) + " points.")

#
# Problem #5: Playing a game
#


    
    
    
def compChooseWord_thread(in_queue, hand, n):
    global bestScore
    global bestWord
    global topScores
    
    def addToTopScores(score, word):
        for i in range(1,len(topScores)):
            if score > topScores[i][0]:
                topScores[i] = (score, word)
                break
            
    lock = threading.Lock()    
    while True:
        word = in_queue.get()
        if isValidWord(word, hand, wordList):
            # find out how much making that word is worth
            score = getWordScore(word, n)
            # If the score for that word is higher than your best score

            if (score > topScores[len(topScores)][0]):
                # lock to prevent best words/scores being updated 
                # simultaneously (very small probability, I think it's needed
                # since topScores is global)
                lock.acquire()                
                # pass the score and word to the addToTopScores function to be
                # sorted into the list of topScores (if applicable)
                addToTopScores(score, word)
                # release the lock
                lock.release()
        in_queue.task_done()


def compChooseWord(hand, wordList, n):
    """
    Given a hand and a wordList, find the word that gives 
    the maximum value score, and return it.

    This word should be calculated by considering all the words
    in the wordList.

    If no words in the wordList can be made from the hand, return None.

    hand: dictionary (string -> int)
    wordList: list (string)
    n: integer (HAND_SIZE; i.e., hand size required for additional points)

    returns: string or None
    """
    # Create a new variable to store the maximum score seen so far (initially 0)
    global bestScore
    bestScore = 0
    # Create a new variable to store the best word seen so far (initially None)  
    global bestWord
    bestWord = None
    
    global topScores
    topScores = {1:(0, None), 2:(0, None), 3:(0, None), 4:(0, None)}
    
    work = queue.Queue()
    
    # Create 4 threads for processing the data
    for i in range(4):
        t = threading.Thread(target=compChooseWord_thread, args=(work, hand, n))
        t.daemon = True
        t.start()
        
    # For each word in the wordList
    for word in wordList:
        work.put(word)
    # call join() to make sure all the work has been processed
    work.join()
    # return the best word you found.
    
    defaultDiff = [1,2,2,2,3,3,3,3,4,4]
    
    # Initially set the return result to None        
    result = None
    # Loop the choice until a result is returned (in case top N choices didn't
    # provide a usable word)
    while result == None:
        #if the top result is None, return None
        if topScores[1][1] == None:
            return None
        # otherwise, set the result to a random choice of the topScores based
        # on the defaultDiff distribution (work on math for this later)
        else: 
            result = topScores[random.choice(defaultDiff)][1]
    return result

#
# Computer plays a hand
#
def compPlayHand(hand, wordList, n):
    """
    Allows the computer to play the given hand, following the same procedure
    as playHand, except instead of the user choosing a word, the computer 
    chooses it.

    1) The hand is displayed.
    2) The computer chooses a word.
    3) After every valid word: the word and the score for that word is 
    displayed, the remaining letters in the hand are displayed, and the 
    computer chooses another word.
    4)  The sum of the word scores is displayed when the hand finishes.
    5)  The hand finishes when the computer has exhausted its possible
    choices (i.e. compChooseWord returns None).
 
    hand: dictionary (string -> int)
    wordList: list (string)
    n: integer (HAND_SIZE; i.e., hand size required for additional points)
    """
    # Keep track of the total score
    totalScore = 0
    # As long as there are still letters left in the hand:
    while (calculateHandlen(hand) > 0) :
        # Display the hand
        print("Current Hand: ", end=' ')
        displayHand(hand)
        print()
        # computer's word
        word = compChooseWord(hand, wordList, calculateHandlen(hand))
        # If the input is a single period:
        if word == None:
            # End the game (break out of the loop)
            break
            
        # Otherwise (the input is not a single period):
        else :
            # If the word is not valid:
            if (not isValidWord(word, hand, wordList)) :
                print('This is a terrible error! I need to check my own code!')
                break
            # Otherwise (the word is valid):
            else :
                # Tell the user how many points the word earned, and the updated total score 
                score = getWordScore(word, calculateHandlen(hand))
                totalScore += score
                print('"' + word + '" earned ' + str(score) + ' points. Total: ' + str(totalScore) + ' points')              
                # Update hand and show the updated hand to the user
                hand = updateHand(hand, word)
                print()
    # Game is over (user entered a '.' or ran out of letters), so tell user the total score
    if calculateHandlen(hand) > 0:
        print("I give up!")
    else:
        print("Game over!")
    print('Total score: ' + str(totalScore) + ' points.')

    
#
# Problem #6: Playing a game
#
#
def playGame(wordList, HAND_SIZE):
    """
    Allow the user to play an arbitrary number of hands.
 
    1) Asks the user to input 'n' or 'r' or 'x'.
        * If the user inputs 'x', immediately exit the game.
        * If the user inputs anything that's not 'n', 'r', or 'x', keep asking them again.

    2) Asks the user to input a 'u' or a 'c'.
        * If the user inputs anything that's not 'c' or 'u', keep asking them again.

    3) Switch functionality based on the above choices:
        * If the user inputted 'n', play a new (random) hand.
        * Else, if the user inputted 'r', play the last hand again.
      
        * If the user inputted 'u', let the user play the game
          with the selected hand, using playHand.
        * If the user inputted 'c', let the computer play the 
          game with the selected hand, using compPlayHand.

    4) After the computer or user has played the hand, repeat from step 1

    wordList: list (string)
    """

    while True:
        print()
        userInput = input("Enter 'n' to deal a new hand, 'r' to replay the last hand, or 'x' to end game: ")
        if userInput == 'n':
            hand = dealHand(wordList, HAND_SIZE)
            while True:
                print()
                userInputSub = input("Enter 'u' to have yourself play, 'c' to have the computer play: ")
                if userInputSub == 'u':
                    playHand(hand, wordList, HAND_SIZE)
                    break
                elif userInputSub == 'c':
                    compPlayHand(hand, wordList, HAND_SIZE)
                    break
                else: print("Invalid Command")
        elif userInput == 'r':
            if 'hand' in locals():
                while True:
                    print()
                    userInputSub = input("Enter 'u' to have yourself play, 'c' to have the computer play: ")
                    if userInputSub == 'u':
                        playHand(hand, wordList, HAND_SIZE)
                        break
                    elif userInputSub == 'c':
                        compPlayHand(hand, wordList, HAND_SIZE)
                        break
                    else: 
                        print()
                        print("Invalid Command")
            else:
                print()                
                print("You have not played a hand yet. Please play a new hand first!")
        elif userInput == 'x':
            break
        else: 
            print()
            print("Invalid Command.")

def welcome():
    """
    Welcomes the player, brief intro to the game, and returns hand size as integer
    ranging from 4 to 9
    """
    version = '0.1'
    m01 = "Welcome to the MIT 6.00.1x Wordgame (etherwar's mod)"
    m02 = "Build " + version
    m03 = "The Game: "
    m04 = "First, you must select a word length. Word of 4 characters to 8 characters long are supported."
    m05 = "A word of that length will then be scrambled and presented for you to guess. You may guess any " + \
            "word that you can make with any number of the letters given to you. Words are scored using Scrabble(tm)" + \
            "letter values. You get a bonus of 50 points for using all the letters remaining in your hand"
    m06 = "We give you the option to play the game yourself, or to let the computer play the hand."
    m07 = "We recommend that you play the game as yourself first, then enter 'r' to see how your " + \
            "play stacks up against the computer!"
    m08 = "Let's get started!"
    nL = "\n\n"
    defaultWidth = 70
    wrapper = textwrap.TextWrapper(width=defaultWidth)    
    print("{:^80}".format(textwrap.fill(m01, defaultWidth)), end=nL)
    print("{:>80}".format(textwrap.fill(m02, defaultWidth)), end=nL)
    print(wrapper.fill(m03), end=nL)
    print(wrapper.fill(m04), end=nL)
    print(wrapper.fill(m05), end=nL)
    print(wrapper.fill(m06), end=nL)
    print(wrapper.fill(m07), end=nL)
    print(wrapper.fill(m08), end=nL)
    try:  
        userInput = 3
        while int(userInput) < 4 or int(userInput) > 8:
            print()
            userInput = input("How many letters would you like to be dealt? (4-8): ")
            if  4 <= int(userInput) <= 8:
                HAND_SIZE = int(userInput)
            else:
                print("Invalid number. Please select a number from 4 to 8.")
    except:
        HAND_SIZE = 6
        print("Invalid input. Default hand size selected (6).")
    
    return HAND_SIZE
#
# Build data structures used for entire session and play game
#
if __name__ == '__main__':
    HAND_SIZE = welcome()
    wordList = loadWords(HAND_SIZE)
    playGame(wordList, HAND_SIZE)
