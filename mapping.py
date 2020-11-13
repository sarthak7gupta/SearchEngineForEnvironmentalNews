import csv
from os import listdir
import os
import copy
import json
import timeit

class docIDMapping:
    def __init__(self):
        self.docID = "1_1"
        self.mapping = dict()

    def addMapping(self,doc,newdoc):
        if newdoc and self.docID!="0_1":
            curDocID = self.docID
            curDocID = curDocID.split('_')
            newDocID = str(int(curDocID[0])+1)+"_0"
            self.docID = newDocID
        else:
            curDocID = self.docID
            curDocID = curDocID.split('_')
            newDocID = curDocID[0]+"_"+str(int(curDocID[1])+1)
            self.docID = newDocID
        doc['id'] = self.docID
        self.mapping[self.docID] = doc

    def getDoc(self,docID):
        if docID not in self.mapping:
            return None
        return self.mapping[docID]
        
def genTemplate(columns):
    t = {}
    for field in columns:
        t[field] = None 
    return t

def importCSV(path,columns):
    docMap = docIDMapping()
    template = genTemplate(columns)
    files = listdir(path)
    for file in files:
        newdoc = True
        with open(path+"/"+file,encoding='UTF-8',mode="r")as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count == 0:
                    line_count += 1
                    continue
                else:
                    rowt = copy.deepcopy(template)
                    i = 0
                    for key in rowt:
                        rowt[key] = row[i]
                        i+=1
                    rowt['row_number'] = line_count
                    head,tail = os.path.split(csv_file.name)
                    rowt['csv_file'] = tail
                    if newdoc:
                        docMap.addMapping(rowt,True)
                        newdoc = False
                    else:
                        docMap.addMapping(rowt,False)
                    line_count += 1
    return docMap


if __name__=="__main__":
    cols = ["URL","MatchDateTime","Station","Show","IAShowID","IAPreviewThumb","Snippet" ]
    start = timeit.default_timer()
    docMap = importCSV('C:/Users/navne/Documents/Semester 7/Algorithms for Information Retrieval/Project/TelevisionNews',cols)
    stop = timeit.default_timer()
    print('Time: ', stop - start)  
    while True:
        did = input("Enter Doc ID: ")
        doc = docMap.getDoc(did)
        print(json.dumps(doc,sort_keys=True,indent=4))