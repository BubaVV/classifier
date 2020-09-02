from itertools import cycle
import numpy
from sklearn.feature_extraction.text import HashingVectorizer
from keras.layers import Dense, Dropout
from keras.models import Sequential
import h5py
from keras.utils import plot_model
from typing import Generator, Tuple

from classifier.settings import DIFF_WORDS


def batch_gen(source: list, size: int) -> Generator[Tuple[numpy.array, numpy.array]]:
    """
    Group input samples of text to batches and vectorize it to proper format
    :param source: Should be cyclic generator
    :param size: batch size
    :return: list of tuples (input vector, one-hot class vector)
    """
    vectorizer = HashingVectorizer(
        decode_error="ignore", n_features=DIFF_WORDS, alternate_sign=False
    )
    result = ([], [])
    for sample in source:
        result[0].append(sample[0])
        result[1].append(sample[1])
        if len(result[0]) >= size:
            transformed_result = (
                numpy.array(vectorizer.transform(result[0]).todense()),
                numpy.array(result[1]),
            )
            # Vectorizer output is sparse vector, but nn wants dense vector for output. Dense vectors are HUGE, so we
            # should transform it only for separate batches
            yield transformed_result
            result = ([], [])


def cyclic_gen_nobatch(
    source: Generator[str, None, None]
) -> Generator[str, None, None]:
    """
    Convert plain generator to cyclic
    :param source:
    :return:
    """
    # cycle('ABCD') --> A B C D A B C D
    cycle_source = cycle(source)
    while True:
        sample = next(cycle_source)
        yield sample


class NN:
    def __init__(self):
        pass
