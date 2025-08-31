from pathlib import Path
from typing import List, Union
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_community.document_loaders import (
WebBaseLoader,
PyPDFLoader,
TextLoader,
PyPDFDirectoryLoader
)


class  DocumentProcessor:
    """
    Handle Document loading
    """
    def __init__(self, chunk_size:int=500,chunk_overlap:int=50 ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )


    def load_from_url(self, url:str)->List[Document]:
        """
        Load document from url
        :param url:
        :return:
        """

        loader = WebBaseLoader(url)
        return loader.load()
    def load_from_pdf_dir(self, directory: Union[str, Path])->List[Document]:
        """
        Load document from pdf directory
        :param directory:
        :return:
        """
        loader  = PyPDFDirectoryLoader(str(directory))
        return loader.load()

    def load_from_text(self, text:str)->List[Document]:
        """
        Load document from text
        :param text:
        :return:
        """
        loader = TextLoader(text)
        return loader.load()

    def load_from_pdf(self, file_path:Union[str, Path])->List[Document]:
        """
        Load document from pdf file
        :param file_path:
        :return:
        """
        loader = PyPDFDirectoryLoader(str(file_path))
        return loader.load()


    def load_documents(self , sources:List[str])-> List[Document]:
        """
        Load from documents URLs, PDF directories , or TXT files
        :param sources:
        :return:
        """
        docs : List[Document] = []

        for source in sources:
            if source.startswith("http://") or source.startswith("https://"):
                docs.extend(self.load_from_url(source))

            path = Path("data")
            if path.is_dir():
                docs.extend(self.load_from_pdf_dir(path))
            elif path.suffix.lower() == ".txt":
                docs.extend(self.load_from_text(path))
            else:
                raise ValueError(f"Unsupported file type: {source}")

        return docs
    def split_documents(self, documents:List[Document])->List[Document]:
        """
        Split documents into chunks
        :param documents:
        :return:
        """
        return self.splitter.split_documents(documents)

    def process_url(self, urls:List[str])->List[Document]:
        """
        Complete pipeline to load and split documents
        :param urls:
        :return:
        """

        docs = self.load_documents(urls)
        return self.split_documents(docs)
