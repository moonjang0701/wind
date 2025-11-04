#!/usr/bin/env python3
"""
간단한 1초 간격 시뮬레이션

dt=1초로 설정하여 가장 빠르게 시뮬레이션합니다.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.crosswind_simulator import CrosswindSimulator
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 60)
    logger.info("빠른 시뮬레이션 (dt = 1초)")
    logger.info("=" * 60)
    logger.info("")
    logger.info("⚙️  계산 간격: 1초 (60초 시뮬레이션 = 60 스텝만 계산)")
    logger.info("⚡ 예상 시간: 1-2초 (매우 빠름!)")
    logger.info("")
    
    # 시뮬레이터 생성 (dt=1.0초)
    simulator = CrosswindSimulator(
        aircraft_model="c172p",
        crosswind_speed=10.0,
        crosswind_direction=90.0,
        turbulence=0.0,
        dt=1.0,  # ← 1초 간격!
        init_altitude=1000.0,
        init_airspeed=60.0,
    )
    
    # 시뮬레이션 실행
    logger.info("시뮬레이션 시작...")
    results = simulator.run_simulation(duration=60.0, show_progress=True)
    
    # 결과 출력
    logger.info("")
    logger.info("=" * 60)
    logger.info("결과")
    logger.info("=" * 60)
    
    max_dev = results['lateral_deviation_m'].abs().max()
    final_dev = results['lateral_deviation_m'].iloc[-1]
    mean_drift = results['drift_angle_deg'].mean()
    
    logger.info(f"📏 최대 측면 편차: {max_dev:.2f} m")
    logger.info(f"📍 최종 측면 편차: {final_dev:.2f} m")
    logger.info(f"📐 평균 편류각: {mean_drift:.2f}°")
    logger.info("")
    logger.info(f"📊 데이터 포인트: {len(results)}개 (1초마다 1개)")
    logger.info("")
    
    # 시간별 데이터 샘플 출력
    logger.info("시간별 위치 변화 (샘플):")
    logger.info("-" * 60)
    logger.info(f"{'시간(s)':<10} {'측면편차(m)':<15} {'북쪽진행(m)':<15} {'편류각(°)':<10}")
    logger.info("-" * 60)
    
    for i in [0, 10, 20, 30, 40, 50, 59]:
        if i < len(results):
            row = results.iloc[i]
            logger.info(
                f"{row['time']:<10.0f} "
                f"{row['lateral_deviation_m']:<15.2f} "
                f"{row['along_track_distance_m']:<15.2f} "
                f"{row['drift_angle_deg']:<10.2f}"
            )
    
    logger.info("")
    logger.info("💡 해석:")
    logger.info("   • dt=1초로 설정하면 60초를 60번만 계산")
    logger.info("   • dt=0.01초 대비 100배 빠름!")
    logger.info("   • 정확도는 약간 낮지만 빠른 테스트에 적합")
    logger.info("")
    
    simulator.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
