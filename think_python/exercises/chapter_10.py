from collections import Counter


# Exercise 10.11.2
def value_counts(s):
    counts = {}
    for char in s:
        if char in counts:
            counts[char] += 1
        else:
            counts[char] = 1
    return counts


counter = value_counts("brontosaurus")

print(counter)


# Exercise 10.11.3
def has_duplicates(seq):
    """Returns True if there is any duplicate element in seq."""
    return len(seq) != len(set(seq))


print(has_duplicates("apple"))  # True (p duplicate)
print(has_duplicates("banana"))  # True (a, n duplicate)
print(has_duplicates("lamp"))  # False
print(has_duplicates([1, 2, 3]))  # False
print(has_duplicates([1, 2, 1]))  # True

longest = ""

for line in open("data/words.txt"):
    """"""
    word = line.strip()
    if not has_duplicates(word):
        if len(word) > len(longest):
            longest = word

print(longest, len(longest))


# Exercise 10.11.4
def find_repeats(counter):
    return [key for key, count in counter.items() if count > 1]


def value_counts(s):
    counts = {}
    for char in s:
        counts[char] = counts.get(char, 0) + 1
    return counts


counter = value_counts("mississippi")
print(counter)
print(find_repeats(counter))


# Exercuse 10.11.5
def add_counters(counter1, counter2):
    return dict(Counter(counter1) + Counter(counter2))


c1 = value_counts("brontosaurus")
c2 = value_counts("apatosaurus")

print(add_counters(c1, c2))
