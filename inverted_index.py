from collections import defaultdict
from math import log
from time import time
from typing import Union

# from sklearn.feature_extraction.text import TfidfVectorizer


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

	def calc_idf(self, term: str, doc_count: int) -> None:
		if term in self.__indexDictionary:
			self.__indexDictionary[term].idf = log(doc_count / self.get_doc_freq(term)) + 1

	def calc_tf_and_tfidf(self, term: str, doc_id: str) -> None:
		if term in self.__indexDictionary and doc_id in self.__indexDictionary[term].posting_list:
			tf = log(self.get_tf(term, doc_id)) + 1
			self.__indexDictionary[term].posting_list[doc_id].tf_idf = tf * self.get_idf(term)

	def populate_tfidf(self, doc_count: int) -> None:
		for term in self.__indexDictionary:
			self.calc_idf(term, doc_count)
			for doc_id in self.__indexDictionary[term].posting_list:
				self.calc_tf_and_tfidf(term, doc_id)

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
