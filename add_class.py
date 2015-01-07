from count_freqs import Hmm
import sys
import string
from collections import defaultdict
import math

"""
Takes in count file and training data - 
Produces new training data with infrequent words replaced with different classes = not just rare
Output file: ner_classes.dat
"""

def replace_class(file, infreq_words):
     with open(file, "r") as f:
        f2 = open("ner_train_classes.dat", "w")
        for line in f:
            parts = line.strip().split(" ")
            word = parts[0]
            #checks words on different classes - only check the infrequent words
            if word in infreq_words:
                if word.isupper():
                    f2.write("_UPPER_" + " " + parts[1] + "\n")
                elif word.isdigit():
                    f2.write("_DIGIT_" + " " + parts[1] + "\n")
                elif not word.isalpha():
                    f2.write("_NOTALPHA_" + " " + parts[1] + "\n")
                else:
                    f2.write("_RARE_" + " " + parts[1] + "\n")
            else:
                f2.write(line)
        f2.close()


def usage():
    print """
    python add_class.py [count_file] [training_data] 
    """

if __name__ == "__main__":

    if len(sys.argv)!=3: # Expects two argument: original count file and training data file
        usage()
        sys.exit(2)

    counter = Hmm(3)
    # finds count information for words in file
    (em_count, ngram_count, infreq_word_set, all_tags, all_words) = counter.read_counts(sys.argv[1])
    #produces new file with _RARE_
    replace_class(sys.argv[2], infreq_word_set)      
