# 횡풍 좌우편차 시뮬레이션 이론

## 개요

이 문서는 JSBSim을 이용한 횡풍 좌우편차 시뮬레이션의 이론적 배경을 설명합니다.

## 1. 기본 개념

### 1.1 횡풍 (Crosswind)

횡풍은 항공기의 비행 방향에 수직으로 부는 바람입니다. 횡풍이 존재하면:
- 항공기가 의도한 경로에서 측면으로 밀려남
- 파일럿은 편류각(crab angle)을 유지하여 경로를 보정해야 함
- 특히 착륙 시 중요한 고려사항

### 1.2 좌표계

본 시뮬레이션에서는 다음 좌표계를 사용합니다:

#### NED (North-East-Down) 좌표계
- **N (North)**: 북쪽 방향 (지구 표면)
- **E (East)**: 동쪽 방향 (지구 표면)
- **D (Down)**: 아래쪽 방향 (중력 방향)

#### 항공기 좌표계
- **X**: 항공기 기수 방향 (전진)
- **Y**: 항공기 우측날개 방향
- **Z**: 항공기 아래 방향

## 2. 바람 모델링

### 2.1 바람 벡터 표현

바람은 풍속(speed)과 풍향(direction)으로 표현됩니다:

```
V_wind = [V_north, V_east, V_down]
```

풍속과 풍향으로부터 성분을 계산:

```
V_north = V_wind * cos(θ)
V_east = V_wind * sin(θ)
```

여기서 θ는 북쪽 기준 시계방향 각도입니다.

### 2.2 횡풍 성분

항공기 헤딩(ψ)에 대한 횡풍 성분:

```
V_crosswind = V_wind * sin(θ - ψ)
```

정풍/배풍 성분:

```
V_headwind = V_wind * cos(θ - ψ)
```

### 2.3 난기류 모델

난기류는 가우시안 랜덤 프로세스로 모델링됩니다:

```
V_turbulence = N(0, σ²)
σ = V_wind * I_turbulence
```

여기서 I_turbulence는 난기류 강도 (0.0 ~ 1.0)입니다.

## 3. 측면 편차 계산

### 3.1 기본 수식

측면 편차(lateral deviation)는 의도한 경로에서 수직 방향으로의 거리입니다:

```
d_lateral(t) = ∫₀ᵗ V_crosswind(τ) dτ
```

이산 시간에서:

```
d_lateral[n] = d_lateral[n-1] + V_crosswind[n] * Δt
```

### 3.2 실제 구현

실제 구현에서는 항공기의 위치를 추적하여 계산:

```python
# 현재 위치
x_current, y_current = get_position()

# 초기 위치로부터의 변위
dx = x_current - x_initial
dy = y_current - y_initial

# 의도한 경로 방향 벡터 (예: 북쪽)
intended_direction = [0, 1]  # [dx, dy] normalized

# 측면 편차 (외적 이용)
lateral_deviation = dx * intended_direction[1] - dy * intended_direction[0]
```

## 4. 편류각 (Drift Angle)

### 4.1 정의

편류각은 항공기의 헤딩(heading)과 실제 지면 경로(ground track) 사이의 각도입니다.

### 4.2 계산

```python
# 항공기 헤딩
heading = ψ

# 지면 경로 각도
ground_track = atan2(V_east, V_north)

# 편류각
drift_angle = heading - ground_track
```

### 4.3 의미

- **양의 편류각**: 항공기가 오른쪽으로 향하고 있음 (왼쪽 횡풍 보정)
- **음의 편류각**: 항공기가 왼쪽으로 향하고 있음 (오른쪽 횡풍 보정)

## 5. 대기속도와 대지속도

### 5.1 관계식

```
V_ground = V_air + V_wind
```

벡터 형태:

```
V_g = √[(V_a * cos(ψ) + V_w_north)² + (V_a * sin(ψ) + V_w_east)²]
```

### 5.2 시뮬레이션에서의 적용

