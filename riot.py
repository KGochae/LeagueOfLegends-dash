
# ----- json, dataframe ...etc ------#
import re
import streamlit as st
import json
import pandas as pd
import numpy as np
import requests
from sklearn.preprocessing import StandardScaler


# ------ image , animation ----------- #

import matplotlib.pyplot as plt
from time import sleep
from io import BytesIO
from PIL import Image, ImageDraw,ImageEnhance
from matplotlib.animation import FuncAnimation
from sklearn.preprocessing import MinMaxScaler

# Create API client.
# api_key  = st.secrets.RIOTAPI.api_key

# 가장 최근경기 가져오기

def get_match_data_log(summoner_name, api_key, start=0,count=1):
    # Get summoner puuid
    sohwan = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}"
    url = sohwan.format(summoner_name, api_key)
    response = requests.get(url)
    puuid = response.json()['puuid']
    summoner_id = response.json()['id']

    # Get match ids
    matchid_url = "https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{}/ids?type=ranked&start={}&count={}&api_key={}"
    url = matchid_url.format(puuid, start, count, api_key)
    response = requests.get(url)
    match_ids = response.json()
    
    # Get match data for each match id
    match_data_log = []
    time_url = 'https://asia.api.riotgames.com/lol/match/v5/matches/{}/timeline?api_key={}'
    for i, match_id in enumerate(match_ids):
        url = time_url.format(match_id, api_key)
        response = requests.get(url)
        match_data_log.append(pd.DataFrame(response.json()))    

    return  puuid,summoner_id, match_ids, pd.concat(match_data_log)



# 유저의 랭크와 승률  
def get_rank_info (summoner_id, api_key):
    rank_info = "https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{}?api_key={}"
    url = rank_info.format(summoner_id, api_key)
    response = requests.get(url)
    rank_data = response.json()

    return rank_data


# match_v5 (경기가 끝나고 나오는 통계요약약)
def get_match_v5(match_ids, puuid ,api_key):
    url = 'https://asia.api.riotgames.com/lol/match/v5/matches/{}?api_key={}'
    match_data = []
    for match_id in match_ids:
        response = requests.get(url.format(match_id, api_key))
        match_data.append(pd.DataFrame(response.json()))
    
    match_df = pd.concat(match_data)
    game_duration = match_df['info']['gameDuration']
    df = pd.DataFrame(match_df['info']['participants'])
    
    sample = df[['teamId','puuid','summonerName','participantId','teamPosition', 'challenges','summoner1Id','summoner2Id',
        'championName','lane','kills','deaths','assists','totalMinionsKilled','neutralMinionsKilled','goldEarned','goldSpent','champExperience','item0','item1','item2',
        'item3','item4','item5','item6','totalDamageDealt','totalDamageDealtToChampions','totalDamageTaken','damageDealtToTurrets','damageDealtToBuildings',
        'totalTimeSpentDead','longestTimeSpentLiving','visionScore','win','timePlayed','damageSelfMitigated','totalDamageShieldedOnTeammates',
        'totalHealsOnTeammates','damageDealtToObjectives']]

    challenge = pd.DataFrame(sample['challenges'].tolist())

    col = challenge[['soloKills','multikills','abilityUses','damageTakenOnTeamPercentage','skillshotsDodged','skillshotsHit','enemyChampionImmobilizations','laneMinionsFirst10Minutes','controlWardsPlaced'
                    , 'visionScorePerMinute','wardTakedowns','effectiveHealAndShielding','dragonTakedowns','baronTakedowns','teamBaronKills']]
    jungle_col = challenge.filter(regex='^jungle|Jungle|kda')

    match_info = pd.concat([sample , col, jungle_col], axis = 1)
    match_info['totalCS'] = match_info['totalMinionsKilled'] + match_info['neutralMinionsKilled']
    match_info['matchId'] = match_df['metadata']['matchId']
    match_info['championName'] = match_info['championName'].apply(lambda x: 'Fiddlesticks' if x == 'FiddleSticks' else x) # 피들스틱 에러

    summoner_position = match_info[match_info['puuid'] == puuid]['teamPosition'].iloc[0]
    champion_info = match_info[['matchId','participantId','teamId','teamPosition','summonerName','puuid','championName']]

    match_info['win'] = match_info['win'].apply(lambda x: '승리' if x == 1 else '패배')


    return match_info, df ,summoner_position ,champion_info,game_duration



