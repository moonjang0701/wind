#!/usr/bin/env python3
"""
Shapefile을 KML로 빠르게 변환하는 스크립트
XML 문자열 빌더를 사용하여 속도 향상
"""

import geopandas as gpd
from pathlib import Path
import sys

def escape_xml(text):
    """XML 특수문자 이스케이프"""
    if text is None:
        return ''
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&apos;')
    return text

def polygon_to_coords(polygon, height=0):
    """Shapely Polygon을 KML 좌표 문자열로 변환"""
    coords = []
    
    # 외곽선 좌표 추출
    if hasattr(polygon, 'exterior'):
        exterior = polygon.exterior
    else:
        # MultiPolygon의 경우 첫 번째 폴리곤만 사용
        exterior = polygon.geoms[0].exterior
    
    for x, y in exterior.coords:
        coords.append(f"{x},{y},{height}")
    
    return ' '.join(coords)

def shapefile_to_kml_fast(shapefile_path, output_path, height_column='A17', name_prefix='Building', max_buildings=None):
    """
    Shapefile을 KML로 빠르게 변환
    """
    
    print(f"읽는 중: {shapefile_path}")
    
    # Shapefile 읽기
    gdf = gpd.read_file(shapefile_path)
    
    if max_buildings:
        print(f"샘플링: 처음 {max_buildings}개 건물만 변환")
        gdf = gdf.head(max_buildings)
    
    # WGS84 (경위도)로 변환
    print("좌표계 변환 중...")
    gdf = gdf.to_crs(epsg=4326)
    
    # KML 헤더
    file_name = Path(shapefile_path).stem
    kml_parts = []
    kml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    kml_parts.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
    kml_parts.append('  <Document>')
    kml_parts.append(f'    <name>{escape_xml(name_prefix)} - {escape_xml(file_name)}</name>')
    kml_parts.append(f'    <description>총 {len(gdf)}개 건물</description>')
    
    # 스타일 정의
    kml_parts.append('    <Style id="buildingStyle">')
    kml_parts.append('      <LineStyle>')
    kml_parts.append('        <color>ff0000ff</color>')
    kml_parts.append('        <width>1.5</width>')
    kml_parts.append('      </LineStyle>')
    kml_parts.append('      <PolyStyle>')
    kml_parts.append('        <color>7f0000ff</color>')
    kml_parts.append('        <fill>1</fill>')
    kml_parts.append('        <outline>1</outline>')
    kml_parts.append('      </PolyStyle>')
    kml_parts.append('    </Style>')
    
    print(f"KML 변환 중... (총 {len(gdf)}개 건물)")
    
    # 각 건물을 Placemark로 추가
    for idx, row in gdf.iterrows():
        if idx % 5000 == 0:
            print(f"  진행 중: {idx}/{len(gdf)}")
        
        # 높이 정보 추출
        try:
            if height_column in row and row[height_column] is not None:
                height = float(row[height_column])
            else:
                height = 10.0
        except (ValueError, TypeError):
            height = 10.0
        
        # 건물 ID
        building_id = row.get('A0', f'Building_{idx}')
        
        # Placemark 시작
        kml_parts.append('    <Placemark>')
        kml_parts.append(f'      <name>{escape_xml(name_prefix)}_{idx}</name>')
        
        # 설명
        desc_text = f'ID: {escape_xml(building_id)}&lt;br/&gt;'
        desc_text += f'높이: {height}m&lt;br/&gt;'
        if 'A3' in row and row['A3']:
            desc_text += f'주소: {escape_xml(row["A3"])}&lt;br/&gt;'
        if 'A21' in row and row['A21']:
            desc_text += f'용도: {escape_xml(row["A21"])}&lt;br/&gt;'
        
        kml_parts.append(f'      <description>{desc_text}</description>')
        kml_parts.append('      <styleUrl>#buildingStyle</styleUrl>')
        
        # Polygon
        kml_parts.append('      <Polygon>')
        kml_parts.append('        <extrude>1</extrude>')
        kml_parts.append('        <altitudeMode>relativeToGround</altitudeMode>')
        kml_parts.append('        <outerBoundaryIs>')
        kml_parts.append('          <LinearRing>')
        
        coords = polygon_to_coords(row.geometry, height)
        kml_parts.append(f'            <coordinates>{coords}</coordinates>')
        
        kml_parts.append('          </LinearRing>')
        kml_parts.append('        </outerBoundaryIs>')
        kml_parts.append('      </Polygon>')
        kml_parts.append('    </Placemark>')
    
    # KML 푸터
    kml_parts.append('  </Document>')
    kml_parts.append('</kml>')
    
    # 파일로 저장
    print("KML 파일 저장 중...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(kml_parts))
    
    print(f"완료! 저장됨: {output_path}")
    print(f"총 {len(gdf)}개 건물이 변환되었습니다.")
    
    return len(gdf)

def main():
    """메인 함수"""
    
    import argparse
    parser = argparse.ArgumentParser(description='Shapefile을 KML로 변환')
    parser.add_argument('--sample', type=int, help='샘플 건물 수 (전체 변환하려면 생략)')
    args = parser.parse_args()
    
    # D162 변환
    print("="*80)
    print("D162 데이터 변환 시작")
    print("="*80)
    count1 = shapefile_to_kml_fast(
        shapefile_path='D162/AL_D162_28_20250715.shp',
        output_path='buildings_D162.kml',
        height_column='A17',
        name_prefix='D162',
        max_buildings=args.sample
    )
    
    print("\n" + "="*80)
    print("D164 데이터 변환 시작")
    print("="*80)
    
    # D164 변환
    count2 = shapefile_to_kml_fast(
        shapefile_path='D164/AL_D164_28_20250715.shp',
        output_path='buildings_D164.kml',
        height_column='A17',
        name_prefix='D164',
        max_buildings=args.sample
    )
    
    print("\n" + "="*80)
    print("모든 변환 완료!")
    print("="*80)
    print(f"\n생성된 파일:")
    print(f"  - buildings_D162.kml ({count1}개 건물)")
    print(f"  - buildings_D164.kml ({count2}개 건물)")
    print("\nGoogle Earth에서 열어서 확인하세요!")

if __name__ == '__main__':
    main()
