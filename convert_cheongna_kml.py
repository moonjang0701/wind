#!/usr/bin/env python3
"""
청라시티타워 반경 5km 이내 건물을 간단한 KML로 변환
- 사각형 좌표 4개 포인트만 사용 (예제 형식)
- 높이는 A31 컬럼 사용
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point

# 청라시티타워 좌표
CHEONGNA_LAT = 37.533053
CHEONGNA_LON = 126.633973
RADIUS_KM = 5.0

def calc_distance_km(centroid, center_lat, center_lon):
    """두 점 사이 거리 계산 (km)"""
    dx = (centroid.x - center_lon) * 111 * np.cos(np.radians(center_lat))
    dy = (centroid.y - center_lat) * 111
    return np.sqrt(dx**2 + dy**2)

def polygon_to_simple_coords(polygon, height=0):
    """
    Polygon을 간단한 사각형 4개 포인트로 변환
    예제 형식과 동일하게
    """
    # 바운딩 박스 추출
    bounds = polygon.bounds  # (minx, miny, maxx, maxy)
    minx, miny, maxx, maxy = bounds
    
    # 4개 꼭짓점 (시계방향)
    coords = [
        f"{minx},{maxy},{height}",  # 좌상단
        f"{maxx},{maxy},{height}",  # 우상단
        f"{maxx},{miny},{height}",  # 우하단
        f"{minx},{miny},{height}",  # 좌하단
        f"{minx},{maxy},{height}"   # 다시 좌상단 (닫기)
    ]
    
    return '\n              '.join(coords)

def create_cheongna_kml(output_path='cheongna_buildings_5km.kml'):
    """청라 반경 5km KML 생성"""
    
    print("="*80)
    print("청라시티타워 반경 5km 건물 KML 생성")
    print("="*80)
    print(f"중심: {CHEONGNA_LAT}, {CHEONGNA_LON}")
    print(f"반경: {RADIUS_KM}km")
    
    # D162 데이터
    print("\n📍 D162 데이터 로딩...")
    gdf1 = gpd.read_file('D162/AL_D162_28_20250715.shp')
    gdf1 = gdf1.to_crs(epsg=4326)
    gdf1['centroid'] = gdf1.geometry.centroid
    gdf1['distance_km'] = gdf1['centroid'].apply(
        lambda c: calc_distance_km(c, CHEONGNA_LAT, CHEONGNA_LON)
    )
    gdf1_filtered = gdf1[gdf1['distance_km'] <= RADIUS_KM].copy()
    print(f"  필터링: {len(gdf1_filtered):,}개")
    
    # D164 데이터
    print("📍 D164 데이터 로딩...")
    gdf2 = gpd.read_file('D164/AL_D164_28_20250715.shp')
    gdf2 = gdf2.to_crs(epsg=4326)
    gdf2['centroid'] = gdf2.geometry.centroid
    gdf2['distance_km'] = gdf2['centroid'].apply(
        lambda c: calc_distance_km(c, CHEONGNA_LAT, CHEONGNA_LON)
    )
    gdf2_filtered = gdf2[gdf2['distance_km'] <= RADIUS_KM].copy()
    print(f"  필터링: {len(gdf2_filtered):,}개")
    
    # 합치기
    print("\n📦 데이터 병합 중...")
    gdf_all = pd.concat([gdf1_filtered, gdf2_filtered], ignore_index=True)
    total = len(gdf_all)
    print(f"총 건물: {total:,}개")
    
    # KML 생성
    print("\n🏗️ KML 파일 생성 중...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # XML 헤더
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('  <Document>\n')
        f.write(f'    <name>Cheongna City Tower 5km Buildings</name>\n')
        
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
        for idx, row in gdf_all.iterrows():
            if idx % 1000 == 0:
                print(f"  진행: {idx}/{total} ({idx/total*100:.1f}%)")
            
            # 높이 추출 (A31)
            try:
                height = float(row['A31']) if pd.notna(row['A31']) else 5.0
                if height < 0 or height > 200:
                    height = 5.0
            except:
                height = 5.0
            
            # Placemark
            f.write('    <Placemark>\n')
            f.write(f'      <name>Building_{idx}</name>\n')
            f.write('      <styleUrl>#redBox</styleUrl>\n')
            f.write('      <Polygon>\n')
            f.write('        <extrude>1</extrude>\n')
            f.write('        <altitudeMode>relativeToGround</altitudeMode>\n')
            f.write('        <outerBoundaryIs>\n')
            f.write('          <LinearRing>\n')
            f.write('            <coordinates>\n')
            
            # 간단한 4개 좌표
            coords = polygon_to_simple_coords(row.geometry, height)
            f.write(f'              {coords}\n')
            
            f.write('            </coordinates>\n')
            f.write('          </LinearRing>\n')
            f.write('        </outerBoundaryIs>\n')
            f.write('      </Polygon>\n')
            f.write('    </Placemark>\n')
        
        f.write('  </Document>\n')
        f.write('</kml>\n')
    
    print(f"\n✅ 완료! 파일: {output_path}")
    print(f"📊 총 {total:,}개 건물")
    
    # 통계
    heights = []
    for _, row in gdf_all.iterrows():
        try:
            h = float(row['A31']) if pd.notna(row['A31']) else 5.0
            if 0 <= h <= 200:
                heights.append(h)
        except:
            pass
    
    if heights:
        print(f"\n높이 통계:")
        print(f"  평균: {np.mean(heights):.2f}m")
        print(f"  중간값: {np.median(heights):.2f}m")
        print(f"  최소: {np.min(heights):.2f}m")
        print(f"  최대: {np.max(heights):.2f}m")

if __name__ == '__main__':
    create_cheongna_kml()
