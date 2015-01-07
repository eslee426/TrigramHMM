from count_freqs import Hmm
import sys
from collections import defaultdict
import math

'''
calculates and prints emission parameters and puts data into a dictionary
'''

def word_counter(input_file):
	word_counts = defaultdict(int)
	infrequent_words = set()
	f = open(input_file, "r")
	line = f.readline()
	while line:
		word = line.replace("\n", "")
		if word in word_counts:
			word_counts[(word)] += 1
		else:
			word_counts[(word)] = 1
		line = f.readline()

	for word, count in word_counts.iteritems():
		if count < 5:
			infrequent_words.add(word)
	return infrequent_words


def emission_parameters(dev_data, em_count, ngram_count, tags, words, infreq_word):
	file2 = open("ner_dev_emissions.dat", "w")
	emission_prob = defaultdict(int)
	infreq_dev = word_counter(dev_data)

	with open(dev_data, "r") as f:
		for line in f:
			line = line.strip()
			if line != "":
				new_word = line.strip()

				# initialize variables
				tag_output = ""
				count_yx = -1.0

				# check if word is _RARE_
				if (new_word not in words):
					word = "_RARE_"
				elif (new_word in infreq_word):
					word = "_RARE_"
				#elif (new_word in infreq_dev):
				#	word = "_RARE_"
				else:
					word = new_word

				# Find arg max'
				for tag in tags:
					current = float(em_count[(word, tag)])
					count_y = float(ngram_count.get((tag,)))
					em = (current/count_y)
					#print "em_count", current, "count_y: ", count_y, "em: ", em
					if (em > count_yx):
						count_yx = em
						tag_output = tag

				#print "final em_count: ", count_yx
				# calculate emission probabiliy
				#count_y = ngram_count.get((tag_output,))
				#em = (count_yx)/float(count_y)	
				em_prob = math.log(count_yx)

				#add to dictionary
				emission_prob[(word, tag_output)] = count_yx

				# print output results
				file2.write(new_word + " " + tag_output + " " + str(em_prob) + "\n")
			else:
				file2.write("\n")
	file2.close()
	return emission_prob

''' 
calculates and prints log trigram probabilities
'''			
def trigram(ngram_count, sample_data):
	files2 = open("ner_dev_trigram.dat", "w")
	with open(sample_data, "r") as f:
		for line in f:
			line = line.strip()
			if line != "":
				parts = line.split()
				prob = trigram_prob(parts, ngram_count)
				if (prob != 0):
					log_prob = math.log(prob, 2)
				else: 
					log_prob = -float("inf")
				files2.write(parts[0] + " " + parts[1] + " " + parts[2] + " " + str(log_prob) + "\n")
			else:
				files2.write("\n")
	files2.close()

'''
calulates and returns the trigram probabilities
'''
def trigram_prob(trigram, ngram_count):
	ngram_tri = tuple(trigram[0:])
	ngram_bi = tuple(trigram[0:2])
	trigram_count = ngram_count[2][ngram_tri]
	bigram_count = ngram_count[1][ngram_bi]
	if (trigram_count != 0):
		tri_prob = float(trigram_count)/float(bigram_count)
	else: 
		tri_prob = 0
	return tri_prob




def usage():
	print """
	python named_entity_tagger.py [counts_rare_file] [dev_data_file] [original_counts] [sample_tag_seq_OPTIONAL]

	"""

if __name__ == "__main__":
	if len(sys.argv) < 4: # Expects atleast 3 arguments
		usage()
		sys.exit(2)
	try:
		input = file(sys.argv[1],"r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile %s.\n" % arg)
		sys.exit(1)

	# Initialize a trigram counter
	counter = Hmm(3)
	if (len(sys.argv) == 4):
		#to obtain original counts
		(em_count1, ngram_count1, infreq_word1, all_tags1, all_words1) = counter.read_counts(sys.argv[3])
		#to process new data
		(em_count, ngram_count, infreq_word, all_tags, all_words) = counter.read_counts(sys.argv[1])
		#to obtain emission prob
		emission_probabilities = emission_parameters(sys.argv[2], em_count, ngram_count[0], all_tags, all_words1, infreq_word1)
	else:
		#to process new data
		(em_count, ngram_count, infreq_word, all_tags, all_words) = counter.read_counts(sys.argv[1])
		#to obtain trigram prob from samplefile
		trigram(ngram_count, sys.argv[4])

