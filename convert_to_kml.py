#!/usr/bin/env python3
"""
Shapefile을 KML로 변환하는 스크립트
건물의 위치와 높이 정보를 Google Earth에서 볼 수 있는 형식으로 변환
"""

import geopandas as gpd
from xml.dom import minidom
import xml.etree.ElementTree as ET
from pathlib import Path
import sys

def create_kml_header(name, description=""):
    """KML 파일 헤더 생성"""
    kml = ET.Element('kml', xmlns='http://www.opengis.net/kml/2.2')
    document = ET.SubElement(kml, 'Document')
    
    # 문서 이름
    name_elem = ET.SubElement(document, 'name')
    name_elem.text = name
    
    if description:
        desc_elem = ET.SubElement(document, 'description')
        desc_elem.text = description
    
    # 스타일 정의 - 빨간색 반투명
    style = ET.SubElement(document, 'Style', id='buildingStyle')
    line_style = ET.SubElement(style, 'LineStyle')
    line_color = ET.SubElement(line_style, 'color')
    line_color.text = 'ff0000ff'  # 빨간색 (aabbggrr)
    line_width = ET.SubElement(line_style, 'width')
    line_width.text = '1.5'
    
    poly_style = ET.SubElement(style, 'PolyStyle')
    poly_color = ET.SubElement(poly_style, 'color')
    poly_color.text = '7f0000ff'  # 반투명 빨간색 (50% 투명도)
    fill = ET.SubElement(poly_style, 'fill')
    fill.text = '1'
    outline = ET.SubElement(poly_style, 'outline')
    outline.text = '1'
    
    return kml, document

def convert_polygon_to_coordinates(polygon, height=0):
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
    
    return '\n              '.join(coords)

def shapefile_to_kml(shapefile_path, output_path, height_column='A17', name_prefix='Building'):
    """
    Shapefile을 KML로 변환
    
    Parameters:
    -----------
    shapefile_path : str
        입력 Shapefile 경로
    output_path : str
        출력 KML 파일 경로
    height_column : str
        높이 정보가 들어있는 컬럼명 (기본값: 'A17')
    name_prefix : str
        건물 이름 접두사
    """
    
    print(f"읽는 중: {shapefile_path}")
    
    # Shapefile 읽기
    gdf = gpd.read_file(shapefile_path)
    
    # WGS84 (경위도)로 변환
    print("좌표계 변환 중...")
    gdf = gdf.to_crs(epsg=4326)
    
    # KML 생성
    file_name = Path(shapefile_path).stem
    kml, document = create_kml_header(
        name=f"{name_prefix} - {file_name}",
        description=f"총 {len(gdf)}개 건물"
    )
    
    print(f"KML 변환 중... (총 {len(gdf)}개 건물)")
    
    # 각 건물을 Placemark로 추가
    for idx, row in gdf.iterrows():
        if idx % 1000 == 0:
            print(f"  진행 중: {idx}/{len(gdf)}")
        
        # 높이 정보 추출
        try:
            if height_column in row and row[height_column] is not None:
                height = float(row[height_column])
            else:
                height = 10.0  # 기본 높이
        except (ValueError, TypeError):
            height = 10.0
        
        # Placemark 생성
        placemark = ET.SubElement(document, 'Placemark')
        
        # 이름
        name_elem = ET.SubElement(placemark, 'name')
        building_id = row.get('A0', f'Building_{idx}')
        name_elem.text = f"{name_prefix}_{idx}"
        
        # 설명 (추가 정보)
        desc = ET.SubElement(placemark, 'description')
        desc_text = f"ID: {building_id}<br/>"
        desc_text += f"높이: {height}m<br/>"
        if 'A3' in row and row['A3']:
            desc_text += f"주소: {row['A3']}<br/>"
        if 'A21' in row and row['A21']:
            desc_text += f"용도: {row['A21']}<br/>"
        desc.text = desc_text
        
        # 스타일 적용
        style_url = ET.SubElement(placemark, 'styleUrl')
        style_url.text = '#buildingStyle'
        
        # Polygon 생성
        polygon = ET.SubElement(placemark, 'Polygon')
        extrude = ET.SubElement(polygon, 'extrude')
        extrude.text = '1'
        altitude_mode = ET.SubElement(polygon, 'altitudeMode')
        altitude_mode.text = 'relativeToGround'
        
        outer_boundary = ET.SubElement(polygon, 'outerBoundaryIs')
        linear_ring = ET.SubElement(outer_boundary, 'LinearRing')
        coordinates = ET.SubElement(linear_ring, 'coordinates')
        
        # 좌표 변환
        coordinates.text = convert_polygon_to_coordinates(row.geometry, height)
    
    # XML을 예쁘게 포맷팅
    print("KML 파일 저장 중...")
    xml_str = ET.tostring(kml, encoding='utf-8')
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent='  ', encoding='utf-8')
    
    # 파일로 저장
    with open(output_path, 'wb') as f:
        f.write(pretty_xml)
    
    print(f"완료! 저장됨: {output_path}")
    print(f"총 {len(gdf)}개 건물이 변환되었습니다.")

def main():
    """메인 함수"""
    
    # D162 변환
    print("="*80)
    print("D162 데이터 변환 시작")
    print("="*80)
    shapefile_to_kml(
        shapefile_path='D162/AL_D162_28_20250715.shp',
        output_path='buildings_D162.kml',
        height_column='A17',
        name_prefix='D162'
    )
    
    print("\n" + "="*80)
    print("D164 데이터 변환 시작")
    print("="*80)
    
    # D164 변환
    shapefile_to_kml(
        shapefile_path='D164/AL_D164_28_20250715.shp',
        output_path='buildings_D164.kml',
        height_column='A17',
        name_prefix='D164'
    )
    
    print("\n" + "="*80)
    print("모든 변환 완료!")
    print("="*80)
    print("\n생성된 파일:")
    print("  - buildings_D162.kml (D162 지역 건물)")
    print("  - buildings_D164.kml (D164 지역 건물)")
    print("\nGoogle Earth에서 열어서 확인하세요!")

if __name__ == '__main__':
    main()
