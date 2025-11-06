#!/usr/bin/env python3
"""
Shapefile을 KML로 청크 단위로 변환하는 스크립트
메모리 효율적인 처리
"""

import geopandas as gpd
from pathlib import Path

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
    
    if hasattr(polygon, 'exterior'):
        exterior = polygon.exterior
    else:
        exterior = polygon.geoms[0].exterior
    
    for x, y in exterior.coords:
        coords.append(f"{x},{y},{height}")
    
    return ' '.join(coords)

def write_kml_header(f, name, description):
    """KML 헤더 작성"""
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
    f.write('  <Document>\n')
    f.write(f'    <name>{escape_xml(name)}</name>\n')
    f.write(f'    <description>{description}</description>\n')
    f.write('    <Style id="buildingStyle">\n')
    f.write('      <LineStyle>\n')
    f.write('        <color>ff0000ff</color>\n')
    f.write('        <width>1.5</width>\n')
    f.write('      </LineStyle>\n')
    f.write('      <PolyStyle>\n')
    f.write('        <color>7f0000ff</color>\n')
    f.write('        <fill>1</fill>\n')
    f.write('        <outline>1</outline>\n')
    f.write('      </PolyStyle>\n')
    f.write('    </Style>\n')

def write_kml_footer(f):
    """KML 푸터 작성"""
    f.write('  </Document>\n')
    f.write('</kml>\n')

def write_placemark(f, idx, row, height_column, name_prefix):
    """Placemark 작성"""
    # 높이 정보 추출
    try:
        if height_column in row and row[height_column] is not None:
            height = float(row[height_column])
        else:
            height = 10.0
    except (ValueError, TypeError):
        height = 10.0
    
    building_id = row.get('A0', f'Building_{idx}')
    
    f.write('    <Placemark>\n')
    f.write(f'      <name>{escape_xml(name_prefix)}_{idx}</name>\n')
    
    # 설명
    desc_text = f'ID: {escape_xml(building_id)}&lt;br/&gt;'
    desc_text += f'높이: {height}m&lt;br/&gt;'
    if 'A3' in row and row['A3']:
        try:
            addr = row['A3'].encode('latin1').decode('cp949')
        except:
            addr = str(row['A3'])
        desc_text += f'주소: {escape_xml(addr)}&lt;br/&gt;'
    if 'A21' in row and row['A21']:
        try:
            usage = row['A21'].encode('latin1').decode('cp949')
        except:
            usage = str(row['A21'])
        desc_text += f'용도: {escape_xml(usage)}&lt;br/&gt;'
    
    f.write(f'      <description>{desc_text}</description>\n')
    f.write('      <styleUrl>#buildingStyle</styleUrl>\n')
    
    # Polygon
    f.write('      <Polygon>\n')
    f.write('        <extrude>1</extrude>\n')
    f.write('        <altitudeMode>relativeToGround</altitudeMode>\n')
    f.write('        <outerBoundaryIs>\n')
    f.write('          <LinearRing>\n')
    
    coords = polygon_to_coords(row.geometry, height)
    f.write(f'            <coordinates>{coords}</coordinates>\n')
    
    f.write('          </LinearRing>\n')
    f.write('        </outerBoundaryIs>\n')
    f.write('      </Polygon>\n')
    f.write('    </Placemark>\n')

def shapefile_to_kml_chunked(shapefile_path, output_path, height_column='A17', 
                              name_prefix='Building', chunk_size=5000):
    """
    Shapefile을 KML로 청크 단위로 변환 (메모리 효율적)
    """
    
    print(f"읽는 중: {shapefile_path}")
    
    # Shapefile 읽기
    gdf = gpd.read_file(shapefile_path)
    total = len(gdf)
    
    print(f"총 {total}개 건물")
    print("좌표계 변환 및 KML 작성 중...")
    
    file_name = Path(shapefile_path).stem
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # 헤더 작성
        write_kml_header(f, f"{name_prefix} - {file_name}", f"총 {total}개 건물")
        
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
                write_placemark(f, global_idx, row, height_column, name_prefix)
            
            # 메모리 정리
            del chunk
        
        # 푸터 작성
        write_kml_footer(f)
    
    print(f"완료! 저장됨: {output_path}")
    print(f"총 {total}개 건물이 변환되었습니다.")
    
    return total

def main():
    """메인 함수"""
    
    import argparse
    parser = argparse.ArgumentParser(description='Shapefile을 KML로 변환')
    parser.add_argument('--chunk-size', type=int, default=5000, help='청크 크기 (기본값: 5000)')
    args = parser.parse_args()
    
    # D162 변환
    print("="*80)
    print("D162 데이터 변환 시작")
    print("="*80)
    count1 = shapefile_to_kml_chunked(
        shapefile_path='D162/AL_D162_28_20250715.shp',
        output_path='buildings_D162_full.kml',
        height_column='A17',
        name_prefix='D162',
        chunk_size=args.chunk_size
    )
    
    print("\n" + "="*80)
    print("D164 데이터 변환 시작")
    print("="*80)
    
    # D164 변환
    count2 = shapefile_to_kml_chunked(
        shapefile_path='D164/AL_D164_28_20250715.shp',
        output_path='buildings_D164_full.kml',
        height_column='A17',
        name_prefix='D164',
        chunk_size=args.chunk_size
    )
    
    print("\n" + "="*80)
    print("모든 변환 완료!")
    print("="*80)
    print(f"\n생성된 파일:")
    print(f"  - buildings_D162_full.kml ({count1}개 건물)")
    print(f"  - buildings_D164_full.kml ({count2}개 건물)")
    print("\nGoogle Earth에서 열어서 확인하세요!")

if __name__ == '__main__':
    main()
