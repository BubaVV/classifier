from pathlib import Path
from typing import Dict, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from classifier.models_slim import Base, Post, Source, Token

Sources = Optional[Dict[str, str]]


class Classifier:
    def __init__(self, db: Path) -> None:
        engine = create_engine("sqlite://{}".format(db))
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
