"""
조종사 조종 모듈

실제 조종사의 행동을 시뮬레이션합니다:
- 경로 이탈 감지
- 경로 복귀 조종
- 편류각 보정
"""

import numpy as np
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class PilotController:
    """
    조종사 행동 시뮬레이터
    
    횡풍으로 인한 경로 이탈을 감지하고 복귀하는 조종을 시뮬레이션합니다.
    """
    
    def __init__(
        self,
        target_heading: float = 0.0,
        lateral_tolerance: float = 50.0,
        heading_gain: float = 0.02,
        position_gain: float = 0.001,
    ):
        """
        조종사 컨트롤러 초기화
        
        Args:
            target_heading: 목표 방위 (도)
            lateral_tolerance: 측면 편차 허용 범위 (미터)
            heading_gain: 방위 제어 게인 (클수록 민감)
            position_gain: 위치 제어 게인
        """
        self.target_heading = target_heading
        self.lateral_tolerance = lateral_tolerance
        self.heading_gain = heading_gain
        self.position_gain = position_gain
        
        # 조종 모드
        self.control_mode = "MANUAL"  # MANUAL, AUTO_HEADING, AUTO_TRACK
        
        logger.info(
            f"PilotController 초기화: "
            f"목표방위={target_heading}°, 허용편차={lateral_tolerance}m"
        )
    
    def get_control_input(
        self,
        current_state: Dict[str, float],
        lateral_deviation: float,
        crosswind_component: float,
    ) -> Tuple[float, float, float]:
        """
        조종 입력 계산
        
        Args:
            current_state: 현재 항공기 상태
            lateral_deviation: 현재 측면 편차 (m)
            crosswind_component: 횡풍 성분 (m/s)
        
        Returns:
            (aileron_cmd, elevator_cmd, rudder_cmd) 튜플
            각 값은 -1.0 ~ 1.0 범위
        """
        if self.control_mode == "MANUAL":
            # 수동 조종 (조종 없음)
            return 0.0, 0.0, 0.0
        
        elif self.control_mode == "AUTO_HEADING":
            # 방위만 유지 (가장 기본적인 조종)
            aileron = self._heading_control(current_state["yaw_deg"])
            return aileron, 0.0, 0.0
        
        elif self.control_mode == "AUTO_TRACK":
            # 경로 추적 (측면 편차 보정)
            aileron = self._track_control(
                current_state["yaw_deg"],
                lateral_deviation,
                crosswind_component
            )
            return aileron, 0.0, 0.0
        
        return 0.0, 0.0, 0.0
    
    def _heading_control(self, current_heading: float) -> float:
        """
        방위 유지 제어
        
        목표 방위를 유지하도록 보조익(aileron) 조종
        
        Args:
            current_heading: 현재 방위 (도)
        
        Returns:
            aileron 명령 (-1.0 ~ 1.0)
        """
        # 방위 오차 계산
        heading_error = self.target_heading - current_heading
        
        # -180 ~ 180도 범위로 정규화
        if heading_error > 180:
            heading_error -= 360
        elif heading_error < -180:
            heading_error += 360
        
        # 비례 제어 (P 제어)
        aileron_cmd = heading_error * self.heading_gain
        
        # 제한 (-1.0 ~ 1.0)
        aileron_cmd = np.clip(aileron_cmd, -1.0, 1.0)
        
        return aileron_cmd
    
    def _track_control(
        self,
        current_heading: float,
        lateral_deviation: float,
        crosswind_component: float,
    ) -> float:
        """
        경로 추적 제어 (고급)
        
        측면 편차를 감지하고 경로로 복귀하도록 조종
        
        Args:
            current_heading: 현재 방위 (도)
            lateral_deviation: 측면 편차 (m, 양수=오른쪽)
            crosswind_component: 횡풍 성분 (m/s)
        
        Returns:
            aileron 명령 (-1.0 ~ 1.0)
        """
        # 1. 방위 오차
        heading_error = self.target_heading - current_heading
        if heading_error > 180:
            heading_error -= 360
        elif heading_error < -180:
            heading_error += 360
        
        # 2. 위치 오차 (측면 편차)
        # 오른쪽으로 밀렸으면 왼쪽으로 기울여야 함
        position_correction = -lateral_deviation * self.position_gain
        
        # 3. 바람 보정 (편류각)
        # 횡풍을 보정하기 위한 추가 각도
        # crosswind가 양수(오른쪽)면 왼쪽으로 기울여야 함
        wind_correction = -crosswind_component * 0.5
        
        # 4. 총 제어 입력
        aileron_cmd = (
            heading_error * self.heading_gain +
            position_correction +
            wind_correction
        )
        
        # 제한
        aileron_cmd = np.clip(aileron_cmd, -1.0, 1.0)
        
        return aileron_cmd
    
    def should_intervene(self, lateral_deviation: float) -> bool:
        """
        조종사 개입이 필요한지 판단
        
        Args:
            lateral_deviation: 현재 측면 편차 (m)
        
        Returns:
            개입 필요 여부
        """
        return abs(lateral_deviation) > self.lateral_tolerance


