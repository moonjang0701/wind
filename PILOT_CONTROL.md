# 조종사 조종 (Pilot Control) 가이드

## 🎮 개요

실제 조종사는 횡풍을 받을 때 여러 방법으로 대응합니다. 이 모듈은 조종사의 행동을 시뮬레이션합니다.

---

## 🛫 조종 전략 4가지

### 1. 조종 없음 (NO_CORRECTION)
```
❌ 조종사가 아무것도 안함
```

**상황:**
- 조종사가 바람을 무시하고 그냥 비행
- 또는 바람을 인지하지 못함

**결과:**
```
시작점 (0, 0)
    ↑
    |     ↗
    |   ↗
    | ↗   (계속 밀림)
  ↗
바람 → → → → → →

60초 후: 동쪽으로 약 600m 밀림
```

**예상 편차:** **~600m** (최대)

---

### 2. 방위 유지 (HEADING_HOLD)
```
⚠️ 기수 방향만 북쪽으로 유지
```

**상황:**
- 조종사가 나침반만 보고 기수를 북쪽으로 유지
- 측면으로 밀리는 것은 신경 안씀

**조종:**
```python
# 기수가 북쪽에서 벗어나면 보조익으로 보정
if 현재_헤딩 != 0°:
    보조익 = (0° - 현재_헤딩) × 게인
```

**결과:**
```
목표 방향 (북쪽)
    ↑
    ↑ (기수는 북쪽)
    ↑
    ↑
    시작 ─────→ (하지만 측면으로 밀림)

기수: ↑ 북쪽
실제 이동: ↗ 북동쪽
```

**예상 편차:** **~150m** (중간)

---

### 3. 경로 추적 (TRACK_FOLLOWING)
```
✅ 측면 편차를 감지하고 경로로 복귀
```

**상황:**
- 조종사가 GPS나 지표물을 보고 경로 이탈 감지
- 측면 편차가 크면 복귀 조종

**조종:**
```python
# 3가지 요소를 고려
보조익 = (
    방위_오차 × 게인 +           # 기수 방향
    -측면_편차 × 게인 +           # 위치 보정
    -횡풍 × 게인                  # 바람 보정
)
```

**결과:**
```
목표 경로
    ↑
    | (편차 감지하면 복귀)
    |  ↖ ↑
    |    ↑
    |    ↑
    시작점

편차가 50m 이상이면 복귀 조종
```

**예상 편차:** **~10-20m** (작음)

---

### 4. 편류각 보정 (CRAB_CORRECTION)
```
🎯 미리 바람 방향으로 기울여서 보정
```

**상황:**
- 조종사가 바람을 인지하고 사전 보정
- 편류각(crab angle)을 계산하여 적용

**편류각 계산:**
```python
편류각 = arcsin(횡풍_속도 / 대기속도)

예: 횡풍 10 m/s, 속도 60 knots (31 m/s)
편류각 = arcsin(10/31) = 18.8°
```

**조종:**
```python
# 기수를 동쪽으로 약간 틀어서 바람 보정
목표_헤딩 = 0° + 18.8° = 18.8° (북동쪽)
```

**결과:**
```
      목표 (북쪽)
        ↑
        ↑
        ↑ (실제 경로)
        ↑
      시작
      
기수: ↗ 북동쪽 (18.8°)
바람: ← 동풍
실제 이동: ↑ 북쪽 (바람 상쇄!)
```

**예상 편차:** **~0-5m** (거의 완벽)

---

## 📊 전략 비교표

| 전략 | 조종 난이도 | 편차 | 연료 효율 | 승객 편안함 | 실제 사용 |
|------|-----------|------|----------|-----------|----------|
| 조종 없음 | ⭐ | 600m | ⭐⭐⭐⭐⭐ | ⭐ | ❌ 사용 안함 |
| 방위 유지 | ⭐⭐ | 150m | ⭐⭐⭐⭐ | ⭐⭐ | 초보 조종사 |
| 경로 추적 | ⭐⭐⭐⭐ | 10-20m | ⭐⭐⭐ | ⭐⭐⭐ | GPS 비행 |
| 편류각 보정 | ⭐⭐⭐⭐⭐ | 0-5m | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ 표준 |

---

## 💻 코드 사용법

### 기본 사용

```python
from src.crosswind_simulator import CrosswindSimulator
from src.pilot_controller import PilotController

# 시뮬레이터 생성
simulator = CrosswindSimulator(
    crosswind_speed=10.0,
    crosswind_direction=90.0
)

# 조종사 컨트롤러 생성
pilot = PilotController(
    target_heading=0.0,      # 목표 방위
    lateral_tolerance=50.0,  # 허용 편차 (m)
)

# 조종 모드 설정
pilot.control_mode = "AUTO_TRACK"  # 경로 추적

# 시뮬레이션 루프에서 사용
for step in range(num_steps):
    state = simulator.jsbsim.get_state()
    
    # 조종 입력 계산
    aileron, elevator, rudder = pilot.get_control_input(
        state,
        lateral_deviation,
        crosswind_component
    )
    
    # 조종면 적용
    simulator.jsbsim.fdm.set_property_value("fcs/aileron-cmd-norm", aileron)
    
    # 시뮬레이션 실행
    simulator.jsbsim.run_step()
```

