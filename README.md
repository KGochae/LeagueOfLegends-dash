### issue
* ~(2023-07-31) rank url 에 문제가 생겼습니다. (최근 승/패 여부와 rank 에 관한 정보)~ 
* (2023-08-08) 잠시 보안 문제로 APIkey 를 직접 발급해야지 이용할 수 있도록 변경했습니다.🥹
* (2023-11) 11월 21일 이후부터는 소환사 이름이 삭제되고, 모든 라이엇 게임에서 Riot ID가 사용됩니다. -> 고유 태그 KEY가 추가되었습니다.
* (14.1)	2024년 1월 10일 수요일 라이엇 패치 예정

# LeagueOfLegends dashboard
* 대시보드 구경하기 [**LeagueOfLegends-dashboard🎮**](https://leagueoflegends-dash-ytcwvappksi2kdzg8jtjynj.streamlit.app/)
* 해당 프로젝트를 정리한 PDF 요약본 입니다! [**📑요약자료 보기**](https://github.com/KGochae/LeagueOfLegends-dash/blob/main/summary_pdf/%EB%A6%AC%EA%B7%B8%EC%98%A4%EB%B8%8C%EB%A0%88%EC%A0%84%EB%93%9C_%EC%8B%A0%EA%B3%A0%EB%8C%80%EC%8B%9C%EB%B3%B4%EB%93%9C_%EC%B5%9C%EC%A2%85.pdf) 
*  해당[(**VELOG**)](https://velog.io/@liveandletlive/series/RIOT-API)에서 좀 더 자세한 내용을 보실 수 있습니다

#### 사용방법
![image](https://github.com/KGochae/LeagueOfLegends-dash/assets/86241587/f152ee3e-db0a-4966-9389-7e24d9bd0ca6)

- [Riot Developer Portal](https://developer.riotgames.com/) 에 들어가서 로그인 후, api_key를 준비합니다!
- 메인페이지의 SIDE BAR 에 있는 유저의 **닉네임(summoner_name) + 태그(Tagline)** 와 발급받은 API_KEY 를 입력하시면 가장 최근 경기(신고를 받았다는 가정)에 대한 요약이 나옵니다.
#### 유저의 닉네임과 태그라인 예시 (OP.GG 전적검색)
![example](https://github.com/user-attachments/assets/56612005-96a6-4e6a-a7f0-4b25ce36b221)

- 현재는 총 4가지 신고 사유가 있습니다.(현재는 체크하실 필요없이 모든 결과를 볼 수 있습니다.)



# 0. 디렉토리 , 요약본

```bash
├── 📁.streamlit
| └── config.toml
├── css
| └── main_css.css
├── 📁 img
│ ├── minimap.png
| └── wallpaper.jpg 
├── 📁 pages
│ └── 1_💻_설명서.py
├── 📁 portfolio_pdf
│ └── 리그오브레전드_신고대시보드.pdf  # 프로젝트를 정리한 발표자료 입니다. 
├── .gitignore
├── .README.md
├── main.py --------- # 대시보드 메인 
├── requirements.txt
└── riot.py --------- # 데이터 수집 및 전처리 
```

# 1. 프로젝트 소개 

* 대표 AOS 게임 리그 오브 레전드 게임은 몇년동안 사랑받는 만큼 '고의적으로 게임을 망치는 유저들' 흔히 말하는 '트롤' 문제도 꾸준히 이어지고 있습니다.
* 현재 리그 오브 레전드에서 대표적인 신고사유는 아래와 같습니다.
> ![image](https://github.com/KGochae/LeagueOfLegends-dash/assets/86241587/33069244-f364-47fb-9d1b-02c4b8859f50)

* 위와 같은 문제가 일어나고 유저 신고가 들어왔을 때 마땅한 처분을 내려야 하는데 사람의 판단이 꼭 필요한 부분들이 있다고 생각이 들었습니다.
* 예를들어, 부정적인 태도, 의도적으로 적에게 죽음 등 의 기준을 어떻게 봐야할 것 인지, 알고리즘을 통해서 자동화할 수 있는 부분에는 한계가 있다고 생각 들었습니다.
* 위 대시보드는 신고가 접수되었을 때, 그런 부분을 빠르게 파악하기 위해 만들어 본 유저 대시보드입니다.

# 2. 신고사유 4가지 주제
## 📊 유저의 참여도 및 스킬로그
- 포지션별 중요변수들을 선정한뒤 가중치를 부여해서 유저의 참여도를 계산했습니다. (Radar chart)
- 크게 **ATTACK, OBJECT, UTILITY** 부분으로 나뉘어서 점수를 세분화 하고 해당 경기의 랭크를 구합니다. (지표당 10점 만점, 총 합 30점)
- KILL, DEATH, ASSIST 를 달성했을 시 기록된 **스킬로그**를 가져와 스킬을 적극적으로 활용했는지 확인이 가능합니다.

> ![image](https://github.com/KGochae/LeagueOfLegends-dash/assets/86241587/56ac753b-6d38-40f3-820b-42b3c42a4056)

## 👻 비정상적인 프로그램 사용 (GOLD)
- 유저의 전체 EVENT LOG를 확인할 수 있습니다.
- **비정상적인 GOLD 움직임**이 발견될 시 해당구간을 시각화합니다.

#### **current gold , Earned/Spent gold**
> ![image](https://github.com/KGochae/LeagueOfLegends-dash/assets/86241587/95f9358a-ebb4-4c72-a027-823b791cfb06)

#### **이상치구간 시각화**
> ![image](https://github.com/KGochae/LeagueOfLegends-dash/assets/86241587/681b41d1-ae7d-442a-9b90-7a7ebacf5cb1)

## 🥲 자리비움 AFK
- 유저의 이동경로 애니메이션과 유저가 머문비율을 확인할 수 있습니다.
- 장시간 자리를 비웠다면 유저의 XP가 멈춰있음을 이용해 **AFK 여부**를 추정합니다.

#### **이동경로 애니메이션, 머문비율**
> ![image](https://velog.velcdn.com/images/liveandletlive/post/74ed4cec-051a-4b06-b474-e6e154e6d463/image.png)

#### 중간에 탈주한 유저
> ![image](https://velog.velcdn.com/images/liveandletlive/post/924e5b93-b1c3-4953-9879-5d8a8fd269d8/image.gif)

  
## 💀 적에게 고의로 죽은경우
- 유저가 DEATH 했을 때 받은 피해량을 집계하고 **딜교환을 했는지 확인**합니다.
- 15분 전후로 챔피언 및 타워/미니언/몬스터 에게 **받은 피해량**을 볼 수 있습니다.

#### 의도적인 죽음으로 예측되는 유저의 데이터
> ![image](https://github.com/KGochae/LeagueOfLegends-dash/assets/86241587/5430c477-cc93-46d7-a77d-5d34095e41ba)
* before 15/ after 15
> ![image](https://velog.velcdn.com/images/liveandletlive/post/626edde4-c39e-420a-b7eb-6dbea2b67fc9/image.png)


# 3. 사용기술

* Python : Data Preprocessing, EDA,
* Streamlit : visualize, app
* API : RIOT API( RIOT 에서 제공하는 OPEN API를 이용하였습니다.)




