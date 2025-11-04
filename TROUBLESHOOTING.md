# 문제 해결 가이드 (Troubleshooting)

## 일반적인 문제 및 해결 방법

### 1. JSBSim 설치 문제

#### 문제: `ModuleNotFoundError: No module named 'jsbsim'`

**해결 방법:**
```bash
pip install jsbsim
```

또는 특정 버전 설치:
```bash
pip install jsbsim==1.1.13
```

#### 문제: JSBSim 설치 시 컴파일 오류

**해결 방법 (Windows):**
1. Microsoft C++ Build Tools 설치
   - https://visualstudio.microsoft.com/downloads/
   - "Build Tools for Visual Studio" 다운로드
   - "C++ build tools" 워크로드 선택

2. 또는 사전 컴파일된 바이너리 사용:
```bash
# Python 버전에 맞는 wheel 파일 다운로드
pip install jsbsim --no-build-isolation
```

**해결 방법 (Linux):**
```bash
sudo apt-get update
sudo apt-get install build-essential python3-dev
pip install jsbsim
```

**해결 방법 (macOS):**
```bash
xcode-select --install
pip install jsbsim
```

---

### 2. JSBSim API 호환성 문제

#### 문제: `AttributeError: 'jsbsim._jsbsim.FGFDMExec' object has no attribute 'get_ic'`

**원인:** JSBSim v1.2.0 이상에서 API가 변경되었습니다.

**해결 방법:** 
최신 코드(commit 47805b6)로 업데이트하세요. 이미 수정되었습니다!

```bash
git pull origin main
```

#### 수동 수정 방법:
`src/jsbsim_wrapper.py`의 `_initialize_conditions()` 메서드가 이미 양방향 호환성을 지원합니다:
- 새 API: property 기반 (`ic/` 프로퍼티 사용)
- 구 API: `get_ic()` 메서드 사용

---

### 3. 항공기 모델 로드 문제

#### 문제: `WARNING: 항공기 'c172p' 로드 실패`

**원인:** JSBSim 항공기 데이터 파일을 찾을 수 없습니다.

**해결 방법 1: 기본 제공 항공기 사용**
```python
# JSBSim과 함께 설치된 항공기만 사용
simulator = CrosswindSimulator(aircraft_model="c172p")
```

**해결 방법 2: 수동으로 항공기 경로 설정**
```python
import jsbsim
import os

# JSBSim 데이터 경로 확인
jsbsim_path = os.path.dirname(jsbsim.__file__)
print(f"JSBSim 설치 경로: {jsbsim_path}")
print(f"항공기 경로: {os.path.join(jsbsim_path, 'data', 'aircraft')}")

# 사용 가능한 항공기 목록 확인
aircraft_path = os.path.join(jsbsim_path, 'data', 'aircraft')
if os.path.exists(aircraft_path):
    print("사용 가능한 항공기:", os.listdir(aircraft_path))
```

**해결 방법 3: 항공기 데이터 다운로드**
```bash
# JSBSim 저장소에서 항공기 데이터 다운로드
git clone https://github.com/JSBSim-Team/jsbsim.git
# aircraft 폴더를 JSBSim 설치 경로에 복사
```

---

### 4. 시뮬레이션 실행 문제

#### 문제: 시뮬레이션이 즉시 중단됨

**원인:** 초기 조건이 불안정하거나 물리적으로 불가능한 상태일 수 있습니다.

**해결 방법:**
```python
# 안정적인 초기 조건 사용
simulator = CrosswindSimulator(
    aircraft_model="c172p",
    crosswind_speed=10.0,
    init_altitude=1000.0,    # 충분한 고도
    init_airspeed=60.0,      # 실속 속도 이상
    dt=0.01                  # 작은 시간 간격
)

# 시뮬레이션 전 초기 상태 확인
state = simulator.jsbsim.get_state()
print(f"초기 고도: {state['altitude_agl_ft']} ft")
print(f"초기 속도: {state['airspeed_kts']} kts")
```

#### 문제: 시뮬레이션 결과가 이상함

**진단 방법:**
```python
# 디버그 모드 활성화
import logging
logging.basicConfig(level=logging.DEBUG)

# 각 스텝의 상태 확인
for i in range(100):
    simulator.jsbsim.run_step()
    state = simulator.jsbsim.get_state()
    if i % 10 == 0:
        print(f"Step {i}: Alt={state['altitude_agl_ft']:.1f}ft, "
              f"Speed={state['airspeed_kts']:.1f}kts")
```

---

### 5. 시각화 문제

#### 문제: `matplotlib` 관련 오류

**해결 방법:**
```bash
pip install matplotlib seaborn --upgrade
```

#### 문제: 한글 폰트가 깨짐

**해결 방법 (Windows):**
```python
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'  # 또는 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False
```

