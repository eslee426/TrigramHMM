from count_freqs import Hmm
import sys
from collections import defaultdict
import math

"""
Takes in count file and training data - 
Produces new training data with infrequent words replaced with _RARE_
Output file: ner_train_rare.dat
"""

def replace_rare(file, infreq_words):
     with open(file, "r") as f:
        f2 = open("ner_train_rare.dat", "w")
        for line in f:
            parts = line.strip().split(" ")
            word = parts[0]
            if word in infreq_words:
                f2.write("_RARE_" + " " + parts[1] + "\n")
            else:
                f2.write(line)
        f2.close()


def usage():
    print """
    python add_rare.py [count_file] [training_data] 
    """

if __name__ == "__main__":

    if len(sys.argv)!=3: # Expects two argument: original count file and training data file
        usage()
        sys.exit(2)

    counter = Hmm(3)
    # finds count information for words in file
    (em_count, ngram_count, infreq_word_set, all_tags, all_words) = counter.read_counts(sys.argv[1])

    #produces new file with _RARE_
    replace_rare(sys.argv[2], infreq_word_set)      

