"""
풍향/풍속 모델링 모듈

다양한 바람 시나리오를 생성하고 관리하는 클래스입니다.
"""

import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class WindModel:
    """
    바람 모델 클래스
    
    횡풍, 정풍, 배풍 등 다양한 바람 조건을 생성하고 관리합니다.
    """
    
    def __init__(
        self,
        wind_speed_mps: float = 0.0,
        wind_direction_deg: float = 0.0,
        turbulence_intensity: float = 0.0,
    ):
        """
        바람 모델 초기화
        
        Args:
            wind_speed_mps: 평균 풍속 (m/s)
            wind_direction_deg: 풍향 (도, 북쪽 기준 시계방향)
            turbulence_intensity: 난기류 강도 (0.0 ~ 1.0)
        """
        self.base_wind_speed = wind_speed_mps
        self.base_wind_direction = wind_direction_deg
        self.turbulence_intensity = turbulence_intensity
        
        # 난기류 생성을 위한 랜덤 시드 설정
        self.rng = np.random.default_rng()
        
        logger.info(
            f"WindModel 초기화: 풍속={wind_speed_mps}m/s, "
            f"풍향={wind_direction_deg}°, "
            f"난기류={turbulence_intensity}"
        )
    
    def get_wind_components(
        self,
        time: float = 0.0,
        add_turbulence: bool = True
    ) -> Tuple[float, float, float]:
        """
        현재 시간의 바람 성분 반환 (NED 좌표계)
        
        Args:
            time: 현재 시간 (초)
            add_turbulence: 난기류 추가 여부
        
        Returns:
            (wind_north_fps, wind_east_fps, wind_down_fps) 튜플
        """
        # 기본 풍속 계산
        wind_speed = self.base_wind_speed
        wind_direction = self.base_wind_direction
        
        # 난기류 효과 추가
        if add_turbulence and self.turbulence_intensity > 0:
            # 풍속 변동
            speed_variation = self.rng.normal(
                0, 
                self.base_wind_speed * self.turbulence_intensity * 0.2
            )
            wind_speed = max(0, wind_speed + speed_variation)
            
            # 풍향 변동
            direction_variation = self.rng.normal(
                0, 
                15 * self.turbulence_intensity
            )
            wind_direction = wind_direction + direction_variation
            
            # 수직 바람 성분 (난기류)
            wind_down_mps = self.rng.normal(
                0,
                self.base_wind_speed * self.turbulence_intensity * 0.1
            )
        else:
            wind_down_mps = 0.0
        
        # m/s를 fps로 변환
        wind_speed_fps = wind_speed * 3.28084
        wind_down_fps = wind_down_mps * 3.28084
        
        # 풍향을 라디안으로 변환
        wind_direction_rad = np.deg2rad(wind_direction)
        
        # 북쪽/동쪽 성분 계산 (바람이 불어가는 방향)
        wind_north_fps = wind_speed_fps * np.cos(wind_direction_rad)
        wind_east_fps = wind_speed_fps * np.sin(wind_direction_rad)
        
        return wind_north_fps, wind_east_fps, wind_down_fps
    
    def get_crosswind_component(
        self,
        aircraft_heading_deg: float
    ) -> float:
        """
        항공기 진행 방향에 대한 횡풍 성분 계산
        
        Args:
            aircraft_heading_deg: 항공기 헤딩 (도)
        
        Returns:
            횡풍 속도 (m/s, 양수: 오른쪽, 음수: 왼쪽)
        """
        # 항공기와 바람의 상대 각도
        relative_angle = self.base_wind_direction - aircraft_heading_deg
        relative_angle_rad = np.deg2rad(relative_angle)
        
        # 횡풍 성분 계산 (sin 성분)
        crosswind = self.base_wind_speed * np.sin(relative_angle_rad)
        
        return crosswind
    
    def get_headwind_component(
        self,
        aircraft_heading_deg: float
    ) -> float:
        """
        항공기 진행 방향에 대한 정풍/배풍 성분 계산
        
        Args:
            aircraft_heading_deg: 항공기 헤딩 (도)
        
        Returns:
            정풍 속도 (m/s, 양수: 정풍, 음수: 배풍)
        """
        # 항공기와 바람의 상대 각도
        relative_angle = self.base_wind_direction - aircraft_heading_deg
        relative_angle_rad = np.deg2rad(relative_angle)
        
        # 정풍 성분 계산 (cos 성분)
        headwind = self.base_wind_speed * np.cos(relative_angle_rad)
        
        return headwind
    
    @staticmethod
    def create_pure_crosswind(
        wind_speed_mps: float,
        from_right: bool = True
    ) -> 'WindModel':
        """
        순수 횡풍 시나리오 생성
        
        Args:
            wind_speed_mps: 풍속 (m/s)
            from_right: True면 오른쪽에서, False면 왼쪽에서
        
        Returns:
            WindModel 인스턴스
        """
        # 항공기가 북쪽(0도)으로 비행한다고 가정
        # 오른쪽에서 부는 바람: 90도 (동쪽)
        # 왼쪽에서 부는 바람: 270도 (서쪽)
        wind_direction = 90.0 if from_right else 270.0
        
        return WindModel(
            wind_speed_mps=wind_speed_mps,
            wind_direction_deg=wind_direction,
            turbulence_intensity=0.0
        )
    
    @staticmethod
    def create_crosswind_with_headwind(
        crosswind_mps: float,
        headwind_mps: float,
        from_right: bool = True
    ) -> 'WindModel':
        """
        횡풍 + 정풍/배풍 조합 시나리오 생성
        
        Args:
            crosswind_mps: 횡풍 속도 (m/s)
            headwind_mps: 정풍 속도 (m/s, 양수: 정풍, 음수: 배풍)
            from_right: True면 오른쪽에서, False면 왼쪽에서
        
        Returns:
            WindModel 인스턴스
        """
        # 합성 풍속 계산
        wind_speed = np.sqrt(crosswind_mps**2 + headwind_mps**2)
        
        # 풍향 계산
        angle_from_north = np.arctan2(crosswind_mps, headwind_mps)
        wind_direction = np.rad2deg(angle_from_north)
        
        if not from_right:
            wind_direction = -wind_direction
        
        # 0-360도 범위로 정규화
        wind_direction = wind_direction % 360
        
        return WindModel(
            wind_speed_mps=wind_speed,
            wind_direction_deg=wind_direction,
            turbulence_intensity=0.0
        )
    
    def __repr__(self) -> str:
        return (
            f"WindModel(speed={self.base_wind_speed:.2f}m/s, "
            f"direction={self.base_wind_direction:.1f}°, "
            f"turbulence={self.turbulence_intensity:.2f})"
        )
