#!/usr/bin/env python3
"""
Shapefile을 KML로 변환 (이상값 필터링 버전)
200m 이하의 현실적인 건물 높이만 사용
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

def write_placemark(f, idx, row, height, name_prefix):
    """Placemark 작성"""
    building_id = row.get('A0', f'Building_{idx}')
    
    f.write('    <Placemark>\n')
    f.write(f'      <name>{escape_xml(name_prefix)}_{idx}</name>\n')
    
    # 설명
    desc_text = f'ID: {escape_xml(building_id)}&lt;br/&gt;'
    desc_text += f'높이: {height:.1f}m&lt;br/&gt;'
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

def shapefile_to_kml_filtered(shapefile_path, output_path, height_column='A17', 
                               name_prefix='Building', chunk_size=5000, 
                               max_height=200, default_height=10):
    """
    Shapefile을 KML로 변환 (이상값 필터링)
    
    Parameters:
    -----------
    max_height : float
        최대 허용 높이 (미터). 이 값을 초과하면 default_height 사용
    default_height : float
        이상값 대체용 기본 높이 (미터)
    """
    
    print(f"읽는 중: {shapefile_path}")
    
    # Shapefile 읽기
    gdf = gpd.read_file(shapefile_path)
    total = len(gdf)
    
    print(f"총 {total}개 건물")
    print(f"높이 필터링: 0-{max_height}m 범위만 사용")
    print(f"이상값 대체 높이: {default_height}m")
    print("좌표계 변환 및 KML 작성 중...")
    
    file_name = Path(shapefile_path).stem
    
    filtered_count = 0
    
    with open(output_path, 'w', encoding='utf-8') as f:
        # 헤더 작성
        write_kml_header(f, f"{name_prefix} - {file_name} (Filtered)", 
                        f"총 {total}개 건물 (높이 0-{max_height}m 필터링)")
        
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
                
                # 높이 정보 추출 및 필터링
                try:
                    if height_column in row and row[height_column] is not None:
                        height = float(row[height_column])
                        
                        # 높이 범위 검증
                        if height < 0 or height > max_height:
                            height = default_height
                            filtered_count += 1
                    else:
                        height = default_height
                except (ValueError, TypeError):
                    height = default_height
                
                write_placemark(f, global_idx, row, height, name_prefix)
            
            # 메모리 정리
            del chunk
        
        # 푸터 작성
        write_kml_footer(f)
    
    print(f"완료! 저장됨: {output_path}")
    print(f"총 {total}개 건물이 변환되었습니다.")
    print(f"필터링된 건물: {filtered_count}개 ({filtered_count/total*100:.2f}%)")
    
    return total, filtered_count

def main():
    """메인 함수"""
    
    import argparse
    parser = argparse.ArgumentParser(description='Shapefile을 KML로 변환 (필터링)')
    parser.add_argument('--chunk-size', type=int, default=5000, help='청크 크기')
    parser.add_argument('--max-height', type=float, default=200, help='최대 허용 높이 (m)')
    parser.add_argument('--default-height', type=float, default=10, help='이상값 대체 높이 (m)')
    args = parser.parse_args()
    
    # D162 변환
    print("="*80)
    print("D162 데이터 변환 시작 (필터링)")
    print("="*80)
    count1, filtered1 = shapefile_to_kml_filtered(
        shapefile_path='D162/AL_D162_28_20250715.shp',
        output_path='buildings_D162_filtered.kml',
        height_column='A17',
        name_prefix='D162',
        chunk_size=args.chunk_size,
        max_height=args.max_height,
        default_height=args.default_height
    )
    
    print("\n" + "="*80)
    print("D164 데이터 변환 시작 (필터링)")
    print("="*80)
    
    # D164 변환
    count2, filtered2 = shapefile_to_kml_filtered(
        shapefile_path='D164/AL_D164_28_20250715.shp',
        output_path='buildings_D164_filtered.kml',
        height_column='A17',
        name_prefix='D164',
        chunk_size=args.chunk_size,
        max_height=args.max_height,
        default_height=args.default_height
    )
    
    print("\n" + "="*80)
    print("모든 변환 완료!")
    print("="*80)
    print(f"\n생성된 파일:")
    print(f"  - buildings_D162_filtered.kml ({count1}개 건물, {filtered1}개 필터링됨)")
    print(f"  - buildings_D164_filtered.kml ({count2}개 건물, {filtered2}개 필터링됨)")
    print(f"\n총 필터링: {filtered1 + filtered2}개 / {count1 + count2}개 ({(filtered1+filtered2)/(count1+count2)*100:.2f}%)")
    print("\nGoogle Earth에서 열어서 확인하세요!")

if __name__ == '__main__':
    main()
