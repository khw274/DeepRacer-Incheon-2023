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

#### 훈련
차량의 시야각을 줄여가며 훈련했고 시야각이 트랙 너비의 절반 값일 때 가장 최적화된 모습을 보여 주었다.

모델 당 총 1시간 동안 훈련을 진행했으며 다음과 같은 보상 함수 그래프를 도출해냈다.

![image](https://github.com/khw274/DeepRacer-Incheon-2023/assets/125671828/d0f35315-53cb-4321-a533-abf0f451bc67)

#### 하이퍼 파라미터 
```
(Hyperparameter)                                                        (Value)
Gradient descent batch size	                                        64
Entropy	                                                                0.05       
Discount factor	                                                        0.5
Loss type	                                                        Huber
Learning rate	                                                        0.0003
Number of experience episodes between each policy-updating iteration    20
Number of epochs	                                                10
```
훈련을 진행하기 전 단 두 종류의 하이퍼파라미터를 조정했다.

- Entropy: 값이 클수록 차량이 행동 공간을 더 철저히 탐색하도록 유도
  차량이 더 많은 행동 공간을 탐색하도록 해 정확하게 주행할 수 있도록 기본으로 설정된 0.01에서 0.05로 상향 조정함. 
- Discount Factor: 값이 클수록 더 먼 미래의 보상을 고려하여 움직임을 결정하는 Discount Factor
  먼 미래의 보상까지 고려하게 되면 정확도는 증가하겠지만, 그만큼 훈련시간도 늘어나게 된다.  
  긴 시간 훈련시 안정적이지만 기록이 느려지는 과적합 방지를 위해 기본으로 설정된 0.99에서 0.5로 하향 조정함.

 #### 조향각과 조향각별 속도
```
Action space type: Discrete

Action space
No.
        Steering angle (°)    Speed (m/s)
0	-26.0	              1.50
1	-26.0	      	      2.00
2	-13.0	              2.10
3	-13.0	              2.80
4	  0.0	              3.30
5	  0.0	              3.65
6	 13.0	              2.10
7	 13.0 	              2.80
8	 26.0	              1.50
9	 26.0	              2.00
```
<img src="https://github.com/khw274/DeepRacer-Incheon-2023/assets/125671828/629a8ad6-a182-4f01-af0c-2cf8cac46361" width="500" height="500"/>

#### 예선 결과
```47.483초로 3등을 본선 진출```


