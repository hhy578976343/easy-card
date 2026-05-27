"""
计分系统模块 - 斗地主积分计算
"""

from enum import Enum
from typing import Dict, List
from dataclasses import dataclass


class GameScore:
    """游戏积分系统"""
    
    # 基础倍率
    BASE_MULTIPLIER = 1
    
    # 炸弹倍率
    BOMB_MULTIPLIER = 2
    
    # 王炸倍率（火箭）
    ROCKET_MULTIPLIER = 4
    
    # 春天倍率
    SPRING_MULTIPLIER = 2
    
    # 叫地主基础分
    LANDLORD_BASE_SCORE = 1
    
    @staticmethod
    def calculate_round_score(
        landlord_score: int,
        is_landlord_winner: bool,
        bomb_count: int,
        has_rocket: bool,
        is_spring: bool,
        landlord_win_round: bool
    ) -> Dict[str, int]:
        """计算一局的积分
        
        Args:
            landlord_score: 叫地主分数
            is_landlord_winner: 地主是否获胜
            bomb_count: 炸弹数量
            has_rocket: 是否有王炸
            is_spring: 是否春天
            landlord_win_round: 地主是否赢了这一局
        
        Returns:
            {'landlord': 积分变化, 'peasants': 积分变化}
        """
        # 计算基础倍率
        multiplier = GameScore.BASE_MULTIPLIER
        
        # 炸弹翻倍
        for _ in range(bomb_count):
            multiplier *= GameScore.BOMB_MULTIPLIER
        
        # 王炸再翻倍
        if has_rocket:
            multiplier *= GameScore.ROCKET_MULTIPLIER
        
        # 春天翻倍
        if is_spring:
            multiplier *= GameScore.SPRING_MULTIPLIER
        
        # 计算基础积分
        base_score = landlord_score * multiplier
        
        # 地主赢：农民输分给地主
        # 农民赢：地主输分给赢的农民
        if landlord_win_round:
            landlord_change = base_score * 2  # 地主赢两份
            peasant_change = -base_score  # 每个农民输一份
        else:
            landlord_change = -base_score * 2  # 地主输两份
            peasant_change = base_score  # 每个农民赢一份
        
        return {
            'landlord': landlord_change,
            'peasants': peasant_change,
            'multiplier': multiplier,
            'base_score': base_score
        }
    
    @staticmethod
    def count_bombs_and_rockets(cards_list: List) -> Dict[str, int]:
        """统计炸弹和王炸数量"""
        from .game_types import PatternAnalyzer, CardType
        
        bombs = 0
        rockets = 0
        
        for cards in cards_list:
            if len(cards) == 2:
                values = [c.value for c in cards]
                if 16 in values and 17 in values:
                    rockets += 1
            elif len(cards) == 4:
                values = [c.value for c in cards]
                if len(set(values)) == 1:  # 四张相同
                    bombs += 1
        
        return {'bombs': bombs, 'rockets': rockets}


@dataclass
class PlayerScore:
    """玩家积分"""
    player_id: int
    total_score: int = 1000  # 初始分数
    round_scores: List[int] = None
    
    def __post_init__(self):
        if self.round_scores is None:
            self.round_scores = []
    
    def add_score(self, change: int):
        """添加积分变化"""
        self.total_score += change
        self.round_scores.append(change)
    
    def get_history(self) -> str:
        """获取积分历史"""
        if not self.round_scores:
            return "无"
        return " + ".join(f"{s:+d}" for s in self.round_scores)


class ScoreManager:
    """积分管理器"""
    
    def __init__(self):
        self.player_scores: Dict[int, PlayerScore] = {
            0: PlayerScore(0),
            1: PlayerScore(1),
            2: PlayerScore(2)
        }
        self.current_round = 0
        self.total_rounds = 0
        self.round_results: List[Dict] = []
    
    def set_total_rounds(self, rounds: int):
        """设置总回合数"""
        self.total_rounds = rounds
        self.current_round = 0
    
    def reset_scores(self):
        """重置积分"""
        for score in self.player_scores.values():
            score.total_score = 1000
            score.round_scores = []
        self.round_results = []
        self.current_round = 0
    
    def update_round_score(self, landlord_id: int, score_data: Dict):
        """更新回合积分"""
        # 计算地主和农民
        if score_data.get('landlord_win', False):
            # 地主赢
            for pid in range(3):
                if pid == landlord_id:
                    self.player_scores[pid].add_score(score_data['landlord'])
                else:
                    self.player_scores[pid].add_score(score_data['peasants'])
        else:
            # 农民赢
            for pid in range(3):
                if pid == landlord_id:
                    self.player_scores[pid].add_score(score_data['landlord'])
                else:
                    self.player_scores[pid].add_score(score_data['peasants'])
        
        self.current_round += 1
        
        # 记录回合结果
        self.round_results.append({
            'round': self.current_round,
            'landlord_win': score_data.get('landlord_win', False),
            'multiplier': score_data.get('multiplier', 1),
            'bombs': score_data.get('bombs', 0),
            'rockets': score_data.get('rockets', 0),
            'is_spring': score_data.get('is_spring', False)
        })
    
    def get_leaderboard(self) -> List[tuple]:
        """获取排行榜"""
        return sorted(
            [(pid, ps.total_score) for pid, ps in self.player_scores.items()],
            key=lambda x: x[1],
            reverse=True
        )
    
    def is_game_over(self) -> bool:
        """检查游戏是否结束"""
        return self.current_round >= self.total_rounds
    
    def get_winner(self) -> int:
        """获取最终获胜者（积分最高）"""
        leaderboard = self.get_leaderboard()
        return leaderboard[0][0] if leaderboard else 0