def get_moving_data(match_data_log,puuid):
    id_df = pd.DataFrame(match_data_log['info']['participants']) # 참가자의 participantid 와 puuid 
    participant_ids = id_df['participantId'].tolist() 
    summoner_participantId = id_df.loc[id_df['puuid'] == puuid, 'participantId'].iloc[0] # 본인의 particiapnt_id 

    frames_df = pd.DataFrame(match_data_log['info']['frames']) # 이동경로(moving)은 match_data_log 의 info 컬럼 frames 행안에 있는것을 확인
    frames_list = pd.DataFrame(frames_df['participantFrames'])['participantFrames'].tolist() # 다시 list형태로 변경

    moving_data = [ [] for _ in range(len(participant_ids)) ]
    for frame in frames_list:
        # Loop through each participant id
        for i, participant_id in enumerate(participant_ids):
            # Check if the participant id is in the frame data
            if str(participant_id) in frame:
                # Append the position data to the moving data for the current participant
                moving_data[i].append(frame[str(participant_id)])

    moving_dfs = [pd.DataFrame(md) for md in moving_data]
    moving = pd.concat(moving_dfs)
    # 추출한 timestamp열을 frames_timestamp 변수에 저장
    frames_timestamp = frames_df['timestamp']
    # timestamp 열을 추가하여 moving 데이터프레임의 행과 열 개수를 확인
    moving['timestamp'] = frames_timestamp

    return  id_df, participant_ids, summoner_participantId, moving

# 게임중 일어난 이벤트들, 포지션 좌표
def get_events (match_data_log):
    frame_df = pd.DataFrame(match_data_log['info']['frames'])
    events_df = pd.DataFrame(frame_df['events'])
    events = events_df['events'].tolist()

    events_all_participant_ids = []

    for event in events:
        for event_dict in event:
            events_all_participant_ids.append(event_dict)

    all_events = pd.DataFrame(events_all_participant_ids)
    df = all_events[(all_events['type'] == 'CHAMPION_KILL')|(all_events['type'] == 'ELITE_MONSTER_KILL') | (all_events['type'] == 'BUILDING_KILL')] # or = | / and = &
    position_logs = df[['timestamp','type','position','teamId',
                        'killerId','victimId','assistingParticipantIds']]
    
    
    return all_events, position_logs


# 해당유저의 kill/death/assist에 관한 데이터
def get_logs_all (all_events,moving,summoner_participantId):

    df_k = all_events[(all_events['type'] == 'CHAMPION_KILL')]
    df_k = df_k[['timestamp','killerId','victimId','assistingParticipantIds','position','victimDamageDealt','victimDamageReceived']]

    kill_damage = df_k[df_k['killerId'] == summoner_participantId]
    death_damage = df_k[df_k['victimId'] == summoner_participantId]
          
    assist_damage = df_k[df_k['assistingParticipantIds'].apply(lambda x: summoner_participantId in x if isinstance(x, list) else False)]
    assist_damage = assist_damage[['timestamp','killerId','victimId','assistingParticipantIds','position','victimDamageReceived']]

    death = death_damage[['victimId','position','timestamp','assistingParticipantIds']]
    death['death'] = 1
    death.rename(columns={'victimId':'participantId'}, inplace=True) 
    death = death.sort_values(by='participantId',ascending=True)
    death['participantId'] = death['participantId'].astype(int)

    logs_dk = pd.concat([death, moving], axis=0, sort=False)
    # logs_dk = pd.concat([logs_df, kill], axis=0, sort=False)
    logs_dk = logs_dk.sort_values(by=['timestamp'], ignore_index=True, ascending=True)
    logs_all = logs_dk[['timestamp','participantId','position','death','assistingParticipantIds']]

    if not death_damage.empty:
        death_damage.loc[:, 'lane'] = death_damage.apply(lambda row: calculate_lane(row['position']['x'], row['position']['y']), axis=1)
    
    return df_k, logs_all, kill_damage, death_damage, assist_damage


