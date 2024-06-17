'''TwoDigits+최적 경로+시야각 0.5'''

import math

# 두 점 사이의 유클리드 거리를 계산합니다.  
def dist(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5


# 극좌표계의 좌표(r, theta)를 직교좌표계의 좌표(x, y)로 변환합니다.
def rect(r, theta):
    """
    theta in degrees

    returns tuple; (float, float); (x,y)
    """

    x = r * math.cos(math.radians(theta))
    y = r * math.sin(math.radians(theta))
    return x, y

# 직교좌표계의 좌표(x, y)를 극좌표계의 좌표(r, theta)로 변환합니다.
def polar(x, y):
    """
    returns r, theta(degrees)
    """

    r = (x ** 2 + y ** 2) ** .5
    theta = math.degrees(math.atan2(y,x))
    return r, theta


# 각도를 -180도에서 +180도 범위로 보정합니다.
def angle_mod_360(angle):
    """
    Maps an angle to the interval -180, +180.

    Examples:
    angle_mod_360(362) == 2
    angle_mod_360(270) == -90

    :param angle: angle in degree
    :return: angle in degree. Between -180 and +180
    """

    n = math.floor(angle/360.0)

    angle_between_0_and_360 = angle - n*360.0

    if angle_between_0_and_360 <= 180.0:
        return angle_between_0_and_360
    else:
        return angle_between_0_and_360 - 360

# 현재 주행 방향에 따라 최적의 waypoints 리스트를 반환합니다.
def get_waypoints_ordered_in_driving_direction(params):
    # waypoints are always provided in counter clock wise order
    
    waypoints = get_shortcut_waypoints() #최단거리 waypoint 받아옴

    if params['is_reversed']: # driving clock wise.
        return list(reversed(waypoints))
    else: # driving counter clock wise.
        return waypoints

# 주어진 waypoints 리스트를 추가로 분할하여 더 많은 waypoints를 생성합니다.
def up_sample(waypoints, factor):
    """
    Adds extra waypoints in between provided waypoints

    :param waypoints:
    :param factor: integer. E.g. 3 means that the resulting list has 3 times as many points.
    :return:
    """
    p = waypoints
    n = len(p)

    return [
        [i / factor * p[(j+1) % n][0] + (1 - i / factor) * p[j][0],
             i / factor * p[(j+1) % n][1] + (1 - i / factor) * p[j][1]
        ] 
        for j in range(n) 
        for i in range(factor)
    ]

# 차량의 현재 위치를 기준으로 가장 가까운 waypoint와 목표 지점을 찾습니다.
def get_target_point(params):
    waypoints = up_sample(get_waypoints_ordered_in_driving_direction(params), 20)

    car = [params['x'], params['y']]

    distances = [dist(p, car) for p in waypoints]
    min_dist = min(distances)
    i_closest = distances.index(min_dist)

    n = len(waypoints)

    waypoints_starting_with_closest = [waypoints[(i+i_closest) % n] for i in range(n)]

    r = params['track_width'] * 0.5 #waypoint 시야각 좁힘(기본 0.8, 최단거리 좌표를 추가함으로써 시야각을 좁힘)

    is_inside = [dist(p, car) < r for p in waypoints_starting_with_closest]
    i_first_outside = is_inside.index(False)

    if i_first_outside < 0:  # this can only happen if we choose r as big as the entire track
        return waypoints[i_closest]

    return waypoints_starting_with_closest[i_first_outside]

# 목표 지점에 도달하기 위해 필요한 조향 각도를 계산합니다.
def get_target_steering_degree(params):
    tx, ty = get_target_point(params)
    car_x = params['x']
    car_y = params['y']
    dx = tx-car_x
    dy = ty-car_y
    heading = params['heading']

    _, target_angle = polar(dx, dy)

    steering_angle = target_angle - heading

    return angle_mod_360(steering_angle)

# 목표 지점으로 향하는 조향 각도와 현재 조향 각도의 차이를 기반으로 점수를 계산합니다.
def score_steer_to_point_ahead(params):
    best_stearing_angle = get_target_steering_degree(params)
    steering_angle = params['steering_angle']

    error = (steering_angle - best_stearing_angle) / 60.0  # 60 degree is already really bad

    score = 1.0 - abs(error)

    return max(score, 0.01)  # optimizer is rumored to struggle with negative numbers and numbers too close to zero

# 최종 보상 점수를 반환합니다.
def reward_function(params):
    return float(score_steer_to_point_ahead(params))


def get_test_params():
    return {
        'x': 0.7,
        'y': 1.05,
        'heading': 160.0,
        'track_width': 0.45,
        'is_reversed': False,
        'steering_angle': 0.0,
        'waypoints': [
            [0.75, -0.7],
            [1.0, 0.0],
            [0.7, 0.52],
            [0.58, 0.7],
            [0.48, 0.8],
            [0.15, 0.95],
            [-0.1, 1.0],
            [-0.7, 0.75],
            [-0.9, 0.25],
            [-0.9, -0.55],
        ]
    }


def test_reward():
    params = get_test_params()

    reward = reward_function(params)

    print("test_reward: {}".format(reward))

    assert reward > 0.0


def test_get_target_point():
    result = get_target_point(get_test_params())
    expected = [0.33, 0.86]
    eps = 0.1

    print("get_target_point: x={}, y={}".format(result[0], result[1]))

    assert dist(result, expected) < eps


def test_get_target_steering():
    result = get_target_steering_degree(get_test_params())
    expected = 46
    eps = 1.0

    print("get_target_steering={}".format(result))

    assert abs(result - expected) < eps


def test_angle_mod_360():
    eps = 0.001

    assert abs(-90 - angle_mod_360(270.0)) < eps
    assert abs(-179 - angle_mod_360(181)) < eps
    assert abs(0.01 - angle_mod_360(360.01)) < eps
    assert abs(5 - angle_mod_360(365.0)) < eps
    assert abs(-2 - angle_mod_360(-722)) < eps

def test_upsample():
    params = get_test_params()
    print(repr(up_sample(params['waypoints'], 2)))

def test_score_steer_to_point_ahead():
    params_l_45 = {**get_test_params(), 'steering_angle': +45}
    params_l_15 = {**get_test_params(), 'steering_angle': +15}
    params_0 = {**get_test_params(), 'steering_angle': 0.0}
    params_r_15 = {**get_test_params(), 'steering_angle': -15}
    params_r_45 = {**get_test_params(), 'steering_angle': -45}

    sc = score_steer_to_point_ahead

    # 0.828, 0.328, 0.078, 0.01, 0.01
    print("Scores: {}, {}, {}, {}, {}".format(sc(params_l_45), sc(params_l_15), sc(params_0), sc(params_r_15), sc(params_r_45)))

# 테스트 함수
def run_tests():
    test_angle_mod_360()
    test_reward()
    test_upsample()
    test_get_target_point()
    test_get_target_steering()
    test_score_steer_to_point_ahead()

    print("All tests successful")


# run_tests()

# 최적 경로 waypoints 반환 함수
def get_shortcut_waypoints(): # 최적 경로 좌표
    return [[-3.53490617, -0.04164061],
            [-3.55675269, -0.21069381],
            [-3.55706974, -0.38237916],
            [-3.53696616, -0.55561264],
            [-3.49643095, -0.72943705],
            [-3.43485943, -0.90279568],
            [-3.35126422, -1.0744257 ],
            [-3.24080094, -1.24205378],
            [-3.09481526, -1.40053149],
            [-2.90172588, -1.53672613],
            [-2.69142477, -1.66152762],
            [-2.46703669, -1.77659114],
            [-2.23058595, -1.88358365],
            [-1.98412615, -1.98477969],
            [-1.72805329, -2.08099537],
            [-1.46710454, -2.16954877],
            [-1.20508633, -2.24859971],
            [-0.94277812, -2.31739392],
            [-0.68049824, -2.37521034],
            [-0.41850683, -2.42061897],
            [-0.15712608, -2.45177479],
            [ 0.10323054, -2.46679102],
            [ 0.3618151 , -2.46167282],
            [ 0.61737683, -2.43153477],
            [ 0.86773578, -2.37052539],
            [ 1.11205588, -2.28261396],
            [ 1.34993245, -2.17144665],
            [ 1.58083891, -2.03922435],
            [ 1.80402271, -1.88733415],
            [ 2.01869954, -1.71722443],
            [ 2.22411466, -1.53053924],
            [ 2.41955856, -1.3290534 ],
            [ 2.60437853, -1.1145788 ],
            [ 2.77794515, -0.88885545],
            [ 2.93976938, -0.65363624],
            [ 3.0890637 , -0.41036931],
            [ 3.22504348, -0.1604768 ],
            [ 3.34600355,  0.09493826],
            [ 3.4502179 ,  0.354499  ],
            [ 3.53547371,  0.61666045],
            [ 3.59876213,  0.87954236],
            [ 3.6368299 ,  1.14067515],
            [ 3.64596464,  1.39682271],
            [ 3.62310359,  1.64413837],
            [ 3.56275966,  1.87677955],
            [ 3.4584461 ,  2.08545928],
            [ 3.30602451,  2.25616401],
            [ 3.1193225 ,  2.3874289 ],
            [ 2.90971463,  2.48149902],
            [ 2.68556009,  2.54267097],
            [ 2.45192798,  2.57364934],
            [ 2.21252784,  2.57713681],
            [ 1.9699932 ,  2.55525016],
            [ 1.72629982,  2.51031004],
            [ 1.48290038,  2.44427835],
            [ 1.24088807,  2.35912021],
            [ 1.00108873,  2.25693797],
            [ 0.76419314,  2.13999366],
            [ 0.53101011,  2.01072264],
            [ 0.3026016 ,  1.87201036],
            [ 0.08052213,  1.72679055],
            [-0.14070758,  1.59089617],
            [-0.36533785,  1.4635226 ],
            [-0.59482026,  1.34777925],
            [-0.83070647,  1.24732181],
            [-1.07196871,  1.15994998],
            [-1.31837711,  1.08540534],
            [-1.56977429,  1.02369814],
            [-1.82595469,  0.97498121],
            [-2.08646093,  0.93957414],
            [-2.33147742,  0.89233585],
            [-2.56369888,  0.83150743],
            [-2.78045912,  0.75544647],
            [-2.97928827,  0.6634704 ],
            [-3.15663732,  0.55470585],
            [-3.30770178,  0.42856048],
            [-3.41529675,  0.28143114],
            [-3.48907217,  0.12323365],
            [-3.53490617, -0.04164061]]
