import os
from typing import Dict, List

import numpy as np
import streamlit as st
from more_itertools import chunked
from sqlalchemy.sql import func

from classifier.main import Classifier
from classifier.models_slim import Post, Source
from classifier.nn import NN
from classifier.utils import detect_lang


def repr_response(classes_: list) -> str:  # TODO: do func in utils
    return "\n\n".join([f"{x[0]}: {x[1]:0.3f}" for x in classes_])


NN_FNAME = "tiny.nn"

classifier = Classifier(db="tiny.db", from_json="db_tiny.json")
classifier.fill()
classes = classifier.status()["classes"]
classes.sort()

nn = NN(classes=classes)
example_text = (
    classifier.db.query(Post.text)
    .filter(Post.lang == "ru")
    .order_by(func.random())
    .first()[0]
)
example_text = " ".join(example_text.split(" ")[:30])

if os.path.exists(NN_FNAME):
    nn.load(NN_FNAME)
    del classifier.db
else:
    tasks = (
        classifier.db.query(Post.text, Source.class_)
        .filter(Post.lang == "ru")
        .join(Source)
        .order_by(func.random())
        .all()
    )

    ds_size = len(tasks)
    split_point = int(ds_size * 0.9)
    train = tasks[:split_point]
    test = tasks[split_point:]

    x_test = [x[0] for x in test]
    y_test = [x[1] for x in test]

    iteration = 0
    for chunk in chunked(train * 10, 100):
        iteration += 1
        x_train = [x[0] for x in chunk]
        y_train = [x[1] for x in chunk]
        nn.train(x_train, y_train)

    nn.save(NN_FNAME)
    del classifier.db

st.title("Short text classifier")
st.write(
    "Tool to classify short texts in russian languages by classes. "
    "Classes known by model are presented below. "
    "Optimal length of texts are about few dozen words. "
    "\n\nHow to interpret results: if some class has has value more than 0.7, "
    "class describes text well enough"
)
st.write(f"Text example:\n\n\n\n {example_text}")
st.write(f'Known classes: {", ".join(classes)}')

user_input = st.text_input("Text to classify")
click = st.button("Classify!")
if not click:
    st.stop()

st.write(f"Detected text language: {detect_lang(user_input)}")
# TODO Make output fancier: sorting, color highlight for primary class, etc.
st.write(f"Result:\n\n{repr_response(nn.infer([user_input])[0])}")
