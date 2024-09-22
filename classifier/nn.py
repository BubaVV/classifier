from abc import ABC, abstractmethod
from typing import List

from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import HashingVectorizer

from classifier.utils import process_text


class BaseNN(ABC):
    def __init__(self, classes: List[str], n_features: int):
        self.classes = classes
        self.vectorizer = self.init_vectorizer(n_features)
        self._nn = None
        self.n_features = n_features

    # pylint: disable=R0201
    def init_vectorizer(self, n_features: int):
        return HashingVectorizer(
            decode_error="ignore",
            n_features=n_features,
            alternate_sign=False,
            tokenizer=process_text,
        )

    def vectorize(self, text: List[str]) -> csr_matrix:
        return self.vectorizer.transform(text)

    @abstractmethod
    def train(self, text: List[str], target: List):
        pass

    @abstractmethod
    def infer(self, text: List[str]) -> List:
        pass

    @abstractmethod
    def score(self, text: List[str], target: List):
        pass

    @abstractmethod
    def save(self, fname: str):
        pass

    @abstractmethod
    def load(self, fname: str):
        pass

    def reset(self):
        """ Reset the model, freeing resources """
        if hasattr(self, "_nn"):
            del self._nn
            self.__init__(self.classes, self.n_features)
