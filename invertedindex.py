import math 

def union2(dict1, dict2):
    return dict(list(dict1.items()) + list(dict2.items()))

class Node:
	def __init__(self,docID):
		self.docID = docID
		self.tf_idf = None
		self.tf = 1

class PostingList:
	list_dict = dict()
	
	def __init__(self):
		self.list_dict = dict()
	
	def addEntry(self,docID):
		if docID not in self.list_dict:
			self.list_dict[docID] = Node(docID)
			return None
		else:
			self.list_dict[docID].tf += 1
			return "INCREASE"
	
class TermEntry:
	def __init__(self):
		self.docFreq  = 0
		self.postingList = PostingList()

	def addDoc(self,docID):
		if self.postingList.addEntry(docID) == None:
			self.docFreq += 1

class InvertedIndex:
	def __init__(self,numDocs):
		self.__indexDictionary = dict()
		self.numDocs = numDocs

	def __addTerm(self,term):
		self.__indexDictionary[term] = TermEntry()

	def addEntry(self,term,docID):
		if term not in self.__indexDictionary:
			self.__addTerm(term)
		self.__indexDictionary[term].addDoc(docID)

	def getPostingList(self,term):
		if term not in self.__indexDictionary:
			return None 
		return self.__indexDictionary[term].postingList.list_dict
	
	def getTerms(self):
		return list(self.__indexDictionary.keys())

	def getTF(self,term,docID):
		try:
			return self.__indexDictionary[term].postingList.list_dict[docID].tf
		except:
			return None

	def getDocFreq(self,term):
		try:
			return self.__indexDictionary[term].docFreq
		except:
			return None
	def getIDF(self,term):
		try:
			return math.log2(self.numDocs/self.__indexDictionary[term].docFreq)
		except:
			return None

	def calTFIDF(self,term,docID):
		if term not in self.__indexDictionary:
			return None 
		pl = self.__indexDictionary[term].postingList.list_dict
		if docID not in pl:
			return None 
		docFreq = self.__indexDictionary[term].docFreq
		tf = pl[docID].tf
		idf = math.log2(self.numDocs / docFreq )
		pl[docID].tf_idf = tf * idf
		return pl[docID].tf_idf

	def setTFIDF(self,term,docID,tfidf):
		if term not in self.__indexDictionary:
			return None 
		pl = self.__indexDictionary[term].postingList.list_dict
		if docID not in pl:
			return None 
		pl[docID].tf_idf = tfidf
		return tfidf

	def getTFIDF(self,term,docID):
		if term not in self.__indexDictionary:
			return None 
		pl = self.__indexDictionary[term].postingList.list_dict
		if docID not in pl:
			return None 
		return pl[docID].tf_idf
'''		
corpus = [
	"brutus killed caesar brutus",
	"caesar calpurnia",
	"brutus friend john"
]

index = InvertedIndex(3)
index.addEntry('brutus',1)
index.addEntry('brutus',1)
index.addEntry('killed',1)
index.addEntry('caesar',1)
index.addEntry('caesar',2)
index.addEntry('calpurnia',2)
index.addEntry('brutus',3)
index.addEntry('friend',3)
index.addEntry('john',3)


#QUERY = "brutus caesar"
#Note : not actual doing the cosine simmilarity

#Union of posting lists of "brutus" and "caeasar"

posting_list_brutus = index.getPostingList("brutus")
posting_list_caesar = index.getPostingList("caesar")

#print(posting_list_brutus)
#print(posting_list_caesar)

posting_list_union = union2(posting_list_brutus,posting_list_caesar)
#print(posting_list_union) #  3 documetns in union - 1,2,3

#Calcluating tf-idf scores
index.calTFIDF('brutus',1)
index.calTFIDF('brutus',2)
index.calTFIDF('brutus',3)

index.calTFIDF('caesar',1)
index.calTFIDF('caesar',2)
index.calTFIDF('caesar',3)

#Printing result
print('USING INDEX: ')
#print(index.getTerms())
print("term      doc1                  doc2                  doc3")
print('{}    {}    {}    {}'.format('brutus',index.getTFIDF('brutus',1),index.getTFIDF('brutus',2),index.getTFIDF('brutus',3)))
print('{}    {}    {}    {}'.format('caesar',index.getTFIDF('caesar',1),index.getTFIDF('caesar',2),index.getTFIDF('caesar',3)))
print("\n")


'''