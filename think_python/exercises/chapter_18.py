# Exercise 18.11.2
def uses_none(word, forbidden):
    return set(word.lower()) & set(forbidden.lower()) == set()


print(uses_none("Hello", "xyz"))  # True
print(uses_none("Hello", "aeiou"))  # False
print(uses_none("Python", "AEIOU"))  # True


# Exercise 18.11.3
def can_spell(letters, word):
    letter_counts = {}

    for ch in letters.lower():
        letter_counts[ch] = letter_counts.get(ch, 0) + 1

    for ch in word.lower():
        if letter_counts.get(ch, 0) == 0:
            return False
        letter_counts[ch] -= 1

    return True


print(can_spell("TABLE", "BELT"))  # True
print(can_spell("TABLE", "LATE"))  # True
print(can_spell("TABLE", "BEET"))  # False
print(can_spell("MISSISSIPPI", "MISS"))  # True
print(can_spell("MISSISSIPPI", "MISSISSIPPII"))  # False
