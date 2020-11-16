from typing import Dict

from utils import doc_id_type


class File_FileID_Mapping:
	def __init__(self, filenames):
		self.id_to_file_mapping: Dict[int:str] = {}
		self.file_to_id_mapping: Dict[int:str] = {}

		for file_id, filename in enumerate(filenames):
			self.id_to_file_mapping[file_id] = filename
			self.file_to_id_mapping[filename] = file_id

	def get_file_id(self, filename: str) -> int:
		return self.file_to_id_mapping[filename]

	def get_file_name(self, file_id: int) -> str:
		return self.id_to_file_mapping[file_id]

	def __repr__(self) -> str:
		return f"{self.id_to_file_mapping}"


class Doc_DocID_Entry:
	def __init__(self, file_id: int, row_number: int, metadata: dict):
		self.file_id: str = file_id
		self.row_number: int = row_number
		self.metadata: dict = metadata
		# URL, MatchDateTime, Station, Show, IAShowID, IAPreviewThumb, Snippet

	def __repr__(self) -> str:
		return f"{{file_id: {self.file_id}, row_number: {self.row_number}, metadata: {self.metadata}}}"


class Doc_DocID_Mapping:
	def __init__(self):
		self.id_to_doc_mapping: Dict[doc_id_type, Doc_DocID_Entry] = {}

	def add_doc(
		self, doc_id: doc_id_type, file_id: int, row_number: int, metadata: dict
	) -> None:
		self.id_to_doc_mapping[doc_id] = Doc_DocID_Entry(file_id, row_number, metadata)

	def get_doc(self, doc_id: doc_id_type) -> Doc_DocID_Entry:
		return self.id_to_doc_mapping.get(doc_id, None)

	def __repr__(self) -> str:
		return f"{self.id_to_doc_mapping}"
