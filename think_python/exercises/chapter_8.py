import re


# Exercise 8.12.2
def head(infile, n, outfile=None):
    """Reads the first n lines of a file.

    If outfile is None, prints the lines.
    Otherwise, writes them to outfile.

    >>> head('test.txt', 2)
    line1
    line2
    >>> head('test.txt', 1, 'out.txt')
    """
    fin = open(infile)

    if outfile is None:
        count = 0
        for line in fin:
            if count >= n:
                break
            print(line.rstrip())
            count += 1
    else:
        fout = open(outfile, "w")
        count = 0
        for line in fin:
            if count >= n:
                break
            fout.write(line)
            count += 1
        fout.close()

    fin.close()


head("data/data.txt", 5)
head("data/data.txt", 3, "data/output.txt")


# Exercise 8.12.3
def uses_any(word, letters):
    """Checks whether a word uses any of the given letters."""
    for char in word:
        if char in letters:
            return True
    return False


def check_word(word):
    """
    Checks whether a word could be the Wordle target word
    given the guesses SPADE and CLERK.
    """
    if len(word) != 5:
        return False

    word = word.lower()

    forbidden = "spadclrk"
    if uses_any(word, forbidden):
        return False

    if "e" not in word:
        return False

    if word[4] == "e":
        return False
    if word[2] == "e":
        return False

    return True


print(check_word("money"))  # True
print(check_word("never"))  # False
print(check_word("evoke"))  # False


# Exercise 8.12.4
def check_word(word):
    if len(word) != 5:
        return False

    word = word.lower()

    forbidden = "spadclrkto"
    if uses_any(word, forbidden):
        return False

    if "e" not in word:
        return False

    if word[2] == "e":
        return False
    if word[3] == "e":
        return False
    if word[4] == "e":
        return False

    if word[4] != "m":
        return False

    return True


print(check_word("enemy"))  # False
print(check_word("genum"))  # True
print(check_word("venom"))  # False


# Exercise 8.12.5
pattern = re.compile(r"\b(pale|pales|paled|paleness|pallor)\b", re.IGNORECASE)

count = 0

for line in open("data/montecristo.txt"):
    if pattern.search(line):
        count += 1

print(count)
