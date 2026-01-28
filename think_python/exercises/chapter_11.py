# Exercise 11.11.2
list0 = [1, 2, 3]
list1 = [4, 5]

t = (list0, list1)

t[1].append(6)

print(type(t))
print(t)  # ([1, 2, 3], [4, 5, 6])

# d = {t: "this tuple contains two lists"}

# Exercise 11.11.3
letters = "abcdefghijklmnopqrstuvwxyz"
numbers = range(len(letters))
letter_map = dict(zip(letters, numbers))


def shift_word(word, shift):
    result = []

    for ch in word:
        # get the index of a character
        index = letter_map[ch]
        # use modulo to cycle back
        new_index = (index + shift) % len(letters)
        # get the new letter
        result.append(letters[new_index])

    return "".join(result)


print(shift_word("cheer", 7))  # jolly
print(shift_word("melon", 16))  # cubed


# Exercise 11.11.4
def most_frequent_letters(s):
    freq = {}

    # Count the frequency of each character
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1

    # Sort by descending frequency
    for ch, count in sorted(freq.items(), key=lambda item: item[1], reverse=True):
        print(ch, count)


most_frequent_letters("banana")


# Exercise 11.11.5
def print_anagram_sets(word_list):
    anagram_map = {}

    for word in word_list:
        key = "".join(sorted(word))

        if key not in anagram_map:
            anagram_map[key] = []
        anagram_map[key].append(word)

    for words in anagram_map.values():
        if len(words) > 1:
            print(words)


words = [
    "deltas",
    "desalt",
    "lasted",
    "salted",
    "slated",
    "staled",
    "retainers",
    "ternaries",
    "generating",
    "greatening",
    "resmelts",
    "smelters",
    "termless",
]

print_anagram_sets(words)


# Exercise 11.11.6
def word_distance(word1, word2):
    count = 0

    for c1, c2 in zip(word1, word2):
        if c1 != c2:
            count += 1

    return count


print(word_distance("cheer", "jolly"))  # 5
print(word_distance("converse", "conserve"))  # 2


# Exercise 11.11.7
def find_metathesis_pairs(word_list):
    anagram_map = {}

    for word in word_list:
        key = "".join(sorted(word))
        anagram_map.setdefault(key, []).append(word)

    for words in anagram_map.values():
        if len(words) < 2:
            continue

        for i in range(len(words)):
            for j in range(i + 1, len(words)):
                w1 = words[i]
                w2 = words[j]

                diff = 0
                for c1, c2 in zip(w1, w2):
                    if c1 != c2:
                        diff += 1

                if diff == 2:
                    print(w1, w2)


words = [
    "converse",
    "conserve",
    "deltas",
    "desalt",
    "lasted",
    "evil",
    "vile",
    "veil",
    "live",
]

find_metathesis_pairs(words)
