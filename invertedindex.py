import math
import time
from sklearn.feature_extraction.text import TfidfVectorizer

'''
def union2(dict1, dict2):
    return dict(list(dict1.items()) + list(dict2.items()))
'''
def union2(list1, list2):
	return list1 + list2

class DocEntry:
	def __init__(self):
		self.tf_idf = None
		self.tf = 0

class TermEntry:
	def __init__(self):
		self.idf = None
		self.docFreq = 0
		self.postingList = dict()

	def addDoc(self, docID):
		if docID not in self.postingList:
			self.postingList[docID] = DocEntry()
			self.docFreq += 1
		self.postingList[docID].tf += 1

class InvertedIndex:
	def __init__(self):
		self.__indexDictionary = dict()

	def __addTerm(self,term):
		self.__indexDictionary[term] = TermEntry()

	def addEntry(self, term, docID):
		if term not in self.__indexDictionary:
			self.__addTerm(term)
		self.__indexDictionary[term].addDoc(docID)

	def getTerms(self):
		return list(self.__indexDictionary.keys())

	def getPostingList(self, term):
		if term in self.__indexDictionary:
			return list(self.__indexDictionary[term].postingList.keys())
		return None

	def getDocFreq(self, term):
		if term in self.__indexDictionary:
			return self.__indexDictionary[term].docFreq
		return None

	def getIDF(self, term):
		if term in self.__indexDictionary:
			return self.__indexDictionary[term].idf
		return None

	def getTF(self, term, docID):
		if term in self.__indexDictionary and docID in self.__indexDictionary[term].postingList:
				return self.__indexDictionary[term].postingList[docID].tf
		return None

	def getTFIDF(self,term,docID):
		if term in self.__indexDictionary and docID in self.__indexDictionary[term].postingList:
				return self.__indexDictionary[term].postingList[docID].tf_idf
		return None

	def calcIDF(self, term, numDocs):
		if term in self.__indexDictionary:
			self.__indexDictionary[term].idf = math.log(numDocs/self.getDocFreq(term)) + 1

	def calcTFIDF(self, term, docID):
		if term in self.__indexDictionary and docID in self.__indexDictionary[term].postingList:
				tf = math.log(self.getTF(term, docID)) + 1
				self.__indexDictionary[term].postingList[docID].tf_idf = tf * self.getIDF(term)

	def populateTFIDF(self, numDocs):
		for term in self.__indexDictionary:
			self.calcIDF(term, numDocs)
			for docID in self.__indexDictionary[term].postingList:
				self.calcTFIDF(term, docID)
'''
	def setTFIDF(self,term,docID,tfidf):
		if term not in self.__indexDictionary:
			return None 
		pl = self.__indexDictionary[term].postingList.list_dict
		if docID not in pl:
			return None 
		pl[docID].tf_idf = tfidf
		return tfidf
'''

corpus = [
	"brutus killed caesar brutus",
	"caesar calpurnia",
	"brutus friend john"
]

# LIBRARY TEST (comment lines 26&27)

start_time=time.time()

vectorizer = TfidfVectorizer(smooth_idf=False, sublinear_tf=True)
X = vectorizer.fit_transform(corpus)
print(vectorizer.idf_)

index = InvertedIndex()
index.addEntry('brutus',1)
index.addEntry('brutus',1)
index.addEntry('killed',1)
index.addEntry('caesar',1)
index.addEntry('caesar',2)
index.addEntry('calpurnia',2)
index.addEntry('brutus',3)
index.addEntry('friend',3)
index.addEntry('john',3)

print(time.time()-start_time)


# OWN TEST

start_time=time.time()

index = InvertedIndex()
index.addEntry('brutus',1)
index.addEntry('brutus',1)
index.addEntry('killed',1)
index.addEntry('caesar',1)
index.addEntry('caesar',2)
index.addEntry('calpurnia',2)
index.addEntry('brutus',3)
index.addEntry('friend',3)
index.addEntry('john',3)

index.populateTFIDF(3)

print(index.getIDF('brutus'))
print(index.getIDF('caesar'))
print(index.getIDF('calpurnia'))
print(index.getIDF('friend'))
print(index.getIDF('john'))
print(index.getIDF('killed'))

print(time.time()-start_time)


'''
#Printing result
print('USING INDEX: ')
#print(index.getTerms())
print("term      doc1                  doc2                  doc3")
print('{}    {}    {}    {}'.format('brutus',index.getTFIDF('brutus',1),index.getTFIDF('brutus',2),index.getTFIDF('brutus',3)))
print('{}    {}    {}    {}'.format('caesar',index.getTFIDF('caesar',1),index.getTFIDF('caesar',2),index.getTFIDF('caesar',3)))
print("\n")
'''