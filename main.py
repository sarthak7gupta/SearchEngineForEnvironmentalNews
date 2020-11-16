from time import time

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter

from engine_utils import build_engine, load_engine_from_pickle


if __name__ == "__main__":
	engine = build_engine()
	# engine = load_engine_from_pickle()

	completer = WordCompleter(engine.all_terms, ignore_case=True)

	session = PromptSession(completer=completer, search_ignore_case=True)

	while True:
		try: q = session.prompt("> Enter Search Query: ")
		except KeyboardInterrupt: continue
		except EOFError: break
		st = time()
		results = engine.query(q)
		et = time()
		print()
		print(f"{len(results)} result(s) in {et - st} sec(s)")
		print()
		[print(result) for result in results]
		print()
