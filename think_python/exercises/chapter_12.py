# Exercise 12.12.2
import string


def process_word_trigram(word):
    # Convert to lowercase
    word = word.lower()

    # Remove punctuation
    word = word.strip(string.punctuation)

    # Skip empty words
    if word == "":
        return None

    return word


def count_trigram(filename):
    trigram_counts = {}
    prev1 = None
    prev2 = None

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            for word in line.split():
                word = process_word_trigram(word)

                if word is None:
                    continue

                if prev1 is not None and prev2 is not None:
                    trigram = (prev2, prev1, word)
                    trigram_counts[trigram] = trigram_counts.get(trigram, 0) + 1
                prev2 = prev1
                prev1 = word
    return trigram_counts


trigram_counts = count_trigram("data/jekyll_and_hyde.txt")

most_common = max(trigram_counts, key=trigram_counts.get)
print(most_common, trigram_counts[most_common])
