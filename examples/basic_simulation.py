#!/usr/bin/env python3
"""
기본 횡풍 시뮬레이션 예제

단일 횡풍 조건에서 항공기의 측면 편차를 시뮬레이션하고 결과를 시각화합니다.
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.crosswind_simulator import CrosswindSimulator
from src.visualizer import Visualizer
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """메인 함수"""
    
    logger.info("=" * 60)
    logger.info("JSBSim 횡풍 좌우편차 시뮬레이션 - 기본 예제")
    logger.info("=" * 60)
    
    # 시뮬레이션 파라미터 설정
    aircraft = "c172p"  # Cessna 172
    crosswind_speed = 10.0  # 10 m/s (약 19.4 knots)
    crosswind_direction = 90.0  # 동쪽에서 부는 바람 (순수 횡풍)
    duration = 60.0  # 60초간 시뮬레이션
    
    logger.info(f"항공기: {aircraft}")
    logger.info(f"횡풍 속도: {crosswind_speed} m/s")
    logger.info(f"풍향: {crosswind_direction}°")
    logger.info(f"시뮬레이션 시간: {duration}초")
    logger.info("")
    
    try:
        # 시뮬레이터 생성
        logger.info("시뮬레이터 초기화 중...")
        simulator = CrosswindSimulator(
            aircraft_model=aircraft,
            crosswind_speed=crosswind_speed,
            crosswind_direction=crosswind_direction,
            turbulence=0.1,  # 약간의 난기류
            dt=0.01,
            init_altitude=1000.0,  # 1000 feet AGL
            init_airspeed=60.0,  # 60 knots
        )
        
        # 시뮬레이션 실행
        logger.info("시뮬레이션 시작...")
        results = simulator.run_simulation(
            duration=duration,
            autopilot_heading=None,  # 자동조종 없음
            show_progress=True
        )
        
        # 결과 요약 출력
        logger.info("")
        logger.info("=" * 60)
        logger.info("시뮬레이션 결과 요약")
        logger.info("=" * 60)
        
        max_deviation = results['lateral_deviation_m'].abs().max()
        final_deviation = results['lateral_deviation_m'].iloc[-1]
        mean_drift = results['drift_angle_deg'].mean()
        max_drift = results['drift_angle_deg'].abs().max()
        total_distance = results['total_distance_m'].iloc[-1]
        
        logger.info(f"최대 측면 편차: {max_deviation:.2f} m")
        logger.info(f"최종 측면 편차: {final_deviation:.2f} m")
        logger.info(f"평균 편류각: {mean_drift:.2f}°")
        logger.info(f"최대 편류각: {max_drift:.2f}°")
        logger.info(f"총 이동 거리: {total_distance:.0f} m")
        logger.info("")
        
        # 결과 저장
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'results')
        os.makedirs(output_dir, exist_ok=True)
        
        csv_path = os.path.join(output_dir, 'basic_simulation_results.csv')
        results.to_csv(csv_path, index=False)
        logger.info(f"결과 데이터 저장: {csv_path}")
        
        # 시각화
        logger.info("결과 시각화 중...")
        
        # 1. 2D 궤적
        trajectory_path = os.path.join(output_dir, 'trajectory_2d.png')
        Visualizer.plot_trajectory_2d(
            results,
            title=f"Aircraft Trajectory - Crosswind {crosswind_speed} m/s",
            save_path=trajectory_path
        )
        
        # 2. 시간에 따른 편차
        deviation_path = os.path.join(output_dir, 'deviation_over_time.png')
        Visualizer.plot_deviation_over_time(
            results,
            title=f"Lateral Deviation - Crosswind {crosswind_speed} m/s",
            save_path=deviation_path
        )
        
        # 3. 속도 분석
        velocity_path = os.path.join(output_dir, 'velocity_analysis.png')
        Visualizer.plot_velocity_analysis(
            results,
            title=f"Velocity Analysis - Crosswind {crosswind_speed} m/s",
            save_path=velocity_path
        )
        
        # 4. 종합 리포트
        report_path = os.path.join(output_dir, 'comprehensive_report.png')
        Visualizer.plot_comprehensive_report(
            results,
            wind_speed=crosswind_speed,
            save_path=report_path
        )
        
        logger.info("")
        logger.info("=" * 60)
        logger.info("시뮬레이션 완료!")
        logger.info(f"결과 파일 위치: {output_dir}")
        logger.info("=" * 60)
        
        # 정리
        simulator.close()
        
    except ImportError as e:
        logger.error("=" * 60)
        logger.error("JSBSim 라이브러리를 찾을 수 없습니다.")
        logger.error("다음 명령어로 설치하세요: pip install jsbsim")
        logger.error("=" * 60)
        logger.error(f"오류 상세: {e}")
        return 1
    
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"시뮬레이션 중 오류 발생: {e}")
        logger.error("=" * 60)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
