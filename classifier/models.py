# type: ignore
from sqlalchemy import Column, Integer, String, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
import datetime
import enum
from collections import defaultdict

SCHEMA = "classifier"

Base = declarative_base(metadata=MetaData(schema=SCHEMA))


def attach_inst_to_list(attach_list):
    ans = []
    for attach in attach_list:
        if attach["type"] not in Attach_Type.__members__:
            continue
        if attach["type"] == "link":
            ans.append(
                {
                    "type": attach["type"],
                    "url": attach[attach["type"]]["url"],
                    "description": attach[attach["type"]]["title"]
                    + "\n"
                    + attach[attach["type"]]["description"],
                }
            )
        else:
            ans.append(
                {
                    "type": attach["type"],
                    "id": attach[attach["type"]]["id"],
                    "owner_id": attach[attach["type"]]["owner_id"],
                    "description": attach[attach["type"]]["title"],
                }
            )
            if attach["type"] == "video":
                ans[-1]["description"] += "\n" + attach[attach["type"]]["description"]
    return ans


class Attach_Type(enum.Enum):
    audio = "audio"
    video = "video"
    link = "link"


class Post(Base):
    __tablename__ = "corpus"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, primary_key=True)
    from_id = Column(Integer)
    date = Column(DateTime)
    text = Column(String())
    reply_owner_id = Column(Integer, default=None)
    reply_post_id = Column(Integer, default=None)
    comments = Column(Integer)
    likes = Column(Integer)
    reposts = Column(Integer)
    views = Column(Integer)
    signer_id = Column(Integer, default=None)
    repost_history = Column(JSONB)
    attachments = Column(JSONB)

    def __init__(self, post):
        post = defaultdict(lambda: 0, post)
        self.id = post["id"]
        self.owner_id = post["owner_id"]
        self.from_id = post["from_id"]
        self.date = datetime.datetime.fromtimestamp(post["date"])
        self.text = post["text"]
        if "reply_owner_id" in post:
            self.reply_owner_id = post["reply_owner_id"]
        if "reply_post_id" in post:
            self.reply_post_id = post["reply_post_id"]
        try:
            self.comments = post["comments"]["count"]
            self.likes = post["likes"]["count"]
            self.reposts = post["reposts"]["count"]
        except TypeError:
            pass
        try:
            self.views = post["views"]["count"]
        except TypeError:
            pass
        if "signer_id" in post:
            self.signer_id = post["signer_id"]
        if "attachments" in post:
            self.attachments = attach_inst_to_list(post["attachments"])
        else:
            self.attachments = []
        if "copy_history" in post:
            self.repost_history = [
                {"id": x["id"], "owner_id": x["owner_id"]} for x in post["copy_history"]
            ]
            [
                self.attachments.extend(attach_inst_to_list(x["attachments"]))
                for x in post["copy_history"]
                if "attachments" in x
            ]
            self.text += "\n".join([x["text"] for x in post["copy_history"]])


class Group_profile(Base):
    __tablename__ = "group_profiles"
    id = Column(Integer, primary_key=True)  # assume to be positive
    name = Column(String())
    screen_name = Column(String())
    description = Column(String())
    members_count = Column(Integer)
    site = Column(String())
    status = Column(String())

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


class Source(Base):
    __tablename__ = "sources"
    domain = Column(String(), primary_key=True)
    class_ = Column(String())


class Token(Base):
    __tablename__ = "tokens"
    metadata = MetaData(schema="public")
    token = Column(String(), primary_key=True)
