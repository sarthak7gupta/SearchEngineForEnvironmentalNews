import re
from string import punctuation
from typing import List

from pycontractions import Contractions
from spacy.lang.en import English
# from spellchecker import SpellChecker

nlp = English()
# spell = SpellChecker()


def clean_text(text: str) -> str:
	text = text.lower()

	text = re.sub(r"\s+", " ", text)

	text = "".join(filter(lambda x: x not in punctuation, text))

	# text = "".join(filter(lambda x: not x.isdigit(), text))

	return text


def expand_contractions(text: str) -> str:
	return contractions.fix(text)


def remove_stop_words(text: str) -> str:
	doc = nlp(text)

	return " ".join(token.text for token in doc if not nlp.vocab[token.text].is_stop)


def lemmatise(text: str) -> str:
	doc = nlp(text)

	return " ".join(token.lemma_ for token in doc)


def preprocess(text: str) -> List[str]:
	text = clean_text(text)
	text = expand_contractions(text)
	text = remove_stop_words(text)
	text = lemmatise(text)

	return text


if __name__ == "__main__":
	text = """"He determined to drop his	123 litigation with the monastry,and
relinguish his claims to the wood-cuting and fishery rihgts at once. He
was the more ready to do this becuase the rights had become much less
valuable, and he had indeed the vaguest idea where the wood and river
in question were."""

	print(preprocess(text))
