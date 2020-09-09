from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from classifier.utils import detect_lang, process_text

Base = declarative_base()


class Post(Base):
    __tablename__ = "corpus"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, primary_key=True)
    text = Column(String())
    lang = Column(String())
    processed_text = Column(String())

    def __init__(self, post):
        self.id = post.get("id", 0)
        self.owner_id = post.get("owner_id", 0)
        self.text = post.get("text", "")
        self.lang = detect_lang(self.text)
        self.processed_text = process_text(self.text)


class Token(Base):
    __tablename__ = "tokens"

    def __init__(self, token: str):
        self.token = token

    token = Column(String(), primary_key=True)


class Source(Base):
    __tablename__ = "sources"

    def __init__(self, *args: str):
        self.domain, self.class_ = args

    def to_dict(self):
        return {"domain": self.domain, "class": self.class_}

    domain = Column(String(), primary_key=True)
    class_ = Column(String())
