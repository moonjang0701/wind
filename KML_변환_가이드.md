# KML 변환 가이드

## 📋 개요

이 프로젝트는 Shapefile 형식의 건물 데이터를 Google Earth에서 볼 수 있는 KML 형식으로 변환합니다.

## 📦 생성된 파일

### 전체 데이터
- **buildings_D162_full.kml** - D162 지역 전체 건물 (120,657개)
- **buildings_D164_full.kml** - D164 지역 전체 건물 (36,766개)

### 샘플 데이터 (테스트용)
- **buildings_D162.kml** - D162 지역 샘플 (100개)
- **buildings_D164.kml** - D164 지역 샘플 (100개)

## 🎨 KML 특징

### 시각화 스타일
- **색상**: 빨간색 (반투명)
- **선 두께**: 1.5
- **높이**: 건물의 실제 높이 정보 반영 (A17 컬럼)
- **3D 효과**: extrude 활성화로 지면에서 솟아오른 형태

### 포함된 정보
각 건물 Placemark에는 다음 정보가 포함됩니다:
- 건물 ID (A0 컬럼)
- 높이 정보 (A17 컬럼, 미터 단위)
- 주소 (A3 컬럼)
- 용도 (A21 컬럼)

## 🚀 Google Earth에서 열기

### 방법 1: 직접 열기
1. Google Earth Pro 또는 Google Earth Web을 실행
2. `파일 > 열기` 메뉴 선택
3. 생성된 KML 파일 선택

### 방법 2: 드래그 앤 드롭
1. Google Earth 실행
2. KML 파일을 Google Earth 창으로 드래그

### 방법 3: 더블 클릭
- KML 파일을 더블 클릭하면 자동으로 Google Earth가 실행됩니다

## 📊 데이터 정보

### 원본 데이터
- **형식**: Shapefile (.shp, .dbf, .shx, .prj, .fix)
- **좌표계**: EPSG:5186 (Korea 2000 / Central Belt)
- **변환 좌표계**: EPSG:4326 (WGS84 경위도)

### D162 지역
- 위치: 인천광역시 중구 일대
- 건물 수: 120,657개
- 파일 크기: 약 101MB

### D164 지역
- 위치: 인천광역시 중구 일대
- 건물 수: 36,766개
- 파일 크기: 약 36MB

## 🛠️ 사용된 변환 스크립트

### 1. convert_to_kml_fast.py
빠른 변환을 위한 스크립트
```bash
# 샘플 100개만 변환
python3 convert_to_kml_fast.py --sample 100

# 전체 변환
python3 convert_to_kml_fast.py
```

### 2. convert_chunked.py (권장)
메모리 효율적인 청크 방식 변환
```bash
# 기본 (청크 크기 5000)
python3 convert_chunked.py

# 청크 크기 지정
python3 convert_chunked.py --chunk-size 3000
```

## 📝 예제 KML 구조

```xml
<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>D162 - AL_D162_28_20250715</name>
    <description>총 120657개 건물</description>
    <Style id="buildingStyle">
      <LineStyle>
        <color>ff0000ff</color>
        <width>1.5</width>
      </LineStyle>
      <PolyStyle>
        <color>7f0000ff</color>
        <fill>1</fill>
        <outline>1</outline>
      </PolyStyle>
    </Style>
    <Placemark>
      <name>D162_0</name>
      <description>
        ID: 2000166147524374070100000000&lt;br/&gt;
        높이: 106.0m&lt;br/&gt;
        주소: 인천광역시 중구 신흥동3가&lt;br/&gt;
        용도: 주건축물&lt;br/&gt;
      </description>
      <styleUrl>#buildingStyle</styleUrl>
      <Polygon>
        <extrude>1</extrude>
        <altitudeMode>relativeToGround</altitudeMode>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>126.618,37.438,106.0 ...</coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
    ...
  </Document>
</kml>
```

## 🔧 커스터마이징

### 색상 변경
`convert_chunked.py` 파일에서 색상 코드 수정:
```python
# 파란색으로 변경: ff0000ff -> ffff0000
# 초록색으로 변경: ff0000ff -> ff00ff00
```

### 높이 컬럼 변경
다른 컬럼을 높이로 사용하려면:
```bash
python3 convert_chunked.py --height-column A18
```

### 청크 크기 조정
메모리가 부족하면 청크 크기를 줄이세요:
```bash
python3 convert_chunked.py --chunk-size 1000
```

## ⚠️ 주의사항

1. **파일 크기**: 전체 KML 파일은 매우 클 수 있습니다
   - D162: 약 101MB
   - D164: 약 36MB

2. **Google Earth 성능**: 
   - 한 번에 너무 많은 건물을 표시하면 느려질 수 있습니다
   - 필요한 지역만 선택적으로 표시하세요

3. **메모리**: 
   - 큰 파일을 열 때 충분한 메모리가 필요합니다
   - Google Earth Pro 사용을 권장합니다

## 📚 추가 정보

### Shapefile 컬럼 설명
- **A0**: 건물 고유 ID
- **A3**: 주소
- **A17**: 건물 높이 (미터)
- **A21**: 건물 용도
- **geometry**: 건물 폴리곤 좌표

### 좌표계 정보
- **원본**: EPSG:5186 (Korea 2000 / Central Belt)
- **변환**: EPSG:4326 (WGS84 경위도)
- **이유**: Google Earth는 WGS84 좌표계를 사용

## 🎯 사용 예시

### 청나 지역 빨간 박스 예제
제공하신 예제처럼 특정 지역만 표시하려면:

```xml
<Placemark>
  <name>Cheongna Red Box (75 x 75)</name>
  <styleUrl>#redBox</styleUrl>
  <Polygon>
    <extrude>1</extrude>
    <altitudeMode>relativeToGround</altitudeMode>
    <outerBoundaryIs>
      <LinearRing>
        <coordinates>
          126.6334882019707,37.53316986669062,448
          126.6343377980293,37.53316986669062,448
          126.6343377980293,37.53249613330937,448
          126.6334882019707,37.53249613330937,448
          126.6334882019707,37.53316986669062,448
        </coordinates>
      </LinearRing>
    </outerBoundaryIs>
  </Polygon>
</Placemark>
```

생성된 KML 파일은 모든 건물을 이와 동일한 형식으로 표현합니다!

## 🤝 도움말

문제가 발생하면:
1. Python 버전 확인: `python3 --version` (3.7 이상 필요)
2. 필요한 라이브러리 설치: `pip install geopandas shapely pyproj`
3. 메모리 부족 시 청크 크기 줄이기

## 📧 연락처

추가 질문이나 문제가 있으면 알려주세요!
