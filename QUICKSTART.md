# 빠른 시작 가이드 (Quick Start)

## 5분 안에 시뮬레이션 실행하기

### 1단계: 설치

```bash
# 저장소 클론
git clone https://github.com/moonjang0701/wind.git
cd wind

# 가상환경 생성 (선택사항이지만 권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2단계: 기본 시뮬레이션 실행

```bash
python examples/basic_simulation.py
```

**예상 출력:**
```
============================================================
JSBSim 횡풍 좌우편차 시뮬레이션 - 기본 예제
============================================================
항공기: c172p
횡풍 속도: 10.0 m/s
풍향: 90.0°
시뮬레이션 시간: 60초

시뮬레이터 초기화 중...
시뮬레이션 시작...
100%|████████████████████| 6000/6000 [00:15<00:00, 387.21it/s]

============================================================
시뮬레이션 결과 요약
============================================================
최대 측면 편차: 145.32 m
최종 측면 편차: 144.87 m
평균 편류각: 8.45°
최대 편류각: 12.31°
총 이동 거리: 1842 m

결과 데이터 저장: data/results/basic_simulation_results.csv
결과 시각화 중...
============================================================
시뮬레이션 완료!
결과 파일 위치: data/results
============================================================
```

### 3단계: 결과 확인

시뮬레이션이 완료되면 `data/results/` 폴더에 다음 파일들이 생성됩니다:

- `basic_simulation_results.csv` - 원시 데이터
- `trajectory_2d.png` - 2D 비행 궤적
- `deviation_over_time.png` - 시간에 따른 편차
- `velocity_analysis.png` - 속도 분석
- `comprehensive_report.png` - 종합 분석 리포트

---

## Python 코드로 직접 사용하기

### 최소 예제

```python
from src.crosswind_simulator import CrosswindSimulator

# 시뮬레이터 생성
simulator = CrosswindSimulator(
    aircraft_model="c172p",
    crosswind_speed=10.0,
    crosswind_direction=90.0
)

# 시뮬레이션 실행
results = simulator.run_simulation(duration=60.0)

# 최대 편차 확인
print(f"최대 측면 편차: {results['lateral_deviation_m'].max():.2f} m")

# 정리
simulator.close()
```

### 시각화 포함 예제

```python
from src.crosswind_simulator import CrosswindSimulator
from src.visualizer import Visualizer

# 시뮬레이터 생성
simulator = CrosswindSimulator(
    aircraft_model="c172p",
    crosswind_speed=15.0,  # 15 m/s 횡풍
    crosswind_direction=90.0
)

# 시뮬레이션 실행
results = simulator.run_simulation(duration=60.0)

# 궤적 그리기
Visualizer.plot_trajectory_2d(
    results,
    title="My First Simulation",
    save_path="my_trajectory.png"
)

# 종합 리포트 생성
Visualizer.plot_comprehensive_report(
    results,
    wind_speed=15.0,
    save_path="my_report.png"
)

simulator.close()
```

### 여러 풍속 비교 예제

```python
from src.crosswind_simulator import CrosswindSimulator
from src.visualizer import Visualizer

# 비교할 풍속들
wind_speeds = [5, 10, 15, 20]  # m/s
results_dict = {}

# 각 풍속에 대해 시뮬레이션
for wind_speed in wind_speeds:
    print(f"시뮬레이션: {wind_speed} m/s...")
    
    simulator = CrosswindSimulator(
        crosswind_speed=wind_speed,
        crosswind_direction=90.0
    )
    
    results = simulator.run_simulation(duration=60.0, show_progress=False)
    results_dict[wind_speed] = results
    
    simulator.close()

# 비교 그래프 생성
Visualizer.plot_comparison(
    results_dict,
    metric='lateral_deviation_m',
    title='Lateral Deviation Comparison',
    save_path='comparison.png'
)

print("완료!")
```

---

## 고급 사용 예제

### 난기류 포함 시뮬레이션

```python
simulator = CrosswindSimulator(
    aircraft_model="c172p",
    crosswind_speed=10.0,
    crosswind_direction=90.0,
    turbulence=0.3,  # 난기류 강도 (0.0 ~ 1.0)
)

results = simulator.run_simulation(duration=60.0)
simulator.close()
```

### 자동조종 사용

```python
simulator = CrosswindSimulator(
    crosswind_speed=10.0,
    crosswind_direction=90.0
)

# 북쪽 방향(0도)을 유지하도록 자동조종
results = simulator.run_simulation(
    duration=60.0,
    autopilot_heading=0.0
)

simulator.close()
```

### 사용자 정의 바람 모델

```python
from src.wind_model import WindModel

# 횡풍 + 정풍 조합
wind_model = WindModel.create_crosswind_with_headwind(
    crosswind_mps=10.0,  # 10 m/s 횡풍
    headwind_mps=5.0,    # 5 m/s 정풍
    from_right=True
)

print(wind_model)  # 풍속 및 풍향 정보 출력
```

### 결과 데이터 분석

```python
import pandas as pd
import matplotlib.pyplot as plt

# 시뮬레이션 실행
simulator = CrosswindSimulator(crosswind_speed=10.0)
results = simulator.run_simulation(duration=60.0)

# 데이터 분석
print("기본 통계:")
print(results[['lateral_deviation_m', 'drift_angle_deg']].describe())

# 사용자 정의 그래프
plt.figure(figsize=(10, 6))
plt.plot(results['time'], results['lateral_deviation_m'])
plt.xlabel('Time (s)')
plt.ylabel('Lateral Deviation (m)')
plt.title('Custom Analysis')
plt.grid(True)
plt.savefig('custom_plot.png')

# CSV로 저장
results.to_csv('my_results.csv', index=False)

simulator.close()
```

---

## 문제 해결

### JSBSim 설치 문제

```bash
# JSBSim 재설치
pip uninstall jsbsim
pip install jsbsim --no-cache-dir
```

### API 호환성 문제

최신 코드를 받으세요:
```bash
git pull origin main
```

자세한 문제 해결 방법은 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)를 참조하세요.

---

## 다음 단계

1. **고급 분석 실행**
   ```bash
   python examples/advanced_analysis.py
   ```

2. **이론 학습**
   - [docs/theory.md](docs/theory.md) 읽기
   - 횡풍 효과 및 비행 역학 이해

3. **코드 수정**
   - `src/` 폴더의 소스 코드 살펴보기
   - 자신만의 시뮬레이션 시나리오 작성

4. **테스트 실행**
   ```bash
   pytest tests/test_simulator.py -v
   ```

5. **기여하기**
   - 버그 리포트: [GitHub Issues](https://github.com/moonjang0701/wind/issues)
   - Pull Request 환영합니다!

---

## 추가 자료

- [README.md](README.md) - 프로젝트 개요
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 문제 해결
- [docs/theory.md](docs/theory.md) - 이론적 배경
- [JSBSim 공식 문서](http://jsbsim.sourceforge.net/)

---

**즐거운 시뮬레이션 되세요!** ✈️