#  딜교환 여부, 해당 유저의 kill death assist 했을때 스킬,피해량에 대한 로그
def get_damage_logs (death_damage,kill_damage,assist_damage):

    # 내가 죽은경우 받은 피해량을 확인한다.
    death_list = []
    if not death_damage.empty:
        for d, ts in zip(death_damage['victimDamageReceived'], death_damage['timestamp']):
            df = pd.json_normalize(d)
            df['timestamp'] = ts
            death_list.append(df)

        death_damage_log = pd.concat(death_list, axis=0)
        death_damage_log = death_damage_log[['timestamp','name','spellName','magicDamage','participantId','physicalDamage','trueDamage']]
        death_damage_log['name'] = death_damage_log['name'].replace(to_replace=r'^SRU_.*', value='Minion/Monster', regex=True)

    else: 
        death_damage_log = pd.DataFrame(columns=['timestamp', 'name', 'spellName', 'magicDamage', 'participantId', 'physicalDamage', 'trueDamage'])


   # 내가 죽었을 때 반격했는지 확인 할 수 있다.
    valid_data = death_damage[~death_damage['victimDamageDealt'].isna()]
    counter_list = []
    if not death_damage.empty:
        for a, ts in zip(valid_data['victimDamageDealt'], valid_data['timestamp']):
            df = pd.json_normalize(a)
            df['timestamp'] = ts
            counter_list.append(df)
        counter_damage_log = pd.concat(counter_list, axis =0)
        counter_damage_log = counter_damage_log[['timestamp','name','spellName','magicDamage','participantId','physicalDamage','trueDamage']]
        counter_damage_log['name'] = counter_damage_log['name'].replace(to_replace=r'^SRU_.*', value='Minion/Monster', regex=True)
    
    else: 
        counter_damage_log = pd.DataFrame()

    # 소환사의 kill damage 로그 
    k = kill_damage[~kill_damage['victimDamageReceived'].isna()]
    kill_list = []
    if not kill_damage.empty:
        for d, ts in zip(k['victimDamageReceived'], k['timestamp']):
            df = pd.json_normalize(d)
            df['timestamp'] = ts
            kill_list.append(df)
        kill_damage_log = pd.concat(kill_list, axis=0)
        kill_damage_log = kill_damage_log[['timestamp','name','spellName','magicDamage','participantId','physicalDamage','trueDamage']]
        kill_damage_log['name'] = kill_damage_log['name'].replace(to_replace=r'^SRU_.*', value='Minion/Monster', regex=True)

    else: 
        kill_damage_log = pd.DataFrame()

    # 소환사의 assist damage 로그 
    a = assist_damage[~assist_damage['victimDamageReceived'].isna()]
    assist_list = []
    if not assist_damage.empty:
        for d, ts in zip(a['victimDamageReceived'], a['timestamp']):
            df = pd.json_normalize(d)
            df['timestamp'] = ts
            assist_list.append(df)
        assist_damage_log = pd.concat(assist_list, axis=0)
        assist_damage_log = assist_damage_log[['timestamp','name','spellName','magicDamage','participantId','physicalDamage','trueDamage']]
        assist_damage_log['name'] = assist_damage_log['name'].replace(to_replace=r'^SRU_.*', value='Minion/Monster', regex=True)
    else: 
        assist_damage_log = pd.DataFrame()


    damage_counter = pd.concat([death_damage_log, counter_damage_log])
    damage_counter['name'] = damage_counter['name'].apply(lambda x: 'Fiddlesticks' if x == 'FiddleSticks' else x) # 피들스틱 에러
    # ka_dmg_log = pd.concat([kill_damage_log, assist_damage_log]) 
    kda_dmg_log = pd.concat([kill_damage_log,assist_damage_log,counter_damage_log])

    return death_damage_log, counter_damage_log, damage_counter, kill_damage_log, assist_damage_log, kda_dmg_log



# 챔피언의 이동경로
def create_animation(participant_ids,puuid,champion_info, logs_all):
# -------------------------------------------- map , update , animation -------------------------------------------- # 

    fig, ax = plt.subplots(figsize=(5,5),tight_layout=True)
    ax.set_xlim(0, 15000)
    ax.set_ylim(0, 15000)
    ax.axis('off')

    map_path = "img/minimap.png"  # 로컬 이미지 파일 경로
    img = Image.open(map_path)
    ax.imshow(img, extent=[0, 15000, 0, 15000])

