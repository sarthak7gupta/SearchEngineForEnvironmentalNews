import csv
from glob import glob
from heapq import heapify, heappop
from pickle import dump, load
from typing import Any, Dict, Iterator, List

from config import data_dir, min_results, pickle_filename, score_diff_thresh
from Engine import Engine

doc_id_type = str


def read_file(filename: List[str]) -> Iterator[Dict]:
	yield from csv.DictReader(open(filename, encoding="utf-8-sig"))


def save_pickle(obj: Any, filename: str) -> None:
	with open(filename, "wb") as pickle_file:
		dump(obj, pickle_file)


def load_pickle(filename: str) -> Any:
	with open(filename, "rb") as pickle_file:
		return load(pickle_file)


def rank_scores_threshold(
	scores: Dict[doc_id_type, float], thresh: float = score_diff_thresh, min_results: int = min_results
) -> List[doc_id_type]:
	scores = [(-score, doc_id) for doc_id, score in scores.items()]
	heapify(scores)

	thresh_scores = [heappop(scores)]

	while scores and (scores[0][0] - thresh_scores[-1][0] <= thresh):
		thresh_scores.append(heappop(scores))

	num_thresh = len(thresh_scores)

	if num_thresh < min_results:
		thresh_scores += scores[:min_results - num_thresh]

	return [doc_id for _, doc_id in thresh_scores]


def build_engine(data_dir: str = data_dir) -> Engine:
	engine = Engine(sorted(glob(f"{data_dir}/*.csv")))

	save_pickle(engine, pickle_filename)

	return engine


def load_engine_from_pickle() -> Engine:
	return load_pickle(pickle_filename)
