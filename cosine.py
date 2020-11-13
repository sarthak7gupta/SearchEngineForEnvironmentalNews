from heapq import heapify, heappop, nlargest
import pickle
from collections import Counter, defaultdict
from math import log, sqrt
from typing import Iterable, Iterator, List, Tuple

from inverted_index import InvertedIndex
from preprocessing import preprocess


def generate_index_from_corpus(corpus: Iterable[str], doc_count: int) -> InvertedIndex:
	index = InvertedIndex()

	for docid, doc in enumerate(corpus, 1):
		doc = preprocess(doc)
		index.populate_document(doc, docid)
	index.populate_tfidf(doc_count)

	return index

def threshold_scores(scores: dict) -> dict:
	diff_thresh = 0.25
	
	scores = [(-score, doc_id) for doc_id, score in scores.items()]
	heapify(scores)

	thresh_scores = [heappop(scores)]
	while scores and (scores[0][0] - thresh_scores[-1][0] <= diff_thresh):
		thresh_scores.append(heappop(scores))

	return {doc_id: -score for score, doc_id in thresh_scores}

def cosine(index: InvertedIndex, query: str) -> dict:
	query = preprocess(query).split()
	scores = defaultdict(float)
	square_query_magnitude = 0

	for tq, tf_tq in Counter(query).items():
		tf_tq = 1 + log(tf_tq)
		tfidf_tq = tf_tq * index.get_idf(tq)
		square_query_magnitude += tfidf_tq ** 2
		posting_list_tq = index.get_posting_list(tq)
		for doc_id, doc_id_stats in posting_list_tq.items():
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
