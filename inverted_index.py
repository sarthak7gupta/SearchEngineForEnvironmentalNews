#from __future__ import annotations

from collections import defaultdict
from math import log, sqrt
from time import time
from typing import Union
import heapq

# from sklearn.feature_extraction.text import TfidfVectorizer
from preprocessing import preprocess


class DocEntry:
	def __init__(self):
		self.tf_idf: float = 0.0
		self.tf: int = 0

	def __repr__(self) -> str:
		return f"{{tf_idf:{self.tf_idf}, tf: {self.tf}}}"


class TermEntry:
	def __init__(self):
		self.idf: float = 0.0
		self.posting_list: dict = defaultdict(DocEntry)
		self.champ_list: set = set()

	def add_doc(self, doc_id: str):
		self.posting_list[doc_id].tf += 1

	def __repr__(self) -> str:
		return f"{{idf: {self.idf}, posting_list: {self.posting_list}}}"


class InvertedIndex:
	def __init__(self):
		self.__indexDictionary: dict = defaultdict(TermEntry)

	def add_entry(self, term, doc_id) -> None:
		self.__indexDictionary[term].add_doc(doc_id)

	def get_terms(self) -> set:
		return set(self.__indexDictionary.keys())

	def get_posting_list(self, term: str) -> Union[set, None]:
		if term in self.__indexDictionary:
			return self.__indexDictionary[term].posting_list

	def get_champion_list(self, term: str) -> Union[set, None]:
		if term in self.__indexDictionary:
			return self.__indexDictionary[term].champ_list

	def get_doc_freq(self, term: str) -> Union[int, None]:
		if term in self.__indexDictionary:
			return len(self.__indexDictionary[term].posting_list)

	def get_idf(self, term: str) -> Union[float, None]:
		if term in self.__indexDictionary:
			return self.__indexDictionary[term].idf

	def get_tf(self, term: str, doc_id: str) -> Union[int, None]:
		if term in self.__indexDictionary and doc_id in self.__indexDictionary[term].posting_list:
			return self.__indexDictionary[term].posting_list[doc_id].tf

	def get_tfidf(self, term: str, doc_id: str) -> Union[float, None]:
		if term in self.__indexDictionary and doc_id in self.__indexDictionary[term].posting_list:
			return self.__indexDictionary[term].posting_list[doc_id].tf_idf

	def set_tfidf(self, term: str, doc_id: str, tf_idf: float) -> None:
		if term in self.__indexDictionary and doc_id in self.__indexDictionary[term].posting_list:
			self.__indexDictionary[term].posting_list[doc_id].tf_idf = tf_idf

	def calc_idf(self, term: str, doc_count: int) -> None:
		if term in self.__indexDictionary:
			self.__indexDictionary[term].idf = log(doc_count / self.get_doc_freq(term)) + 1

	def calc_tf_and_tfidf(self, term: str, doc_id: str) -> None:
		if term in self.__indexDictionary and doc_id in self.__indexDictionary[term].posting_list:
			tf = log(self.get_tf(term, doc_id)) + 1
			tf_idf = tf * self.get_idf(term)
			self.__indexDictionary[term].posting_list[doc_id].tf_idf = tf_idf
			return tf_idf

	def populate_tfidf(self, doc_count: int) -> None:
		doc_magnitudes = defaultdict(float)
		for term in self.__indexDictionary:
			self.calc_idf(term, doc_count)
			for doc_id in self.__indexDictionary[term].posting_list:
				doc_magnitudes[doc_id] += (self.calc_tf_and_tfidf(term, doc_id))**2
		
		for doc_id in doc_magnitudes:
			doc_magnitudes[doc_id] = sqrt(doc_magnitudes[doc_id])
		
		for term in self.__indexDictionary:
			for doc_id in self.__indexDictionary[term].posting_list:
				self.set_tfidf(term, doc_id, self.get_tfidf(term, doc_id) / doc_magnitudes[doc_id])

	def populate_champion_lists(self, num_champs: int) -> None:
		for term in self.__indexDictionary:
			term_entry = self.__indexDictionary[term]
			if len(term_entry.posting_list) < num_champs:
				term_entry.champ_list = set(term_entry.posting_list.keys())
			else:
				posting_list = [(doc_entry.tf_idf, doc_id) for doc_id, doc_entry in term_entry.posting_list.items()]
				champ_list = heapq.nlargest(num_champs, posting_list)
				term_entry.champ_list = {doc_id for (tf_idf, doc_id) in champ_list}

	def populate_document(self, text: str, doc_id: str) -> None:
		for term in text.split():
			self.add_entry(term, doc_id)

	def __repr__(self) -> str:
		return f"{self.__indexDictionary}"


if __name__ == "__main__":
	corpus = ["brutus killed caesar brutus", "caesar calpurnia", "brutus friend john"]

	# # % SKL Test
	# start_time = time()

	# vectorizer = TfidfVectorizer(smooth_idf=False, sublinear_tf=True)
	# tfidf = vectorizer.fit_transform(corpus)

	# print(time() - start_time)

	# print([round(i, 8) for i in vectorizer.idf_])

	# % Own Test
	start_time = time()

	index = InvertedIndex()
	for doc_id, doc in enumerate(corpus, 1):
		index.populate_document(doc, doc_id)
	index.populate_tfidf(len(corpus))

	print(time() - start_time)

	print([round(index.get_idf(i), 8) for i in ["brutus", "caesar", "calpurnia", "friend", "john", "killed"]])
