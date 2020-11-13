import heapq
import pickle
from collections import defaultdict
from math import sqrt
from typing import Counter, Iterable, Iterator, List

import lorem

from inverted_index import InvertedIndex
from preprocessing import preprocess


def generate_index_from_corpus(corpus: Iterable[str], doc_count: int) -> InvertedIndex:
	index = InvertedIndex()

	for docid, doc in enumerate(corpus, 1):
		doc = preprocess(doc)
		index.populate_document(doc, docid)
	index.populate_tfidf(doc_count)

	return index


def cosine(index: InvertedIndex, doc_count: int, query: str):
	query = preprocess(query).split()
	scores = defaultdict(float)
	square_document_magnitudes = defaultdict(float)
	square_query_magnitude = 0

	for tq, tf_tq in Counter(query).items():
		tfidf_tq = tf_tq * index.get_idf(tq)
		square_query_magnitude += tfidf_tq ** 2
		posting_list_tq = index.get_posting_list(tq)
		for doc_id, doc_id_stats in posting_list_tq.items():
			tfidf_doc_id = doc_id_stats.tf_idf
			scores[doc_id] += (tfidf_doc_id * tfidf_tq)
			square_document_magnitudes[doc_id] += (tfidf_doc_id ** 2)

	query_magnitude = sqrt(square_query_magnitude)

	print(query, scores, square_document_magnitudes, square_query_magnitude, query_magnitude, sep='\n\n!')

	for doc_id in scores:
		scores[doc_id] /= (query_magnitude * sqrt(square_document_magnitudes[doc_id]))

	scores = [(score, doc_id) for doc_id, score in scores.items()]

	heapq.heapify(scores)

	return heapq.nlargest(3, scores)


def read_corpus(filenames: List[str]) -> Iterator[str]:
	for filename in filenames:
		yield filename


if __name__ == "__main__":
	corpus = [lorem.sentence() for _ in range(10)]
	# corpus = ["brutus killed caesar brutus", "caesar calpurnia", "brutus friend john"]

	doc_iterator = read_corpus(corpus)

	index = generate_index_from_corpus(doc_iterator, len(corpus))

	# print(index)

	with open("index.pickle", "wb") as f:
		pickle.dump(index, f)

	print(cosine(index, len(corpus), "ipsum"))
