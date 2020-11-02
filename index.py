class Node:
	def __init__(self,docID):
		self.docID = docID 
		self.next = None
		self.tf = 1


class PostingList:
	def __init__(self):
		self.head = None
		self.tail = None 

	def addEntry(self,docID):
		newNode = Node(docID)
		if self.head == None:
			self.head = newNode 
			self.tail = newNode
		else:
			if self.tail.docID == docID:
				self.tail.tf += 1
				return "REPEAT"
			self.tail.next = newNode
			self.tail = newNode
		return None
	
	def __iter__(self):
		return PostingListIterator(self)

class PostingListIterator:
	def __init__(self,PostingList):
		self.__PostingList = PostingList
		self.__currentPointer = PostingList.head
	
	def __next__(self):
		if self.__currentPointer!= None:
			node = self.__currentPointer
			self.__currentPointer = self.__currentPointer.next 
			return node 
		else:
			raise StopIteration


class TermEntry:
	def __init__(self):
		self.docFreq = 0
		self.postingList = PostingList()

	def addDoc(self,docID):
		if self.postingList.addEntry(docID) == None:
			self.docFreq += 1

class InvertedIndex:
	def __init__(self):
		self.__indexDictionary = dict()

	def __addTerm(self,term):
		self.__indexDictionary[term] = TermEntry()
		
	def addEntry(self,term,docID):
		if term not in self.__indexDictionary:
			self.__addTerm(term)
		self.__indexDictionary[term].addDoc(docID)

	def getPostingList(self,term):
		if term not in self.__indexDictionary:
			return None
		else:
			return self.__indexDictionary[term].postingList

	def getDocFreq(self,term):
		if term not in self.__indexDictionary:
			return None
		else:
			return self.__indexDictionary[term].docFreq

'''

if __name__=="__main__":


	myindex = InvertedIndex()
	# doc1  - brutus killed ceasar
	# doc2  - brutus betrayed caesar
	# doc3  - calpurnia in macbeth caesar


	myindex.addEntry('brutus',1)
	myindex.addEntry('brutus',1)
	myindex.addEntry('killed',1)
	myindex.addEntry('caesar',1)
	myindex.addEntry('brutus',2)
	myindex.addEntry('betrayed',2)
	myindex.addEntry('caesar',2)
	myindex.addEntry('calpurnia',3)
	myindex.addEntry('in',3)
	myindex.addEntry('macbeth',3)
	myindex.addEntry('caesar',3)

	pl_brutus = myindex.getPostingList('brutus')


	list_iter = iter(pl_brutus)

	print("Posting List(docID,tf): ",end =" ")
	while True:
		try:
			elem = next(list_iter)
			print((elem.docID,elem.tf),end =" ")
		except StopIteration:
			print()
			break
	print("docFreq: ",myindex.getDocFreq('brutus'))
'''