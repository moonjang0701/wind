#!/usr/bin/env python3
"""
여러 KML 파일을 하나로 병합하는 스크립트
"""

import sys

def merge_kml_files(input_files, output_file):
    """
    여러 KML 파일을 하나로 병합
    
    Parameters:
    -----------
    input_files : list
        입력 KML 파일 경로 리스트
    output_file : str
        출력 KML 파일 경로
    """
    
    print(f"병합할 파일: {len(input_files)}개")
    for f in input_files:
        print(f"  - {f}")
    
    # 출력 파일 열기
    with open(output_file, 'w', encoding='utf-8') as out_f:
        # KML 헤더 작성
        out_f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        out_f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n')
        out_f.write('  <Document>\n')
        out_f.write('    <name>통합 건물 데이터 (D162 + D164)</name>\n')
        out_f.write('    <description>D162와 D164 지역의 모든 건물</description>\n')
        out_f.write('    <Style id="buildingStyle">\n')
        out_f.write('      <LineStyle>\n')
        out_f.write('        <color>ff0000ff</color>\n')
        out_f.write('        <width>1.5</width>\n')
        out_f.write('      </LineStyle>\n')
        out_f.write('      <PolyStyle>\n')
        out_f.write('        <color>7f0000ff</color>\n')
        out_f.write('        <fill>1</fill>\n')
        out_f.write('        <outline>1</outline>\n')
        out_f.write('      </PolyStyle>\n')
        out_f.write('    </Style>\n')
        
        # 각 입력 파일의 Placemark만 추출하여 병합
        for input_file in input_files:
            print(f"\n처리 중: {input_file}")
            
            with open(input_file, 'r', encoding='utf-8') as in_f:
                in_placemark = False
                placemark_count = 0
                
                for line in in_f:
                    # Placemark 시작
                    if '<Placemark>' in line:
                        in_placemark = True
                        placemark_count += 1
                        if placemark_count % 10000 == 0:
                            print(f"  진행 중: {placemark_count}개 건물 처리됨")
                    
                    # Placemark 내용 복사
                    if in_placemark:
                        out_f.write(line)
                    
                    # Placemark 끝
                    if '</Placemark>' in line:
                        in_placemark = False
                
                print(f"  완료: {placemark_count}개 건물 병합됨")
        
        # KML 푸터 작성
        out_f.write('  </Document>\n')
        out_f.write('</kml>\n')
    
    print(f"\n병합 완료! 저장됨: {output_file}")

def main():
    """메인 함수"""
    
    input_files = [
        'buildings_D162_full.kml',
        'buildings_D164_full.kml'
    ]
    
    output_file = 'buildings_combined.kml'
    
    print("="*80)
    print("KML 파일 병합")
    print("="*80)
    
    merge_kml_files(input_files, output_file)
    
    print("\n" + "="*80)
    print("병합 완료!")
    print("="*80)
    print(f"\n생성된 파일: {output_file}")
    print("\nGoogle Earth에서 열어서 확인하세요!")

if __name__ == '__main__':
    main()
