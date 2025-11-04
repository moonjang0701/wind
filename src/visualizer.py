"""
시뮬레이션 결과 시각화 모듈

시뮬레이션 결과를 다양한 형태의 그래프와 차트로 시각화합니다.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# 한글 폰트 설정 (선택적)
try:
    plt.rcParams['font.family'] = 'DejaVu Sans'
except:
    pass

# 스타일 설정
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


class Visualizer:
    """
    시뮬레이션 결과 시각화 클래스
    """
    
    @staticmethod
    def plot_trajectory_2d(
        df: pd.DataFrame,
        title: str = "Aircraft Trajectory (Top View)",
        save_path: Optional[str] = None,
    ):
        """
        2D 비행 궤적 플롯 (상면도)
        
        Args:
            df: 시뮬레이션 결과 DataFrame
            title: 그래프 제목
            save_path: 저장 경로 (None이면 표시만)
        """
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # 궤적 그리기
        ax.plot(df['x_m'], df['y_m'], 'b-', linewidth=2, label='Actual Path')
        
        # 시작점과 끝점 표시
        ax.plot(df['x_m'].iloc[0], df['y_m'].iloc[0], 'go', 
                markersize=10, label='Start')
        ax.plot(df['x_m'].iloc[-1], df['y_m'].iloc[-1], 'ro', 
                markersize=10, label='End')
        
        # 의도한 경로 (직선) 그리기
        intended_path_y = [df['y_m'].iloc[0], df['y_m'].iloc[-1]]
        intended_path_x = [df['x_m'].iloc[0], df['x_m'].iloc[0]]
        ax.plot(intended_path_x, intended_path_y, 'r--', 
                linewidth=1.5, alpha=0.7, label='Intended Path')
        
        # 축 설정
        ax.set_xlabel('East (m)', fontsize=12)
        ax.set_ylabel('North (m)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"궤적 그래프 저장: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    @staticmethod
    def plot_deviation_over_time(
        df: pd.DataFrame,
        title: str = "Lateral Deviation Over Time",
        save_path: Optional[str] = None,
    ):
        """
        시간에 따른 측면 편차 플롯
        
        Args:
            df: 시뮬레이션 결과 DataFrame
            title: 그래프 제목
            save_path: 저장 경로
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # 측면 편차
        ax1.plot(df['time'], df['lateral_deviation_m'], 'b-', linewidth=2)
        ax1.set_xlabel('Time (s)', fontsize=11)
        ax1.set_ylabel('Lateral Deviation (m)', fontsize=11)
        ax1.set_title(title, fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        
        # 편류각
        ax2.plot(df['time'], df['drift_angle_deg'], 'g-', linewidth=2)
        ax2.set_xlabel('Time (s)', fontsize=11)
        ax2.set_ylabel('Drift Angle (deg)', fontsize=11)
        ax2.set_title('Drift Angle Over Time', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"편차 그래프 저장: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    @staticmethod
    def plot_velocity_analysis(
        df: pd.DataFrame,
        title: str = "Velocity Analysis",
        save_path: Optional[str] = None,
    ):
        """
        속도 분석 플롯
        
        Args:
            df: 시뮬레이션 결과 DataFrame
            title: 그래프 제목
            save_path: 저장 경로
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 대기속도 vs 대지속도
        axes[0, 0].plot(df['time'], df['airspeed_kts'], 'b-', 
                        linewidth=2, label='Airspeed')
        axes[0, 0].plot(df['time'], df['groundspeed_kts'], 'r-', 
                        linewidth=2, label='Groundspeed')
        axes[0, 0].set_xlabel('Time (s)', fontsize=10)
        axes[0, 0].set_ylabel('Speed (knots)', fontsize=10)
        axes[0, 0].set_title('Airspeed vs Groundspeed', fontsize=11, fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 속도 성분 (북쪽/동쪽)
        axes[0, 1].plot(df['time'], df['v_north_fps'], 'b-', 
                        linewidth=2, label='North')
        axes[0, 1].plot(df['time'], df['v_east_fps'], 'r-', 
                        linewidth=2, label='East')
        axes[0, 1].set_xlabel('Time (s)', fontsize=10)
        axes[0, 1].set_ylabel('Velocity (fps)', fontsize=10)
        axes[0, 1].set_title('Velocity Components', fontsize=11, fontweight='bold')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 풍속 성분
        axes[1, 0].plot(df['time'], df['wind_north_fps'], 'b-', 
                        linewidth=2, label='North')
        axes[1, 0].plot(df['time'], df['wind_east_fps'], 'r-', 
                        linewidth=2, label='East')
        axes[1, 0].set_xlabel('Time (s)', fontsize=10)
        axes[1, 0].set_ylabel('Wind Speed (fps)', fontsize=10)
        axes[1, 0].set_title('Wind Components', fontsize=11, fontweight='bold')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 횡풍 성분
        axes[1, 1].plot(df['time'], df['crosswind_component_mps'], 'g-', 
                        linewidth=2)
        axes[1, 1].set_xlabel('Time (s)', fontsize=10)
        axes[1, 1].set_ylabel('Crosswind (m/s)', fontsize=10)
        axes[1, 1].set_title('Crosswind Component', fontsize=11, fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].axhline(y=0, color='r', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"속도 분석 그래프 저장: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    @staticmethod
    def plot_comparison(
        results_dict: Dict[float, pd.DataFrame],
        metric: str = 'lateral_deviation_m',
        title: Optional[str] = None,
        save_path: Optional[str] = None,
    ):
        """
        여러 시뮬레이션 결과 비교 플롯
        
        Args:
            results_dict: {조건: DataFrame} 딕셔너리
            metric: 비교할 메트릭 컬럼명
            title: 그래프 제목
            save_path: 저장 경로
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(results_dict)))
        
        for (condition, df), color in zip(results_dict.items(), colors):
            label = f"{condition} m/s" if isinstance(condition, (int, float)) else str(condition)
            ax.plot(df['time'], df[metric], linewidth=2, 
                   label=label, color=color)
        
        ax.set_xlabel('Time (s)', fontsize=12)
        
        # Y축 라벨 설정
        ylabel_map = {
            'lateral_deviation_m': 'Lateral Deviation (m)',
            'drift_angle_deg': 'Drift Angle (deg)',
            'airspeed_kts': 'Airspeed (knots)',
            'groundspeed_kts': 'Groundspeed (knots)',
        }
        ax.set_ylabel(ylabel_map.get(metric, metric), fontsize=12)
        
        if title is None:
            title = f"Comparison: {metric}"
        ax.set_title(title, fontsize=14, fontweight='bold')
        
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"비교 그래프 저장: {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    @staticmethod
    def plot_comprehensive_report(
        df: pd.DataFrame,
        wind_speed: float,
        save_path: Optional[str] = None,
    ):
        """
        종합 분석 리포트 생성
        
        Args:
            df: 시뮬레이션 결과 DataFrame
            wind_speed: 횡풍 속도 (m/s)
            save_path: 저장 경로
        """
        fig = plt.figure(figsize=(16, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. 궤적 (2D)
        ax1 = fig.add_subplot(gs[0:2, 0:2])
        ax1.plot(df['x_m'], df['y_m'], 'b-', linewidth=2, label='Actual Path')
        ax1.plot(df['x_m'].iloc[0], df['y_m'].iloc[0], 'go', markersize=10, label='Start')
        ax1.plot(df['x_m'].iloc[-1], df['y_m'].iloc[-1], 'ro', markersize=10, label='End')
        intended_x = [df['x_m'].iloc[0], df['x_m'].iloc[0]]
        intended_y = [df['y_m'].iloc[0], df['y_m'].iloc[-1]]
        ax1.plot(intended_x, intended_y, 'r--', linewidth=1.5, alpha=0.7, label='Intended')
        ax1.set_xlabel('East (m)', fontsize=10)
        ax1.set_ylabel('North (m)', fontsize=10)
        ax1.set_title(f'Trajectory (Crosswind: {wind_speed} m/s)', fontsize=11, fontweight='bold')
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3)
        ax1.axis('equal')
        
        # 2. 측면 편차
        ax2 = fig.add_subplot(gs[0, 2])
        ax2.plot(df['time'], df['lateral_deviation_m'], 'b-', linewidth=2)
        ax2.set_xlabel('Time (s)', fontsize=9)
        ax2.set_ylabel('Deviation (m)', fontsize=9)
        ax2.set_title('Lateral Deviation', fontsize=10, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        
        # 3. 편류각
        ax3 = fig.add_subplot(gs[1, 2])
        ax3.plot(df['time'], df['drift_angle_deg'], 'g-', linewidth=2)
        ax3.set_xlabel('Time (s)', fontsize=9)
        ax3.set_ylabel('Angle (deg)', fontsize=9)
        ax3.set_title('Drift Angle', fontsize=10, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        
        # 4. 속도
        ax4 = fig.add_subplot(gs[2, 0])
        ax4.plot(df['time'], df['airspeed_kts'], 'b-', linewidth=1.5, label='Airspeed')
        ax4.plot(df['time'], df['groundspeed_kts'], 'r-', linewidth=1.5, label='Groundspeed')
        ax4.set_xlabel('Time (s)', fontsize=9)
        ax4.set_ylabel('Speed (kts)', fontsize=9)
        ax4.set_title('Speed', fontsize=10, fontweight='bold')
        ax4.legend(fontsize=8)
        ax4.grid(True, alpha=0.3)
        
        # 5. 고도
        ax5 = fig.add_subplot(gs[2, 1])
        ax5.plot(df['time'], df['altitude_agl_ft'], 'purple', linewidth=2)
        ax5.set_xlabel('Time (s)', fontsize=9)
        ax5.set_ylabel('Altitude (ft)', fontsize=9)
        ax5.set_title('Altitude AGL', fontsize=10, fontweight='bold')
        ax5.grid(True, alpha=0.3)
        
        # 6. 통계 정보
        ax6 = fig.add_subplot(gs[2, 2])
        ax6.axis('off')
        
        # 통계 계산
        max_deviation = df['lateral_deviation_m'].abs().max()
        final_deviation = df['lateral_deviation_m'].iloc[-1]
        mean_drift = df['drift_angle_deg'].mean()
        max_drift = df['drift_angle_deg'].abs().max()
        
        stats_text = f"""
        STATISTICS
        ───────────────────
        Max Deviation: {max_deviation:.2f} m
        Final Deviation: {final_deviation:.2f} m
        
        Mean Drift Angle: {mean_drift:.2f}°
        Max Drift Angle: {max_drift:.2f}°
        
        Duration: {df['time'].iloc[-1]:.1f} s
        Distance: {df['total_distance_m'].iloc[-1]:.0f} m
        
        Crosswind: {wind_speed} m/s
        """
        
        ax6.text(0.1, 0.5, stats_text, fontsize=9, 
                verticalalignment='center', family='monospace')
        
        plt.suptitle('Crosswind Simulation Comprehensive Report', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"종합 리포트 저장: {save_path}")
        else:
            plt.show()
        
        plt.close()
