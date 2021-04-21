import pycld2 as cld2
import pymorphy2
import re
import vk_api

from typing import List, Tuple

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

def download_posts(token: str, source_id: int) -> list:
    vk_session = vk_api.VkApi(token=token)
    tools = vk_api.VkTools(vk_session)
    wall = tools.get_all('wall.get', 2500, {'owner_id': source_id})
    result = []
    for post in wall["items"]:
        result.append({k : post[k] for k in ['text', 'owner_id', 'id']})
    return result

def resolve_source(token: str, domain: int) -> dict:
    vk_session = vk_api.VkApi(token=token)
    api = vk_session.get_api()
    response = api.utils.resolveScreenName(screen_name=domain)
    result = {'domain': domain}
    if response == []:
        raise ValueError('Invalid source: %s' % domain)
    if response['type'] == 'group':
        result['id'] = -response['object_id']  # negative for groups
    elif response['type'] == 'user':
        result['id'] = response['object_id']
    else:
        raise ValueError('Strange source: %s' % response)
    return result


def download_all(token: str, sources: List[List]) -> dict:
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    tools = vk_api.VkTools(vk_session)
    resolved_sources = []
    for source in sources:
        try:
            resolved_source = resolve_source(token, source[0])
        except ValueError:
            print('Broken source: %s' % source)  # TODO convert to logger
            continue
        resolved_source.update({'class': source[1]})
        resolved_sources.append(resolved_source)

    posts = []
    for source in resolved_sources:
        group_id = source['id']
        try:
            wall = tools.get_all('wall.get', 100, {'owner_id': group_id})
        except Exception as e:
            print(e)
            print(group_id)
            continue
        posts.extend(wall['items'])
    return {'sources': resolved_sources, 'posts': posts}

token = 'token'
vk_session = vk_api.VkApi(token=token, api_version='5.130')
vk = vk_session.get_api()
tools = vk_api.VkTools(vk_session)
group_id = -1980
wall = tools.get_all('wall.get', 100, {'owner_id': group_id})
# Get error 500
piece_of_wall = vk.wall.get(owner_id=group_id)
# piece_of_wall contains 100 posts

group_id = -40747355
wall = tools.get_all('wall.get', 100, {'owner_id': group_id})
# Get "Can't load items. Check access to requested items"
piece_of_wall = vk.wall.get(owner_id=group_id)
# piece_of_wall contains 100 posts