# --------------------------------------------- 챔피언별 이미지 추가 ------------------------------------------------ #
    champion_images = {}
    for idx, champ in champion_info.iterrows():
        champion_name = champ['championName']
        champion_url = f"https://ddragon.leagueoflegends.com/cdn/13.22.1/img/champion/{champion_name}.png"
        response = requests.get(champion_url)
        img = Image.open(BytesIO(response.content))
        champion_images[champion_name] = img

    # 이미지 원형으로 자르기 및 크기 조절
    for champion_name, img in champion_images.items():
        # 원형으로 자르기
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + img.size, fill=255)
        img.putalpha(mask)
        # 크기 조절
        img = img.resize((100, 100))
        
    # 참가자별 plot image
    images = []
    for participant_id in participant_ids:
        participant_champs = champion_info[champion_info['participantId'] == participant_id]
        
        champion_name = participant_champs.iloc[0]['championName']
        
        image = champion_images[champion_name]
        
        alpha = 1.0 if participant_champs.iloc[0]['puuid'] == puuid else 0.3
        plot = ax.imshow(image,alpha=alpha)
        images.append(plot)
        

    def update(frame):
        # Get timestamp for the current frame
        timestamp = logs_all['timestamp'].unique()[frame]
        for i, participant_id in enumerate(participant_ids):
            # Filter logs_all to only include rows for the current participant and timestamp
            participant_df = logs_all[(logs_all['participantId'] == participant_id) & (logs_all['timestamp'] == timestamp)]
            # Get x and y positions for the current participant
            if not participant_df.empty:
                x = participant_df.iloc[0]['position']['x']
                y = participant_df.iloc[0]['position']['y']
                # Update the image plot for the current participant
                if participant_df.iloc[0]['death'] == 1:
                    # Decrease saturation of the image
                    image = Image.fromarray(images[i].get_array())
                    enhancer = ImageEnhance.Color(image)
                    image = enhancer.enhance(0)
                    images[i].set_data(np.array(image))
                else:
                    image = champion_images[champion_info[champion_info['participantId'] == participant_id].iloc[0]['championName']]
                    images[i].set_data(image)

                images[i].set_extent([x - 600, x + 600, y - 600, y + 600])
                
        return tuple(images)


    # 애니메이션
    
    num_frames = len(logs_all['timestamp'].unique())
    ani = FuncAnimation(fig, update, frames=num_frames, interval=600, blit=True)
    # ani.save('C:/test/Animation.gif', writer='imagemagick', fps=5, dpi=100) # gif파일로 저장
 
    return  champion_images, ani



# 라인을 머문 점수 계산
def calculate_lane(x, y):
    top_ranges = [(500, 2000, 6000, 14000),(600, 9000, 13000, 14500), (1900,4500,11100,13100)]

    bottom_ranges = [(6000, 14000, 500, 2000),(13000,14500, 500,9000),(10500,13000,2000,3800)]

    mid_ranges = [(4500, 6000, 4500, 6000),(5200,6700,5200,6700),(5900,7400,5900,7400),(6000,8500,6000,8500),
                  (7300,8800,7300,8800),(8000,9500,8000,9500),(8700,10200,8700,10200),(9200,10500,9200,10500)]

    blue_zone = [(0,4500,0,4500)]
    red_zone = [(10500,15000,10500,15000)]

    for range_ in top_ranges:
        if range_[0] <= x <= range_[1] and range_[2] <= y <= range_[3]:
            return 'top'
    for range_ in mid_ranges:
        if range_[0] <= x <= range_[1] and range_[2] <= y <= range_[3]:
            return 'mid'
    for range_ in bottom_ranges:
        if range_[0] <= x <= range_[1] and range_[2] <= y <= range_[3]:
            return 'bottom'
    for range_ in blue_zone:
        if range_[0] <= x <= range_[1] and range_[2] <= y <= range_[3]:
            return 'blue_zone'
    for range_ in red_zone:
        if range_[0] <= x <= range_[1] and range_[2] <= y <= range_[3]:
            return 'red_zone'
    return 'jungle' # 나머지는 jungle



