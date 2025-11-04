# JSBSim 횡풍 좌우편차 시뮬레이션

JSBSim을 활용하여 항공기가 횡풍(crosswind)을 받을 때 발생하는 측면 편차(lateral deviation)를 시뮬레이션하는 프로젝트입니다.

## 프로젝트 개요

이 프로젝트는 다음과 같은 기능을 제공합니다:
- JSBSim Flight Dynamics Model을 이용한 항공기 비행 시뮬레이션
- 다양한 강도의 횡풍 조건 설정
- 시간에 따른 항공기의 측면 편차 계산 및 분석
- 시뮬레이션 결과의 시각적 표현 (궤적, 그래프 등)

## 주요 특징

- **횡풍 모델링**: 다양한 풍속과 방향의 횡풍 시나리오 설정
- **실시간 시뮬레이션**: JSBSim 엔진을 활용한 고정밀 비행 역학 계산
- **편차 분석**: 측면 편차, 편류각(drift angle), 풍향 보정 등 분석
- **시각화**: matplotlib를 이용한 비행 궤적 및 데이터 시각화
- **확장 가능**: 다양한 항공기 모델 및 비행 조건 적용 가능

## 설치 방법

### 1. 필수 요구사항
- Python 3.8 이상
- JSBSim 라이브러리

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. JSBSim 설치
```bash
# pip를 통한 설치 (권장)
pip install jsbsim

# 또는 소스에서 빌드
git clone https://github.com/JSBSim-Team/jsbsim.git
cd jsbsim
python setup.py install
```

## 사용 방법

### 기본 사용 예제
```python
from src.crosswind_simulator import CrosswindSimulator

# 시뮬레이터 초기화
simulator = CrosswindSimulator(
    aircraft_model="c172p",  # Cessna 172
    crosswind_speed=10.0,     # 10 m/s 횡풍
    crosswind_direction=90.0  # 90도 (정측풍)
)

# 시뮬레이션 실행 (60초간)
results = simulator.run_simulation(duration=60.0)

# 결과 시각화
simulator.plot_results(results)
```

### 고급 사용 예제
```python
# 다양한 풍속 조건에서 시뮬레이션
wind_speeds = [5, 10, 15, 20]  # m/s
for wind_speed in wind_speeds:
    simulator = CrosswindSimulator(
        aircraft_model="c172p",
        crosswind_speed=wind_speed,
        crosswind_direction=90.0
    )
    results = simulator.run_simulation(duration=60.0)
    simulator.save_results(results, f"results_wind_{wind_speed}ms.csv")
```

## 프로젝트 구조
```
jsbsim-crosswind-simulation/
├── src/
│   ├── crosswind_simulator.py   # 메인 시뮬레이터 클래스
│   ├── jsbsim_wrapper.py        # JSBSim 래퍼 클래스
│   ├── wind_model.py            # 풍향/풍속 모델링
│   └── visualizer.py            # 결과 시각화 도구
├── examples/
│   ├── basic_simulation.py      # 기본 시뮬레이션 예제
│   └── advanced_analysis.py     # 고급 분석 예제
├── tests/
│   └── test_simulator.py        # 유닛 테스트
├── docs/
│   └── theory.md                # 이론 및 수식 설명
├── data/
│   └── results/                 # 시뮬레이션 결과 저장
├── requirements.txt
└── README.md
```

## 시뮬레이션 결과

시뮬레이션은 다음과 같은 데이터를 제공합니다:
- **위치 데이터**: 위도, 경도, 고도
- **속도 데이터**: 대지속도, 대기속도, 수직속도
- **자세 데이터**: 롤, 피치, 요 각도
- **편차 데이터**: 측면 편차, 편류각
- **풍향 데이터**: 풍속, 풍향

## 이론적 배경

### 횡풍 효과
횡풍(crosswind)은 항공기의 비행 방향에 수직으로 부는 바람입니다. 횡풍이 존재하면:
1. 항공기가 의도한 경로에서 측면으로 밀려남
2. 파일럿은 편류각(crab angle)을 유지하여 보정해야 함
3. 착륙 시 특히 중요한 고려사항

### 측면 편차 계산
측면 편차는 다음과 같이 계산됩니다:
- Lateral Deviation = ∫(V_crosswind) dt
- 여기서 V_crosswind는 횡풍에 의한 측면 속도 성분

## 라이선스
MIT License

## 기여
이슈 및 풀 리퀘스트를 환영합니다.

## 참고 자료
- [JSBSim Official Documentation](http://jsbsim.sourceforge.net/)
- [JSBSim GitHub Repository](https://github.com/JSBSim-Team/jsbsim)
- [Flight Dynamics Theory](https://en.wikipedia.org/wiki/Flight_dynamics)
