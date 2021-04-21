from sqlalchemy import Column, Integer, String, ForeignKey
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
    owner_id = Column(Integer, ForeignKey('source.id_'), primary_key=True)
    text = Column(String())
    lang = Column(String())

    def __init__(self, post):
        self.id = post.get("id", 0)
        self.owner_id = post.get("owner_id", 0)
        self.text = extract_text(post)
        self.lang = detect_lang(self.text)

class Source(Base):
    __tablename__ = "sources"

    def __init__(self, args: dict):
        self.id_ = args["id"]  # negative for groups
        self.domain = args["domain"]  # vk.com/domain as shortcut to number id
        self.class_ = args["class"]

    def to_dict(self):
        return {"domain": self.domain, "class": self.class_, "id": self.id_}

    id_ = Column(Integer, primary_key=True)
    domain = Column(String(), primary_key=True)
    class_ = Column(String())
