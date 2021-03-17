import argparse
from pathlib import Path, PurePath
from typing import Dict, Optional

from models_slim import Base, Post, Source, Token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Sources = Optional[Dict[str, str]]

parser = argparse.ArgumentParser()
parser.add_argument("--db", help="path to db", default="classifier.db")
parser.add_argument("--from-json", help="fill db from provided json file", default="")
parser.add_argument("--to-json", help="fill data to provided json file", default="")
parser.add_argument(
    "action",
    help="fill, train, classify or status",
    nargs=1,
    choices=("fill", "train", "classify", "status"),
)


class Classifier:
    def __init__(self, db: Path) -> None:
        db_path = "sqlite:///" + db
        engine = create_engine(db_path)
        Session = sessionmaker()
        Session.configure(bind=engine)
        self.db = Session()
        Base.metadata.create_all(engine)

    def fill(self) -> dict:
        return {}

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
    def tokens(self):
        return None

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
    classifier = Classifier(args.db)
