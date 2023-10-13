# api_key
# from dotenv import load_dotenv
# import os
# load_dotenv()
# api_key = os.getenv('api_key')

# chart 
import streamlit as st
from streamlit_elements import dashboard
import plotly.graph_objects as go
from streamlit_elements import nivo, elements, mui
import plotly.express as px


# RIOT.PY
from riot import get_match_data_log, get_rank_info, get_match_v5, get_moving_data, get_events,create_animation,calculate_lane
from riot import get_logs_all, radar_chart, get_item_gold, get_damage_logs, score_weighted, get_spell_info, score3

import pandas as pd
import streamlit.components.v1 as components
import matplotlib as mpl

# -------------------------------------------- main -----------------------------------------------------
pd.set_option('mode.chained_assignment',  None)
st.set_page_config(layout="wide",page_title = "League Of Legends report dash board")


with open( "css/main_css.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)


mpl.rcParams['animation.embed_limit'] = 40 # 단위: MB


st.title('League Of Legends')
st.subheader('Report dash board')
st.caption('신고된 경기의 데이터를 기반으로 유저의 제제여부를 결정할 수 있는 대시보드입니다. 경기가 끝나고 신고를했다는 가정이므로 가장 최근에 진행한 경기의 정보가 나옵니다.😀')

# 사이드바
with st.sidebar:
    with st.form(key ='searchform'):
        summoner_name = st.text_input("search_summoner")
        api_key = st.text_input("api_key",
                                type = "password"
                               )
        st.markdown("---")
        st.write('유저 신고 사유')
        clue = st.checkbox(label="All")
        st.checkbox(label="고의적으로 적에게 죽음", value=clue)
        st.checkbox(label="게임에 참가하지 않음(잠수)", value=clue)
        st.checkbox(label= "부정적인 태도")
        st.checkbox(label= "핵 사용 의심", value=clue)
        st.text_area("자세한 내용을 적어주세요")
        submit_search = st.form_submit_button()



if submit_search :
    try:
        puuid, summoner_id, match_ids, match_data_log = get_match_data_log(summoner_name, api_key)
        rank_data  = get_rank_info(summoner_id,api_key)
        match_info, df, summoner_position, champion_info, game_duration =  get_match_v5(match_ids, puuid ,api_key)
        id_df, participant_ids, summoner_participantId, moving = get_moving_data(match_data_log,puuid)
        all_events, position_logs = get_events(match_data_log)
        
        radar_data = radar_chart(match_info)
        total_score, match_score, normalization_df = score_weighted(match_info)
        score_3  = score3(match_score)

        item_gold = get_item_gold()
        spell_info = get_spell_info(champion_info, puuid)

        df_k, logs_all, kill_damage, death_damage, assist_damage = get_logs_all (all_events,moving,summoner_participantId)
        death_damage_log, counter_damage_log, damage_counter, kill_damage_log, assist_damage_log, kda_dmg_log = get_damage_logs(death_damage, kill_damage, assist_damage)

        champion_images, ani = create_animation(participant_ids,puuid,champion_info,logs_all)
        html = ani.to_jshtml()



    #  ------------------------------- session ------------------------- 
        st.session_state.puuid = puuid
        st.session_state.rank_data = rank_data
        st.session_state.summoner_name = summoner_name
        st.session_state.champion_info = champion_info
        st.session_state.match_info = match_info

        st.session_state.match_ids = match_ids
        st.session_state.df = df
        st.session_state.summoner_participantId = summoner_participantId
        st.session_state.summoner_position = summoner_position
        st.session_state.game_duration = game_duration

        st.session_state.moving = moving
        st.session_state.position_logs = position_logs

        st.session_state.logs_all = logs_all
        st.session_state.df_k = df_k
        st.session_state.radar_data = radar_data
        st.session_state.match_score = match_score
        st.session_state.score_3 = score_3

        st.session_state.item_gold = item_gold
        st.session_state.spell_info = spell_info
        st.session_state.all_events = all_events

        st.session_state.death_damage = death_damage
        st.session_state.death_damage_log = death_damage_log

        st.session_state.counter_damage_log = counter_damage_log
        st.session_state.damage_counter = damage_counter

        st.session_state.kill_damage = kill_damage
        st.session_state.assist_damage = assist_damage
        st.session_state.kill_damage_log = kill_damage_log
        st.session_state.assist_damage_log = assist_damage_log
        st.session_state.kda_dmg_log = kda_dmg_log

        st.session_state.champion_images = champion_images
        st.session_state.html = html

    except Exception as e:
            st.markdown('''
                        --- 
                        ### 🚨 :red[Error]: RIOT_APIkey와 유저 닉네임을 확인해주세요🥹.
                        ''')
            # 에러가 발생하면 세션 초기화
            st.session_state.clear()





#  ------------------------------------------------------------------

if hasattr(st.session_state, 'puuid'):
    puuid = st.session_state.puuid


if hasattr(st.session_state, 'summoner_name'):
    summoner_name = st.session_state.summoner_name

if hasattr(st.session_state, 'df'):
    df = st.session_state.df

if hasattr(st.session_state, 'rank_data'):
    rank_data = st.session_state.rank_data
    try:
        if rank_data:
            tier = rank_data[0]['tier']
            rank = rank_data[0]['rank']
            wins = rank_data[0]['wins']
            losses = rank_data[0]['losses']

            wins = sum([entry['wins'] for entry in rank_data])
            losses = sum([entry['losses'] for entry in rank_data])
            win_lose = [
                {"id": "Wins", "label": "Wins", "value": wins},
                {"id": "Losses", "label": "Losses", "value": losses}
            ]
        else:
            win_lose = []
    except:
        win_lose = []


if hasattr(st.session_state, 'all_events'):
    all_events = st.session_state.all_events

if hasattr(st.session_state, 'match_ids'):
    match_ids = st.session_state.match_ids
    match_id = match_ids[0]
    
if hasattr(st.session_state, 'champion_info'):
    champion_info = st.session_state.champion_info

if hasattr(st.session_state, 'df_k'):
    df_k = st.session_state.df_k

if hasattr(st.session_state, 'item_gold'):
    item_gold = st.session_state.item_gold

if hasattr(st.session_state, 'summoner_participantId'):
    summoner_participantId = st.session_state.summoner_participantId

if hasattr(st.session_state, 'champion_images'):
    champion_images = st.session_state.champion_images

if hasattr(st.session_state, 'game_duration'):
    game_duration = st.session_state.game_duration

# 스펠 정보
if hasattr(st.session_state, 'spell_info'):
    spell_info = st.session_state.spell_info
    q = spell_info['spellid'].iloc[0]
    w = spell_info['spellid'].iloc[1]
    e = spell_info['spellid'].iloc[2]
    r = spell_info['spellid'].iloc[3]
    kr_q = spell_info['kr_spell'].iloc[0]
    kr_w = spell_info['kr_spell'].iloc[1]
    kr_e = spell_info['kr_spell'].iloc[2]
    kr_r = spell_info['kr_spell'].iloc[3]

# AFK 여부
if hasattr(st.session_state, 'moving'):
    moving = st.session_state.moving
    summoner_moving = moving[moving['participantId'] == summoner_participantId][['participantId','level','xp','position','timestamp']]

    is_afk = False
    for xp, group in summoner_moving.groupby('xp'):
        if len(group) > 10:  # 10분 이상 아무런 행동을 하지 않은 경우
            is_afk = True
            afk = "10분 ▲"
            break
        elif len(group) > 5:  # 5분 이상 아무런 행동을 하지 않은 경우
            is_afk = True
            afk = "5분 ▲"
            break

    if not is_afk:
        afk = "X"


if hasattr(st.session_state, 'summoner_position'):
    summoner_position = st.session_state.summoner_position
    summoner_position_low = summoner_position.lower()

#  --------------------- spell name/e ------------------------------------------------------------------------- #

spell = {'21': 'SummonerBarrier', '1': 'SummonerBoost', 
         '14': 'SummonerDot', '3': 'SummonerExhaust', 
         '4': 'SummonerFlash', '6': 'SummonerHaste', 
         '7': 'SummonerHeal', '13': 'SummonerMana', 
         '30': 'SummonerPoroRecall', '31': 'SummonerPoroThrow', 
         '11': 'SummonerSmite', '39': 'SummonerSnowURFSnowball_Mark', 
         '32': 'SummonerSnowball', '12': 'SummonerTeleport', 
         '54': 'Summoner_UltBookPlaceholder', '55': 'Summoner_UltBookSmitePlaceholder'}

# ------------------ MAIN match 요약  / champion / spell / item  ----------------------------------------------- #


if hasattr(st.session_state, 'match_info'):
    match_info = st.session_state.match_info
    summoner_match_info = match_info[(match_info['puuid'] == puuid)][['matchId','win','teamId','championName',
                                                                    'summonerName','participantId','teamPosition','summoner1Id','summoner2Id',
                                                                    'kills','deaths','assists',
                                                                    'item0','item1','item2','item3','item4','item5','item6','timePlayed']]
    
    summoner_match_info['summoner1Id'] = summoner_match_info['summoner1Id'].apply(lambda x: spell.get(str(x), 'Unknown'))
    summoner_match_info['summoner2Id'] = summoner_match_info['summoner2Id'].apply(lambda x: spell.get(str(x), 'Unknown'))
    
    summoner_team = summoner_match_info['teamId'].iloc[0]
    sum_team_death = match_info[match_info['teamId'] == summoner_team]['deaths'].sum()
    sum_team_kills = match_info[match_info['teamId'] == summoner_team]['kills'].sum()

    k = match_info.loc[match_info['puuid'] == puuid, 'kills'].iloc[0]
    d = match_info.loc[match_info['puuid'] == puuid, 'deaths'].iloc[0]
    a = match_info.loc[match_info['puuid'] == puuid, 'assists'].iloc[0]

    kda = round(match_info.loc[match_info['puuid'] == puuid, 'kda'].iloc[0],1)
    kill_per = round(((k+a)/ sum_team_kills)*100, 0)
    
    timeplayed = match_info['timePlayed'].iloc[0] // 60  # 초 단위에서 분 단위로 변환
    game = summoner_match_info['win'].iloc[0]
    
    summoner_champion = summoner_match_info['championName'].iloc[0]


# -- item image
    item0,item1,item2,item3,item4,item5,item6 = summoner_match_info[['item0','item1','item2','item3','item4','item5','item6']].iloc[0]

# -- spell image
    spell1, spell2 = summoner_match_info[['summoner1Id', 'summoner2Id']].iloc[0]

if hasattr(st.session_state, 'match_score'):
    match_score = st.session_state.match_score
    # st.write(match_score)
    rnk = match_score[match_score['championName'] == summoner_champion]['rank'].iloc[0].astype(int)
    # st.write(rnk)

# --- 소환사 info card 

        

    st.divider()
    
# score
if hasattr(st.session_state, 'score_3'): 
    score_3 = st.session_state.score_3
    score_atk = round(score_3[score_3['championName'] == summoner_champion]['attack_score'].iloc[0],1) 
    score_obj = round(score_3[score_3['championName'] == summoner_champion]['object_score'].iloc[0],1) 
    score_util = round(score_3[score_3['championName'] == summoner_champion]['util_score'].iloc[0],1) 
    score_total = round(score_atk + score_obj + score_util,1)

    

# ------ RADAR 차트 , 참여도/ 포지션 점수
if hasattr(st.session_state, 'spell_info'):
    spell_info = st.session_state.spell_info
if hasattr(st.session_state, 'kda_dmg_log'):
    kda_dmg_log = st.session_state.kda_dmg_log


    if not kda_dmg_log.empty:  

        # kill/assist (딜관점)비중
        kda_dmg_log = kda_dmg_log[kda_dmg_log['name'] == summoner_champion]
        
        kdl = kda_dmg_log.groupby('name').agg({'magicDamage': 'sum', 'physicalDamage': 'sum', 'trueDamage': 'sum'}).reset_index()
        kdl['total'] = kdl[['magicDamage', 'physicalDamage', 'trueDamage']].sum(axis=1)

        # 스킬 맞춘 횟수
        kdl_summoner = kda_dmg_log[kda_dmg_log['name'] == summoner_champion] 
        kdl_summoner['spellName'] = kdl_summoner['spellName'].apply(lambda x: next((i for i in spell_info['spellName'] if i in x), x))
        kdl_skill = kdl_summoner.groupby('spellName').size().reset_index(name='count')  

        merged_kill = pd.merge(kdl_skill, spell_info, on='spellName') 
        merged = merged_kill.to_dict('records')
        # st.write(merged)
    else:
        merged = []



    with st.container():
        st.subheader("🎮 결과 내용 요약")
        st.caption(f" {summoner_name} ({summoner_champion}/{summoner_position}) 소환사님의 {match_id} 경기 결과입니다. ")
        col1,col2 = st.columns([1.2,2])
        with col1: 
            if hasattr(st.session_state, 'radar_data'):
                radar_data = st.session_state.radar_data
                user = champion_info[champion_info['puuid']== puuid]['summonerName'].iloc[0]
                with elements("info/radar"):
                    layout = [
                              dashboard.Item("first_item", 0, 0, 2, 1.1,isDraggable=True, isResizable=False ),
                              dashboard.Item("second_item", 2, 0, 2, 3,isDraggable=True, isResizable=False ),
                              dashboard.Item("third_item", 4, 0, 2, 1,isDraggable=True, isResizable=False ),]
                    card_sx = {"background-color":"#0a0a0adb","borderRadius": "23px", "outline": "1px solid #31323b"}
                    with dashboard.Grid(layout):
                        mui.Card( # 챔피언,스펠,kda,게임결과,시간,탈주여부, 아이템
                            children=[
                                mui.CardContent( 
                                    sx={
                                        "display": "flex",
                                        "align-items": "center",
                                        "text-align":"center",
                                        "padding": "0 8px 0 8px",
                                        "gap" : 2
                                        
                                    },
                                    children=[
                                        mui.CardMedia( # 챔피언
                                            sx={
                                                "height": 80,
                                                "width": 80,
                                                "borderRadius": "10%",
                                                "backgroundImage": f"url(https://ddragon.leagueoflegends.com/cdn/13.9.1/img/champion/{summoner_champion}.png)",  
                                            },
                                        ),

                                        mui.CardContent( # 스펠
                                            sx={
                                                "align-items": "center",
                                                "padding-top": "10px",
                                                "padding-bottom" : "10px",
                                                "padding-right" : "5px",
                                                "padding-left" : "5px"
                                            },
                                            children=[
                                                mui.CardMedia( # 스펠1
                                                    sx={
                                                        "height": 40,
                                                        "width": 40,
                                                        "borderRadius": "10%",
                                                        "backgroundImage": f"url(https://ddragon.leagueoflegends.com/cdn/13.8.1/img/spell/{spell1}.png)",
                                                        "align-self": "center",
                                                        "outline": "1px solid #31323b",

                                                    },
                                                    title=f"{spell1}",
                                                ),
                                                mui.CardMedia( # 스펠2
                                                    sx={
                                                        "height": 40,
                                                        "width": 40,
                                                        "borderRadius": "10%",
                                                        "backgroundImage": f"url(https://ddragon.leagueoflegends.com/cdn/13.8.1/img/spell/{spell2}.png)",
                                                        "align-self": "center",
                                                        "outline": "1px solid #31323b",

                                                    },
                                                    title=f"{spell2}",
                                                ),
                                            ],
                                        ),
                                        mui.Divider(orientation="vertical",sx={"height": "100px"}),

                                        mui.Box( # KDA/시간/
                                            sx={
                                                "border-top-width": "8px",
                                            },
                                            children=[
                                                mui.Typography(
                                                    "KDA",
                                                    variant = "body2",
                                                    color="text.secondary",

                                                ),                                        
                                                mui.Typography(
                                                    f"{k}/{d}/{a}",
                                                    variant="body2",
                                                    sx={"font-size":"18px",
                                                        }
                                                ),
                                                mui.Typography(
                                                    "miniute",
                                                    variant="body2",
                                                    color="text.secondary"
                                                ),
                                                mui.Typography(
                                                    f"{timeplayed}"
                                                )
                                            ]                               
                                        ),
                                        mui.Divider(orientation="vertical",sx={"height": "100px"}),

                                        mui.Box( # 게임결과 

                                            children=[
                                                mui.Typography(                                                    
                                                    "Results",
                                                    color="text.secondary",
                                                    sx={"font-size":"18px"},
                                                ),
                                                mui.Typography(
                                                    f"{game}",
                                                    variant="body3",
                                                    sx={"font-size":"20px"}
                                                )
                                            ]
                                        ),
                                        mui.Divider(orientation="vertical",sx={"height": "100px"}),

                                        mui.Box( # 탈주여부
                                            children = [
                                                mui.Typography(
                                                    "AFK",
                                                    color="text.secondary",
                                                    sx={'font-size':"18px"}
                                                ),
                                                mui.Typography(
                                                    f"{afk}",
                                                    variant="body3",
                                                    sx={"font-size":"20px",
                                                        "color": "red" if afk == "10분▲" or afk == "5분▲" else "white",
                                                    }
                                                )
                                            ]
                                        ),

                                    ],
                                ),
                                mui.Divider(),
                                mui.CardContent( # item 0~6
                                    sx={               
                                        "padding-top":"10px",                  
                                        "display": "flex",
                                        "align-items": "center",
                                        "gap": 1,
                                    },
                                    children=[
                                        
                                        mui.CardMedia(
                                            sx={
                                                "height": 45,
                                                "width": 45,
                                                "borderRadius": "10%",
                                                "outline": "1px solid #31323b",
                                                "backgroundImage": f"url(https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-{summoner_position_low}.png)"
                                            },
                                            title = f'{summoner_position}'
                                        ),                                            
                                        mui.CardMedia(
                                            sx={
                                                "height": 45,
                                                "width": 45,
                                                "borderRadius": "10%",
                                                "outline": "1px solid #31323b",
                                                **({"backgroundImage": f"url(https://ddragon.leagueoflegends.com/cdn/13.9.1/img/item/{item0}.png)"}
                                                    if item0 != 0 else{}),
                                            },
                                        ),
                                        mui.CardMedia(
                                            sx={
                                                "height": 45,
                                                "width": 45,
                                                "borderRadius": "10%",
                                                "outline": "1px solid #31323b",
                                                **({"backgroundImage": f"url(https://ddragon.leagueoflegends.com/cdn/13.9.1/img/item/{item1}.png)"}
                                                    if item1 != 0 else{}),
                                            },
                                        ),
                                        mui.CardMedia(
                                            sx={
                                                "height": 45,
                                                "width": 45,
                                                "borderRadius": "10%",
                                                "outline": "1px solid #31323b",
                                                **({"backgroundImage": f"url(https://ddragon.leagueoflegends.com/cdn/13.9.1/img/item/{item2}.png)"}
                                                    if item2 != 0 else{}),
                                            },
                                        ),
                                        mui.CardMedia(
                                            sx={
                                                "height": 45,
                                                "width": 45,
                                                "borderRadius": "10%",
                                                "outline": "1px solid #31323b",
                                                **({"backgroundImage": f"url(https://ddragon.leagueoflegends.com/cdn/13.9.1/img/item/{item3}.png)"}
                                                    if item3 != 0 else{}),
                                            },
                                        ),
                                        mui.CardMedia(
                                            sx={
                                                "height": 45,
                                                "width": 45,
                                                "borderRadius": "10%",
                                                "outline": "1px solid #31323b",
                                                **({"backgroundImage": f"url(https://ddragon.leagueoflegends.com/cdn/13.9.1/img/item/{item4}.png)"}
                                                    if item4 != 0 else{}),
                                            },
                                        ),
                                        mui.CardMedia(
                                            sx={
                                                "height": 45,
                                                "width": 45,
                                                "borderRadius": "10%",
                                                "outline": "1px solid #31323b",
                                                **({"backgroundImage": f"url(https://ddragon.leagueoflegends.com/cdn/13.9.1/img/item/{item5}.png)"}
                                                    if item5 != 0 else{}),
                                            },
                                        ),                                   
                                        mui.CardMedia(
                                            sx={
                                                "height": 30,
                                                "width": 30,
                                                "borderRadius": "30%",
                                                "outline": "1px solid #31323b",
                                                **({"backgroundImage": f"url(https://ddragon.leagueoflegends.com/cdn/13.9.1/img/item/{item6}.png)"}
                                                    if item6 != 0 else{}),
                                            },
                                        ),
                                    ],
                                ),
                            ],
                            key="first_item",sx=card_sx
                        )

                        mui.Card( # radar charts
                            children = [
                                mui.Typography(
                                " Radar Charts ",
                                variant="h5",
                                sx={
                                    "padding-left": "20px",
                                    "padding-top": "20px"} 
                                ),

                            nivo.Radar(
                                data=radar_data,
                                keys=[user,'평균'],
                                
                                indexBy="var",
                                valueFormat=">-.2f",
                                maxValue={1.1},
                                margin={ "top": 70, "right": 80, "bottom": 70, "left": 80 },
                                borderColor={ "from": "color" },
                                gridShape="linear",
                                gridLevels={4},
                                gridLabelOffset=15,
                                dotSize=8,
                                dotColor={ "theme": "background" },
                                dotBorderWidth=2,
                                motionConfig="wobbly",
                                legends=[
                                    {
                                        "anchor": "top-left",
                                        "direction": "column",
                                        "translateX": -50,
                                        "translateY": -40,
                                        "itemWidth": 120,
                                        "itemHeight": 20,
                                        "itemTextColor": "white",
                                        "symbolSize": 12,
                                        "symbolShape": "circle",
                                        "effects": [
                                            {
                                                "on": "hover",
                                                "style": {
                                                    "itemTextColor": "white"
                                                }
                                            }
                                        ]
                                    }
                                ],
                                theme={
                                    "textColor": "white",
                                    "tooltip": {
                                        "container": {
                                            "background": "#262730",
                                            "color": "white",
                                        }
                                    }
                                }
                            ),
                            
                            ]
                            ,key="second_item",sx=card_sx)

        with col2: 
            with elements("dashboard"):

                layout = [
                    # Parameters: element_identifier, x_pos, y_pos, width, height, [isDraggable=False, moved=False (사이즈/이동 가능)]
                    dashboard.Item("first_item", 0, 0, 2.5, 3), #isDraggable=False, moved=False 
                    dashboard.Item("second_item", 2.5, 0, 3.5, 2),
                    dashboard.Item("third_item", 0, 0, 2.5, 1),
                    dashboard.Item("forth_item", 2.5, 2, 3.5, 2)]                

                with dashboard.Grid(layout):
                    mui.Card( # 스코어점수(참여도)
                            children=[      
                                mui.CardMedia( # 챔피언paper
                                    sx={ "height": 100,
                                        "backgroundImage": f"linear-gradient(rgba(0, 0, 0, 0), rgba(0,0,0,1)),url(https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{summoner_champion}_0.jpg)",
                                        "backgroundPosition": "top"
                                        },
                                    
                                    title = 'champimage'
                                        ),
                                mui.CardContent( # 설명
                                    children=[  
                                        mui.Typography(
                                            " 참여도 ",
                                            variant="h5",
                                            component="div"
                                        ),
                                        mui.Typography(
                                            "유저의 게임 참여도를 포지션에 따라 가중치를 부여해서 측정합니다. 각 지표별 10점을 기준으로  \
                                            크게 공격성, 오브젝트, 서포터 점수로 나뉘어집니다. \
                                                ",
                                            variant="body2",
                                            color="text.secondary",
                                            sx={"mb":2,
                                                "font-size": "12px"},
                                            
                                        )]
                                    ),
                                
                                mui.Box(# score
                                        sx={"display": "flex",
                                            "gap": "35px",
                                            "padding" : "0",
                                            "font-size" : "25px",
                                            "justify-content": "center",  
                                            },

                                    children=[  
                                        mui.Typography(
                                            " Attack ",
                                            variant="body3",
                                            color="text.secondary"
                                        ),

                                        mui.Typography(
                                            " Object ",
                                            variant="body3",
                                            color="text.secondary"
                                        ),
                                        mui.Typography(
                                            " Utility ",
                                            variant="body3",
                                            color="text.secondary"
                                        )]
                                    ),

                                mui.CardContent(# score_value
                                        sx={"display": "flex",
                                            "gap": "50px",
                                            "padding": "10px",
                                            "justify-content": "center",
                                            },

                                    children = [
                                        mui.Typography(
                                            f'{score_atk}',
                                            sx={"font-size" : "35px"}
                                        ),
                                        mui.Typography(                               
                                            f'{score_obj}',
                                            sx={"font-size" : "35px"}
                                        ),
                                        mui.Typography(
                                            f'{score_util}',
                                            sx={"font-size" : "35px"}

                                        )]
                                    ) ,
                               
                                mui.Divider(sx={"border-width":"1px"}),

                                mui.CardContent(# total/ 팀 등수?
                                        sx={
                                            "text-align":"center"},
                                    children = [
                                        mui.Typography(
                                            "Total score / rank",
                                            variant='h5',
                                            color="text.secondary"
                                        ),
                                        mui.Typography(
                                            f"{score_total} / {rnk}",
                                            sx={"font-size":"58px"}

                                        )
                                    ]
                                )                                                        
                                    
                            ] , key="first_item",elevation=0, sx=card_sx)
                    
                    mui.Card( #skill
                            children=[      
                                mui.CardMedia( # background img
                                    sx={ "height": 100,
                                        "backgroundImage": f"linear-gradient(rgba(0, 0, 0, 0), rgba(0,0,0,1)),url(https://get.wallhere.com/photo/League-of-Legends-jungle-Terrain-screenshot-atmospheric-phenomenon-computer-wallpaper-284470.jpg)"},
                                    title = 'champimage'
                                        ),

                                mui.CardContent( # skill text
                                    children=[  
                                        mui.Typography(
                                            "스킬활용로그",
                                            variant="h5",
                                            component="div"
                                        ),
                                        mui.Typography(
                                            f"{summoner_name}({summoner_champion})의 스킬 로그 입니다. \
                                                유저가 kill/death/assist를 했을 때 기록되었으며, 유저가 전반적으로 맞춘 스킬횟수를 확인합니다.",
                                            sx={
                                                "font-size": "14px"
                                                  },
                                            color="text.secondary"
                                        )]
                                       ),

                                mui.CardContent( #spell_img
                                    sx={
                                        "display": "flex",
                                        "gap": "30px",  # 이미지 간격 조절
                                        "padding":0,
                                        "justify-content": "center",
                                        },
                                        
                                    children = [
                                        mui.CardMedia(
                                            sx={ "height": 60, "width":60,
                                                "borderRadius": '20%', 
                                                "backgroundImage": f"url(https://ddragon.leagueoflegends.com/cdn/13.9.1/img/spell/{q}.png)",
                                                },
                                            title=f"Q:{kr_q}"
                                        ),
                                        mui.CardMedia(
                                            sx={ "height": 60, "width":60,
                                                "borderRadius": '20%', 
                                                "backgroundImage": f"url(https://ddragon.leagueoflegends.com/cdn/13.9.1/img/spell/{w}.png)",
                                                },
                                            title=f"W:{kr_w}"
                                               
                                        ),
                                        mui.CardMedia(
                                            sx={ "height": 60, "width":60,
                                                "borderRadius": '20%', 
                                                "backgroundImage": f"url(https://ddragon.leagueoflegends.com/cdn/13.9.1/img/spell/{e}.png)",
                                                },
                                            title=f'E:{kr_e}'
                                        ),
                                        mui.CardMedia(
                                            sx={ "height": 60, "width":60,
                                                "borderRadius": '20%', 
                                                "backgroundImage": f"url(https://ddragon.leagueoflegends.com/cdn/13.9.1/img/spell/{r}.png)",
                                                },
                                            title=f'R:{kr_r}'
                                        ),

                                            ]
                                        ),

                                    ] , 
                            
                                        key="second_item",elevation=0, sx=card_sx)

                    if win_lose:

                        mui.Card(# 승률
                            nivo.Pie( 
                                data=win_lose,
                                margin={"top": 8, "right": 30, "bottom": 20, "left": 20 },
                                innerRadius={0.5},
                                padAngle={2},
                                activeOuterRadiusOffset={8},
                                colors=['#459ae5', '#ed4141'],                   
                                borderWidth={1},
                                borderColor={
                                    "from": 'color',
                                    "modifiers": [
                                        [
                                            'darker',
                                            0.2,
                                            'opacity',
                                            0.6
                                        ]
                                    ]
                                },
                                enableArcLinkLabels=False,
                                arcLinkLabelsSkipAngle={10},
                                arcLinkLabelsTextColor="white",
                                arcLinkLabelsThickness={0},
                                arcLinkLabelsColor={ "from": 'color', "modifiers": [] },
                                arcLabelsSkipAngle={10},
                                arcLabelsTextColor={ "theme": 'background' },
                                legends=[
                                    {
                                        "anchor": "bottom",
                                        "direction": "row",
                                        "translateX": 0,
                                        "translateY": 20,
                                        "itemWidth": 50,
                                        "itemsSpacing" : 5,
                                        "itemHeight": 20,
                                        "itemTextColor": "white",
                                        "symbolSize": 7,
                                        "symbolShape": "circle",
                                        "effects": [
                                            {
                                                "on": "hover",
                                                "style": {
                                                    "itemTextColor": "white"
                                                }
                                            }
                                        ]
                                    }
                                ],
                                theme={
                                    "background": "black",
                                    "textColor": "white",
                                    "tooltip": {
                                        "container": {
                                            "background": "#3a3c4a",
                                            "color": "white",
                                        }
                                    }
                                },
                            )
                            ,key="third_item",sx=card_sx)
                    else:
                        mui.Card(
                                mui.Typography(
                                        '(승률) 유저의 아이디가 변경되었거나, rank를 불러오는 api에 문제가 생겼습니다🥹',
                                    sx={
                                        "font-size": "14px"
                                            },
                                    color="text.secondary"                            
                                )                            
                            ,key="third_item",sx=card_sx)


                    if merged: #(nivo.bar)
                        mui.Card(
                            nivo.Bar(
                            data=merged,
                            keys=["count"],  # 막대 그래프의 그룹을 구분하는 속성
                            indexBy="kr_spell",  # x축에 표시할 속성

                            margin={"top": 20, "right": 30, "bottom": 70, "left": 30},
                            padding={0.5},

                            valueScale={ "type" : 'linear' },
                            indexScale={ "type": 'band', "round": 'true'},
                            borderRadius={5},
                            colors={ 'scheme': 'category10' },

                            innerRadius=0.3,
                            padAngle=0.7,
                            activeOuterRadiusOffset=8,
                            enableGridY= False,
                            axisLeft=None,  # Y축 단위 제거
                    
                            labelSkipWidth={2},
                            labelSkipHeight={36},
                            axisBottom={"tickSize": 0,
                                        "tickRotation": 90,
                                        },
                            theme={
                                    "background": "black",
                                    "textColor": "white",
                                    "tooltip": {
                                        "container": {
                                            "background": "#3a3c4a",
                                            "color": "white",
                                        }
                                    }
                                }                         
                            ),key = 'forth_item',sx=card_sx)
                    else:
                        mui.Card(
                               mui.CardContent(
                                    sx={
                                        "display": "flex",
                                        "gap": "30px",  # 이미지 간격 조절
                                        "justify-content": "center",
                                        },
                                        
                                    children = [
                                        mui.CardMedia(
                                            sx={ "height": 150, "width":150,
                                                "borderRadius": '20%', 
                                                "backgroundImage": "url(https://raw.communitydragon.org/latest/game/assets/loadouts/summoneremotes/champions/blitzcrank/blitzcrank_sad_confused_vfx.png)",
                                                }
                                        )]
                                    ),   

                                mui.CardContent(
                                        mui.Typography(
                                            " 측정 가능한 kill/assist 가 없습니다.",
                                            variant="body3",
                                            color="text.secondary"                                        
                                            )                                      
                                        )  ,key='forth_item', sx= card_sx)


    st.divider()    
    

# -------------------------------- XP / LEVEL / GOLD logs --------------------------------------------------------#

if hasattr(st.session_state, 'moving'):
    moving = st.session_state.moving
    t = moving[moving['participantId'] == summoner_participantId][['timestamp','participantId','position','xp','level']]

    gold = moving[['timestamp','participantId','currentGold','totalGold']]
    # teamid / summonerName 추가 (team 구분)
    gold['teamId'] = gold['participantId'].apply(lambda x: 'blue' if x <= 5 else 'red')
    gold_merge = gold.merge(champion_info[['participantId', 'summonerName']], on='participantId', how='left')
    gold_merge['timestamp'] = gold_merge['timestamp']/60000  # 분단위

    with st.container():
        st.header('GOLD')
        col1,col2 = st.columns(2)
        with col1:
            if hasattr(st.session_state, 'moving'):
                moving = st.session_state.moving
                st.subheader('current gold')
                st.caption('시간별로 유저의 gold값 변동을 확인할 수 있습니다')

                team_option = st.selectbox('Select team', ['blue', 'red'])

                filtered_gold = gold_merge[gold_merge['teamId'] == str(team_option)]
                pivot_gold = filtered_gold.pivot(index='timestamp', columns='summonerName')

                tab1, tab2  = st.tabs(['currentGold','totalGold'])
                with tab1:
                    # st.write(pivot_gold)
                    st.area_chart(pivot_gold['currentGold'], use_container_width=True)
                with tab2:
                    st.line_chart(pivot_gold['totalGold'], use_container_width=True)
                
                # st.dataframe(gold_merge[gold_merge['participantId'] == summoner_participantId])

                    

        with col2:
            if hasattr(st.session_state, 'match_info'):
                match_info = st.session_state.match_info
                st.subheader('Earned/Spent Gold')
                st.caption('유저가 얻은 총 골드와 사용한 골드량 입니다.     ')

                fig = go.Figure()
                fig.add_trace(go.Bar(x=match_info['summonerName'], y=match_info['goldEarned'], name='goldEarned'))
                fig.add_trace(go.Bar(x=match_info['summonerName'], y=match_info['goldSpent'], name='goldSpent'))
                fig.update_layout(barmode='group',
                                # xaxis=dict(
                                #     tickmode='linear',
                                #     dtick=1
                                # ),
                                    xaxis_title='summonerName',
                                    yaxis_title='gold')
                st.plotly_chart(fig, use_container_width=True)


    # --------------------------------------- 이상치 탐지----------------------------------------------------- #

    with st.container():
            
    #------ 해당 summoner의 events_log 정리 (gold에 관한)
        summoner_gold = gold_merge[gold_merge['participantId']== summoner_participantId]
        summoner_events = all_events[(all_events['participantId']==summoner_participantId) | (all_events['killerId']==summoner_participantId)]
        summoner_events['timestamp'] = summoner_events['timestamp'] / 60000
        se = summoner_events[['timestamp','type','itemId','goldGain','bounty','level','skillSlot','killerId','victimId']]
        se_item = se.merge(item_gold, on='itemId', how='left')


    #------ 이동평균으로 이상치 탐지

        window_size = 5
        rolling_mean = summoner_gold['currentGold'].rolling(window_size).mean()

        # 표준편차 계산
        rolling_std = summoner_gold['currentGold'].rolling(window_size).std()

        # 이상치 점수 계산
        threshold = 2 # 이상치로 판단할 threshold
        z_score = (summoner_gold['currentGold'] - rolling_mean) / rolling_std
        z_score[abs(z_score) > threshold] = threshold # threshold 이상치 값으로 대체

        # 결과 출력
        result = pd.concat([summoner_gold['timestamp'], summoner_gold['currentGold'], rolling_mean, rolling_std, z_score], axis=1)
        result.columns = ['timestamp', 'currentGold', 'rolling_mean', 'rolling_std', 'z_score']
        outliers = summoner_gold[result['z_score'] >= 2]
        outliers_list_2 = outliers['timestamp'].tolist() # 이상치로 파악되는 시간 list

    #------ current GOLD 가 total GOLD 보다 많을수가 없음. 

        outliers_list_1 = summoner_gold[summoner_gold['currentGold'] > summoner_gold['totalGold']]['timestamp'].tolist() 

        if outliers_list_1: # 1차 구간 
            start_time = round(min(outliers_list_1) - 1,4) 
            end_time = round(max(outliers_list_1), 4) 
            selected_data = se_item.loc[(se_item['timestamp'] >= start_time) & (se_item['timestamp'] <= end_time)]
        # item log 정보추가        
            count = selected_data.groupby('type')['type'].count()
            # purchased_sum = selected_data[selected_data['type'] == 'ITEM_PURCHASED'].groupby('name')['total'].sum().sum()
            # destroyed_sum = selected_data[selected_data['type'] == 'ITEM_DESTROYED'].groupby('name')['base'].sum().sum()

            new_se = se.copy()
            new_se['timestamp'] = new_se['timestamp'].apply(lambda x: int(x))

            grouped_logs = new_se.groupby(['timestamp', 'type']).size().reset_index(name='count')

            # 각 timestamp에서의 로그별 빈도수를 계산
            pivot_type = pd.pivot_table(grouped_logs, values='count', index='timestamp', columns='type', fill_value=0)
            st.markdown(f'#### 이상치 구간 {start_time}~{end_time}')
            st.caption(' 해당구간에서 current gold 가 total gold를 넘어섰습니다. 비정상적인 행동이 의심됩니다.')
            st.line_chart(pivot_type, use_container_width=True)

            count = se_item.groupby('type')['type'].count()
            expander = st.expander("유저의 전체 LOG 보기")

            with expander:
                col1, col2 = st.columns([2,1]) # 두 개의 컬럼 생성
                col1.dataframe(se_item)
                col2.dataframe(count)

        elif outliers_list_2:
            start_time = round(min(outliers_list_2) - 1, 4) 
            end_time = round(max(outliers_list_2), 4) 
            selected_data = se.loc[(se['timestamp'] >= start_time) & (se['timestamp'] <= end_time)]
            logs_with_price = selected_data.merge(item_gold, on='itemId', how='left')
            st.markdown(f'#### outliers :  {start_time}~{end_time}')


        else :
            st.markdown('> 비정상적으로 판단되는 GOLD_LOG 가 없습니다.')
            count = se_item.groupby('type')['type'].count()

            new_se = se.copy()
            new_se['timestamp'] = new_se['timestamp'].apply(lambda x: int(x))

            grouped_logs = new_se.groupby(['timestamp', 'type']).size().reset_index(name='count')
            # 각 timestamp에서의 로그별 빈도수를 계산
            pivot_type = pd.pivot_table(grouped_logs, values='count', index='timestamp', columns='type', fill_value=0)
             
            expander = st.expander("유저의 전체 LOG 보기")
            with expander:
                col1, col2 = st.columns([2,1]) # 두 개의 컬럼 생성
                col1.dataframe(se_item)
                # col2.line_chart(pivot_type, use_container_width=True)
                col2.dataframe(count)

        st.divider()    

#  ------------------------------------- 이동경로 logs -------------------------------------------------- #

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        if hasattr(st.session_state, 'html'):
            html = st.session_state.html
            st.subheader("match animation")
            st.caption('해당 경기의 유저별 이동경로와 death 좌표입니다.')
            components.html(html, width=700, height=600)

    # 1분간격 position log
    with col2:
        if hasattr(st.session_state, 'moving'):
            moving = st.session_state.moving
            summoner_moving = moving[moving['participantId'] == summoner_participantId][['participantId','level','xp','position','timestamp']]
            summoner_moving.loc[:, 'lane'] = summoner_moving.apply(lambda row: calculate_lane(row['position']['x'], row['position']['y']), axis=1)

            lane_counts = summoner_moving['lane'].value_counts()
            # x축 범위와 label 정의
            x_range = ['top', 'mid', 'bottom', 'jungle', 'red_zone', 'blue_zone']
            lane_counts = lane_counts.reindex(x_range, fill_value=0)

            # 슬라이더 추가
            st.subheader('Position Log')
            st.caption(f'{summoner_name}({summoner_position}/{summoner_champion}) 소환사가 머물었던 라인 비율입니다. \
                        시간별로 어떤 라인에 머물렀는지 확인할 수 있습니다. ')
            
            slide = st.slider('시간(minute):', 0, len(summoner_moving), (0, len(summoner_moving)))
            lane_counts = summoner_moving[slide[0]:slide[1]]['lane'].value_counts()
            lane_counts = lane_counts.reindex(x_range, fill_value=0)
            fig = go.Figure([go.Bar(x=x_range, y=lane_counts.values)])
            fig.update_layout(title='lane', xaxis_title='position', yaxis_title='ration')

            st.plotly_chart(fig, use_container_width=True)
            

 
    st.divider()

# --------------------------------- 피해량 측정(타워/챔피언) ---------------------------------- #


# 어떤 참가자에 의해 가장 많이죽고, 피해를받고, 어디서 죽었을까 . 
# 참여도를 보려면 가장 좋은게, 얼만큼 딜을 넣었는지 (jungle,top,mid,bottom) 보는게 가장 큰 부분을 차지할것이다.
# 그런데 게임이 끝나고나야 총 데미지가 기록 된다. 혹은 kill 이나 assist 를 한 경우 얼마나 기여했는지 볼 수 있음
# CC기가 있는 챔피언이나 , 논타겟 챔피언인 경우 CC기로그, skillhit로그를 확인 할 수있다.

if hasattr(st.session_state, 'death_damage'):
    death_damage = st.session_state.death_damage

#  death 할때 받은 데미지
if hasattr(st.session_state, 'death_damage_log'):
    death_damage_log = st.session_state.death_damage_log    
    dmg_total = death_damage_log.groupby('name').agg({'magicDamage': 'sum', 'physicalDamage': 'sum', 'trueDamage': 'sum'}).reset_index()
    dmg_total['total'] = dmg_total[['magicDamage', 'physicalDamage', 'trueDamage']].sum(axis=1)

# (딜교환) death 할때 , 받은피해량과 내가 카운터한 딜량까지 포함 

if hasattr(st.session_state, 'damage_counter'):
    damage_counter = st.session_state.damage_counter
 
    #전체    
    total = damage_counter.groupby('name').agg({'magicDamage': 'sum', 'physicalDamage': 'sum', 'trueDamage': 'sum'}).reset_index()
    total['total'] = total[['magicDamage', 'physicalDamage', 'trueDamage']].sum(axis=1)
    
    #15분전
    
    before = damage_counter[damage_counter['timestamp'] <= 900000 ].groupby('name').agg({'magicDamage': 'sum', 'physicalDamage': 'sum', 'trueDamage': 'sum'}).reset_index()
    before['total'] = before[['magicDamage', 'physicalDamage', 'trueDamage']].sum(axis=1)

    if summoner_champion not in before['name'].values:
        new_row = pd.DataFrame({
            'name': [summoner_champion],
            'magicDamage': [0],
            'physicalDamage': [0],
            'trueDamage': [0],
            'total':[0]
        })
        before = pd.concat([before, new_row], ignore_index=True)
    
    #15분이후
    after = damage_counter[damage_counter['timestamp'] > 900000 ].groupby('name').agg({'magicDamage': 'sum', 'physicalDamage': 'sum', 'trueDamage': 'sum'}).reset_index()
    after['total'] = after[['magicDamage', 'physicalDamage', 'trueDamage']].sum(axis=1)


    if summoner_champion not in after['name'].values:
        new_row = pd.DataFrame({
            'name': [summoner_champion],
            'magicDamage': [0],
            'physicalDamage': [0],
            'trueDamage': [0],
            'total':[0]
        })
        after = pd.concat([after, new_row], ignore_index=True)

    with st.container():

        st.header(" DEATH Log / 딜교환 ")
        st.markdown(f'> **{summoner_name} ({summoner_position}/ {summoner_champion})** 소환사 의 죽은 횟수는 팀데스**{sum_team_death}**번중 **{d}번** 입니다.')
        st.caption('15분전후로 해당 유저의 받은 피해량과 해당 유저가 딜교환을 어떻게 했는지 확인할 수 있습니다. \
                   또한 소환사가 죽었을 시 챔피언 이외에 타워, 몬스터 같은 오브젝트들에게 고의적으로 죽었을 경우 확인이 가능합니다.\
                   ')


    with st.container():
            tab1,tab2 = st.tabs(['TOTAL','DAMAGE LOG(15/15)'])
            with tab2:
                col1,col2 = st.columns(2)
                with col1:
                    if not before.empty:
                        st.markdown('#### before 15 ')
                        expander = st.expander("damage log")
                        expander.caption(f'{summoner_name} ({summoner_position}/ {summoner_champion})의 딜교환')
                        expander.dataframe(before)                          

                        before = before[['name','total']].sort_values('total')
                        b = before.to_dict('records')

                        result = []

                        for i, row in enumerate(b):
                            result.append({
                                "id": row["name"],
                                "label": row["name"],
                                "value": row["total"],
                            })
                        with elements("nivo_pie"):
                            with mui.Box(sx={"height":350}):
                                nivo.Pie(
                                        data=result,
                                        margin={"top": 70, "right": 90, "bottom": 70, "left": 80 },
                                        innerRadius={0.5},
                                        padAngle={2},
                                        activeOuterRadiusOffset={8},
                                        colors={ 'scheme': 'nivo' },
                                        borderWidth={1},
                                        borderColor={
                                            "from": 'color',
                                            "modifiers": [
                                                [
                                                    'darker',
                                                    0.2,
                                                    'opacity',
                                                    0.6
                                                ]
                                            ]
                                        },
                                        arcLinkLabelsSkipAngle={10},
                                        arcLinkLabelsTextColor="white",
                                        arcLinkLabelsThickness={2},
                                        arcLinkLabelsColor={ "from": 'color', "modifiers": [] },
                                        arcLabelsSkipAngle={10},
                                        arcLabelsTextColor={ "theme": 'background' },
                                        legends=[
                                            {
                                                "anchor": "top-left",
                                                "direction": "column",
                                                "translateX": -50,
                                                "translateY": -40,
                                                "itemWidth": 80,
                                                "itemHeight": 20,
                                                "itemTextColor": "white",
                                                "symbolSize": 12,
                                                "symbolShape": "circle",
                                                "effects": [
                                                    {
                                                        "on": "hover",
                                                        "style": {
                                                            "itemTextColor": "white"
                                                        }
                                                    }
                                                ]
                                            }
                                        ],
                                        theme={
                                            "background": "#0e1117",
                                            "textColor": "white",
                                            "tooltip": {
                                                "container": {
                                                    "background": "#3a3c4a",
                                                    "color": "white",
                                                }
                                            }
                                        }
                                    )

                    else:
                        st.caption('15분전 death log 가 없습니다.')

                with col2:
                    if not after.empty:
                        st.markdown('#### after 15 ')

                        expander = st.expander("damage log")
                        expander.caption(f'{summoner_name} ({summoner_position}/ {summoner_champion})의 딜교환')
                        expander.dataframe(after)                          

                        after = after[['name','total']].sort_values('total')
                        a = after.to_dict('records')

                        result = []

                        for i, row in enumerate(a):
                            result.append({
                                "id": row["name"],
                                "label": row["name"],
                                "value": row["total"],
                            })
                    
                        with elements("nivo_pie_2"):
                            with mui.Box(sx={"height":350}):
                                nivo.Pie(
                                        data=result,
                                        margin={"top": 70, "right": 90, "bottom": 70, "left": 80 },
                                        innerRadius={0.5},
                                        padAngle={2},
                                        activeOuterRadiusOffset={8},
                                        colors={ 'scheme': 'nivo' },
                                        borderWidth={1},
                                        borderColor={
                                            "from": 'color',
                                            "modifiers": [
                                                [
                                                    'darker',
                                                    0.2,
                                                    'opacity',
                                                    0.6
                                                ]
                                            ]
                                        },
                                        arcLinkLabelsSkipAngle={10},
                                        arcLinkLabelsTextColor="white",
                                        arcLinkLabelsThickness={2},
                                        arcLinkLabelsColor={ "from": 'color', "modifiers": [] },
                                        arcLabelsSkipAngle={10},
                                        arcLabelsTextColor={ "theme": 'background' },
                                        legends=[
                                            {
                                                "anchor": "top-left",
                                                "direction": "column",
                                                "translateX": -50,
                                                "translateY": -40,
                                                "itemWidth": 80,
                                                "itemHeight": 20,
                                                "itemTextColor": "white",
                                                "symbolSize": 12,
                                                "symbolShape": "circle",
                                                "effects": [
                                                    {
                                                        "on": "hover",
                                                        "style": {
                                                            "itemTextColor": "white"
                                                        }
                                                    }
                                                ]
                                            }
                                        ],
                                        
                                        theme={
                                            "background": "#0e1117",
                                            "textColor": "white",
                                            "tooltip": {
                                                "container": {
                                                    "background": "#3a3c4a",
                                                    "color": "white",
                                                }
                                            }
                                        }
                                    )

                    else: 
                        st.caption('15분 이후 death log가 없습니다.')

 # ------ 전체 death 딜교환           
            with tab1:
                if not total.empty:
                    col1,col2 = st.columns([2,1])
                    
                    with col1 :
                        st.subheader(f'')
                        # st.dataframe(dmg_total)
                        marker_color = []
                        for name in total['name']:
                            if name in ['Turret','Minion/Monster']:
                                marker_color.append('#b72325')
                            elif name == summoner_champion:
                                marker_color.append('#ffffff')
                            else:
                                marker_color.append('#80c4f9')
    
                        fig = px.bar(total, x='total', y='name', color='name', orientation='h',
                                    title=f'{summoner_champion} vs 받은피해량',color_discrete_sequence= marker_color)
                        
                        st.plotly_chart(fig,use_container_width=True)
                    
                    with col2 :
                        st.markdown("##### 15분전 영향을 받은 챔피언 TOP3")
                        if not before.empty:
                            
                            before_filtered = before.loc[before['name'] != summoner_champion].sort_values('total',ascending=False)
                
                            champion_names = before_filtered['name'].head(3).tolist()
                            
                        #--- before top3  
                            with st.container():
                                _,col2_1,col2_2,col2_3,_ = st.columns([0.25,1,1,1,0.25])
                                with col2_1:
                                    if len(champion_names) < 1:
                                        st.caption('None')
                                    elif not champion_names[0] in ['Minion/Monster','Turret']:
                                        position = champion_info[champion_info['championName'] == champion_names[0]]['teamPosition'].iloc[0]
                                        st.image(champion_images[champion_names[0]])
                                        st.metric('hide',f'{position}',f'{champion_names[0]}', delta_color='off')
                                    else:
                                        st.caption('None')
                                with col2_2:
                                    if len(champion_names) < 2:
                                        st.caption('None')
                                    elif not champion_names[1] in ['Minion/Monster','Turret','']:
                                        position = champion_info[champion_info['championName'] == champion_names[1]]['teamPosition'].iloc[0]
                                        st.image(champion_images[champion_names[1]])
                                        st.metric('hide',f'{position}',f'{champion_names[1]}', delta_color='off')
                                    else: 
                                        st.caption('None')
                                with col2_3:
                                    if len(champion_names) < 3:
                                        st.caption('None')
                                    elif not champion_names[2] in ['Minion/Monster','Turret']:
                                        position = champion_info[champion_info['championName'] == champion_names[2]]['teamPosition'].iloc[0]
                                        st.image(champion_images[champion_names[2]])
                                        st.metric('hide',f'{position}',f'{champion_names[2]}', delta_color='off')
                                    else:
                                        st.subheader(f'{champion_names[2]}')


                                        
                        else:
                            st.caption('NO death')       


                    # ---- After 15
                        st.markdown("##### 15분 이후 영향을 받은 챔피언 TOP3")
                        after_filtered = after.loc[after['name'] != summoner_champion].sort_values('total',ascending=False)
                        champion_names = after_filtered['name'].head(3).tolist()

                        with st.container():
                            _,col2_1,col2_2,col2_3,_ = st.columns([0.25,1,1,1,0.25])

                            with col2_1:
                                if len(champion_names) < 1:
                                    st.caption('None')                                
                                elif not champion_names[0] in ['Minion/Monster','Turret']:
                                    position = champion_info[champion_info['championName'] == champion_names[0]]['teamPosition'].iloc[0]
                                    st.image(champion_images[champion_names[0]])
                                    st.metric('hide',f'{position}',f'{champion_names[0]}', delta_color='off')
                                else:
                                    st.write(f'{champion_names[0]}')

                            with col2_2:
                                if len(champion_names) < 2:
                                    st.caption('None')                                
                                elif not champion_names[1] in ['Minion/Monster','Turret']:
                                    position = champion_info[champion_info['championName'] == champion_names[1]]['teamPosition'].iloc[0]
                                    st.image(champion_images[champion_names[1]])
                                    st.metric('hide',f'{position}',f'{champion_names[1]}', delta_color='off')
                                else:
                                    st.caption('None')
                           
                            with col2_3:
                                if len(champion_names) < 3:
                                    st.caption('None')                                
                                elif not champion_names[2] in ['Minion/Monster','Turret']:
                                    position = champion_info[champion_info['championName'] == champion_names[2]]['teamPosition'].iloc[0]
                                    st.image(champion_images[champion_names[2]])
                                    st.metric('hide',f'{position}',f'{champion_names[2]}', delta_color='off')
                                else:
                                    st.caption('None')