# 전체적인 참여도 Radar chart 
def radar_chart(match_info):
    score = match_info[['summonerName','visionScore','damageSelfMitigated','totalCS',
                        'totalDamageDealtToChampions','damageDealtToObjectives']]
    

    score_mean = score.mean(numeric_only=True).to_frame().T
    score_mean['summonerName'] = '평균'
    score = pd.concat([score, score_mean], ignore_index=True)
    score.columns = ['summonerName','시야점수','막은피해','CS','공격','오브젝트']
    normalization_df = (score - score.min(numeric_only=True))/(score.max(numeric_only=True) - score.min(numeric_only=True))
    normalization_df['summonerName'] = score['summonerName']
    melted_df = pd.melt(normalization_df, id_vars=["summonerName"], var_name="var", value_name="value")
    
    # nivo chart 데이터 형태에 맞게 pivot to dict
    pivoted_df = melted_df.pivot(index="var", columns="summonerName", values="value").reset_index() 
    radar_data = pivoted_df.to_dict("records")


    return radar_data



# item에 대한 정보  
def get_item_gold():
    item_gold = 'https://ddragon.leagueoflegends.com/cdn/13.8.1/data/ko_KR/item.json'
    response = requests.get(item_gold)
    json_data = response.json()

    gold_data = {}
    for item_id, item_data in json_data['data'].items():
        gold = item_data.get('gold')
        name = item_data.get('name')
        if gold:
            base = gold.get('base')
            total = gold.get('total')
            sell = gold.get('sell')
            gold_data[item_id] = {'name': name,'base':base, 'total': total, 'sell': sell}
    
    item_gold = pd.DataFrame.from_dict(gold_data, orient='index')[['name','base','total','sell']]
    item_gold = item_gold.reset_index().rename(columns={'index': 'itemId'})
    item_gold['itemId'] = item_gold['itemId'].astype('float64')
    
    return item_gold


# champion skill 정보
def get_spell_info(champion_info, puuid):
    
    summoner_champion = champion_info.loc[champion_info['puuid'] == puuid, 'championName'].iloc[0]

    url = f'https://ddragon.leagueoflegends.com/cdn/13.8.1/data/ko_KR/champion/{summoner_champion}.json'
    response = requests.get(url)
    champion = response.json()


    spells = champion['data'][summoner_champion]['spells']
    spell_data = []

    for spell in spells:
        spell_id = spell['id']
        spell_name = spell['name']
        spell_data.append({'spellid': spell_id, 'kr_spell': spell_name})
    
    spell_info = pd.DataFrame(spell_data)
    new_row = {'spellid': f'{summoner_champion}BasicAttack', 'kr_spell': '기본공격', 'spellName': f'{summoner_champion}basicattack'}   
    spell_info = pd.concat([spell_info, pd.DataFrame([new_row])], ignore_index=True)
    spell_info['spellName'] = spell_info['spellid'].str.lower()
    
    return spell_info



# var_ = ['totalDamageTaken','death','totalTimeSpentDead']


