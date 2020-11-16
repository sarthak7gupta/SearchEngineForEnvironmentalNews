from __future__ import annotations

from collections import defaultdict
from math import log
import heapq

from typing import Dict

from config import num_champs
from utils import doc_id_type


class DocEntry:
	def __init__(self):
		self.tf_idf: float = 0.0
		self.tf: float = 0

	def __repr__(self) -> str:
		return f"{{tf_idf: {self.tf_idf}, tf: {self.tf}}}"


class TermEntry:
	def __init__(self):
		self.idf: float = 0.0
		self.posting_list: Dict[doc_id_type, DocEntry] = defaultdict(DocEntry)
		self.champ_list: set = set()
		self.term_count: int = 0

	def add_doc(self, doc_id: doc_id_type):
		self.posting_list[doc_id].tf += 1
		self.term_count += 1

	def __repr__(self) -> str:
		return f"{{idf: {self.idf}, posting_list: {self.posting_list}, " +\
			f"champion_list: {self.champ_list}, term_count: {self.term_count}}}"


class InvertedIndex:
	def __init__(self):
		self.index: Dict[str, TermEntry] = defaultdict(TermEntry)

	def add_entry(self, term: str, doc_id: doc_id_type) -> None:
		self.index[term].add_doc(doc_id)

	def get_terms(self) -> set:
		return set(self.index.keys())

	def get_posting_list(self, term: str) -> Dict[doc_id_type, DocEntry]:
		return self.index[term].posting_list

	def get_champion_list(self, term: str) -> set:
		return self.index[term].champ_list

	def get_term_count(self, term: str) -> int:
		return self.index[term].term_count

	def get_doc_freq(self, term: str) -> int:
		return len(self.index[term].posting_list)

	def get_idf(self, term: str) -> float:
		return self.index[term].idf

	def get_tf(self, term: str, doc_id: doc_id_type) -> int:
		return self.index[term].posting_list[doc_id].tf

	def set_tf(self, term: str, doc_id: doc_id_type, tf: float) -> None:
		self.index[term].posting_list[doc_id].tf = tf

	def get_tfidf(self, term: str, doc_id: doc_id_type) -> float:
		return self.index[term].posting_list[doc_id].tf_idf

	def set_tfidf(self, term: str, doc_id: doc_id_type, tfidf: float) -> None:
		self.index[term].posting_list[doc_id].tf_idf = tfidf

	def calculate_idf(self, term: str, doc_count: int) -> None:
		self.index[term].idf = log(doc_count / self.get_doc_freq(term)) + 1

	def calculate_tf_and_tfidf(self, term: str, doc_id: doc_id_type) -> None:
		tf = log(self.get_tf(term, doc_id)) + 1
		self.set_tf(term, doc_id, tf)
		tfidf = tf * self.get_idf(term)
		self.set_tfidf(term, doc_id, tfidf)

	def populate_tfidf(self, doc_count: int) -> None:
		for term in self.index:
			self.calculate_idf(term, doc_count)
			for doc_id in self.index[term].posting_list:
				self.calculate_tf_and_tfidf(term, doc_id)

	def populate_champion_list(self, num_champs: int = num_champs) -> None:
		for term_entry in self.index.values():
			if len(term_entry.posting_list) < num_champs:
				term_entry.champ_list = set(term_entry.posting_list.keys())
			else:
				posting_list = [
					(doc_entry.tf_idf, doc_id)
					for doc_id, doc_entry in term_entry.posting_list.items()
				]
				champ_list = heapq.nlargest(num_champs, posting_list)
				term_entry.champ_list = {doc_id for _, doc_id in champ_list}

	def __repr__(self) -> str:
		return f"{self.index}"
