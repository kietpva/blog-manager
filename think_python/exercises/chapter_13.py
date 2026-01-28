import shelve


# Exercise 13.10.2
def replace_all(old, new, source_path, dest_path):
    with open(source_path) as reader:
        text = reader.read()

    text = text.replace(old, new)

    with open(dest_path, "w") as writer:
        writer.write(text)


replace_all("photos", "images", "data/notes.txt", "data/new_notes.txt")


# Exercise 13.10.3
def add_word(word, shelf):
    key = "".join(sorted(word))

    if key not in shelf:
        shelf[key] = [word]
    else:
        shelf[key].append(word)


with shelve.open("data/anagrams.db") as shelf:
    add_word("listen", shelf)
    add_word("silent", shelf)
    add_word("enlist", shelf)