class PilotBehavior:
    """
    조종사 행동 패턴 시뮬레이터
    
    실제 조종사의 행동 특성을 모델링합니다.
    """
    
    @staticmethod
    def calculate_crab_angle(crosswind_mps: float, airspeed_kts: float) -> float:
        """
        편류각(crab angle) 계산
        
        조종사가 횡풍을 보정하기 위해 기체를 기울이는 각도
        
        Args:
            crosswind_mps: 횡풍 속도 (m/s)
            airspeed_kts: 대기속도 (knots)
        
        Returns:
            편류각 (도)
        """
        # knots를 m/s로 변환
        airspeed_mps = airspeed_kts * 0.514444
        
        # 편류각 계산: arcsin(횡풍/대기속도)
        if airspeed_mps > 0:
            crab_ratio = crosswind_mps / airspeed_mps
            crab_ratio = np.clip(crab_ratio, -1.0, 1.0)
            crab_angle = np.rad2deg(np.arcsin(crab_ratio))
        else:
            crab_angle = 0.0
        
        return crab_angle
    
    @staticmethod
    def get_pilot_response_delay(
        deviation: float,
        threshold: float = 30.0
    ) -> float:
        """
        조종사 반응 시간
        
        편차가 작으면 천천히, 크면 빠르게 반응
        
        Args:
            deviation: 측면 편차 (m)
            threshold: 반응 시작 임계값 (m)
        
        Returns:
            반응 지연 시간 (초)
        """
        if abs(deviation) < threshold:
            return 5.0  # 작은 편차는 천천히 반응
        elif abs(deviation) < threshold * 2:
            return 2.0  # 중간 편차
        else:
            return 0.5  # 큰 편차는 즉시 반응


class PilotStrategy:
    """
    조종사 전략 (시나리오별 조종 방법)
    """
    
    @staticmethod
    def no_correction():
        """전략 1: 조종 안함 (바람에 밀림)"""
        return {
            'name': 'NO_CORRECTION',
            'description': '조종사가 아무것도 안함 (바람에 그대로 밀림)',
            'control_mode': 'MANUAL',
        }
    
    @staticmethod
    def heading_hold():
        """전략 2: 방위 유지 (기수 방향만 유지)"""
        return {
            'name': 'HEADING_HOLD',
            'description': '기수 방향만 북쪽으로 유지 (측면 편차는 계속 증가)',
            'control_mode': 'AUTO_HEADING',
        }
    
    @staticmethod
    def track_following():
        """전략 3: 경로 추적 (측면 편차 보정)"""
        return {
            'name': 'TRACK_FOLLOWING',
            'description': '측면 편차를 감지하고 경로로 복귀',
            'control_mode': 'AUTO_TRACK',
        }
    
    @staticmethod
    def crab_correction(crosswind: float, airspeed: float):
        """전략 4: 편류각 보정 (사전 보정)"""
        crab_angle = PilotBehavior.calculate_crab_angle(crosswind, airspeed)
        return {
            'name': 'CRAB_CORRECTION',
            'description': f'편류각 {crab_angle:.1f}도로 사전 보정',
            'control_mode': 'AUTO_HEADING',
            'crab_angle': crab_angle,
        }


def demo_pilot_strategies():
    """조종사 전략 데모"""
    
    print("=" * 70)
    print("조종사 조종 전략")
    print("=" * 70)
    print()
    
    strategies = [
        PilotStrategy.no_correction(),
        PilotStrategy.heading_hold(),
        PilotStrategy.track_following(),
        PilotStrategy.crab_correction(10.0, 60.0),
    ]
    
    for i, strategy in enumerate(strategies, 1):
        print(f"{i}. {strategy['name']}")
        print(f"   설명: {strategy['description']}")
        print()
    
    print("예상 결과:")
    print("1. NO_CORRECTION: 측면 편차 최대 (~600m)")
    print("2. HEADING_HOLD: 측면 편차 중간 (~150m)")
    print("3. TRACK_FOLLOWING: 측면 편차 최소 (~10m)")
    print("4. CRAB_CORRECTION: 측면 편차 거의 없음 (~5m)")
    print()


if __name__ == "__main__":
    demo_pilot_strategies()
