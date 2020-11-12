# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 08:02:26 2020

@author: Pranav Aditya
"""
import re
from spacy.lang.en import English
import en_core_web_sm




class Text_Preprocessing:
    def __init__(self):
        self.contractions_dict = { "ain't": "are not","'s":" is","aren't": "are not","can't": "can not","can't've": "cannot have",
"'cause": "because","could've": "could have","couldn't": "could not","couldn't've": "could not have",
"didn't": "did not","doesn't": "does not","don't": "do not","hadn't": "had not","hadn't've": "had not have",
"hasn't": "has not","haven't": "have not","he'd": "he would","he'd've": "he would have","he'll": "he will",
"he'll've": "he will have","how'd": "how did","how'd'y": "how do you","how'll": "how will","i'd": "i would",
"i'd've": "i would have","i'll": "i will","i'll've": "i will have","i'm": "i am","i've": "i have",
"isn't": "is not","it'd": "it would","it'd've": "it would have","it'll": "it will","it'll've": "it will have",
"let's": "let us","ma'am": "madam","mayn't": "may not","might've": "might have","mightn't": "might not",
"mightn't've": "might not have","must've": "must have","mustn't": "must not","mustn't've": "must not have",
"needn't": "need not","needn't've": "need not have","o'clock": "of the clock","oughtn't": "ought not",
"oughtn't've": "ought not have","shan't": "shall not","sha'n't": "shall not",
"shan't've": "shall not have","she'd": "she would","she'd've": "she would have","she'll": "she will",
"she'll've": "she will have","should've": "should have","shouldn't": "should not",
"shouldn't've": "should not have","so've": "so have","that'd": "that would","that'd've": "that would have",
"there'd": "there would","there'd've": "there would have",
"they'd": "they would","they'd've": "they would have","they'll": "they will","they'll've": "they will have",
"they're": "they are","they've": "they have","to've": "to have","wasn't": "was not","we'd": "we would",
"we'd've": "we would have","we'll": "we will","we'll've": "we will have","we're": "we are","we've": "we have",
"weren't": "were not","what'll": "what will","what'll've": "what will have","what're": "what are",
"what've": "what have","when've": "when have","where'd": "where did",
"where've": "where have","who'll": "who will","who'll've": "who will have","who've": "who have",
"why've": "why have","will've": "will have","won't": "will not","won't've": "will not have",
"would've": "would have","wouldn't": "would not","wouldn't've": "would not have","y'all": "you all",
"y'all'd": "you all would","y'all'd've": "you all would have","y'all're": "you all are","y'all've": "you all have",
"you'd": "you would","you'd've": "you would have","you'll": "you will","you'll've": "you will have",
"you're": "you are","you've": "you have"}
		

    def replace(self,match):
        return self.contractions_dict[match.group(0)]


    def expand_contractions(self,text,contractions_re):
        
        return contractions_re.sub(self.replace, text)


    def clean_text(self,text):
        
        # removes \n
        text=re.sub('\n',' ',text)
        # removes url in text
        text=re.sub(r"http\S+", "", text)
        return text
    
    def remove_stop_words(self,text):
        nlp = English()
        
        
        #  "nlp" Object is used to create documents with linguistic annotations.
        my_doc = nlp(txt)
        
        # Create list of word tokens
        token_list = []
        for token in my_doc:
            token_list.append(token.text)
            
        # Create list of word tokens after removing stopwords
        filtered_sentence =[] 
        
        for word in token_list:
            lexeme = nlp.vocab[word]
            if lexeme.is_stop == False:
                filtered_sentence.append(word)
        return filtered_sentence
    
    
    def lemmatisation(self,filtered_sentence):
        nlp = en_core_web_sm.load()
        
        doc = nlp(filtered_sentence)
        
        lemma_word = [] 
        for token in doc:
            lemma_word.append(token.lemma_)
        return lemma_word
    
    
# Main function 
    def text_preprocessing(self,txt):
        txt=txt.lower()
        
        
        #finds all the contrations
        contractions_re=re.compile('(%s)' % '|'.join(self.contractions_dict.keys()))
        txt=self.expand_contractions(txt,contractions_re)
    
        
        # cleans urls
        txt=self.clean_text(txt)
        txt=re.sub(' +',' ',txt)
        
        
       # removing stop words
        filtered_list=self.remove_stop_words(txt)
                
        filtered_sentence=" ".join(filtered_list) 
        
        #lemmatisation
        lem_list=self.lemmatisation(filtered_sentence)
        
        return lem_list 
       
    
        


txt=""""He determined to drop his  123 litigation with the monastry,and relinguish his claims to the wood-cuting and 
fishery rihgts at once. He was the more ready to do this becuase the rights had become much less valuable, and he had 
indeed the vaguest idea where the wood and river in question were."""
tp=Text_Preprocessing()

print(tp.text_preprocessing(txt))


