# 2023년 AWS DeepRacer Championship 인천
제3회 대한민국 인공지능(AI) 융합 자율주행 경진대회 [AWS DeepRacer Championship 리그]

```본선 진출```

## 공모 내용
 인공지능 자율주행 장비(딥레이서)를 활용한 AI융합 아이디어 경진대회

## 대회 진행
### 트랙
<img src="https://github.com/khw274/DeepRacer-Incheon-2023/assets/125671828/198cfcb0-e954-4489-a87d-52998666ac7f" width="600" height="400"/>


### 예선
#### 보상함수 코드 설계
차량이 맵을 이탈하지 않으면서 최대한 빠른 기록으로 완주하기 위해서 최적의 waypoint를 찾는 프로그램을 사용했다.
https://github.com/cdthompson/deepracer-k1999-race-lines/blob/master/Race-Line-Calculation.ipynb

![image](https://github.com/khw274/DeepRacer-Incheon-2023/assets/125671828/424cba59-d354-4729-8aef-fd6272cc5054)

그 결과 다음과 같은 최적 경로와 waypoint를 얻을 수 있었다.

최적 경로 waypoint를 불러와 차량에 근접한 최적 경로 waypoint를 따라가면 보상을 주는 형태로 설계했다.

최적 경로 특성상 인코스를 타게 되는 경향이 있기 때문에 시야각을 트랙 너비의 절반으로 줄여 조밀하게 따라갈 수 있도록 해 커브시 맵을 이탈할 가능성을 줄였다.
