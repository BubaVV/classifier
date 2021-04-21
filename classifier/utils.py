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
    failed_sources = []
    for source in resolved_sources:
        source_id = source['id']
        try:
            print(source_id)
            wall = tools.get_all('wall.get', 40, {'owner_id': source_id},
                                 limit=1000)
        except Exception as e:
            print(e)
            failed_sources.append(source_id)
            continue
        posts.extend(wall['items'])
    print('Falling back to slow download')

    for source_id in failed_sources:
        try:
            print(source_id)
            wall = tools.get_all_slow('wall.get', 100, {'owner_id': source_id},
                                      limit=1000)  # TODO manage hardcoded limit
        except Exception as e:
            print('Slow download failed')
            print(e)
            continue
        posts.extend(wall['items'])
    return {'sources': resolved_sources, 'posts': posts}