# 포지션별 점수 
def score_weighted(match_info):
    # 가중치를 부여한 점수 계산 함수 정의, MID/BOTTOM/TOP
   
    weights = {
        # ----- 공격성 지표 비중 40%
                'totalDamageDealtToChampions': 0.15, 
                'soloKills': 0.15,    
                'multikills': 0.05, 
                'kda': 0.05, 

        # ----- 오브젝트 지표 비중 30% 
                'goldEarned':0.05,
                'totalCS': 0.05,
                'damageDealtToTurrets': 0.1,
                'damageDealtToObjectives': 0.1, 
                'dragonTakedowns':0.01,
                'baronTakedowns':0.01,
                 
        # ----- 보조/CC/서포터 지표 비중 30 %
                'damageSelfMitigated': 0.15, 
                'visionScore': 0.1,  
                'enemyChampionImmobilizations':0.05 , 
                'effectiveHealAndShielding':0.01 
           } 
 
    # jungle
    weights_JUNGLE = {
        # ----- 공격성 지표 비중 40%
                'totalDamageDealtToChampions': 0.15, 
                'soloKills': 0.05,  
                'multikills': 0.05, 
                'kda': 0.15, 

        # ----- 오브젝트 지표 비중 40%
                'damageDealtToTurrets': 0.1,
                'damageDealtToObjectives': 0.1, 
                'dragonTakedowns':0.05,
                'baronTakedowns':0.05,
                'totalCS': 0.1,  
                'goldEarned':0.05,

        # ----- 보조/CC/서포터 지표 비중 20%
                'damageSelfMitigated': 0.05,
                'visionScore': 0.1,  
                'enemyChampionImmobilizations':0.05 , 
                'effectiveHealAndShielding':0.01

            } # (0.01)'effectiveHealAndShielding': 0.01
    
 
    # 4 : 6
    weights_utility = {
        # ----- 공격성 지표 비중 20%
                'kda': 0.15,  
                'totalDamageDealtToChampions': 0.05, 
                'soloKills': 0.01, 
                'multikills': 0.01,  

        # ----- 오브젝트 지표 비중 15%
                'goldEarned':0.05,
                'totalCS': 0.001,   
                'damageDealtToObjectives': 0.05, 
                'damageDealtToTurrets': 0.05 , 
                'dragonTakedowns':0.001,
                'baronTakedowns':0.001,

        # ----- 보조/CC/서포터 지표 비중 65%
                'visionScore': 0.2,  #                
                'effectiveHealAndShielding' : 0.2,
                'enemyChampionImmobilizations': 0.2,
                'damageSelfMitigated': 0.05, 
                } 
    

    # 점수 계산에 사용할 변수 선택
    match_score = match_info[['summonerName','championName' ,'totalDamageDealtToChampions', 'damageDealtToObjectives', 'totalCS',
                              'soloKills', 'multikills', 'visionScore', 
                              'enemyChampionImmobilizations','damageDealtToTurrets', 'damageSelfMitigated','dragonTakedowns','baronTakedowns',
                               'effectiveHealAndShielding','kda','goldEarned']] #'effectiveHealAndShielding'
    # 표준화할 변수 선택
    cols_to_standardize = ['totalDamageDealtToChampions', 'damageDealtToObjectives', 'totalCS', 'soloKills', 'multikills','dragonTakedowns','baronTakedowns',
                           'kda' ,'goldEarned','visionScore', 'enemyChampionImmobilizations', 'damageSelfMitigated','damageDealtToTurrets','effectiveHealAndShielding']

    # position에 따른 가중치 지정
    if 'UTILITY' in match_info['teamPosition'].values:
        weights = weights_utility

    if 'JUNGLE' in match_info['teamPosition'].values:
        weights = weights_JUNGLE

    # StandardScaler 객체 생성
    scaler = StandardScaler()

    # 표준화할 변수들만 추출해서 표준화 수행
    match_score[cols_to_standardize] = scaler.fit_transform(match_score[cols_to_standardize])

    # 각 변수에 가중치를 곱해서 점수 계산
    for col in weights.keys():
        match_score[col] = match_score[col] * weights[col]

    # 점수 총합 계산
    valid_columns = match_score.select_dtypes(include='number').columns
    total_score = match_score[valid_columns].iloc[:, 1:].sum(axis=1)

    # 총합이 가장 높은 참가자에게 100점
    max_score = total_score.max()
    match_score['score'] = total_score.apply(lambda x: x / max_score * 100)

    # 점수 순위 계산
    match_score['rank'] = match_score['score'].rank(ascending=False)
    match_info_score = match_info.copy()  
    match_info_score['rank'] = match_score['rank']  # 새로운 데이터프레임에 'rank' 열 추가
    

    return total_score,match_score



def score3 (match_score):
    score_attack = match_score[['championName',
                                'totalDamageDealtToChampions','soloKills','multikills','kda']]
    score_object = match_score[['championName','damageDealtToTurrets','damageDealtToObjectives','dragonTakedowns',
                                'baronTakedowns','totalCS','goldEarned']]
    score_util = match_score[['championName','visionScore','effectiveHealAndShielding',
                                'enemyChampionImmobilizations','damageSelfMitigated' ]]                


    score_attack['attack_score'] = score_attack.sum(numeric_only=True, axis=1)
    score_object['object_score'] = score_object.sum(numeric_only=True, axis=1)
    score_util['util_score'] = score_util.sum(numeric_only=True, axis=1)
    score_3 = score_attack[['championName', 'attack_score']].merge(score_object[['championName', 'object_score']], on='championName').merge(score_util[['championName', 'util_score']], on='championName')

    # MinMaxScaler를 사용해 attackscore, objectscore, utilscore 값을 1부터 10까지의 값으로 변환
    scaler = MinMaxScaler(feature_range=(1, 10))
    score_3[["attack_score", "object_score", "util_score"]] = scaler.fit_transform(score_3[["attack_score", "object_score", "util_score"]])
    return score_3
