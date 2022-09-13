import re
from typing import List

import pycld2 as cld2
import pymorphy2
import vk_api
from vk_api.exceptions import VkApiError


morph = pymorphy2.MorphAnalyzer()
punctuation = re.compile(r"[^\w\s]")


def detect_lang(text: str) -> str:
    isReliable, _, details = cld2.detect(text)
    return details[0][1] if isReliable else ""


def process_text(text: str) -> List[str]:
    content = text
    content = content.replace("\n", " ")
    content = punctuation.sub(" ", content).strip()
    splitted_content = re.split(r"\s+", content)
    result = []
    for word in splitted_content:
        m = morph.parse(word)
        if len(m) != 0:
            wrd = m[0]
            if wrd.tag.POS not in ("NUMR", "PREP", "CONJ", "PRCL", "INTJ"):
                result.append(wrd.normal_form)
    return result


def resolve_source(token: str, domain: int) -> dict:
    vk_session = vk_api.VkApi(token=token)
    api = vk_session.get_api()
    response = api.utils.resolveScreenName(screen_name=domain)
    result = {"domain": domain}
    if response == []:
        raise ValueError("Invalid source: %s" % domain)
    if response["type"] == "group":
        result["id"] = -response["object_id"]  # negative for groups
    elif response["type"] == "user":
        result["id"] = response["object_id"]
    else:
        raise ValueError("Strange source: %s" % response)
    return result


def download_all(token: str, sources: List[List]) -> dict:
    vk_session = vk_api.VkApi(token=token)
    tools = vk_api.VkTools(vk_session)
    resolved_sources = []
    for source in sources:
        try:
            resolved_source = resolve_source(token, source[0])
        except ValueError:
            print("Broken source: %s" % source)  # TODO convert to logger
            continue
        resolved_source.update({"class": source[1]})
        resolved_sources.append(resolved_source)

    posts = []
    failed_sources = []
    for resolved_source in resolved_sources:
        source_id = resolved_source["id"]
        try:
            print(source_id)
            wall = tools.get_all("wall.get", 40, {"owner_id": source_id}, limit=1000)
        except VkApiError as e:
            print(e)
            failed_sources.append(source_id)
            continue
        posts.extend(wall["items"])
    print("Falling back to slow download")

    for source_id in failed_sources:
        try:
            print(source_id)
            wall = tools.get_all_slow(
                "wall.get", 100, {"owner_id": source_id}, limit=1000
            )  # TODO manage hardcoded limit
        except VkApiError as e:
            print("Slow download failed")
            print(e)
            continue
        posts.extend(wall["items"])
    return {"sources": resolved_sources, "posts": posts}
