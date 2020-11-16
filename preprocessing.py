import re
from string import punctuation
from typing import List
from urllib.parse import urlsplit

import contractions
from spacy.lang.en import English

nlp = English()


def clean_text(text: str) -> str:
	text = text.lower()

	text = re.sub(r"\s+", " ", text)

	text = "".join(filter(lambda x: x not in punctuation, text))

	text = text.strip()

	return text


def expand_contractions(text: str) -> str:
	return contractions.fix(text)


def remove_stop_words(text: str) -> str:
	doc = nlp(text)

	return " ".join(token.text for token in doc if not nlp.vocab[token.text].is_stop)


def lemmatise(text: str) -> str:
	doc = nlp(text)

	return " ".join(token.lemma_ for token in doc)


def clean_url(url: str) -> str:
	url = " ".join(urlsplit(url)[2:])

	url = "".join(char if not char.isdigit() and char not in punctuation else " " for char in url)

	url = re.sub(r"\s+", " ", url)

	return url


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
