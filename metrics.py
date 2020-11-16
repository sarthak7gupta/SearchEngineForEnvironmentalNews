import copy
import math
import timeit

import matplotlib.pyplot as plt
import numpy as np
import requests

from utils import build_engine, load_engine_from_pickle


def genTemplate(columns):
	t = {}
	for field in columns:
		t[field] = None
	return t


class Metrics:
	def __init__(
		self, elasticSearchHost, elasticSearchPort, elasticSearchIndex, columns
	):
		self.url = (
			f"http://{elasticSearchHost}:{elasticSearchPort}/{elasticSearchIndex}/_search?pretty"
		)
		self.cols = columns
		self.engine = load_engine_from_pickle()

	def commonDocs(self, docsSet1, docsSet2):
		common = [value for value in docsSet1 if value in docsSet2]
		return common

	def formatResultElastic(self, elasticDocs, cols):
		formatted = []
		template = genTemplate(cols)
		for i in range(0, len(elasticDocs)):
			rowt = copy.deepcopy(template)
			for j in cols:
				rowt[j] = elasticDocs[i]["_source"][j]
			formatted.append(rowt)
		return formatted

	def formatResult(self, elasticDocs, cols):
		formatted = []
		template = genTemplate(cols)
		for i in range(0, len(elasticDocs)):
			rowt = copy.deepcopy(template)
			for j in cols:
				rowt[j] = elasticDocs[i][j]
			formatted.append(rowt)
		return formatted

	def getElasticSearchResults(self, query):
		request = {"query": {"query_string": {"query": query}}}
		elastic_results = requests.post(self.url, json=request)
		# numElasticDocuments = len(elastic_results.json()["hits"]["hits"])
		formattedElastic = self.formatResultElastic(
			elastic_results.json()["hits"]["hits"], self.cols
		)
		return formattedElastic

	def elasticSearchTime(self, query):
		request = {"query": {"query_string": {"query": query}}}
		elastic_results = requests.post(self.url, json=request)
		return elastic_results.json()["took"]

	def searchTime(self, Index, query):
		start = timeit.default_timer()
		results = Index.query(query)
		stop = timeit.default_timer()
		return (stop - start) * 1000

	def precision(self, query, docs):
		formattedElastic = self.getElasticSearchResults(query)
		formattedDocs = self.formatResult(docs, self.cols)
		numRelevantItemsRetreived = len(
			self.commonDocs(formattedElastic, formattedDocs)
		)
		numRetrievedItems = len(docs)
		prec_value = numRelevantItemsRetreived / numRetrievedItems
		return round(prec_value, 4)

	def recall(self, query, docs):
		formattedElastic = self.getElasticSearchResults(query)
		numElasticDocuments = len(formattedElastic)
		formattedDocs = self.formatResult(docs, self.cols)
		numRelevantItemsRetreived = len(
			self.commonDocs(formattedElastic, formattedDocs)
		)
		recall_value = numRelevantItemsRetreived / numElasticDocuments
		return round(recall_value, 4)

	def f1score(self, query, docs):
		prec_value = self.precision(query, docs)
		recall_value = self.recall(query, docs)
		if prec_value == recall_value == 0:
			return math.nan
		f1_value = (2 * prec_value * recall_value) / (prec_value + recall_value)
		return round(f1_value, 4)

	def p_at_k(self, query, docs, k):
		top_k_docs = docs[0:k]
		top_k_docs = self.formatResult(top_k_docs, self.cols)
		elasticResults = self.getElasticSearchResults(query)
		top_k_elastic = elasticResults[0:k]
		numRelevantItemsRetreived = len(self.commonDocs(top_k_docs, top_k_elastic))
		k_prec_value = numRelevantItemsRetreived / k
		return round(k_prec_value, 4)

	def r_at_k(self, query, docs, k):
		top_k_docs = docs[0:k]
		top_k_docs = self.formatResult(top_k_docs, self.cols)
		elasticResults = self.getElasticSearchResults(query)
		top_k_elastic = elasticResults
		numRelevantItemsRetreived = len(self.commonDocs(top_k_docs, top_k_elastic))
		k_rec_value = numRelevantItemsRetreived / len(elasticResults)
		return round(k_rec_value, 4)

	def pr_graph(self, query, docs, k):
		precisions = []
		recalls = []
		elasticResults = self.getElasticSearchResults(query)
		for i in range(1, k + 1):
			top_k_docs = docs[0:i]
			top_k_docs = self.formatResult(top_k_docs, self.cols)
			top_k_elastic = elasticResults[0:i]
			numRelevantItemsRetreived = len(self.commonDocs(top_k_docs, top_k_elastic))
			k_prec_value = numRelevantItemsRetreived / i
			precisions.append(k_prec_value)
			top_k_elastic = elasticResults
			numRelevantItemsRetreived = len(self.commonDocs(top_k_docs, top_k_elastic))
			k_rec_value = numRelevantItemsRetreived / len(elasticResults)
			recalls.append(k_rec_value)
		ranks = np.arange(1, k + 1, 1)
		plt.plot(ranks, precisions, "r--", label="Precision")
		plt.plot(ranks, recalls, "b--", label="Recall")
		plt.xlabel("Ranks")
		plt.legend()
		plt.show()

	def MAP(self, queriesSet, docsSet, k):
		elasticResultsSet = [
			self.getElasticSearchResults(query) for query in queriesSet
		]
		for i in range(0, len(docsSet)):
			docsSet[i] = self.formatResult(docsSet[i], self.cols)
		queryAverages = []
		for i in range(0, len(queriesSet)):
			queryPrecisions = []
			for j in range(0, k):
				if docsSet[i][j] in elasticResultsSet[i]:
					top_k_docs = docsSet[i][0:j + 1]
					top_k_elastic = elasticResultsSet[i][0:j + 1]
					numRelevantItemsRetreived = len(
						self.commonDocs(top_k_docs, top_k_elastic)
					)
					k_prec_value = numRelevantItemsRetreived / (j + 1)
					queryPrecisions.append(k_prec_value)
			avg_precision = 0.0
			if len(queryPrecisions) != 0:
				avg_precision = sum(queryPrecisions) / len(queryPrecisions)
				queryAverages.append(avg_precision)
			print("Query:", queriesSet[i], " Average Precision: ", avg_precision)
		if len(queryAverages) != 0:
			map_val = sum(queryAverages) / len(queryAverages)
			return map_val
		return 0.0

	"""
	Return queries per second in milliseconds(for elastic search)
	"""

	def qps_elastic(self, queriesSet):
		time_taken = 0
		num_queries = len(queriesSet)
		for query in queriesSet:
			request = {"query": {"query_string": {"query": query}}}
			elastic_results = requests.post(self.url, json=request)
			time_taken += elastic_results.json()["took"]
		qps_val = time_taken / num_queries
		return qps_val

	"""
	Return queries per second in milliseconds(for our IR system)
	"""

	def qps_index(self, queriesSet, Index):
		time_taken = 0
		num_queries = len(queriesSet)
		for query in queriesSet:
			self.searchTime(Index, query)
		qps_val = time_taken / num_queries
		return qps_val


