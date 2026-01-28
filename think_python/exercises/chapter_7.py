# Exercise 7.9.2
# Write a function named uses_none that takes a word and a string of forbidden letters,
# and returns True if the word does not use any of the forbidden letters.
# Here’s an outline of the function that includes two doctests.
# Fill in the function so it passes these tests, and add at least one more doctest.
def uses_none(word, forbidden):
    """Checks whether a word avoids forbidden letters.

    >>> uses_none('banana', 'xyz')
    True
    >>> uses_none('apple', 'efg')
    False
    >>> uses_none('hello', 'aeiou')
    False
    """
    for letter in word:
        if letter in forbidden:
            return False
    return True


print(uses_none("banana", "xyz"))
print(uses_none("apple", "efg"))
print(uses_none("hello", "aeiou"))


# Exercise 7.9.3
def uses_only(word, available):
    """Checks whether a word uses only the available letters.

    >>> uses_only('banana', 'ban')
    True
    >>> uses_only('apple', 'apl')
    False
    >>> uses_only('aaa', 'a')
    True
    """
    for letter in word:
        if letter not in available:
            return False
    return True


print(uses_only("banana", "ban"))
print(uses_only("apple", "apl"))
print(uses_only("aaa", "a"))


# Exercise 7.9.4
def uses_all(word, required):
    """Checks whether a word uses all required letters.

    >>> uses_all('banana', 'ban')
    True
    >>> uses_all('apple', 'api')
    False
    >>> uses_all('education', 'aeiou')
    True
    """
    for letter in required:
        if letter not in word:
            return False
    return True


print(uses_all("banana", "ban"))
print(uses_all("apple", "api"))
print(uses_all("education", "aeiou"))


# Exercise 7.9.5
def check_word(word, available, required):
    """Check whether a word is acceptable.

    >>> check_word('color', 'ACDLORT', 'R')
    True
    >>> check_word('ratatat', 'ACDLORT', 'R')
    True
    >>> check_word('rat', 'ACDLORT', 'R')
    False
    >>> check_word('told', 'ACDLORT', 'R')
    False
    >>> check_word('bee', 'ACDLORT', 'R')
    False
    """
    if len(word) < 4:
        return False
    if not uses_only(word.lower(), available.lower()):
        return False
    if required.lower() not in word.lower():
        return False
    return True


print(check_word("color", "ACDLORT", "R"))
print(check_word("ratatat", "ACDLORT", "R"))
print(check_word("rat", "ACDLORT", "R"))
print(check_word("told", "ACDLORT", "R"))
print(check_word("bee", "ACDLORT", "R"))


def word_score(word, available):
    """Compute the score for an acceptable word.

    >>> word_score('card', 'ACDLORT')
    1
    >>> word_score('color', 'ACDLORT')
    5
    >>> word_score('cartload', 'ACDLORT')
    15
    """
    if len(word) == 4:
        score = 1
    else:
        score = len(word)

    if uses_all(word.lower(), available.lower()):
        score += 7

    return score


print(word_score("card", "ACDLORT"))
print(word_score("color", "ACDLORT"))
print(word_score("cartload", "ACDLORT"))


## Exercise 7.9.6
def uses_any(word, letters):
    """Checks whether a word uses any of the given letters.

    >>> uses_any('banana', 'xyz')
    False
    >>> uses_any('apple', 'efg')
    True
    """
    for letter in word:
        if letter in letters:
            return True
    return False


def uses_none(word, forbidden):
    """Checks whether a word avoids forbidden letters.

    >>> uses_none('banana', 'xyz')
    True
    >>> uses_none('apple', 'efg')
    False
    >>> uses_none('', 'abc')
    True
    """
    return not uses_any(word, forbidden)


def uses_all(word, required):
    """Checks whether a word uses all required letters.

    >>> uses_all('banana', 'ban')
    True
    >>> uses_all('apple', 'api')
    False
    """
    return uses_only(required, word)
