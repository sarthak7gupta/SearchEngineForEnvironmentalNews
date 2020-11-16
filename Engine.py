from collections import Counter, defaultdict
from math import log, sqrt
from typing import List, Set

from symspellpy import SymSpell

from config import min_scores, num_champs, term_idf_thresh
from inverted_index import InvertedIndex
from mappings import Doc_DocID_Mapping, File_FileID_Mapping
from preprocessing import preprocess
from utils import doc_id_type, rank_scores_threshold, read_file


class Engine:
	def __init__(self, filenames: List[str]) -> InvertedIndex:
		self.inverted_index = InvertedIndex()
		self.fileid_mapping = File_FileID_Mapping(filenames)
		self.docid_mapping = Doc_DocID_Mapping()
		self.sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)

		self.doc_count: int = 0

		for filename in filenames:

			for row_number, row in enumerate(read_file(filename)):
				doc = preprocess(row["Snippet"]).split()
				metadata = row
				file_id = self.fileid_mapping.get_file_id(filename)
				doc_id = f"{file_id}_{row_number}"
				self.doc_count += 1
				self.docid_mapping.add_doc(doc_id, file_id, row_number, metadata)

				for term in doc:
					self.inverted_index.add_entry(term, doc_id)

		self.inverted_index.populate_tfidf(self.doc_count)
		self.inverted_index.populate_champion_list(num_champs)

		self.all_terms: set = self.inverted_index.get_terms()

		self.load_symspell()

	def ranked_retrieval(self, query: List[str]) -> List[doc_id_type]:
		if not any(term in self.all_terms for term in query):
			return []

		scores = defaultdict(float)
		square_query_magnitude = 0

		query_term_counter = Counter(query)

		top_docs = self.get_top_docs(set(query_term_counter.keys()))

		for tq, tf_tq in query_term_counter.items():
			tf_tq = 1 + log(tf_tq)
			tfidf_tq = tf_tq * self.inverted_index.get_idf(tq)
			square_query_magnitude += tfidf_tq ** 2

			for doc_id, doc_id_stats in self.inverted_index.get_posting_list(
				tq
			).items():
				if doc_id in top_docs:
					scores[doc_id] += doc_id_stats.tfidf * tfidf_tq

		query_magnitude = sqrt(square_query_magnitude)

		for doc_id in scores:
			scores[doc_id] /= query_magnitude

		return rank_scores_threshold(scores, thresh=0.25)

	def get_top_docs(
		self,
		query_terms: set,
		term_idf_thresh: float = term_idf_thresh,
		min_scores: int = min_scores
	) -> Set[doc_id_type]:
		top_docs = set()

		while len(top_docs) < min_scores and term_idf_thresh > 0:
			for term in query_terms:
				if self.inverted_index.get_idf(term) > term_idf_thresh:
					top_docs |= self.inverted_index.get_champion_list(term)
			term_idf_thresh -= 0.25

		return top_docs

	def load_symspell(self) -> None:
		freq_dict = {term: self.inverted_index.get_term_count(term) for term in self.all_terms}

		with open("freq.dict", "w") as f:
			for term, freq in freq_dict.items():
				f.write(f"{term} {freq}\n")

		self.sym_spell.load_dictionary("freq.dict", 0, 1)

	def spell_check(self, query: str) -> str:
		return self.sym_spell.lookup_compound(query, max_edit_distance=2)[0].term

	def query(self, query: str):
		query = preprocess(query)

		q = self.spell_check(query)

		if q != query:
			print(f"Did You Mean `{q}`?")

		top_doc_ids = self.ranked_retrieval(q.split())

		results = []

		for doc_id in top_doc_ids:
			top_doc = self.docid_mapping.get_doc(doc_id)
			result = top_doc.metadata
			result["csv_file"] = self.fileid_mapping.get_file_name(top_doc.file_id)
			result["id"] = doc_id
			result["row_number"] = top_doc.row_number

			results.append(result)

		return results

	def __repr__(self) -> str:
		return f"""{{
	index: {self.inverted_index},
	file_mapping: {self.fileid_mapping},
	doc_mapping: {self.docid_mapping},
	doc_count: {self.doc_count},
	all_terms: {self.all_terms}
}}"""
