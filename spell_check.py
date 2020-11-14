# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 23:36:18 2020

@author: Pranav Aditya
"""
from time import time
from typing import Union

from collections import defaultdict

class TermEntry:
	def __init__(self):
		self.tf_idf: float = 0.0
		self.tf: int = 0

	def __repr__(self) -> str:
		return f"{{tf_idf:{self.tf_idf}, tf: {self.tf}}}"


class PermEntry:
	def __init__(self):
		self.idf: float = 0.0
		self.posting_list: dict = defaultdict(TermEntry)
		self.champ_list: set = set()

	def add_term(self, term: str):
		self.posting_list[term].tf += 1

	def __repr__(self) -> str:
		return f"{{idf: {self.idf}, posting_list: {self.posting_list}}}"


class bigram_Index:
    def __init__(self):
        self.__indexDictionary: dict = defaultdict(PermEntry)

    def add_entry(self, perm, term) -> None:
        self.__indexDictionary[perm].add_term(term)

    

    def get_posting_list(self, perm: str) -> Union[set, None]:
        if perm in self.__indexDictionary:
            return self.__indexDictionary[perm].posting_list

    def query_sugessions(self,query):
        d={}
        for i in range(len(query)-1):
            pl=index.get_posting_list(query[i:i+2])
            if(pl):
                terms=pl.keys()
                for j in terms:
                    if(j not in d ):
                        d[j]=pl[j].tf
                    else:
                        d[j]=d[j]+pl[j].tf
            
        for w in sorted(d, key=d.get, reverse=True):
            return w
            
            
    def populate_bigram_Index(self,corpus):
        for  doc in corpus:
            for term in list(doc.split(" ")):
                for i in range(len(term)-1):
                    self.add_entry(term[i:i+2],term)
                    
                
        

	

    def __repr__(self) -> str:
        return f"{self.__indexDictionary}"



if __name__ == "__main__":
    corpus = ["Microsoft Word 97, 98, 2000, and 2001 include an undocumented feature that generates all of the sample text I need. Maybe you’ll find it helpful too. To use it, type the following line into a Word document and press the ENTER key", "I’m trying to learn more about some feature of Microsoft Word and don’t want to practice on a real document", " I’m creating a macro and need some text for testing purposes"]

    start_time = time()

    index = bigram_Index()
    index.populate_bigram_Index(corpus)
    
    query="docment"
    print(index.query_sugessions(query))
