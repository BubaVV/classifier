import argparse
import json
from pathlib import Path, PurePath
from typing import Dict, List, Optional

from models_slim import Base, Post, Source
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils import download_all

Sources = Optional[Dict[str, str]]

parser = argparse.ArgumentParser()
parser.add_argument("--db", help="path to db", default="classifier.db")
parser.add_argument("--tokens", help="path to tokens file", default="tokens.txt")
parser.add_argument("--from-json", help="fill db from provided json file", default="")
parser.add_argument("--to-json", help="fill data to provided json file", default="")
parser.add_argument(
    "action",
    help="fill, train, classify or status",
    nargs=1,
    choices=("fill", "train", "classify", "status"),
)


class Classifier:
    def __init__(self, args) -> None:
        self._args = args
        db_path = "sqlite:///" + self._args.db
        self._engine = create_engine(db_path)
        Session = sessionmaker()
        Session.configure(bind=self._engine)
        self.db = Session()
        Base.metadata.create_all(self._engine)
        with open(self._args.tokens) as f:
            self._tokens = f.readlines()

    def fill(self) -> None:
        if not self._args.from_json:
            data = download_all(self.tokens[0], self.groups) # TODO add multithread
        else:
            with open(self._args.from_json) as f:
                data = json.load(f)
        Base.metadata.drop_all(bind=self._engine, tables=[Post.__table__])
        Base.metadata.drop_all(bind=self._engine, tables=[Post.__table__])
        self.db.add_all((Post(record) for record in data if record["text"]))
        self.db.commit()

    def train(self) -> dict:
        return {}

    def classify(self) -> dict:
        return {}

    def status(self) -> dict:
        return {}

    def resolve_group(self, name: str) -> int:
        pass

    @property
    def nn(self):
        return None

    @property
    def tokens(self) -> List[str]:
        return self._tokens

    @property
    def sources(self) -> Sources:
        sources = self.db.query(Source).all()
        return {x.source: x.class_ for x in sources}

    @sources.setter
    def sources(self, sources: Sources) -> None:
        if sources:
            for source, class_ in sources.items():
                record = Source(source, class_)
                self.db.merge(record)
        else:
            self.db.query(Source).delete()
        try:
            self.db.commit()
        except:
            self.db.rollback()


if __name__ == "__main__":
    args = parser.parse_args()
    classifier = Classifier(args)
    if "fill" in args.action:
        classifier.fill()