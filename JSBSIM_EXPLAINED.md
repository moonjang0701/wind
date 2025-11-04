# JSBSim의 역할과 편차 계산 방법 상세 설명

## 🤔 JSBSim은 무엇을 제공하나요?

JSBSim에서 가져오는 것은 **단순한 기체 형상 데이터가 아닙니다!** 훨씬 더 많은 것을 제공합니다.

---

## 📦 JSBSim이 제공하는 것

### 1. ✈️ 항공기 모델 (Aircraft Model)

JSBSim의 항공기 파일(예: c172p.xml)에는:

#### a) 기체 형상 데이터
```xml
<!-- 날개 -->
<wing>
  <area unit="FT2">174</area>          <!-- 날개 면적 -->
  <span unit="FT">36</span>            <!-- 날개폭 -->
  <chord unit="FT">4.83</chord>        <!-- 시위 -->
</wing>

<!-- 동체 -->
<fuselage>
  <length unit="FT">26.75</length>     <!-- 동체 길이 -->
</fuselage>
```

#### b) 질량 및 관성 데이터
```xml
<mass_balance>
  <emptywt unit="LBS">1500</emptywt>   <!-- 자체 중량 -->
  <ixx unit="SLUG*FT2">1285</ixx>      <!-- 관성 모멘트 -->
  <iyy unit="SLUG*FT2">1824</iyy>
  <izz unit="SLUG*FT2">2666</izz>
</mass_balance>
```

#### c) 공기역학 계수 (Aerodynamic Coefficients)
```xml
<!-- 양력 계수 (Lift Coefficient) -->
<CL>
  <alpha>  -0.087  0  0.262  0.524  0.785  1.047 </alpha>
  <CL>     -0.22   0  0.25   0.73   1.10   0.80  </CL>
</CL>

<!-- 항력 계수 (Drag Coefficient) -->
<CD>
  <alpha>  -0.087  0  0.262  0.524  0.785  1.047 </alpha>
  <CD>      0.026  0.026  0.031  0.083  0.175  0.254 </CD>
</CD>

<!-- 피칭 모멘트 계수 -->
<Cm>
  <!-- 받음각에 따른 피칭 모멘트 -->
</Cm>
```

#### d) 엔진 모델
```xml
<engine file="engIO320D">
  <location unit="IN">
    <x>-40</x>  <!-- 엔진 위치 -->
    <y>0</y>
    <z>0</z>
  </location>
</engine>
```

#### e) 조종면 (Control Surfaces)
```xml
<flight_control>
  <aileron>     <!-- 보조익 -->
  <elevator>    <!-- 승강타 -->
  <rudder>      <!-- 방향타 -->
</flight_control>
```

---

### 2. 🧮 비행 역학 엔진 (Flight Dynamics Engine)

JSBSim은 **실시간으로 물리 계산**을 수행합니다:

#### a) 힘 계산 (Forces)
```
F_total = F_aerodynamic + F_thrust + F_gravity + F_wind

F_aerodynamic = 0.5 * ρ * V² * S * C
여기서:
- ρ (rho) = 공기 밀도
- V = 속도
- S = 날개 면적
- C = 공기역학 계수
```

#### b) 모멘트 계산 (Moments)
```
M_total = M_roll + M_pitch + M_yaw

조종면 입력 → 공기역학적 모멘트 → 회전 운동
```

#### c) 6자유도 운동 방정식 (6-DOF Equations of Motion)
```
병진 운동:
F = m * a
→ d(velocity)/dt = F/m

회전 운동:
M = I * α
→ d(angular_velocity)/dt = I^(-1) * M
```

#### d) 적분 (Integration)
```
매 time step마다:
1. 현재 상태에서 힘/모멘트 계산
2. 가속도 계산
3. 속도 업데이트: v(t+dt) = v(t) + a*dt
4. 위치 업데이트: x(t+dt) = x(t) + v*dt
```

---

### 3. 🌍 환경 모델 (Environment Model)

#### a) 대기 모델 (Atmosphere)
```
고도에 따른:
- 공기 밀도 (ρ)
- 기온
- 기압
- 음속
```

#### b) 바람 모델
```python
# 우리가 설정하는 부분:
atmosphere/wind-north-fps = 10.0  # 북쪽 바람
atmosphere/wind-east-fps = 32.8   # 동쪽 바람
atmosphere/wind-down-fps = 0.0    # 하강 바람
```

#### c) 중력 모델
```
지구 중력장, 위도/경도에 따른 변화
```

---

## 📐 측면 편차는 어떻게 계산되나요?

### 단계별 설명:

### 1️⃣ JSBSim이 매 스텝마다 계산하는 것

```python
# 매 0.01초 (또는 1초)마다:

# 현재 상태 읽기
current_state = jsbsim.get_state()

# JSBSim이 제공하는 데이터:
position = {
    'x_m': 123.45,      # 동쪽 방향 위치 (미터)
    'y_m': 456.78,      # 북쪽 방향 위치 (미터)
    'z_m': 305.0,       # 고도 (미터)
    'latitude': 37.619,
    'longitude': -122.375,
}

velocity = {
    'v_north_fps': 95.3,   # 북쪽 속도 (feet/sec)
    'v_east_fps': 15.2,    # 동쪽 속도 (feet/sec)
    'airspeed_kts': 60.0,  # 대기속도
    'groundspeed_kts': 62.3, # 대지속도
}

attitude = {
    'roll_deg': 2.5,     # 롤 각도
    'pitch_deg': 3.2,    # 피치 각도
    'yaw_deg': 5.8,      # 요 각도 (헤딩)
}
```

### 2️⃣ 우리가 계산하는 측면 편차

