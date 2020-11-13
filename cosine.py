from heapq import heapify, heappop, nlargest
import pickle
from collections import Counter, defaultdict
from math import log, sqrt
from typing import Iterable, Iterator, List, Tuple

from inverted_index import InvertedIndex
from preprocessing import preprocess

NUM_CHAMPS = 2
SCORE_DIFF_THRESH = 0.25
TERM_IDF_THRESH = 2 #2.5 means query terms in <22.3% of docs will be considered, 2 means <36.7%, 1.5 means <60.6%, 1 means <100% (all)

def generate_index_from_corpus(corpus: Iterable[str], doc_count: int) -> InvertedIndex:
	num_champs = NUM_CHAMPS
	
	index = InvertedIndex()

	for docid, doc in enumerate(corpus, 1):
		doc = preprocess(doc)
		index.populate_document(doc, docid)
	index.populate_tfidf(doc_count)

	index.populate_champion_lists(num_champs)

	return index

def threshold_scores(scores: dict) -> dict:
	diff_thresh = SCORE_DIFF_THRESH
	
	scores = [(-score, doc_id) for doc_id, score in scores.items()]
	heapify(scores)

	thresh_scores = [heappop(scores)]
	while scores and (scores[0][0] - thresh_scores[-1][0] <= diff_thresh):
		thresh_scores.append(heappop(scores))

	return {doc_id: -score for score, doc_id in thresh_scores}

def get_top_docs(index: InvertedIndex, query_terms: set) -> set:
	idf_thresh = TERM_IDF_THRESH
	
	docs = set()
	while not docs:
		for term in query_terms:
			if index.get_idf(term) > idf_thresh:
				docs |= index.get_champion_list(term)
		idf_thresh -=0.25

	return docs


def cosine(index: InvertedIndex, query: str) -> dict:
	query = preprocess(query).split()
	scores = defaultdict(float)
	square_query_magnitude = 0
	query_counts = Counter(query)

	top_docs = get_top_docs(index, set(query_counts.keys()))

	for tq, tf_tq in query_counts.items():
		tf_tq = 1 + log(tf_tq)
		tfidf_tq = tf_tq * index.get_idf(tq)
		square_query_magnitude += tfidf_tq ** 2
		posting_list_tq = index.get_posting_list(tq)
		for doc_id, doc_id_stats in posting_list_tq.items():
			if doc_id in top_docs:
				tfidf_doc_id = doc_id_stats.tf_idf
				scores[doc_id] += (tfidf_doc_id * tfidf_tq)

	query_magnitude = sqrt(square_query_magnitude)

	for doc_id in scores:
		scores[doc_id] /= query_magnitude

	return threshold_scores(scores)
	#scores = [(score, doc_id) for doc_id, score in scores.items()]
	#return nlargest(3, scores)


def read_corpus(filenames: List[str]) -> Iterator[str]:
	for filename in filenames:
		yield filename


if __name__ == "__main__":
	corpus = ["brutus killed caesar brutus", "caesar calpurnia", "brutus friend john"]

	doc_iterator = read_corpus(corpus)

	index = generate_index_from_corpus(doc_iterator, len(corpus))

	with open("index.pickle", "wb") as f:
		pickle.dump(index, f)

	print(cosine(index, "brutus"))
