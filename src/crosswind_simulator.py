"""
횡풍 좌우편차 시뮬레이터 메인 클래스

JSBSim을 이용하여 횡풍 환경에서의 항공기 측면 편차를 시뮬레이션합니다.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional
import logging
from tqdm import tqdm

from .jsbsim_wrapper import JSBSimWrapper, convert_wind_to_components
from .wind_model import WindModel

logger = logging.getLogger(__name__)


class CrosswindSimulator:
    """
    횡풍 좌우편차 시뮬레이터
    
    항공기가 횡풍을 받을 때 발생하는 측면 편차를 시뮬레이션하고 분석합니다.
    """
    
    def __init__(
        self,
        aircraft_model: str = "c172p",
        crosswind_speed: float = 10.0,
        crosswind_direction: float = 90.0,
        turbulence: float = 0.0,
        dt: float = 0.01,
        init_altitude: float = 1000.0,
        init_airspeed: float = 60.0,
    ):
        """
        시뮬레이터 초기화
        
        Args:
            aircraft_model: 항공기 모델
            crosswind_speed: 횡풍 속도 (m/s)
            crosswind_direction: 풍향 (도, 북쪽 기준)
            turbulence: 난기류 강도 (0.0 ~ 1.0)
            dt: 시뮬레이션 시간 간격 (초)
            init_altitude: 초기 고도 (feet)
            init_airspeed: 초기 대기속도 (knots)
        """
        # JSBSim 래퍼 초기화
        self.jsbsim = JSBSimWrapper(
            aircraft=aircraft_model,
            dt=dt,
            init_altitude=init_altitude,
            init_airspeed=init_airspeed,
        )
        
        # 바람 모델 초기화
        self.wind_model = WindModel(
            wind_speed_mps=crosswind_speed,
            wind_direction_deg=crosswind_direction,
            turbulence_intensity=turbulence,
        )
        
        # 시뮬레이션 파라미터
        self.dt = dt
        self.aircraft_model = aircraft_model
        
        # 초기 위치 저장 (편차 계산용)
        initial_state = self.jsbsim.get_state()
        self.initial_latitude = initial_state["latitude"]
        self.initial_longitude = initial_state["longitude"]
        self.initial_x = initial_state["x_m"]
        self.initial_y = initial_state["y_m"]
        
        logger.info(
            f"CrosswindSimulator 초기화 완료: "
            f"항공기={aircraft_model}, 횡풍={crosswind_speed}m/s"
        )
    
    def run_simulation(
        self,
        duration: float = 60.0,
        autopilot_heading: Optional[float] = None,
        show_progress: bool = True,
    ) -> pd.DataFrame:
        """
        시뮬레이션 실행
        
        Args:
            duration: 시뮬레이션 지속 시간 (초)
            autopilot_heading: 자동조종 목표 방위 (None이면 자동조종 없음)
            show_progress: 진행 상황 표시 여부
        
        Returns:
            시뮬레이션 결과 DataFrame
        """
        num_steps = int(duration / self.dt)
        results = []
        
        # 진행 표시 설정
        iterator = range(num_steps)
        if show_progress:
            iterator = tqdm(iterator, desc="시뮬레이션 진행")
        
        for step in iterator:
            # 현재 시간
            current_time = step * self.dt
            
            # 바람 설정
            wind_n, wind_e, wind_d = self.wind_model.get_wind_components(
                time=current_time,
                add_turbulence=True
            )
            self.jsbsim.set_wind(wind_n, wind_e, wind_d)
            
            # 자동조종 (옵션)
            if autopilot_heading is not None:
                self._apply_autopilot(autopilot_heading)
            
            # 시뮬레이션 1 스텝 실행
            if not self.jsbsim.run_step():
                logger.warning(f"시뮬레이션이 {current_time:.2f}초에 중단되었습니다.")
                break
            
            # 현재 상태 가져오기
            state = self.jsbsim.get_state()
            
            # 편차 계산
            deviation_data = self._calculate_deviations(state)
            
            # 결과 저장
            result = {**state, **deviation_data}
            results.append(result)
        
        # DataFrame으로 변환
        df = pd.DataFrame(results)
        
        logger.info(
            f"시뮬레이션 완료: {len(results)} 스텝, "
            f"최대 측면편차={df['lateral_deviation_m'].max():.2f}m"
        )
        
        return df
    
    def _apply_autopilot(self, target_heading: float):
        """
        간단한 방위 자동조종 적용
        
        Args:
            target_heading: 목표 방위 (도)
        """
        current_state = self.jsbsim.get_state()
        current_heading = current_state["yaw_deg"]
        
        # 방위 오차 계산 (-180 ~ 180도 범위로 정규화)
        heading_error = target_heading - current_heading
        if heading_error > 180:
            heading_error -= 360
        elif heading_error < -180:
            heading_error += 360
        
        # 간단한 비례 제어 (P 제어)
        aileron_cmd = np.clip(heading_error * 0.01, -1.0, 1.0)
        
        # 조종면 명령 설정
        self.jsbsim.fdm.set_property_value("fcs/aileron-cmd-norm", aileron_cmd)
    
    def _calculate_deviations(self, state: Dict[str, float]) -> Dict[str, float]:
        """
        측면 편차 및 관련 파라미터 계산
        
        Args:
            state: 현재 항공기 상태
        
        Returns:
            편차 데이터 딕셔너리
        """
        # 현재 위치 (미터)
        current_x = state["x_m"]
        current_y = state["y_m"]
        
        # 초기 위치로부터의 변위
        dx = current_x - self.initial_x
        dy = current_y - self.initial_y
        
        # 거리 계산
        distance_traveled = np.sqrt(dx**2 + dy**2)
        
        # 항공기 헤딩 (라디안)
        heading_rad = np.deg2rad(state["yaw_deg"])
        
        # 의도한 경로 방향 (초기 헤딩, 북쪽=0도로 가정)
        intended_heading_rad = 0.0
        
        # 측면 편차 계산 (의도한 경로에서 수직 방향 거리)
        # 동쪽 방향이 양의 측면 편차
        lateral_deviation = dx * np.cos(intended_heading_rad) - dy * np.sin(intended_heading_rad)
        
        # 진행 거리 (의도한 경로 방향)
        along_track_distance = dx * np.sin(intended_heading_rad) + dy * np.cos(intended_heading_rad)
        
        # 편류각 (drift angle) 계산
        # 항공기 헤딩과 실제 이동 방향의 차이
        ground_track_rad = np.arctan2(state["v_east_fps"], state["v_north_fps"])
        drift_angle = np.rad2deg(heading_rad - ground_track_rad)
        
        # -180 ~ 180도 범위로 정규화
        if drift_angle > 180:
            drift_angle -= 360
        elif drift_angle < -180:
            drift_angle += 360
        
        # 횡풍 성분 계산
        crosswind_component = self.wind_model.get_crosswind_component(
            state["yaw_deg"]
        )
        
        return {
            "lateral_deviation_m": lateral_deviation,
            "along_track_distance_m": along_track_distance,
            "total_distance_m": distance_traveled,
            "drift_angle_deg": drift_angle,
            "crosswind_component_mps": crosswind_component,
        }
    
    def reset(self):
        """시뮬레이션 리셋"""
        self.jsbsim.reset()
        
        # 초기 위치 재설정
        initial_state = self.jsbsim.get_state()
        self.initial_latitude = initial_state["latitude"]
        self.initial_longitude = initial_state["longitude"]
        self.initial_x = initial_state["x_m"]
        self.initial_y = initial_state["y_m"]
        
        logger.info("시뮬레이션 리셋 완료")
    
    def close(self):
        """리소스 정리"""
        self.jsbsim.close()
        logger.info("CrosswindSimulator 종료")
    
    @staticmethod
    def compare_wind_conditions(
        wind_speeds: List[float],
        duration: float = 60.0,
        aircraft_model: str = "c172p",
    ) -> Dict[float, pd.DataFrame]:
        """
        여러 풍속 조건에서 시뮬레이션 비교
        
        Args:
            wind_speeds: 비교할 풍속 리스트 (m/s)
            duration: 각 시뮬레이션 지속 시간
            aircraft_model: 항공기 모델
        
        Returns:
            {풍속: 결과 DataFrame} 딕셔너리
        """
        results_dict = {}
        
        for wind_speed in wind_speeds:
            logger.info(f"풍속 {wind_speed}m/s 시뮬레이션 시작...")
            
            simulator = CrosswindSimulator(
                aircraft_model=aircraft_model,
                crosswind_speed=wind_speed,
                crosswind_direction=90.0,  # 순수 횡풍 (동쪽에서)
            )
            
            results = simulator.run_simulation(duration=duration)
            results_dict[wind_speed] = results
            
            simulator.close()
        
        return results_dict
