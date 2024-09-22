import pickle
from typing import List

import numpy as np
from sklearn.neural_network import MLPClassifier

from classifier.nn import BaseNN
from classifier.settings import DIFF_WORDS


class SklearnNN(BaseNN):
    def __init__(self, classes: List[str], n_features: int = DIFF_WORDS):
        super().__init__(classes, n_features)
        self._nn = MLPClassifier(hidden_layer_sizes=(50, 50))

    def train(self, text: List[str], target: List):
        x = np.asarray(self.vectorize(text).todense())
        self._nn.partial_fit(x, target, self.classes)

    def infer(self, text: List[str]) -> List:
        x = np.asarray(self.vectorize(text).todense())
        result = self._nn.predict_proba(x).tolist()
        return [list(zip(self.classes, r)) for r in result]

    def score(self, text: List[str], target: List):
        x = np.asarray(self.vectorize(text).todense())
        return self._nn.score(x, np.array(target))

    def save(self, fname: str):
        with open(fname, "wb") as f:
            pickle.dump(self._nn, f)

    def load(self, fname: str):
        with open(fname, "rb") as f:
            self._nn = pickle.load(f)
