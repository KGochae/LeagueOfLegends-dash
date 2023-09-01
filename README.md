# LeagueOfLegends dashboard

* (2023-06-01) 
* ~(2023-07-31) rank url 에 문제가 생겼습니다. (최근 승/패 여부와 rank 에 관한 정보)~ 
* (2023-08-08) 잠시 보안 문제로 APIkey 를 직접 발급해야지 이용할 수 있도록 변경했습니다.🥹
* (2023-08-20) rank url 해결

### 목적  
- 위 대시보드는 신고가 접수되었을 때, 사람의 판단이 필요한 부분을 빠르게 파악하기 위해 만들어 본 유저 대시보드입니다.

### 사용방법
* [LeagueOfLegends-dashboard](https://leagueoflegends-dash-ytcwvappksi2kdzg8jtjynj.streamlit.app/)

![image](https://github.com/KGochae/LeagueOfLegends-dash/assets/86241587/f152ee3e-db0a-4966-9389-7e24d9bd0ca6)

- [Riot Developer Portal](https://developer.riotgames.com/) 에 들어가서 로그인 후, api_key를 준비합니다!
- 메인페이지의 SIDE BAR 에 있는 **유저의 닉네임(summoner_name)** 과 발급받은 **API_KEY** 를 입력하시면 가장 최근 경기에 대한 요약이 나옵니다.
- 현재는 총 4가지 신고 사유가 있습니다.( 체크하실 필요없이 모든 결과를 볼 수 있습니다.)

----
# 신고사유 4가지 주제

### 📊 유저의 참여도 및 스킬로그
- 포지션별 중요변수들을 선정한뒤 가중치를 부여해서 유저의 참여도를 계산했습니다. 
- 크게 **ATTACK, OBJECT, UTILITY** 부분으로 나뉘어서 점수를 세분화 됩니다. (각 10점 만점)
- KILL, DEATH, ASSIST 를 달성했을 시 기록된 스킬로그를 가져와 스킬을 적극적으로 활용했는지 확인이 가능합니다.

### 👻 비정상적인 프로그램 사용 (GOLD)
- 유저의 전체 EVENT LOG를 확인할 수 있습니다.
- 비정상적인 GOLD 움직임이 발견될 시 해당구간을 시각화합니다.

### 🥲 자리비움 AFK
- 유저의 이동경로 애니메이션과 유저가 머문비율을 확인할 수 있습니다.
- XP변동에 따라 AFK 여부가 결정됩니다.

### 💀 적에게 고의로 죽은경우
- 유저가 DEATH 했을 때 받은 피해량을 집계하고 딜교환을 했는지 확인합니다.
- 15분 전후로 챔피언 및 타워/미니언/몬스터 에게 받은 피해량을 볼 수 있습니다.
---

### 자세한 내용보러가기
- 항목별 자세한 내용은 [VELOG](https://velog.io/@liveandletlive/series/RIOT-API) 에서 확인하실 수 있습니다😀.
