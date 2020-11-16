from glob import glob

from config import data_dir, pickle_filename
from Engine import Engine
from utils import load_pickle, save_pickle


def build_engine(data_dir: str = data_dir) -> Engine:
	engine = Engine(sorted(glob(f"{data_dir}/*.csv")))

	save_pickle(engine, pickle_filename)

	return engine


def load_engine_from_pickle() -> Engine:
	return load_pickle(pickle_filename)
