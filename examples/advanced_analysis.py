#!/usr/bin/env python3
"""
고급 횡풍 분석 예제

여러 풍속 조건에서 시뮬레이션을 수행하고 결과를 비교 분석합니다.
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.crosswind_simulator import CrosswindSimulator
from src.visualizer import Visualizer
import logging
import pandas as pd

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """메인 함수"""
    
    logger.info("=" * 60)
    logger.info("JSBSim 횡풍 좌우편차 시뮬레이션 - 고급 분석")
    logger.info("=" * 60)
    
    # 분석할 풍속 조건들
    wind_speeds = [5, 10, 15, 20]  # m/s
    duration = 60.0  # 60초
    aircraft = "c172p"
    
    logger.info("")
    logger.info("【비교 분석 조건】")
    logger.info(f"✈️  항공기: {aircraft} (Cessna 172)")
    logger.info(f"📍 위치: 샌프란시스코(SFO) 상공")
    logger.info(f"🧭 비행 방향: 북쪽 (0°)")
    logger.info(f"⚡ 비행 속도: 60 knots (111 km/h)")
    logger.info(f"🏔️  고도: 1,000 feet (305 m)")
    logger.info(f"⏱️  각 시뮬레이션: {duration}초")
    logger.info("")
    logger.info("【비교할 횡풍 조건】")
    for ws in wind_speeds:
        kmh = ws * 3.6
        knots = ws * 1.94384
        if ws <= 5:
            level = "🍃 약한 바람"
        elif ws <= 10:
            level = "🌬️  보통 바람"
        elif ws <= 15:
            level = "💨 강한 바람"
        else:
            level = "🌪️  매우 강한 바람"
        logger.info(f"  {ws:2d} m/s = {kmh:5.1f} km/h = {knots:5.1f} knots - {level}")
    logger.info("")
    
    try:
        # 여러 풍속 조건에서 시뮬레이션 실행
        results_dict = {}
        
        for wind_speed in wind_speeds:
            logger.info(f"풍속 {wind_speed} m/s 시뮬레이션 시작...")
            
            simulator = CrosswindSimulator(
                aircraft_model=aircraft,
                crosswind_speed=wind_speed,
                crosswind_direction=90.0,  # 순수 횡풍
                turbulence=0.05,
                dt=0.01,
                init_altitude=1000.0,
                init_airspeed=60.0,
            )
            
            results = simulator.run_simulation(
                duration=duration,
                autopilot_heading=None,
                show_progress=True
            )
            
            results_dict[wind_speed] = results
            simulator.close()
            
            logger.info(f"완료: 최대 편차 = {results['lateral_deviation_m'].abs().max():.2f} m")
            logger.info("")
        
        # 결과 요약 테이블 생성
        logger.info("=" * 60)
        logger.info("비교 분석 결과")
        logger.info("=" * 60)
        
        summary_data = []
        for wind_speed, df in results_dict.items():
            summary = {
                '풍속 (m/s)': wind_speed,
                '최대 편차 (m)': df['lateral_deviation_m'].abs().max(),
                '최종 편차 (m)': df['lateral_deviation_m'].iloc[-1],
                '평균 편류각 (°)': df['drift_angle_deg'].mean(),
                '최대 편류각 (°)': df['drift_angle_deg'].abs().max(),
                '총 거리 (m)': df['total_distance_m'].iloc[-1],
            }
            summary_data.append(summary)
        
        summary_df = pd.DataFrame(summary_data)
        print(summary_df.to_string(index=False))
        logger.info("")
        
        # 결과 저장
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'results')
        os.makedirs(output_dir, exist_ok=True)
        
        # 요약 테이블 저장
        summary_path = os.path.join(output_dir, 'comparison_summary.csv')
        summary_df.to_csv(summary_path, index=False)
        logger.info(f"요약 테이블 저장: {summary_path}")
        
        # 개별 결과 저장
        for wind_speed, df in results_dict.items():
            csv_path = os.path.join(output_dir, f'results_wind_{wind_speed}ms.csv')
            df.to_csv(csv_path, index=False)
            logger.info(f"결과 저장: {csv_path}")
        
        logger.info("")
        
        # 비교 시각화
        logger.info("비교 시각화 생성 중...")
        
        # 1. 측면 편차 비교
        deviation_comparison_path = os.path.join(
            output_dir, 'comparison_lateral_deviation.png'
        )
        Visualizer.plot_comparison(
            results_dict,
            metric='lateral_deviation_m',
            title='Lateral Deviation Comparison - Different Wind Speeds',
            save_path=deviation_comparison_path
        )
        
        # 2. 편류각 비교
        drift_comparison_path = os.path.join(
            output_dir, 'comparison_drift_angle.png'
        )
        Visualizer.plot_comparison(
            results_dict,
            metric='drift_angle_deg',
            title='Drift Angle Comparison - Different Wind Speeds',
            save_path=drift_comparison_path
        )
        
        # 3. 각 풍속별 상세 리포트
        for wind_speed, df in results_dict.items():
            report_path = os.path.join(
                output_dir, f'report_wind_{wind_speed}ms.png'
            )
            Visualizer.plot_comprehensive_report(
                df,
                wind_speed=wind_speed,
                save_path=report_path
            )
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("고급 분석 완료!")
        logger.info(f"결과 파일 위치: {output_dir}")
        logger.info("=" * 60)
        
        # 주요 발견사항 출력
        logger.info("")
        logger.info("주요 발견사항:")
        logger.info(f"- 풍속 {wind_speeds[0]} m/s: 최대 편차 {summary_df.iloc[0]['최대 편차 (m)']:.2f} m")
        logger.info(f"- 풍속 {wind_speeds[-1]} m/s: 최대 편차 {summary_df.iloc[-1]['최대 편차 (m)']:.2f} m")
        
        deviation_ratio = summary_df.iloc[-1]['최대 편차 (m)'] / summary_df.iloc[0]['최대 편차 (m)']
        wind_ratio = wind_speeds[-1] / wind_speeds[0]
        logger.info(f"- 풍속 {wind_ratio:.1f}배 증가 시 편차 약 {deviation_ratio:.1f}배 증가")
        logger.info("")
        
    except ImportError as e:
        logger.error("=" * 60)
        logger.error("JSBSim 라이브러리를 찾을 수 없습니다.")
        logger.error("다음 명령어로 설치하세요: pip install jsbsim")
        logger.error("=" * 60)
        logger.error(f"오류 상세: {e}")
        return 1
    
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"분석 중 오류 발생: {e}")
        logger.error("=" * 60)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
