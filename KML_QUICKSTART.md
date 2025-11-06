# 🚀 KML 변환 빠른 시작 가이드

## ⚡ 5분 안에 시작하기

### 1️⃣ 필요한 것
```bash
# Python 3.7 이상
python3 --version

# 필요한 라이브러리 설치
pip install geopandas shapely pyproj
```

### 2️⃣ 데이터 준비
- Shapefile 데이터를 프로젝트 폴더에 압축 해제
- 예: `D162/`, `D164/` 폴더

### 3️⃣ 변환 실행
```bash
# 전체 데이터 변환 (권장)
python3 convert_chunked.py

# 또는 샘플 100개만 테스트
python3 convert_to_kml_fast.py --sample 100
```

### 4️⃣ Google Earth에서 열기
1. 생성된 `buildings_*.kml` 파일을 찾기
2. 더블 클릭 또는 Google Earth로 드래그
3. 3D 건물 보기! 🏢

## 📦 생성되는 파일

| 파일명 | 크기 | 설명 |
|--------|------|------|
| `buildings_D162_full.kml` | 101 MB | D162 지역 120,657개 건물 |
| `buildings_D164_full.kml` | 36 MB | D164 지역 36,766개 건물 |
| `buildings_combined.kml` | 137 MB | 두 지역 통합 (157,423개) |

## 🎨 어떻게 보이나요?

```
🏢 3D 건물
- 빨간색 반투명 박스
- 실제 높이 반영
- 건물 정보 포함:
  ✓ ID
  ✓ 높이 (미터)
  ✓ 주소
  ✓ 용도
```

## ⚙️ 고급 옵션

### 청크 크기 조정 (메모리가 부족한 경우)
```bash
python3 convert_chunked.py --chunk-size 1000
```

### 여러 KML 병합
```bash
python3 merge_kml.py
```

## ❓ 문제 해결

### 메모리 부족
```bash
# 더 작은 청크로 실행
python3 convert_chunked.py --chunk-size 1000
```

### 변환이 느림
```bash
# 샘플로 먼저 테스트
python3 convert_to_kml_fast.py --sample 100
```

### Google Earth가 느림
- 지역별로 나누어 로드 (D162, D164 개별)
- Google Earth Pro 사용 권장

## 📚 더 알아보기

- 상세 가이드: `KML_변환_가이드.md`
- 프로젝트 요약: `SUMMARY.md`

## ✅ 체크리스트

- [ ] Python 설치 확인
- [ ] 라이브러리 설치
- [ ] Shapefile 데이터 준비
- [ ] 변환 스크립트 실행
- [ ] KML 파일 생성 확인
- [ ] Google Earth에서 열기

---

**🎉 완료! 이제 Google Earth에서 15만 개 이상의 건물을 3D로 볼 수 있습니다!**