JSBSim은 다음을 자동으로 계산합니다:
- True Airspeed (TAS): 항공기가 공기에 대해 움직이는 속도
- Ground Speed: 항공기가 지면에 대해 움직이는 속도
- Wind Triangle: 대기속도, 대지속도, 풍속의 벡터 관계

## 6. JSBSim 비행 역학

### 6.1 6자유도 (6-DOF) 모델

JSBSim은 6자유도 비행 역학 모델을 사용합니다:

**병진 운동 (3자유도)**
- X축: 전후 이동
- Y축: 좌우 이동
- Z축: 상하 이동

**회전 운동 (3자유도)**
- Roll (φ): X축 회전
- Pitch (θ): Y축 회전
- Yaw (ψ): Z축 회전

### 6.2 운동 방정식

뉴턴의 운동 방정식:

```
F = m * a
M = I * α
```

여기서:
- F: 힘 벡터 (양력, 항력, 추력, 중력)
- M: 모멘트 벡터
- m: 질량
- I: 관성 모멘트 텐서
- a: 가속도
- α: 각가속도

### 6.3 공기역학 모델

JSBSim은 다음을 계산합니다:
- 양력 계수 (C_L)
- 항력 계수 (C_D)
- 모멘트 계수 (C_m, C_l, C_n)

이들은 받음각(α), 옆미끄럼각(β), 조종면 위치에 따라 결정됩니다.

## 7. 시뮬레이션 시나리오

### 7.1 순수 횡풍

```
V_wind = 10 m/s
θ_wind = 90° (동쪽)
ψ_aircraft = 0° (북쪽)
```

결과:
- 최대 횡풍 효과
- 시간에 따라 선형적으로 증가하는 측면 편차

### 7.2 사선 바람

```
V_wind = 10 m/s
θ_wind = 45° (북동쪽)
ψ_aircraft = 0° (북쪽)
```

결과:
- 횡풍과 정풍의 조합
- 대지속도 증가 + 측면 편차

### 7.3 난기류 포함

```
V_wind = 10 m/s
θ_wind = 90°
I_turbulence = 0.3
```

결과:
- 불규칙한 측면 편차
- 변동하는 편류각

## 8. 실용적 고려사항

### 8.1 항공기 성능

- **Cessna 172 (c172p)**
  - 순항속도: 약 122 knots (63 m/s)
  - 최대 횡풍 한계: 약 15 knots (7.7 m/s)
  
### 8.2 바람 조건

| 풍속 (m/s) | 풍속 (knots) | 등급 |
|-----------|-------------|------|
| 0-5       | 0-10        | 약한 바람 |
| 5-10      | 10-19       | 보통 바람 |
| 10-15     | 19-29       | 강한 바람 |
| 15+       | 29+         | 매우 강한 바람 |

### 8.3 안전 마진

실제 비행에서 파일럿은 다음을 고려합니다:
- 항공기 최대 횡풍 한계의 70-80%만 사용
- 돌풍 요소 (gust factor) 추가
- 활주로 폭 및 길이

## 9. 결과 해석

### 9.1 측면 편차

```
최대 허용 편차 = 활주로 폭 / 2 - 안전 마진
```

일반적인 활주로:
- 너비: 30-60m
- 안전 마진: 5-10m

### 9.2 편류각

적절한 편류각:
```
β_crab ≈ arcsin(V_crosswind / V_airspeed)
```

## 10. 참고 문헌

1. Stevens, B. L., & Lewis, F. L. (2003). *Aircraft Control and Simulation*
2. Nelson, R. C. (1998). *Flight Stability and Automatic Control*
3. JSBSim Documentation: http://jsbsim.sourceforge.net/
4. FAA Pilot's Handbook of Aeronautical Knowledge

## 11. 추가 자료

- 항공 역학 기초
- 바람 시어 (Wind Shear) 효과
- 자동조종 시스템
- 횡풍 착륙 기법 (Crab, Slip)
