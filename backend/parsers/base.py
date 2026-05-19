from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ParseResult:
    def __init__(self):
        self.types: List[Dict[str, Any]] = []
        self.functions: List[Dict[str, Any]] = []
        self.calls: List[Dict[str, Any]] = []
        self.refs: List[Dict[str, Any]] = []

class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> ParseResult:
        pass

    @abstractmethod
    def get_language(self) -> str:
        pass

def get_parser_for_language(language: str) -> BaseParser:
    from .python_parser import PythonParser
    from .js_parser import JSParser
    from .go_parser import GoParser

    parsers = {
        "python": PythonParser(),
        "javascript": JSParser(),
        "typescript": JSParser(),
        "go": GoParser(),
    }
    return parsers.get(language, None)
