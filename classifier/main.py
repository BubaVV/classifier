import argparse
import json
from pathlib import Path, PurePath
from typing import Dict, List, Optional

from classifier.models_slim import Base, Post, Source
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from classifier.utils import download_all

Sources = Optional[Dict[str, str]]

parser = argparse.ArgumentParser()
json_arg = parser.add_mutually_exclusive_group()
json_arg.add_argument("--from-json", help="fill db from provided json file", default="")
json_arg.add_argument("--to-json", help="fill data to provided json file", default="")

parser.add_argument("--db", help="path to db", default="classifier.db")
parser.add_argument("--sources", help="path to list of data sources", default="corpus_groups.txt")
parser.add_argument("--tokens", help="path to tokens file", default="tokens.txt")
parser.add_argument(
    "action",
    help="fill, train, classify or status",
    nargs=1,
    choices=("fill", "train", "classify", "status"),
)


class Classifier:
    def __init__(self, **kwargs) -> None:
        self._args = kwargs
        db_path = "sqlite:///" + self._args['db']
        self._engine = create_engine(db_path)
        Session = sessionmaker()
        Session.configure(bind=self._engine)
        self.db = Session()
        Base.metadata.create_all(self._engine)
        if 'tokens' in self._args:
            with open(self._args['tokens']) as f:
                self._tokens = f.readlines()
        if 'sources' in self._args:
            with open(self._args['sources']) as f:
                self.sources = [line.strip().split() for line in f.readlines()]

    def fill(self) -> None:
        if 'from_json' in self._args:
            with open(self._args['from_json']) as f:
                data = json.load(f)
            self.sources =[[source['domain'], source['class']] for source in data['sources']]
        else:
            data = download_all(self.tokens[0],
                                self.sources)  # TODO add multithread

        if 'to_json' in self._args:
            with open(self._args['to_json'], 'w') as f:
                json.dump(data, f)
            return

        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.db.add_all((Source(record) for record in data['sources']))
        for record in data['posts']:
            if not record["text"]:
                continue
            # duplicates are possible, so add() is not an option
            self.db.merge(Post(record))
        self.db.commit()

    def train(self) -> dict:
        return {}

    def classify(self) -> dict:
        return {}

    def status(self) -> dict:
        # TODO add some integrity checks here
        classes = self.db.query(Source.class_).distinct().all()
        result = {'classes': [x[0] for x in classes]}
        return result
    
    def validate(selfself) -> dict:
        # validates token, sources, etc.
        pass

    @property
    def nn(self):
        return None

    @property
    def tokens(self) -> List[str]:
        return self._tokens

    # @property
    # def sources(self) -> Sources:
    #     sources = self.db.query(Source).all()
    #     return {x.source: x.class_ for x in sources}

    # @sources.setter
    # def sources(self, sources: Sources) -> None:
    #     if sources:
    #         for source, class_ in sources.items():
    #             record = Source(source, class_)
    #             self.db.merge(record)
    #     else:
    #         self.db.query(Source).delete()
    #     try:
    #         self.db.commit()
    #     except:
    #         self.db.rollback()


if __name__ == "__main__":
    args = parser.parse_args()
    classifier = Classifier(vars(args))
    if "fill" in args.action:
        classifier.fill()
    if "status" in args.action:
        status = classifier.status()
        print(status)