from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

from utils import detect_lang, process_text

Base = declarative_base()


def extract_text(post: dict) -> str:
    result = [post["text"]]
    if "attachments" in post:
        for attach in post["attachments"]:
            if attach["type"] == "poll":
                result.append(attach["poll"]["question"])
                continue
            if attach["type"] in ["doc", "page", "link"]:
                result.append(attach[attach["type"]]["title"])
            if attach["type"] == "link":
                result.append(attach["link"]["description"])

    if "copy_history" in post:
        result.extend([extract_text(repost) for repost in post["copy_history"]])

    return " ".join(result)


class Post(Base):
    __tablename__ = "corpus"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, primary_key=True)
    text = Column(String())
    lang = Column(String())

    def __init__(self, post):
        self.id = post.get("id", 0)
        self.owner_id = post.get("owner_id", 0)
        self.text = extract_text(post)
        self.lang = detect_lang(self.text)


class Token(Base):
    __tablename__ = "tokens"

    def __init__(self, token: str):
        self.token = token

    token = Column(String(), primary_key=True)


class Source(Base):
    __tablename__ = "sources"

    def __init__(self, args: dict):
        self.domain = args["domain"]
        self.class_ = args["class"]

    def to_dict(self):
        return {"domain": self.domain, "class": self.class_}

    domain = Column(String(), primary_key=True)
    class_ = Column(String())


class Groups(Base):
    __tablename__ = "groups"

    def __init__(self, args: dict):
        self.id_ = args["id"]
        self.name = args["name"]

    def to_dict(self):
        return {"id": self.id_, "name": self.name}

    id_ = Column(Integer, primary_key=True)  # assume to be negative for groups
    name = Column(String(), primary_key=True)
