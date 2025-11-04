#!/usr/bin/env python3
"""
빠른 시뮬레이션 예제 (dt = 1초)

계산 간격을 1초로 설정하여 빠르게 시뮬레이션합니다.
정확도는 약간 감소하지만 계산 속도가 100배 빨라집니다.
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.crosswind_simulator import CrosswindSimulator
from src.visualizer import Visualizer
import logging
import time

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def compare_dt_values():
    """
    다양한 dt 값으로 시뮬레이션 비교
    """
    
    logger.info("=" * 70)
    logger.info("계산 간격(dt) 비교 - JSBSim 시뮬레이션")
    logger.info("=" * 70)
    logger.info("")
    
    # 비교할 dt 값들
    dt_values = [0.01, 0.1, 1.0]  # 초
    duration = 60.0  # 60초
    crosswind_speed = 10.0  # 10 m/s
    
    results_dict = {}
    
    for dt in dt_values:
        logger.info(f"{'='*70}")
        logger.info(f"【시뮬레이션: dt = {dt}초】")
        logger.info(f"{'='*70}")
        
        num_steps = int(duration / dt)
        logger.info(f"📊 계산 스텝 수: {num_steps:,} 스텝")
        logger.info(f"⏱️  예상 계산 시간: {'매우 빠름' if dt >= 1.0 else '보통' if dt >= 0.1 else '느림'}")
        logger.info("")
        
        try:
            # 시뮬레이터 생성
            simulator = CrosswindSimulator(
                aircraft_model="c172p",
                crosswind_speed=crosswind_speed,
                crosswind_direction=90.0,
                turbulence=0.0,  # 비교를 위해 난기류 제거
                dt=dt,  # ← 여기서 dt 변경!
                init_altitude=1000.0,
                init_airspeed=60.0,
            )
            
            # 시간 측정 시작
            start_time = time.time()
            
            # 시뮬레이션 실행
            results = simulator.run_simulation(
                duration=duration,
                autopilot_heading=None,
                show_progress=True
            )
            
            # 시간 측정 종료
            elapsed_time = time.time() - start_time
            
            # 결과 저장
            results_dict[dt] = {
                'dataframe': results,
                'elapsed_time': elapsed_time,
                'num_steps': num_steps
            }
            
            # 결과 출력
            max_deviation = results['lateral_deviation_m'].abs().max()
            final_deviation = results['lateral_deviation_m'].iloc[-1]
            mean_drift = results['drift_angle_deg'].mean()
            
            logger.info(f"✅ 시뮬레이션 완료!")
            logger.info(f"⏱️  실제 계산 시간: {elapsed_time:.2f}초")
            logger.info(f"📏 최대 측면 편차: {max_deviation:.2f} m")
            logger.info(f"📍 최종 측면 편차: {final_deviation:.2f} m")
            logger.info(f"📐 평균 편류각: {mean_drift:.2f}°")
            logger.info("")
            
            simulator.close()
            
        except Exception as e:
            logger.error(f"❌ 오류 발생: {e}")
            continue
    
    # 비교 요약
    logger.info("=" * 70)
    logger.info("【비교 결과 요약】")
    logger.info("=" * 70)
    logger.info("")
    
    # 표 헤더
    logger.info(f"{'dt (초)':<10} {'스텝 수':<12} {'계산 시간':<12} {'최종 편차(m)':<15} {'정확도':<10}")
    logger.info("-" * 70)
    
    # 기준값 (dt=0.01)
    if 0.01 in results_dict:
        baseline_deviation = results_dict[0.01]['dataframe']['lateral_deviation_m'].iloc[-1]
        
        for dt in sorted(results_dict.keys()):
            data = results_dict[dt]
            deviation = data['dataframe']['lateral_deviation_m'].iloc[-1]
            accuracy = (1 - abs(deviation - baseline_deviation) / baseline_deviation) * 100
            
            logger.info(
                f"{dt:<10.2f} {data['num_steps']:<12,} "
                f"{data['elapsed_time']:<12.2f} {deviation:<15.2f} {accuracy:<10.1f}%"
            )
    
    logger.info("")
    logger.info("💡 해석:")
    logger.info("   • dt = 0.01초: 가장 정확하지만 느림 (기본 권장)")
    logger.info("   • dt = 0.1초:  빠르면서도 충분히 정확함")
    logger.info("   • dt = 1.0초:  매우 빠르지만 정확도 다소 감소")
    logger.info("")
    logger.info("📌 권장:")
    logger.info("   • 정확한 분석: dt = 0.01초")
    logger.info("   • 빠른 테스트: dt = 1.0초")
    logger.info("   • 균형잡힌 선택: dt = 0.1초")
    logger.info("")
    
    # 결과 저장
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'results')
    os.makedirs(output_dir, exist_ok=True)
    
    # 비교 그래프 생성
    logger.info("시각화 생성 중...")
    
    comparison_data = {
        f"dt={dt}s": data['dataframe'] 
        for dt, data in results_dict.items()
    }
    
    Visualizer.plot_comparison(
        comparison_data,
        metric='lateral_deviation_m',
        title='Lateral Deviation Comparison - Different Time Steps',
        save_path=os.path.join(output_dir, 'dt_comparison.png')
    )
    
    logger.info("=" * 70)
    logger.info(f"완료! 결과는 {output_dir}에 저장되었습니다.")
    logger.info("=" * 70)


def main():
    """메인 함수"""
    compare_dt_values()


if __name__ == "__main__":
    sys.exit(main())