### 편류각 계산

```python
from src.pilot_controller import PilotBehavior

# 편류각 자동 계산
crab_angle = PilotBehavior.calculate_crab_angle(
    crosswind_mps=10.0,   # 횡풍 10 m/s
    airspeed_kts=60.0     # 속도 60 knots
)

print(f"필요한 편류각: {crab_angle:.2f}°")
```

### 전략 비교 실행

```bash
python examples/pilot_control_comparison.py
```

---

## 🎯 실제 항공 적용

### VFR (유시계 비행)

**조종사의 판단:**
1. 육안으로 지표물 확인
2. 경로 이탈 감지
3. 기수를 바람 방향으로 틀어 보정

**사용 전략:** 경로 추적 + 편류각 보정

### IFR (계기 비행)

**자동조종장치:**
1. GPS로 정확한 위치 파악
2. 자동으로 경로 이탈 보정
3. 최적 편류각 계산 및 적용

**사용 전략:** 편류각 보정 (자동)

### 착륙 시 (Landing)

**3단계 접근:**
1. **접근 단계**: 편류각 유지 (Crab)
2. **활주로 임계**: 기수를 활주로와 평행하게 (De-crab)
3. **터치다운**: 측풍용 착륙 (Crosswind Landing)

---

## 📐 수학적 설명

### 편류각 공식

```
         바람
          ↓
    ╱───────╲
   ╱    θ    ╲  항공기
  ↗           ↗
실제 이동

sin(θ) = V_wind / V_airspeed

편류각 θ = arcsin(V_wind / V_airspeed)
```

### 제어 입력 공식

```python
# 비례 제어 (P Control)
aileron = K_p × error

# 비례-미분 제어 (PD Control)
aileron = K_p × error + K_d × d(error)/dt

# 비례-적분-미분 제어 (PID Control)
aileron = K_p × error + K_i × ∫error·dt + K_d × d(error)/dt
```

**현재 구현:** 비례 제어 (P Control)

---

## 🔧 파라미터 조정

### heading_gain (방위 게인)
```python
heading_gain = 0.02  # 기본값

# 높으면: 빠르게 반응 (민감)
# 낮으면: 천천히 반응 (부드러움)
```

### position_gain (위치 게인)
```python
position_gain = 0.001  # 기본값

# 높으면: 경로 복귀가 빠름
# 낮으면: 경로 복귀가 느림
```

### lateral_tolerance (허용 편차)
```python
lateral_tolerance = 50.0  # 50m

# 이 범위 내에서는 조종 안함
# 초과하면 복귀 조종 시작
```

---

## 🎮 예제 실행

### 1. 전략 비교 시뮬레이션
```bash
python examples/pilot_control_comparison.py
```

**출력:**
```
전략              최대 편차(m)    최종 편차(m)    효과
------------------------------------------------------------------
조종 없음         598.45          598.23          ❌ 계속 밀림
방위 유지         152.34          151.87          ⚠️  편차 증가
경로 추적         18.92           12.45           ✅ 편차 보정
편류각 보정       4.23            2.11            🎯 거의 완벽
```

### 2. 생성되는 그래프
- `pilot_strategies_comparison.png` - 전략별 편차 비교
- `trajectory_조종_없음.png` - 각 전략별 궤적
- `trajectory_방위_유지.png`
- `trajectory_경로_추적.png`
- `trajectory_편류각_보정.png`

---

## 💡 실전 팁

### 언제 어떤 전략을 사용하나?

#### 순항 비행 (Cruise)
→ **편류각 보정** (가장 효율적)

#### GPS 경로 추적
→ **경로 추적** (자동조종)

#### 연습 비행
→ **방위 유지** (기본 기술)

#### 비상 상황
→ **조종 없음** (절대 하면 안됨!)

---

## 🚀 추가 기능 계획

- [ ] PID 제어 구현
- [ ] 반응 지연 시간 추가
- [ ] 조종사 피로도 모델
- [ ] 난기류에서의 조종
- [ ] 다양한 항공기별 조종 특성

---

## 📚 관련 문서

- [SIMULATION_CONDITIONS.md](SIMULATION_CONDITIONS.md) - 시뮬레이션 조건
- [JSBSIM_EXPLAINED.md](JSBSIM_EXPLAINED.md) - JSBSim 설명
- [QUICKSTART.md](QUICKSTART.md) - 빠른 시작

---

**이제 조종사처럼 비행해보세요!** 🛫✈️