docs = [
	{
		"IAPreviewThumb": "https://archive.org/download/BBCNEWS_20170329_023000_Westminster_Terror_Attack_-_Panorama/BBCNEWS_20170329_023000_Westminster_Terror_Attack_-_Panorama.thumbs/BBCNEWS_20170329_023000_Westminster_Terror_Attack_-_Panorama_001798.jpg",
		"IAShowID": "BBCNEWS_20170329_023000_Westminster_Terror_Attack_-_Panorama",
		"MatchDateTime": "3/29/2017 3:00:19",
		"Show": "Westminster Terror Attack - Panorama",
		"Snippet": "and around the globe. i'm reged ahmad. our top stories: brexit begins. britain's prime minister signs the letter kick-starting the uk's departure from the european union. president trump scraps us plans to combat climate change.",
		"Station": "BBCNEWS",
		"URL": "https://archive.org/details/BBCNEWS_20170329_023000_Westminster_Terror_Attack_-_Panorama#start/1804/end/1839",
		"csv_file": "BBCNEWS.201703.csv",
		"id": "4_23",
		"row_number": 24,
	}
]

docs2 = [
	{
		"IAPreviewThumb": "https://archive.org/download/MSNBCW_20170120_150000_The_Inauguration_of_Donald_Trump/MSNBCW_20170120_150000_The_Inauguration_of_Donald_Trump.thumbs/MSNBCW_20170120_150000_The_Inauguration_of_Donald_Trump_000297.jpg",
		"IAShowID": "MSNBCW_20170120_150000_The_Inauguration_of_Donald_Trump",
		"MatchDateTime": "1/20/2017 15:05:13",
		"Show": "The Inauguration of Donald Trump",
		"Snippet": "confirmation hearings not so successfully. and to roll back everything, it's frightening on climate change. the president-elect said about his son-in-law last night, if he can't bring about middle",
		"Station": "MSNBC",
		"URL": "https://archive.org/details/MSNBCW_20170120_150000_The_Inauguration_of_Donald_Trump#start/298/end/333",
	}
]

mymetrics = Metrics(
	"54.157.12.8",
	9200,
	"env_news",
	[
		"URL",
		"MatchDateTime",
		"Station",
		"Show",
		"IAShowID",
		"IAPreviewThumb",
		"Snippet",
	],
)
# print(mymetrics.precision("Westminster terror attack",docs))
# print(mymetrics.recall("Westminster terror attack",docs))
# print(mymetrics.f1score("Westminster terror attack",docs))
# print(mymetrics.elasticSearchTime("Westminster terror attack"))
# print(mymetrics.f1score("Westminster terror attack",docs))
# mymetrics.pr_graph("Westminster terror attack",docs,20)
query1Results = docs2 * 10
query2Results = docs * 10
ldocs = [query1Results, query2Results]
# doc = mymetrics.getElasticSearchResults("Donald trump")[0]
print(mymetrics.MAP(["Westminster terror attack", "Donald trump"], ldocs, 4))
# print(mymetrics.qps_elastic(["Westminster terror attack","Donald trump"]))

# print(mymetrics.f1score("Modi",docs))
