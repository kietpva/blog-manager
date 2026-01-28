# Exercise 9.15.2
def is_anagram(word1, word2):
    """Checks whether two words are anagrams."""
    return sorted(word1) == sorted(word2)


print(is_anagram("tops", "stop"))  # True
print(is_anagram("takes", "steak"))  # True
print(is_anagram("takes", "stake"))  # True
print(is_anagram("takes", "task"))  # False


# Exercise 9.15.3
def is_palindrome(word):
    return word == "".join(reversed(word))


for line in open("data/words.txt"):
    word = line.strip()
    if len(word) >= 7 and is_palindrome(word):
        print(word)

print(is_palindrome("noon"))  # True
print(is_palindrome("rotator"))  # True
print(is_palindrome("python"))  # False


# Exercise 9.15.4
def reverse_sentence(sentence):
    words = sentence.split()[::-1]
    return (
        " ".join([words[0].capitalize()] + [w.lower() for w in words[1:]])
        if words
        else ""
    )


print(reverse_sentence("Reverse this sentence"))
# Sentence this reverse

print(reverse_sentence("HELLO world PYTHON"))
# Python world hello

print(reverse_sentence("one"))
# One
