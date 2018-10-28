# Welcome to Wikipedia Bingo


### *The excitement of Wikipedia and the trepidations of Bingo combined into one game!*

### Goal 
Find all the words in a column or a row to get Bingo! and win the game!

### Rules 
* Type the name of a Wikipedia article which you think will contain some of the words on your Bingo grid.
* If it contains a word that is in the grid, good job! But be careful: Every occurance of the word in the article will be counted.
* If a word is found too many times during the game, the counter will overflow and the word will be replaced! Potentially ruining a nearly finished column or row.

How many wikipedia articles will you need to visit to get Bingo!?

**Note:** There are no losers... but there are winners. Will **you** be at the top of the leaderboard?


def scoring_algorithm(N, mode, grid):
    """
    Scores a player's performance
    
    Parameters
    ---------
    N : int
        number of wiki articles used to win
    mode : int
        Either 3, 5 or 7 for Easy, Medium and Hard 
    grid : int 
        Either 3, 5 or 7 for size of grid 3by3, 5by5 and 7by7
    """
    score = 0 
    if grid == 3:
        score += 2000
    elif grid == 5:
        score += 4000
    elif grid == 7: 
        score += 6000
        
    if mode == 3: 
        score += 4000
    elif mode == 5:
        score += 6000
    elif mode == 7:
        score += 8000
    
    return int(score/N)
