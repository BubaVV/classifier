import pickle
from typing import List

# import h5py
import numpy as np

# from keras.layers import Dense, Dropout
# from keras.models import Sequential
# from keras.utils import plot_model
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.neural_network import MLPClassifier

from classifier.settings import DIFF_WORDS
from classifier.utils import process_text


class NN:  # TODO: do base class and implement Keras also
    def __init__(self, classes: List[str], n_features=DIFF_WORDS):
        super().__init__()
        self._nn = MLPClassifier(hidden_layer_sizes=(50, 50))
        self.classes = classes
        self.vectorizer = HashingVectorizer(
            decode_error="ignore",
            n_features=n_features,
            alternate_sign=False,
            tokenizer=process_text,
        )

    def save(self, fname):
        with open(fname, "wb") as f:
            pickle.dump(self._nn, f)

    def load(self, fname):
        with open(fname, "rb") as f:
            self._nn = pickle.load(f)

    def vectorize(self, text: List[str]) -> List[List[int]]:  # TODO: do caching here
        return self.vectorizer.transform(text)

    def train(self, text: List[str], target: List):
        x = np.asarray(self.vectorize(text).todense())
        self._nn.partial_fit(x, target, self.classes)

    def infer(self, text: List[str]) -> List:
        x = np.asarray(self.vectorize(text).todense())
        result = self._nn.predict_proba(x).tolist()
        return [list(zip(self.classes, x)) for x in result]

    def score(self, text: List[str], target: List):
        x = np.asarray(self.vectorize(text).todense())
        y = np.array(target)
        return self._nn.score(x, y)

    def drop(self):
        if hasattr(self, "_nn"):
            del self._nn
            self.__init__(self.classes)
