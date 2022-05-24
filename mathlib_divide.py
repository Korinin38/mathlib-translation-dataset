#!/usr/bin/python3
from collections import namedtuple

non_theorem_words = ["meta", "add_tactic_doc"]
theorem_words = ["lemma", "theorem", "def"]

Sentence = namedtuple("Sentence", [
    "data", # list of pairs (line, comment)
    "commented", # True if there is at least one comment
    "is_theorem", # True if meets conditions of being a theorem which are defined in label_sentences
    ])

def extract_sentences(matlib_filename):
    """Group lines in given file by sentences, keeping comments and proofs together, returning list of string lists."""
    with open(matlib_filename, "r") as src:
        single_sentences = []
        sentence = []
        commented = False
        proving = False
        for line in src.readlines():
            if "begin" in line:
                proving = True
            if "end" in line:
                proving = False
            if "/-" in line:
                commented = True
            if "-/" in line:
                commented = False
            if not commented and not proving and line == '\n':
                single_sentences.append(sentence)
                sentence = []
            else:
                sentence.append(line)
    return single_sentences


def label_sentences(single_sentences, whitelist=theorem_words, blacklist=non_theorem_words):
    """Process sentences by adding specific labels to them, i.e. if sentence is a theorem or if it has any comments.

    Args:
        single_sentences -- list of string lists
        whitelist -- words that are required for sentence to be a theorem
        blacklist -- words that are prohibited for theorems (i.e. 'tactic' is not a theorem)
    
    Returns:
        list of Sentence
    
    """
    sentences_labeled = []
    for sentence in single_sentences:
        resentence = []
        commented = False
        is_theorem = False
        squashed = ''.join(sentence)
        
        if any(nword in squashed for nword in blacklist):
            is_theorem = False
        elif (("begin" in squashed and "end" in squashed) or ":=" in squashed) and \
            any(lword + " " in squashed for lword in whitelist):
            is_theorem = True
        
        inside_comment = False
        pre_comment = ""
        for line in sentence:
            if line.strip()[:2] == "/-":
                commented = True
                inside_comment = True
            elif "--" in line:
                commented = True
                pre_comment += line
                continue
            
            if inside_comment:
                pre_comment += line
                if "-/" in line:
                     inside_comment = False
            else:
                resentence.append((line.strip(), pre_comment.strip()))
                pre_comment = ""
        if pre_comment != "":
            resentence.append(("", pre_comment.strip()))

        sentences_labeled.append(Sentence(resentence, commented, is_theorem))
    return sentences_labeled


def example(mathlib_filename):
    labeled = label_sentences(extract_sentences(mathlib_filename))
    with open("mathlib_divided.txt", "w") as f:
        for s in labeled:
            if s.is_theorem and s.commented:
                for line in s.data:
                    f.write(line[0] + " ♥ " + line[1] + "\n")


if __name__ == "__main__":
    # example("mathlib_full.txt")
    pass