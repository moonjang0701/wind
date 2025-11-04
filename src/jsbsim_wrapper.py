"""
JSBSim Flight Dynamics Model 래퍼 클래스

JSBSim 엔진을 Python에서 쉽게 사용할 수 있도록 래핑한 클래스입니다.
"""

import os
import numpy as np
from typing import Dict, Optional, Tuple
import logging

try:
    import jsbsim
except ImportError:
    raise ImportError(
        "JSBSim이 설치되어 있지 않습니다. "
        "'pip install jsbsim'을 실행하여 설치하세요."
    )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JSBSimWrapper:
    """
    JSBSim Flight Dynamics Model 래퍼 클래스
    
    항공기 시뮬레이션을 위한 JSBSim 엔진의 인터페이스를 제공합니다.
    """
    
    def __init__(
        self,
        aircraft: str = "c172p",
        dt: float = 0.01,
        init_altitude: float = 1000.0,
        init_airspeed: float = 60.0,
    ):
        """
        JSBSim 래퍼 초기화
        
        Args:
            aircraft: 항공기 모델 이름 (기본값: c172p - Cessna 172)
            dt: 시뮬레이션 시간 간격 (초)
            init_altitude: 초기 고도 (feet)
            init_airspeed: 초기 대기속도 (knots)
        """
        self.aircraft = aircraft
        self.dt = dt
        self.init_altitude = init_altitude
        self.init_airspeed = init_airspeed
        
        # JSBSim FDM 객체 생성
        self.fdm = jsbsim.FGFDMExec(None)
        self.fdm.set_debug_level(0)
        
        # 시뮬레이션 시간 간격 설정
        self.fdm.set_dt(dt)
        
        # 항공기 로드 및 초기화
        self._load_aircraft()
        self._initialize_conditions()
        
        logger.info(f"JSBSim 초기화 완료: {aircraft}, dt={dt}s")
    
    def _load_aircraft(self):
        """항공기 모델 로드"""
        # JSBSim 데이터 경로 설정 시도
        try:
            # 일반적인 JSBSim 설치 경로 시도
            jsbsim_path = os.path.dirname(jsbsim.__file__)
            aircraft_path = os.path.join(jsbsim_path, "data", "aircraft")
            
            if os.path.exists(aircraft_path):
                self.fdm.set_aircraft_path(aircraft_path)
            
            # 항공기 로드
            loaded = self.fdm.load_model(self.aircraft)
            
            if not loaded:
                logger.warning(
                    f"항공기 '{self.aircraft}' 로드 실패. "
                    "기본 설정을 사용합니다."
                )
        except Exception as e:
            logger.error(f"항공기 로드 중 오류: {e}")
            # 기본 항공기 사용 계속 진행
    
    def _initialize_conditions(self):
        """초기 비행 조건 설정"""
        ic = self.fdm.get_ic()
        
        # 초기 위치 설정 (샌프란시스코 국제공항 근처)
        ic.set_longitude_deg(-122.3748)
        ic.set_latitude_deg(37.6189)
        ic.set_altitude_ft_agl(self.init_altitude)
        
        # 초기 자세 설정 (수평 비행)
        ic.set_phi_deg(0.0)    # Roll
        ic.set_theta_deg(0.0)  # Pitch
        ic.set_psi_deg(0.0)    # Yaw (북쪽 방향)
        
        # 초기 속도 설정
        ic.set_v_calibrated_kts(self.init_airspeed)
        ic.set_v_north_fps(0.0)
        ic.set_v_east_fps(0.0)
        ic.set_v_down_fps(0.0)
        
        # 엔진 시동
        self.fdm.set_property_value("propulsion/engine[0]/set-running", 1)
        self.fdm.set_property_value("fcs/throttle-cmd-norm", 0.6)
        self.fdm.set_property_value("fcs/mixture-cmd-norm", 1.0)
        
        logger.info(
            f"초기 조건 설정: Alt={self.init_altitude}ft, "
            f"IAS={self.init_airspeed}kts"
        )
    
    def set_wind(
        self,
        wind_north: float = 0.0,
        wind_east: float = 0.0,
        wind_down: float = 0.0,
    ):
        """
        풍향/풍속 설정
        
        Args:
            wind_north: 북쪽 방향 바람 속도 (fps, feet per second)
            wind_east: 동쪽 방향 바람 속도 (fps)
            wind_down: 아래쪽 방향 바람 속도 (fps)
        """
        self.fdm.set_property_value("atmosphere/wind-north-fps", wind_north)
        self.fdm.set_property_value("atmosphere/wind-east-fps", wind_east)
        self.fdm.set_property_value("atmosphere/wind-down-fps", wind_down)
        
        logger.debug(
            f"풍향 설정: N={wind_north:.2f}, E={wind_east:.2f}, "
            f"D={wind_down:.2f} fps"
        )
    
    def run_step(self) -> bool:
        """
        시뮬레이션 1 스텝 실행
        
        Returns:
            성공 여부
        """
        return self.fdm.run()
    
    def get_state(self) -> Dict[str, float]:
        """
        현재 항공기 상태 반환
        
        Returns:
            항공기 상태 딕셔너리
        """
        state = {
            # 시간
            "time": self.fdm.get_property_value("simulation/sim-time-sec"),
            
            # 위치 (지구 좌표계)
            "latitude": self.fdm.get_property_value("position/lat-gc-deg"),
            "longitude": self.fdm.get_property_value("position/long-gc-deg"),
            "altitude_ft": self.fdm.get_property_value("position/h-sl-ft"),
            "altitude_agl_ft": self.fdm.get_property_value("position/h-agl-ft"),
            
            # 위치 (로컬 좌표계)
            "x_m": self.fdm.get_property_value("position/distance-from-start-lon-mt"),
            "y_m": self.fdm.get_property_value("position/distance-from-start-lat-mt"),
            "z_m": self.fdm.get_property_value("position/h-sl-meters"),
            
            # 자세
            "roll_deg": self.fdm.get_property_value("attitude/roll-rad") * 180 / np.pi,
            "pitch_deg": self.fdm.get_property_value("attitude/pitch-rad") * 180 / np.pi,
            "yaw_deg": self.fdm.get_property_value("attitude/psi-deg"),
            
            # 속도 (대기 기준)
            "airspeed_kts": self.fdm.get_property_value("velocities/vc-kts"),
            "groundspeed_kts": self.fdm.get_property_value("velocities/vg-kts"),
            
            # 속도 (지구 좌표계)
            "v_north_fps": self.fdm.get_property_value("velocities/v-north-fps"),
            "v_east_fps": self.fdm.get_property_value("velocities/v-east-fps"),
            "v_down_fps": self.fdm.get_property_value("velocities/v-down-fps"),
            
            # 바람
            "wind_north_fps": self.fdm.get_property_value("atmosphere/wind-north-fps"),
            "wind_east_fps": self.fdm.get_property_value("atmosphere/wind-east-fps"),
            "wind_down_fps": self.fdm.get_property_value("atmosphere/wind-down-fps"),
        }
        
        return state
    
    def reset(self):
        """시뮬레이션 리셋"""
        self.fdm.reset_to_initial_conditions(0)
        logger.info("시뮬레이션 리셋 완료")
    
    def close(self):
        """리소스 정리"""
        # JSBSim FDM 객체는 Python GC가 처리
        logger.info("JSBSim 래퍼 종료")


def convert_wind_to_components(
    wind_speed_mps: float,
    wind_direction_deg: float
) -> Tuple[float, float]:
    """
    풍속과 풍향을 북쪽/동쪽 성분으로 변환
    
    Args:
        wind_speed_mps: 풍속 (m/s)
        wind_direction_deg: 풍향 (도, 북쪽 기준 시계방향)
    
    Returns:
        (wind_north_fps, wind_east_fps) 튜플
    """
    # m/s를 fps로 변환 (1 m/s = 3.28084 fps)
    wind_speed_fps = wind_speed_mps * 3.28084
    
    # 풍향을 라디안으로 변환
    wind_direction_rad = np.deg2rad(wind_direction_deg)
    
    # 북쪽/동쪽 성분 계산
    # 풍향은 바람이 불어오는 방향이므로 음수 처리
    wind_north_fps = -wind_speed_fps * np.cos(wind_direction_rad)
    wind_east_fps = -wind_speed_fps * np.sin(wind_direction_rad)
    
    return wind_north_fps, wind_east_fps
