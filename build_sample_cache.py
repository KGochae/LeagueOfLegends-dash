"""샘플 데이터 캐시 생성 스크립트 (최초 1회, API 키 필요).

사용법 (Windows PowerShell):
    $env:RGK='<RIOT_API_KEY>'; python build_sample_cache.py

빛 챤#xoxv 의 최근 랭크 경기 원본 Riot API 응답(JSON)을 sample_data/riot_cache.json 에 저장한다.
저장 키는 riot.py 가 런타임에 만드는 URL(api_key 제거)과 정확히 동일해야 하므로,
riot.py 의 URL 포맷 문자열을 그대로 사용한다. (원본 JSON이라 pandas 버전에 독립적)
"""
import os
import json
import requests

SAMPLE_NAME, SAMPLE_TAG = '빛 챤', 'xoxv'
DIR = os.path.join(os.path.dirname(__file__), 'sample_data')
os.makedirs(DIR, exist_ok=True)
api_key = os.environ['RGK']

cache = {}


def _strip_key(url):
    for sep in ('&api_key=', '?api_key='):
        if sep in url:
            return url.split(sep)[0]
    return url


def fetch(url):
    resp = requests.get(url)
    cache[_strip_key(url)] = resp.json()
    return resp.json()


# --- riot.py 와 동일한 URL 포맷 (start=0, count=1 기본값 포함) ---
account = fetch("https://asia.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{}/{}?api_key={}".format(SAMPLE_NAME, SAMPLE_TAG, api_key))
puuid = account['puuid']

fetch("https://kr.api.riotgames.com/lol/league/v4/entries/by-puuid/{}?api_key={}".format(puuid, api_key))

match_ids = fetch("https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?type=ranked&start={}&count={}&api_key={}".format(puuid, 0, 1, api_key))

for match_id in match_ids:
    fetch('https://asia.api.riotgames.com/lol/match/v5/matches/{}/timeline?api_key={}'.format(match_id, api_key))

# get_match 는 match_ids[0] 의 match-v5 통계를 받는다
fetch('https://asia.api.riotgames.com/lol/match/v5/matches/{}?api_key={}'.format(match_ids[0], api_key))

out = os.path.join(DIR, 'riot_cache.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(cache, f, ensure_ascii=False)

print('저장 완료:', out)
print('캐시된 엔드포인트 수:', len(cache))
for k in cache:
    print('  -', k)
