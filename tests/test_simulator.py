"""
CrosswindSimulator 유닛 테스트
"""

import pytest
import numpy as np
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.wind_model import WindModel


class TestWindModel:
    """WindModel 클래스 테스트"""
    
    def test_wind_model_initialization(self):
        """WindModel 초기화 테스트"""
        wind = WindModel(
            wind_speed_mps=10.0,
            wind_direction_deg=90.0,
            turbulence_intensity=0.1
        )
        
        assert wind.base_wind_speed == 10.0
        assert wind.base_wind_direction == 90.0
        assert wind.turbulence_intensity == 0.1
    
    def test_wind_components_no_turbulence(self):
        """난기류 없는 바람 성분 계산 테스트"""
        wind = WindModel(
            wind_speed_mps=10.0,
            wind_direction_deg=0.0,  # 북쪽
            turbulence_intensity=0.0
        )
        
        north, east, down = wind.get_wind_components(
            time=0.0,
            add_turbulence=False
        )
        
        # 북쪽 방향 바람이므로 north 성분이 커야 함
        assert north > 0
        assert abs(east) < 1.0  # 거의 0
        assert abs(down) < 0.1  # 거의 0
    
    def test_crosswind_component(self):
        """횡풍 성분 계산 테스트"""
        wind = WindModel(
            wind_speed_mps=10.0,
            wind_direction_deg=90.0,  # 동쪽
            turbulence_intensity=0.0
        )
        
        # 항공기가 북쪽(0도)으로 비행할 때
        crosswind = wind.get_crosswind_component(aircraft_heading_deg=0.0)
        
        # 90도 바람이므로 순수 횡풍
        assert abs(crosswind - 10.0) < 0.1
    
    def test_headwind_component(self):
        """정풍/배풍 성분 계산 테스트"""
        wind = WindModel(
            wind_speed_mps=10.0,
            wind_direction_deg=0.0,  # 북쪽
            turbulence_intensity=0.0
        )
        
        # 항공기가 북쪽(0도)으로 비행할 때
        headwind = wind.get_headwind_component(aircraft_heading_deg=0.0)
        
        # 정풍
        assert abs(headwind - 10.0) < 0.1
    
    def test_pure_crosswind_creation(self):
        """순수 횡풍 생성 테스트"""
        # 오른쪽에서 부는 횡풍
        wind_right = WindModel.create_pure_crosswind(
            wind_speed_mps=10.0,
            from_right=True
        )
        
        assert wind_right.base_wind_speed == 10.0
        assert wind_right.base_wind_direction == 90.0
        
        # 왼쪽에서 부는 횡풍
        wind_left = WindModel.create_pure_crosswind(
            wind_speed_mps=10.0,
            from_right=False
        )
        
        assert wind_left.base_wind_speed == 10.0
        assert wind_left.base_wind_direction == 270.0
    
    def test_crosswind_with_headwind_creation(self):
        """횡풍+정풍 조합 생성 테스트"""
        wind = WindModel.create_crosswind_with_headwind(
            crosswind_mps=6.0,
            headwind_mps=8.0,
            from_right=True
        )
        
        # 합성 풍속은 피타고라스 정리로 계산
        expected_speed = np.sqrt(6.0**2 + 8.0**2)
        assert abs(wind.base_wind_speed - expected_speed) < 0.1
    
    def test_turbulence_effect(self):
        """난기류 효과 테스트"""
        wind = WindModel(
            wind_speed_mps=10.0,
            wind_direction_deg=0.0,
            turbulence_intensity=0.5  # 강한 난기류
        )
        
        # 여러 번 샘플링하여 변동성 확인
        samples = []
        for _ in range(10):
            north, east, down = wind.get_wind_components(
                time=0.0,
                add_turbulence=True
            )
            samples.append(north)
        
        # 난기류로 인해 값이 변동해야 함
        std_dev = np.std(samples)
        assert std_dev > 0


class TestJSBSimIntegration:
    """JSBSim 통합 테스트 (JSBSim이 설치된 경우에만 실행)"""
    
    def test_jsbsim_import(self):
        """JSBSim 임포트 테스트"""
        try:
            import jsbsim
            assert jsbsim is not None
        except ImportError:
            pytest.skip("JSBSim이 설치되어 있지 않습니다.")
    
    def test_jsbsim_wrapper_initialization(self):
        """JSBSimWrapper 초기화 테스트"""
        try:
            from src.jsbsim_wrapper import JSBSimWrapper
            
            wrapper = JSBSimWrapper(
                aircraft="c172p",
                dt=0.01,
                init_altitude=1000.0,
                init_airspeed=60.0
            )
            
            assert wrapper.aircraft == "c172p"
            assert wrapper.dt == 0.01
            
            wrapper.close()
            
        except ImportError:
            pytest.skip("JSBSim이 설치되어 있지 않습니다.")
    
    def test_crosswind_simulator_initialization(self):
        """CrosswindSimulator 초기화 테스트"""
        try:
            from src.crosswind_simulator import CrosswindSimulator
            
            simulator = CrosswindSimulator(
                aircraft_model="c172p",
                crosswind_speed=10.0,
                crosswind_direction=90.0
            )
            
            assert simulator.aircraft_model == "c172p"
            
            simulator.close()
            
        except ImportError:
            pytest.skip("JSBSim이 설치되어 있지 않습니다.")


def test_wind_conversion_utility():
    """풍향/풍속 변환 유틸리티 테스트"""
    from src.jsbsim_wrapper import convert_wind_to_components
    
    # 북쪽 바람
    north, east = convert_wind_to_components(10.0, 0.0)
    assert north < 0  # 북쪽으로 부는 바람은 음수
    assert abs(east) < 1.0
    
    # 동쪽 바람
    north, east = convert_wind_to_components(10.0, 90.0)
    assert abs(north) < 1.0
    assert east < 0  # 동쪽으로 부는 바람은 음수


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
