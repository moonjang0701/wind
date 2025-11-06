#!/usr/bin/env python3
"""
Shapefile을 간단한 KML로 변환 (높이, 색상, 위치만)
사용자가 제공한 예제 형식과 동일하게 생성
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path

def polygon_to_coords(polygon, height=0):
    """Shapely Polygon을 KML 좌표 문자열로 변환"""
    coords = []
    
    if hasattr(polygon, 'exterior'):
        exterior = polygon.exterior
    else:
        exterior = polygon.geoms[0].exterior
    
    for x, y in exterior.coords:
        coords.append(f"{x},{y},{height}")
    
    return '\n              '.join(coords)

def shapefile_to_simple_kml(shapefile_path, output_path, height_column='A31', 
                            name_prefix='Building', chunk_size=5000):
    """
    Shapefile을 간단한 KML로 변환 (높이, 색상, 위치만 포함)
    """
    
    print(f"읽는 중: {shapefile_path}")
    
    # Shapefile 읽기
    gdf = gpd.read_file(shapefile_path)
    total = len(gdf)
    
    print(f"총 {total}개 건물")
    print(f"높이 컬럼: {height_column}")
    print("좌표계 변환 및 KML 작성 중...")
    
    file_name = Path(shapefile_path).stem
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # XML 헤더
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        f.write('  <Document>\n')
        f.write(f'    <name>{name_prefix} - {file_name}</name>\n')
        
        # LookAt (시작 뷰)
        f.write('    <LookAt>\n')
        f.write('      <heading>327.04412726540033</heading>\n')
        f.write('      <tilt>83.29890837595849</tilt>\n')
        f.write('      <latitude>37.533053</latitude>\n')
        f.write('      <longitude>126.633973</longitude>\n')
        f.write('      <range>500</range>\n')
        f.write('      <altitude>0</altitude>\n')
        f.write('    </LookAt>\n')
        
        # 스타일 정의 (빨간색)
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
        
        # 청크 단위로 처리
        for start_idx in range(0, total, chunk_size):
            end_idx = min(start_idx + chunk_size, total)
            print(f"  진행 중: {start_idx}-{end_idx}/{total} ({(end_idx/total*100):.1f}%)")
            
            # 청크 추출 및 변환
            chunk = gdf.iloc[start_idx:end_idx].copy()
            chunk = chunk.to_crs(epsg=4326)
            
            # 각 건물 작성
            for idx_in_chunk, (idx, row) in enumerate(chunk.iterrows()):
                global_idx = start_idx + idx_in_chunk
                
                # 높이 정보 추출
                try:
                    if height_column in row and row[height_column] is not None:
                        height = float(row[height_column])
                        if height < 0 or height > 200:  # 현실적인 범위로 제한
                            height = 5.0
                    else:
                        height = 5.0
                except (ValueError, TypeError):
                    height = 5.0
                
                # Placemark
                f.write('    <Placemark>\n')
                f.write(f'      <name>{name_prefix}_{global_idx}</name>\n')
                f.write('      <styleUrl>#redBox</styleUrl>\n')
                f.write('      <Polygon>\n')
                f.write('        <extrude>1</extrude>\n')
                f.write('        <altitudeMode>relativeToGround</altitudeMode>\n')
                f.write('        <outerBoundaryIs>\n')
                f.write('          <LinearRing>\n')
                f.write('            <coordinates>\n')
                
                coords = polygon_to_coords(row.geometry, height)
                f.write(f'              {coords}\n')
                
                f.write('            </coordinates>\n')
                f.write('          </LinearRing>\n')
                f.write('        </outerBoundaryIs>\n')
                f.write('      </Polygon>\n')
                f.write('    </Placemark>\n')
            
            del chunk
        
        # 푸터
        f.write('  </Document>\n')
        f.write('</kml>\n')
    
    print(f"완료! 저장됨: {output_path}")
    print(f"총 {total}개 건물이 변환되었습니다.")
    
    return total

def main():
    """메인 함수"""
    
    import argparse
    parser = argparse.ArgumentParser(description='Shapefile을 간단한 KML로 변환')
    parser.add_argument('--chunk-size', type=int, default=5000, help='청크 크기')
    parser.add_argument('--height-column', type=str, default='A31', help='높이 컬럼 이름')
    args = parser.parse_args()
    
    # D162 변환
    print("="*80)
    print("D162 데이터 변환 시작 (간단한 KML)")
    print("="*80)
    count1 = shapefile_to_simple_kml(
        shapefile_path='D162/AL_D162_28_20250715.shp',
        output_path='buildings_D162_simple.kml',
        height_column=args.height_column,
        name_prefix='D162',
        chunk_size=args.chunk_size
    )
    
    print("\n" + "="*80)
    print("D164 데이터 변환 시작 (간단한 KML)")
    print("="*80)
    
    # D164 변환
    count2 = shapefile_to_simple_kml(
        shapefile_path='D164/AL_D164_28_20250715.shp',
        output_path='buildings_D164_simple.kml',
        height_column=args.height_column,
        name_prefix='D164',
        chunk_size=args.chunk_size
    )
    
    print("\n" + "="*80)
    print("모든 변환 완료!")
    print("="*80)
    print(f"\n생성된 파일:")
    print(f"  - buildings_D162_simple.kml ({count1}개 건물)")
    print(f"  - buildings_D164_simple.kml ({count2}개 건물)")
    print(f"\n사용된 높이 컬럼: {args.height_column}")
    print("\nGoogle Earth에서 열어서 확인하세요!")

if __name__ == '__main__':
    main()
