import pycld2 as cld2
import pymorphy2
import re
import vk_api

morph = pymorphy2.MorphAnalyzer()
punctuation = re.compile('[^\w\s]')

def detect_lang(text: str) -> str:
    isReliable, textBytesFound, details = cld2.detect(text)
    if isReliable:
        return details[0][1]
    else:
        return ""


def process_text(text: str) -> str:
    content = text
    content = content.replace('\n', ' ')
    content = punctuation.sub(' ', content)
    splitted_content = content.split(' ')
    result = ''
    for word in splitted_content:
        m = morph.parse(word)
        if len(m) != 0:
            wrd = m[0]
            if wrd.tag.POS not in ('NUMR', 'PREP', 'CONJ', 'PRCL', 'INTJ'):
                result = ' '.join([result, wrd.normal_form])
    return result

def download_posts(token: str, group_id: int) -> list:
    vk_session = vk_api.VkApi(token=token)
    tools = vk_api.VkTools(vk_session)
    wall = tools.get_all('wall.get', 2500, {'owner_id': group_id})
    result = []
    for post in wall["items"]:
        result.append({k : post[k] for k in ['text', 'owner_id', 'id']})
    return result

def download_all(token: str, groups: list):
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    tools = vk_api.VkTools(vk_session)
    group_ids = [-x['id'] for x in vk.groups.getById(group_ids=groups)]

    result = []
    for group_id in group_ids:
        try:
            wall = tools.get_all('wall.get', 100, {'owner_id': group_id})
        except Exception as e:
            print(e)
            print(group_id)
            continue
        result.extend(wall['items'])
