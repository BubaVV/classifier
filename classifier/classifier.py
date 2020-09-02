from typing import Dict, Optional
from dataclasses import dataclass, field

Sources = Optional[Dict[str, str]]


def detect_lang(text: str) -> str:
    return ""


def process_text(text: str) -> str:
    return ""


@dataclass
class Classifier:
    sources: Sources
    _sources: Sources = field(init=False, repr=False)

    def __init__(self, sources: Sources = None) -> None:
        self.sources = sources

    def fill(self) -> dict:
        return {}

    def train(self) -> dict:
        return {}

    def classify(self) -> dict:
        return {}

    def status(self) -> dict:
        return {}

    @property
    def nn(self):
        return None

    @property
    def tokens(self):
        return None

    @property  # mypy: ignore
    def sources(self) -> Sources:
        return self._sources

    @sources.setter
    def sources(self, sources: Sources) -> None:
        if sources:
            self._sources = dict(sources)
        else:
            self._sources = {}