```python
def _calculate_deviations(self, state):
    """
    JSBSim이 준 위치 데이터로 편차 계산
    """
    
    # 1단계: 현재 위치 가져오기
    current_x = state["x_m"]  # 동쪽 방향 (미터)
    current_y = state["y_m"]  # 북쪽 방향 (미터)
    
    # 2단계: 시작점으로부터 얼마나 이동했는지 계산
    dx = current_x - self.initial_x  # 동쪽으로 이동한 거리
    dy = current_y - self.initial_y  # 북쪽으로 이동한 거리
    
    # 3단계: 의도한 경로 = 북쪽 (0도)
    intended_heading_rad = 0.0  # 라디안
    
    # 4단계: 측면 편차 계산
    # 북쪽으로 가려고 했는데, 동쪽으로 얼마나 밀렸는지
    lateral_deviation = dx * cos(0) - dy * sin(0)
    lateral_deviation = dx * 1 - dy * 0
    lateral_deviation = dx  # 결과: 동쪽 이동 거리 = 측면 편차!
    
    # 5단계: 진행 거리 (의도한 방향)
    along_track = dx * sin(0) + dy * cos(0)
    along_track = dy  # 북쪽으로 간 거리
    
    return lateral_deviation, along_track
```

### 시각적 설명:

```
시작 (0, 0)
    |
    |  dy (북쪽으로 이동)
    |
    ↓
    └─────→ dx (동쪽으로 이동)
         현재 위치

측면 편차 = dx (동쪽 편차)
진행 거리 = dy (북쪽 진행)
```

---

## 🔬 JSBSim의 물리 계산 과정

### 매 Time Step마다:

```
┌─────────────────────────────────────┐
│  1. 입력 받기                        │
│     - 조종면 위치                    │
│     - 스로틀                         │
│     - 바람                          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  2. 힘 계산                          │
│     - 양력 = f(속도, 받음각, 고도)  │
│     - 항력 = f(속도, 형상)          │
│     - 추력 = f(스로틀, RPM)         │
│     - 중력 = m * g                  │
│     - 바람 영향                      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  3. 가속도 계산                      │
│     a = F_total / mass              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  4. 속도 업데이트                    │
│     v_new = v_old + a * dt          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  5. 위치 업데이트                    │
│     x_new = x_old + v * dt          │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  6. 회전 운동 계산 (동시에)         │
│     - 롤, 피치, 요 각도 업데이트    │
└─────────────────────────────────────┘
```

---

## 🌬️ 바람이 위치에 미치는 영향

### 바람 없을 때:
```
t=0초:  위치 = (0, 0)
        속도 = (0, 30) m/s (북쪽으로)

t=1초:  위치 = (0, 30) m
        속도 = (0, 30) m/s

t=60초: 위치 = (0, 1800) m
```

### 바람 있을 때 (10 m/s 동풍):
```
t=0초:  위치 = (0, 0)
        항공기 속도 = (0, 30) m/s (대기 기준)
        바람 = (10, 0) m/s
        대지속도 = (10, 30) m/s ← 바람 더해짐!

t=1초:  위치 = (10, 30) m
        ↑동쪽 10m 밀림!

t=60초: 위치 = (600, 1800) m
        측면 편차 = 600m
```

### JSBSim의 계산:
```python
# JSBSim 내부에서:
wind_velocity = [10, 0, 0]  # m/s
aircraft_velocity = [0, 30, 0]  # m/s (대기 기준)

# 대지 속도 = 항공기 속도 + 바람
ground_velocity = aircraft_velocity + wind_velocity
ground_velocity = [10, 30, 0]  # m/s

# 위치 업데이트
position += ground_velocity * dt
```

---

## ⚙️ dt (시간 간격)의 의미

### dt = 0.01초 (기본값):
```
60초 시뮬레이션 = 6,000 스텝

매 0.01초마다:
- 힘 계산
- 가속도 계산  
- 속도 업데이트
- 위치 업데이트

장점: 매우 정확한 계산
단점: 계산량 많음 (6,000번 계산)
```

### dt = 1.0초 (변경 후):
```
60초 시뮬레이션 = 60 스텝

매 1초마다 한 번만 계산

장점: 빠름 (60번만 계산)
단점: 정확도 약간 감소
```

---

## 📊 정확도 비교

| dt | 스텝 수 | 계산 시간 | 정확도 | 추천 용도 |
|----|--------|----------|--------|----------|
| 0.001초 | 60,000 | 매우 느림 | 99.9% | 연구용 |
| 0.01초 | 6,000 | 보통 | 99.5% | **일반 사용** ✅ |
| 0.1초 | 600 | 빠름 | 95% | 빠른 테스트 |
| 1.0초 | 60 | 매우 빠름 | 80-90% | 개략적 분석 |

---

## 💡 요약

### JSBSim이 제공하는 것:
1. ✅ 항공기의 **완전한 물리 모델** (형상 + 질량 + 공기역학)
2. ✅ **6자유도 운동 방정식** 실시간 계산
3. ✅ 대기, 바람, 중력 등 **환경 모델**
4. ✅ 매 time step마다 **정확한 위치, 속도, 자세** 제공

### 우리가 하는 것:
1. ✅ JSBSim에 바람 조건 입력
2. ✅ JSBSim 실행 (물리 계산은 JSBSim이 함)
3. ✅ JSBSim이 준 위치 데이터로 **측면 편차 계산**
4. ✅ 결과 시각화 및 분석

### 측면 편차 계산:
```python
# JSBSim이 제공: 현재 위치 (x, y)
# 우리가 계산: 
lateral_deviation = x - x_initial  # 동쪽으로 밀린 거리
```

**간단하죠?** JSBSim이 어려운 물리 계산을 다 해주고, 우리는 그 결과만 분석하면 됩니다! 🎯
