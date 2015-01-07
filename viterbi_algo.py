from count_freqs import Hmm
import named_entity_tagger
import sys
from collections import defaultdict
import math

class Viterbi(object):
	def __init__(self, n=3):
		self.n = n
		self.emission_counts = defaultdict(int)
		self.ngram = [defaultdict(int) for i in xrange(self.n)]
		self.all_tags = set()
		self.all_words = defaultdict(int)
		self.infreq = set()
		self.pi_total = dict([((0, '*', '*'), 1)])
		self.word_tags = defaultdict(list)
		self.tag_count = defaultdict(int)
		
	# initiazes words given corpus file
	def read_counts(self, corpusfile, dev_data):
		for line in open(corpusfile, "r"):
			parts = line.strip().split(" ")
			count = int(parts[0])

			if parts[1] == "WORDTAG":
				ne_tag = parts[2]
				word = parts[3]
				self.all_words[(word)] += count
				self.emission_counts[(word, ne_tag)] = count
				self.all_tags.add(ne_tag)
				self.word_tags[word].append(ne_tag)
				self.tag_count[ne_tag] += self.emission_counts[(word, ne_tag)]
			elif parts[1].endswith("GRAM"):
				n = int(parts[1].replace("-GRAM",""))
				ngram_word = tuple(parts[2:])
				self.ngram[n-1][ngram_word] = count

		for word, count in self.all_words.iteritems():
			if count < 5:
				self.infreq.add(word)
		#added to consider the cases of *
		self.word_tags["*"].append("*")

	# calculates the emissions for given tag and word
	def em_prob(self, word, tag):
		if word == "*" and tag == "*":
			return 1
		elif self.tag_count[tag] == 0:
			return 0
		else:
			return self.emission_counts[(word, tag)]/float(self.tag_count[tag])

	# calculates the trigram estimate
	def trigram_calc(self, w, u, v):
		tri = self.ngram[2][w, u, v]
		bi = float(self.ngram[1][w, u])
		if bi == 0 or tri == 0:
			return 0
		else: 
			return tri/bi

	#calculates each pi variable and stores it in pi dict
	def pi_calc(self, n, u, v, sent):
		tags = self.possible_tags(n-2)
		word = sent[n]
		if (n == 0) and (u == "*") and (v == "*"):
			return 1
		elif (n, u, v) in self.pi_total: # checks if it is already in pi dict
			return self.pi_total[(n, u, v)]
		else: 
			max_prob = -float('inf')
			for t in tags:
				tri_prob = self.trigram_calc(t, u, v)
				em_calc = self.em_prob(word, v)
				if tri_prob == 0 or em_calc == 0: # if either is 0 no need to calculate
					continue
				else: 
					curr_prob = self.pi_calc(n-1, t, u, sent) * tri_prob * em_calc
					if curr_prob > max_prob:
						max_prob = curr_prob
			# adds pi to dictionary
			self.pi_total[(n, u, v)] = max_prob
			return max_prob

	# calculates backpointer tag and returns tag 
	def bp(self, k, u, v, sentence):
		tags = self.possible_tags(k-2)
		word = sentence[k]
		max_prob = -float('inf')
		best_tag = ""
		for w in tags:
			tri_prob = self.trigram_calc(w, u, v)
			em_calc = self.em_prob(word, v)
			prob = self.pi_calc(k-1, w, u, sentence) * tri_prob * em_calc
			if prob > max_prob:
				max_prob = prob
				best_tag = w
		return best_tag

	# returns a list of all possible tags
	def possible_tags(self, index):
		if (index == -1) or (index == 0):
			return ["*"]
		else:
			return self.all_tags

	#implements viterbi algorithm
	def viterbi_algorithm(self, sent):
		# adjusts length for the * put in earlier
		n = len(sent)-2
		pi = {(0,'*','*'):1}
		max_prob = 0
		u_tag = ""
		v_tag = ""

		for k in range(1, n+1):
			S2 = self.possible_tags(k-2)
			S1 = self.possible_tags(k-1)
			S0 = self.possible_tags(k)

			for u in S1:
				for v in S0:
					#calculating the pi and bp values to find max
					for w in S2:
						self.pi_calc(k, u, v, sent)
						prob = self.pi_total[(k, u, v)]

		# calculating STOP case
		N1 = self.possible_tags(n-1)
		N0 = self.possible_tags(n)
		max_prob2 = -float('inf')
		tag_n0 = ""
		tag_n1 = ""
		
		for u_tag in N1:
			for v_tag in N0:
				p = self.pi_total[(n, u_tag, v_tag)]
				t = self.trigram_calc(u_tag, v_tag, "STOP")
				curr_prob = self.pi_total[n, u_tag, v_tag] * t
				if curr_prob > max_prob2:
					max_prob2 = curr_prob
					tag_n1 = u_tag
					tag_n0 = v_tag

		# finds best tag for word considering the pi prob
		tags = {n-1: tag_n1, n: tag_n0, 0:"*"}
		for k in range(n-2, 0, -1):
			tags[k] = self.bp(k+2, tags[k+1], tags[k+2], sent)
		return tags

	# Function that writes out file with most likely tag and it's log probability
	def write_viterbi(self, input_file, output_file):
		out_file = open(output_file, "w")
		orig_sent = ["*"]
		sent = ["*"]
		with open(input_file, "r") as f:
			for line in f:
				word = line.strip()
				if word != "":
					orig_sent.append(word)
					if (word not in self.all_words) or (word in self.infreq):
						sent.append("_RARE_")
					else: 
						sent.append(word)
				else:
					orig_sent.append("*")
					sent.append("*")
					tags = self.viterbi_algorithm(sent)
					for k in range(1, len(sent) - 1):
						argmax = self.pi_total[k, tags[k-1], tags[k]]
						prob = math.log(argmax)
						out_file.write(orig_sent[k] + " " + tags[k] + " " + str(prob) + "\n")
					out_file.write("\n")
					self.pi_total.clear()
					orig_sent = ["*"]
					sent = ["*"]
		out_file.close()

def usage():
	print """
	python named_entity_tagger.py [counts_rare_file] [dev_data_file] [out_file]

	"""
if __name__ == "__main__":
	if len(sys.argv) != 4: # Expects atleast 3 arguments
		usage()
		sys.exit(2)
	try:
		input = file(sys.argv[1],"r")
	except IOError:
		sys.stderr.write("ERROR: Cannot read inputfile %s.\n" % arg)
		sys.exit(1)

	vit = Viterbi(3)
	vit.read_counts(sys.argv[1], sys.argv[2])
	vit.write_viterbi(sys.argv[2], sys.argv[3])




