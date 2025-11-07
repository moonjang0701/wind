#!/usr/bin/env python3
"""
청라시티타워 반경 5km 이내 건물을 필터링하여 KML로 변환
- 높이 > 0m and 높이 <= 300m
- 면적 <= 100m²
- 간단한 4개 좌표
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point

# 청라시티타워 좌표
CHEONGNA_LAT = 37.533053
CHEONGNA_LON = 126.633973
RADIUS_KM = 5.0

# 필터링 조건
MAX_HEIGHT = 300.0  # 최대 높이 (m)
MAX_AREA = 100.0    # 최대 면적 (m²)
MIN_HEIGHT = 0.0    # 최소 높이 (0 제외)

def calc_distance_km(centroid, center_lat, center_lon):
    """두 점 사이 거리 계산 (km)"""
    dx = (centroid.x - center_lon) * 111 * np.cos(np.radians(center_lat))
    dy = (centroid.y - center_lat) * 111
    return np.sqrt(dx**2 + dy**2)

def calc_area_m2(geometry):
    """폴리곤 면적 계산 (대략적, m²)"""
    # 바운딩 박스 기준으로 대략 계산
    bounds = geometry.bounds
    width_deg = bounds[2] - bounds[0]
    height_deg = bounds[3] - bounds[1]
    
    # 위도/경도를 미터로 변환 (대략)
    width_m = width_deg * 111000 * np.cos(np.radians(CHEONGNA_LAT))
    height_m = height_deg * 111000
    
    return width_m * height_m

def polygon_to_simple_coords(polygon, height=0):
    """Polygon을 간단한 사각형 4개 포인트로 변환"""
    bounds = polygon.bounds
    minx, miny, maxx, maxy = bounds
    
    # 4개 꼭짓점 (시계방향)
    coords = [
        f"{minx},{maxy},{height}",
        f"{maxx},{maxy},{height}",
        f"{maxx},{miny},{height}",
        f"{minx},{miny},{height}",
        f"{minx},{maxy},{height}"
    ]
    
    return '\n              '.join(coords)

def create_cheongna_kml(output_path='cheongna_buildings_filtered.kml'):
    """청라 반경 5km 필터링된 KML 생성"""
    
    print("="*80)
    print("청라시티타워 반경 5km 건물 KML 생성 (필터링)")
    print("="*80)
    print(f"중심: {CHEONGNA_LAT}, {CHEONGNA_LON}")
    print(f"반경: {RADIUS_KM}km")
    print(f"\n필터링 조건:")
    print(f"  - 높이: {MIN_HEIGHT}m < height <= {MAX_HEIGHT}m")
    print(f"  - 면적: <= {MAX_AREA}m²")
    
    # D162 데이터
    print("\n📍 D162 데이터 로딩...")
    gdf1 = gpd.read_file('D162/AL_D162_28_20250715.shp')
    gdf1 = gdf1.to_crs(epsg=4326)
    gdf1['centroid'] = gdf1.geometry.centroid
    gdf1['distance_km'] = gdf1['centroid'].apply(
        lambda c: calc_distance_km(c, CHEONGNA_LAT, CHEONGNA_LON)
    )
    gdf1_5km = gdf1[gdf1['distance_km'] <= RADIUS_KM].copy()
    print(f"  5km 이내: {len(gdf1_5km):,}개")
    
    # D164 데이터
    print("📍 D164 데이터 로딩...")
    gdf2 = gpd.read_file('D164/AL_D164_28_20250715.shp')
    gdf2 = gdf2.to_crs(epsg=4326)
    gdf2['centroid'] = gdf2.geometry.centroid
    gdf2['distance_km'] = gdf2['centroid'].apply(
        lambda c: calc_distance_km(c, CHEONGNA_LAT, CHEONGNA_LON)
    )
    gdf2_5km = gdf2[gdf2['distance_km'] <= RADIUS_KM].copy()
    print(f"  5km 이내: {len(gdf2_5km):,}개")
    
    # 합치기
    print("\n📦 데이터 병합 중...")
    gdf_all = pd.concat([gdf1_5km, gdf2_5km], ignore_index=True)
    print(f"병합 후: {len(gdf_all):,}개")
    
    # 높이 및 면적 필터링
    print("\n🔍 필터링 중...")
    
    filtered_data = []
    stats = {
        'total': len(gdf_all),
        'height_zero': 0,
        'height_too_high': 0,
        'area_too_large': 0,
        'height_invalid': 0,
        'passed': 0
    }
    
    for idx, row in gdf_all.iterrows():
        # 높이 추출
        try:
            height = float(row['A31']) if pd.notna(row['A31']) else 0.0
        except:
            stats['height_invalid'] += 1
            continue
        
        # 높이 필터링
        if height <= MIN_HEIGHT:
            stats['height_zero'] += 1
            continue
        
        if height > MAX_HEIGHT:
            stats['height_too_high'] += 1
            continue
        
        # 면적 계산
        area = calc_area_m2(row.geometry)
        
        # 면적 필터링
        if area > MAX_AREA:
            stats['area_too_large'] += 1
            continue
        
        # 통과
        stats['passed'] += 1
        filtered_data.append({
            'geometry': row.geometry,
            'height': height,
            'area': area
        })
    
    print(f"\n필터링 결과:")
    print(f"  원본: {stats['total']:,}개")
    print(f"  높이 0: {stats['height_zero']:,}개 제외")
    print(f"  높이 > {MAX_HEIGHT}m: {stats['height_too_high']:,}개 제외")
    print(f"  면적 > {MAX_AREA}m²: {stats['area_too_large']:,}개 제외")
    print(f"  높이 무효: {stats['height_invalid']:,}개 제외")
    print(f"  ✅ 최종: {stats['passed']:,}개")
    
    if stats['passed'] == 0:
        print("\n⚠️ 필터링 후 건물이 없습니다!")
        return
    
    # KML 생성
    print("\n🏗️ KML 파일 생성 중...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # XML 헤더
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('  <Document>\n')
        f.write(f'    <name>Cheongna City Tower 5km (Filtered)</name>\n')
        
        # LookAt
        f.write('    <LookAt>\n')
        f.write('      <heading>327.04412726540033</heading>\n')
        f.write('      <tilt>83.29890837595849</tilt>\n')
        f.write(f'      <latitude>{CHEONGNA_LAT}</latitude>\n')
        f.write(f'      <longitude>{CHEONGNA_LON}</longitude>\n')
        f.write('      <range>5000</range>\n')
        f.write('      <altitude>0</altitude>\n')
        f.write('    </LookAt>\n')
        
        # 스타일 (빨간색 박스)
        f.write('    <Style id="redBox">\n')
        f.write('      <LineStyle>\n')
        f.write('        <color>ff0000ff</color>\n')
        f.write('        <width>1.5</width>\n')
        f.write('      </LineStyle>\n')
        f.write('      <PolyStyle>\n')
        f.write('        <color>ff0000ff</color>\n')
        f.write('        <fill>1</fill>\n')
        f.write('        <outline>1</outline>\n')
        f.write('      </PolyStyle>\n')
        f.write('    </Style>\n')
        
        # 각 건물
        for idx, building in enumerate(filtered_data):
            if idx % 1000 == 0 and idx > 0:
                print(f"  진행: {idx}/{len(filtered_data)} ({idx/len(filtered_data)*100:.1f}%)")
            
            f.write('    <Placemark>\n')
            f.write(f'      <name>Building_{idx}</name>\n')
            f.write('      <styleUrl>#redBox</styleUrl>\n')
            f.write('      <Polygon>\n')
            f.write('        <extrude>1</extrude>\n')
            f.write('        <altitudeMode>relativeToGround</altitudeMode>\n')
            f.write('        <outerBoundaryIs>\n')
            f.write('          <LinearRing>\n')
            f.write('            <coordinates>\n')
            
            coords = polygon_to_simple_coords(building['geometry'], building['height'])
            f.write(f'              {coords}\n')
            
            f.write('            </coordinates>\n')
            f.write('          </LinearRing>\n')
            f.write('        </outerBoundaryIs>\n')
            f.write('      </Polygon>\n')
            f.write('    </Placemark>\n')
        
        f.write('  </Document>\n')
        f.write('</kml>\n')
    
    print(f"\n✅ 완료! 파일: {output_path}")
    print(f"📊 총 {len(filtered_data):,}개 건물")
    
    # 통계
    heights = [b['height'] for b in filtered_data]
    areas = [b['area'] for b in filtered_data]
    
    print(f"\n높이 통계:")
    print(f"  평균: {np.mean(heights):.2f}m")
    print(f"  중간값: {np.median(heights):.2f}m")
    print(f"  최소: {np.min(heights):.2f}m")
    print(f"  최대: {np.max(heights):.2f}m")
    
    print(f"\n면적 통계:")
    print(f"  평균: {np.mean(areas):.2f}m²")
    print(f"  중간값: {np.median(areas):.2f}m²")
    print(f"  최소: {np.min(areas):.2f}m²")
    print(f"  최대: {np.max(areas):.2f}m²")

if __name__ == '__main__':
    create_cheongna_kml()
