#!/usr/bin/env python3
"""
조종사 조종 비교 예제

다양한 조종 전략을 비교합니다:
1. 조종 없음 (바람에 밀림)
2. 방위 유지 (기수 방향만 유지)
3. 경로 추적 (측면 편차 보정)
4. 편류각 보정 (사전 보정)
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.crosswind_simulator import CrosswindSimulator
from src.pilot_controller import PilotController, PilotStrategy, PilotBehavior
from src.visualizer import Visualizer
import logging
import pandas as pd
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_with_pilot_control(
    strategy_name: str,
    control_mode: str,
    crab_angle: float = 0.0,
    duration: float = 60.0,
    crosswind_speed: float = 10.0,
):
    """
    조종 전략을 적용하여 시뮬레이션 실행
    
    Args:
        strategy_name: 전략 이름
        control_mode: 제어 모드
        crab_angle: 편류각 (도)
        duration: 시뮬레이션 시간 (초)
        crosswind_speed: 횡풍 속도 (m/s)
    
    Returns:
        시뮬레이션 결과 DataFrame
    """
    logger.info(f"전략 실행: {strategy_name}")
    
    # 시뮬레이터 생성
    simulator = CrosswindSimulator(
        aircraft_model="c172p",
        crosswind_speed=crosswind_speed,
        crosswind_direction=90.0,
        turbulence=0.0,
        dt=0.1,  # 0.1초 간격 (빠르면서도 정확)
        init_altitude=1000.0,
        init_airspeed=60.0,
    )
    
    # 조종사 컨트롤러 생성
    pilot = PilotController(
        target_heading=crab_angle,  # 편류각 적용
        lateral_tolerance=50.0,
        heading_gain=0.02,
        position_gain=0.001,
    )
    pilot.control_mode = control_mode
    
    # 시뮬레이션 실행
    num_steps = int(duration / simulator.dt)
    results = []
    
    for step in range(num_steps):
        current_time = step * simulator.dt
        
        # 바람 설정
        wind_n, wind_e, wind_d = simulator.wind_model.get_wind_components(
            time=current_time,
            add_turbulence=False
        )
        simulator.jsbsim.set_wind(wind_n, wind_e, wind_d)
        
        # 현재 상태 가져오기
        state = simulator.jsbsim.get_state()
        
        # 편차 계산
        deviation_data = simulator._calculate_deviations(state)
        lateral_deviation = deviation_data['lateral_deviation_m']
        crosswind_component = deviation_data['crosswind_component_mps']
        
        # 조종사 조종 적용
        aileron_cmd, elevator_cmd, rudder_cmd = pilot.get_control_input(
            state,
            lateral_deviation,
            crosswind_component
        )
        
        # 조종면 명령 설정
        if control_mode != "MANUAL":
            simulator.jsbsim.fdm.set_property_value("fcs/aileron-cmd-norm", aileron_cmd)
        
        # 시뮬레이션 1 스텝 실행
        simulator.jsbsim.run_step()
        
        # 결과 저장 (매 10 스텝마다)
        if step % 10 == 0:
            state = simulator.jsbsim.get_state()
            deviation_data = simulator._calculate_deviations(state)
            result = {**state, **deviation_data, 'aileron_cmd': aileron_cmd}
            results.append(result)
    
    simulator.close()
    
    return pd.DataFrame(results)


def main():
    logger.info("=" * 70)
    logger.info("조종사 조종 전략 비교 시뮬레이션")
    logger.info("=" * 70)
    logger.info("")
    
    duration = 60.0
    crosswind_speed = 10.0
    
    # 시뮬레이션 조건 출력
    logger.info("【시뮬레이션 조건】")
    logger.info(f"✈️  항공기: Cessna 172P")
    logger.info(f"📍 출발: 샌프란시스코(SFO)")
    logger.info(f"🧭 목표 방향: 북쪽 (0°)")
    logger.info(f"⚡ 속도: 60 knots")
    logger.info(f"🌬️  횡풍: {crosswind_speed} m/s (동풍)")
    logger.info(f"⏱️  시간: {duration}초")
    logger.info("")
    
    # 편류각 계산
    crab_angle = PilotBehavior.calculate_crab_angle(crosswind_speed, 60.0)
    logger.info(f"💡 이론적 편류각: {crab_angle:.2f}°")
    logger.info("")
    
    # 4가지 전략 실행
    strategies = [
        ('조종 없음', 'MANUAL', 0.0),
        ('방위 유지', 'AUTO_HEADING', 0.0),
        ('경로 추적', 'AUTO_TRACK', 0.0),
        ('편류각 보정', 'AUTO_HEADING', crab_angle),
    ]
    
    results_dict = {}
    
    for strategy_name, control_mode, crab in strategies:
        logger.info(f"▶ [{strategy_name}] 시뮬레이션 중...")
        
        results = run_with_pilot_control(
            strategy_name,
            control_mode,
            crab,
            duration,
            crosswind_speed
        )
        
        results_dict[strategy_name] = results
        
        # 결과 출력
        max_dev = results['lateral_deviation_m'].abs().max()
        final_dev = results['lateral_deviation_m'].iloc[-1]
        
        logger.info(f"   최대 편차: {max_dev:.2f}m")
        logger.info(f"   최종 편차: {final_dev:.2f}m")
        logger.info("")
    
    # 비교 요약
    logger.info("=" * 70)
    logger.info("【결과 비교】")
    logger.info("=" * 70)
    logger.info("")
    
    logger.info(f"{'전략':<15} {'최대 편차(m)':<15} {'최종 편차(m)':<15} {'효과':<20}")
    logger.info("-" * 70)
    
    for strategy_name in strategies:
        name = strategy_name[0]
        results = results_dict[name]
        max_dev = results['lateral_deviation_m'].abs().max()
        final_dev = results['lateral_deviation_m'].iloc[-1]
        
        if name == '조종 없음':
            effect = "❌ 계속 밀림"
        elif name == '방위 유지':
            effect = "⚠️  편차 증가"
        elif name == '경로 추적':
            effect = "✅ 편차 보정"
        else:
            effect = "🎯 거의 완벽"
        
        logger.info(f"{name:<15} {max_dev:<15.2f} {final_dev:<15.2f} {effect:<20}")
    
    logger.info("")
    logger.info("💡 해석:")
    logger.info("   1. 조종 없음: 바람에 그대로 밀림 (가장 큰 편차)")
    logger.info("   2. 방위 유지: 기수는 북쪽이지만 측면으로 계속 밀림")
    logger.info("   3. 경로 추적: 편차를 감지하고 복귀 (편차 최소화)")
    logger.info("   4. 편류각 보정: 미리 각도를 틀어서 바람 보정 (최선)")
    logger.info("")
    
    # 결과 저장 및 시각화
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'results')
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info("시각화 생성 중...")
    
    # 1. 측면 편차 비교
    Visualizer.plot_comparison(
        results_dict,
        metric='lateral_deviation_m',
        title='Lateral Deviation - Different Pilot Strategies',
        save_path=os.path.join(output_dir, 'pilot_strategies_comparison.png')
    )
    
    # 2. 각 전략별 상세 그래프
    for strategy_name, results in results_dict.items():
        Visualizer.plot_trajectory_2d(
            results,
            title=f'Trajectory - {strategy_name}',
            save_path=os.path.join(output_dir, f'trajectory_{strategy_name.replace(" ", "_")}.png')
        )
    
    logger.info("")
    logger.info("=" * 70)
    logger.info(f"완료! 결과는 {output_dir}에 저장되었습니다.")
    logger.info("=" * 70)
    logger.info("")
    logger.info("📊 생성된 파일:")
    logger.info("   • pilot_strategies_comparison.png - 전략 비교")
    logger.info("   • trajectory_*.png - 각 전략별 궤적")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
