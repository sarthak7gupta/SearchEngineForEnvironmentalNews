import copy
import math
import timeit
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np
import requests
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from termcolor import colored

from engine_utils import build_engine, load_engine_from_pickle


def genTemplate(columns):
	t = {}
	for field in columns:
		t[field] = None
	return t


class Metrics:
	def __init__(
		self, elasticSearchHost, elasticSearchPort, elasticSearchIndex, columns
	):
		self.url = f"http://{elasticSearchHost}:{elasticSearchPort}/{elasticSearchIndex}/_search?pretty"
		self.cols = columns
		#self.engine = build_engine()
		self.engine = load_engine_from_pickle()

	def commonDocs(self, docsSet1, docsSet2):
		common = [value for value in docsSet1 if value in docsSet2]
		return common

	def getQueriesFile(self, filename):
		with open(filename) as f:
			content = f.readlines()
		content = [x.strip() for x in content]
		return content

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
		request = {"query": {"query_string": {"query": query}},"from" : 0, "size" : 20}
		elastic_results = requests.post(self.url, json=request)
		# numElasticDocuments = len(elastic_results.json()["hits"]["hits"])
		formattedElastic = self.formatResultElastic(
			elastic_results.json()["hits"]["hits"], self.cols
		)
		return formattedElastic

	def elasticSearchTime(self, query):
		request = {"query": {"query_string": {"query": query}},"from" : 0, "size" : 20}
		elastic_results = requests.post(self.url, json=request)
		return elastic_results.json()["took"]

	def searchTime(self, query):
		start = timeit.default_timer()
		results = self.engine.query(query)
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
			# print(time_taken)
		qps_val = time_taken / num_queries
		return qps_val

	"""
	Return queries per second in milliseconds(for our IR system)
	"""

	def qps_index(self, queriesSet):
		time_taken = 0
		num_queries = len(queriesSet)
		for query in queriesSet:
			self.searchTime(query)
		qps_val = time_taken / num_queries
		return qps_val


if __name__ == "__main__":
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
	engine = mymetrics.engine
	completer = WordCompleter(engine.all_terms, ignore_case=True)
	print(colored("Metrics available: ", "red"))
	print(
		" 1.Precision(Single Query) \n 2.Recall(Single Query) \n 3.F1-Score(Single Query) \n 4.Mean Average Precision[MAP](Multiple Queries) \n 5.P@K(Single Query) \n 6.R@K(Single Query) \n 7.Precision-Recall curves against K ranks(Single Query) \n 8.ElasticSearch Latency(Single Query) \n 9.Search Engine Latency(Single Query) \n 10.ElasticSearch Queries Per Second(Mutlitple Queries) \n 11.Search Engine Queries Per Second(Mutlitple Queries)"
	)
	print("----------")
	print(colored("Other: ","red"))
	print("12. View ElasticSearch results")
	session = PromptSession(completer=completer, search_ignore_case=True)

	while True:
		try:
			metric = int(session.prompt("> Enter Metric: "))
		except KeyboardInterrupt:
			continue
		except EOFError:
			break
		if metric == 1:
			query = session.prompt(">> Enter Query: ")
			prec = mymetrics.precision(query, mymetrics.engine.query(query))
			print("---------------------------")
			print("Query given: ", query)
			print("Precision: ", prec)
			print("---------------------------")
		elif metric == 2:
			query = session.prompt(">> Enter Query: ")
			#print(mymetrics.engine.query(query))
			reca = mymetrics.recall(query, mymetrics.engine.query(query))
			print("---------------------------")
			print("Query given: ", query)
			print("Recall: ", reca)
			print("---------------------------")
		elif metric == 3:
			query = session.prompt(">> Enter Query: ")
			f1score = mymetrics.f1score(query, mymetrics.engine.query(query))
			print("---------------------------")
			print("Query given: ", query)
			print("F1 Score: ", f1score)
			print("---------------------------")
		elif metric == 4:
			print("[MESSAGE]This metric requires multiple queries")
			num_queries = int(session.prompt(">> Enter number of queries: "))
			queryList = []
			for i in range(0, num_queries):
				queryList.append(session.prompt(">> Query: "))
			k = int(session.prompt(">> Enter value of K(Ranks) for MAP: "))
			docList = []
			for query in queryList:
				docList.append(mymetrics.engine.query(query))
			# print(docList)
			map = mymetrics.MAP(queryList, docList, k)
			print("---------------------------")
			print("Queries given: ")
			for i in queryList:
				print("- ", i)
			print("Mean Average Precision: ", map)
			print("---------------------------")
		elif metric == 5:
			query = session.prompt(">> Enter Query: ")
			k = int(session.prompt(">> Enter K(Rank): "))
			pk = mymetrics.p_at_k(query, mymetrics.engine.query(query), k)
			print("---------------------------")
			print("Precision at ", k, ": ", pk)
		elif metric == 6:
			query = session.prompt(">> Enter Query: ")
			k = int(session.prompt(">> Enter K(Rank): "))
			rk = mymetrics.p_at_k(query, mymetrics.engine.query(query), k)
			print("---------------------------")
			print("Recall at ", k, ": ", rk)
		elif metric == 7:
			print("[MESSAGE]This metric will display a graph,close graph to proceed")
			query = session.prompt(">> Enter Query: ")
			k = int(session.prompt(">> Enter K(Rank): "))
			mymetrics.pr_graph(query, mymetrics.engine.query(query), k)
		elif metric == 8:
			query = session.prompt(">> Enter Query: ")
			latency = mymetrics.elasticSearchTime(query)
			print("Query: ", query)
			print("Elastic Search took: ", latency, "ms")
		elif metric == 9:
			query = session.prompt(">> Enter Query: ")
			latency = mymetrics.searchTime(query)
			print("Query: ", query)
			print("Search Engine took: ", latency, "ms")
		elif metric == 10:
			print(
				"[MESSAGE]This metric requires a text file containing multiple queries"
			)
			file_name = session.prompt(">> Enter filename(with .txt): ")
			queryList = mymetrics.getQueriesFile(file_name)
			qps = mymetrics.qps_elastic(queryList)
			print("Number of queries given: ", len(queryList))
			print("Queries Per Second for ElasticSearch: ", qps)
		elif metric == 11:
			print(
				"[MESSAGE]This metric requires a text file containing multiple queries"
			)
			file_name = session.prompt(">> Enter filename(with .txt): ")
			queryList = mymetrics.getQueriesFile(file_name)
			qps = mymetrics.qps_index(queryList)
			print("Number of queries given: ", len(queryList))
			print("Queries Per Millisecond for Index: ", max(qps, len(queryList)))
		elif metric == 12:
			results = mymetrics.getElasticSearchResults(session.prompt(">> Enter Query: "))
			print()
			[pprint(result) for result in results]
			print()