**해결 방법 (Linux/macOS):**
```bash
# 나눔고딕 설치
sudo apt-get install fonts-nanum  # Ubuntu/Debian
brew install font-nanum            # macOS

# Python에서 설정
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'NanumGothic'
```

#### 문제: 그래프가 표시되지 않음

**해결 방법:**
```python
# 백엔드 확인 및 변경
import matplotlib
print(f"현재 백엔드: {matplotlib.get_backend()}")

# GUI 백엔드 사용 (대화형)
matplotlib.use('TkAgg')  # 또는 'Qt5Agg'

# 파일 저장 백엔드 사용 (서버 환경)
matplotlib.use('Agg')
```

---

### 6. 성능 문제

#### 문제: 시뮬레이션이 너무 느림

**해결 방법 1: 시간 간격 조정**
```python
# dt를 크게 설정 (정확도는 약간 감소)
simulator = CrosswindSimulator(
    dt=0.02,  # 기본값: 0.01
    # ... 기타 파라미터
)
```

**해결 방법 2: 진행 상황 표시 비활성화**
```python
results = simulator.run_simulation(
    duration=60.0,
    show_progress=False  # tqdm 비활성화
)
```

**해결 방법 3: 난기류 비활성화**
```python
simulator = CrosswindSimulator(
    turbulence=0.0,  # 난기류 없음
    # ... 기타 파라미터
)
```

---

### 7. 메모리 문제

#### 문제: 메모리 부족 오류

**해결 방법:**
```python
# 긴 시뮬레이션을 여러 세그먼트로 분할
duration_per_segment = 60.0
num_segments = 10

all_results = []
for i in range(num_segments):
    results = simulator.run_simulation(duration=duration_per_segment)
    # 필요한 데이터만 저장
    all_results.append(results[['time', 'lateral_deviation_m', 'drift_angle_deg']])
    simulator.reset()

# 결과 병합
import pandas as pd
combined_results = pd.concat(all_results, ignore_index=True)
```

---

### 8. 데이터 저장 문제

#### 문제: 결과 저장 시 권한 오류

**해결 방법:**
```python
import os

# 결과 디렉토리 확인 및 생성
output_dir = "data/results"
os.makedirs(output_dir, exist_ok=True)

# 절대 경로 사용
import os.path
output_path = os.path.abspath(os.path.join(output_dir, "results.csv"))
results.to_csv(output_path, index=False)
```

---

## 환경별 권장 설정

### Windows

```bash
# 가상환경 생성
python -m venv venv
venv\Scripts\activate

# 패키지 설치
pip install --upgrade pip
pip install -r requirements.txt

# 실행
python examples/basic_simulation.py
```

### Linux/macOS

```bash
# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install --upgrade pip
pip install -r requirements.txt

# 실행
python examples/basic_simulation.py
```

### Anaconda/Miniconda

```bash
# 환경 생성
conda create -n jsbsim-env python=3.9
conda activate jsbsim-env

# 패키지 설치
pip install -r requirements.txt

# 실행
python examples/basic_simulation.py
```

---

## 추가 도움말

### 로그 레벨 조정

```python
import logging

# 디버그 정보 표시
logging.basicConfig(level=logging.DEBUG)

# 경고만 표시
logging.basicConfig(level=logging.WARNING)

# 로그 비활성화
logging.basicConfig(level=logging.CRITICAL)
```

### JSBSim 버전 확인

```python
import jsbsim

print(f"JSBSim 버전: {jsbsim.__version__}")

# FDMExec 정보
fdm = jsbsim.FGFDMExec(None)
print(f"JSBSim 빌드 정보: {fdm.get_version()}")
```

### 지원되는 프로퍼티 확인

```python
fdm = jsbsim.FGFDMExec(None)

# 사용 가능한 프로퍼티 목록 (일부)
properties = [
    "position/lat-gc-deg",
    "position/long-gc-deg",
    "position/h-sl-ft",
    "velocities/vc-kts",
    "attitude/psi-deg",
    # ... 등등
]

for prop in properties:
    try:
        value = fdm.get_property_value(prop)
        print(f"{prop}: {value}")
    except:
        print(f"{prop}: 사용 불가")
```

---

## 버그 리포트

문제가 계속되면 GitHub Issues에 다음 정보와 함께 리포트해주세요:

1. Python 버전: `python --version`
2. JSBSim 버전: `pip show jsbsim`
3. OS 정보: Windows/Linux/macOS 버전
4. 오류 메시지 전체 (traceback 포함)
5. 재현 가능한 최소 코드

**GitHub Issues**: https://github.com/moonjang0701/wind/issues

---

## 유용한 링크

- [JSBSim 공식 문서](http://jsbsim.sourceforge.net/)
- [JSBSim GitHub](https://github.com/JSBSim-Team/jsbsim)
- [JSBSim Reference Manual](https://jsbsim-team.github.io/jsbsim-reference-manual/)
- [프로젝트 이슈 트래커](https://github.com/moonjang0701/wind/issues)
