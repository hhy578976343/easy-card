"""
游戏逻辑模块 - 游戏流程控制
"""

import random
from typing import List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from .cards import Card, CardUtils, Suit, Rank
from .game_types import CardType, CardPattern, PatternAnalyzer


class PlayerPosition(Enum):
    """玩家位置"""
    LANDLORD = 0      # 地主
    PEASANT1 = 1      # 农民1
    PEASANT2 = 2      # 农民2


@dataclass
class Player:
    """玩家数据"""
    position: PlayerPosition
    cards: List[Card] = None
    is_landlord: bool = False
    
    def __post_init__(self):
        if self.cards is None:
            self.cards = []
    
    @property
    def name(self) -> str:
        if self.is_landlord:
            return f"{self.position.name}(地主)"
        return self.position.name
    
    def add_cards(self, cards: List[Card]):
        """添加卡牌"""
        self.cards.extend(cards)
        self.cards = CardUtils.sort_cards(self.cards, descending=True)
    
    def remove_cards(self, cards: List[Card]):
        """移除卡牌"""
        for card in cards:
            for i, c in enumerate(self.cards):
                if c.suit == card.suit and c.rank == card.rank:
                    self.cards.pop(i)
                    break


class GameAction(Enum):
    """游戏动作"""
    PASS = 0          # 不出
    PLAY = 1          # 出牌
    QUIT = -1         # 退出


@dataclass
class TurnResult:
    """出牌结果"""
    player: Player
    action: GameAction
    cards: List[Card] = None
    pattern: CardPattern = None
    
    def __repr__(self):
        if self.action == GameAction.PASS:
            return f"{self.player.name}: 不出"
        return f"{self.player.name}: {' '.join(str(c) for c in self.cards)}"


class LandlordsGame:
    """斗地主游戏主类"""
    
    def __init__(self):
        self.players: List[Player] = []
        self.landlord_cards: List[Card] = []  # 底牌
        self.current_landlord: Optional[Player] = None
        self.current_turn: int = 0  # 当前出牌轮次 (0, 1, 2)
        self.last_play: Optional[TurnResult] = None  # 上一次出牌
        self.turn_pass_count: int = 0  # 连续过牌次数
        self.round_number: int = 0  # 回合数
        
    def initialize(self):
        """初始化游戏"""
        self.players = [
            Player(PlayerPosition.PEASANT1),
            Player(PlayerPosition.LANDLORD),
            Player(PlayerPosition.PEASANT2)
        ]
        self.landlord_cards = []
        self.current_landlord = None
        self.last_play = None
        self.turn_pass_count = 0
        self.round_number = 0
    
    def deal_cards(self) -> Tuple[List[Player], List[Card]]:
        """发牌"""
        deck = CardUtils.create_standard_deck()
        random.shuffle(deck)
        
        # 每人17张
        for i in range(3):
            self.players[i].cards = CardUtils.sort_cards(deck[i*17:(i+1)*17], descending=True)
        
        # 3张底牌
        self.landlord_cards = deck[51:54]
        
        return self.players, self.landlord_cards
    
    def set_landlord(self, winner_idx: int):
        """设置地主"""
        self.current_landlord = self.players[winner_idx]
        self.players[winner_idx].is_landlord = True
        self.current_landlord.add_cards(self.landlord_cards)
        # 确定出牌顺序：地主先出
        self.current_turn = winner_idx
    
    def get_player_at_turn(self, turn: int) -> Player:
        """获取指定回合的玩家"""
        return self.players[turn % 3]
    
    def can_play_cards(self, player: Player, cards: List[Card]) -> bool:
        """检查玩家是否能出这些牌"""
        # 检查玩家是否有这些牌（更严格的检查）
        player_cards_copy = player.cards.copy()
        for card in cards:
            found = False
            for i, c in enumerate(player_cards_copy):
                if c.value == card.value and c.suit == card.suit:
                    player_cards_copy.pop(i)
                    found = True
                    break
            if not found:
                return False
        
        # 分析牌型
        pattern = PatternAnalyzer.analyze(cards)
        if not pattern:
            return False
        
        # 检查是否能打过上家的牌
        if self.last_play and self.last_play.player != player:
            if self.last_play.action == GameAction.PASS:
                return True
            return PatternAnalyzer.can_beat(pattern, self.last_play.pattern)
        
        return True
    
    def play_cards(self, player: Player, cards: List[Card]) -> TurnResult:
        """玩家出牌"""
        if not self.can_play_cards(player, cards):
            raise ValueError("Invalid cards")
        
        # 移除牌
        player.remove_cards(cards)
        
        # 分析牌型
        pattern = PatternAnalyzer.analyze(cards)
        
        result = TurnResult(player, GameAction.PLAY, cards, pattern)
        
        # 更新状态
        self.last_play = result
        self.turn_pass_count = 0
        
        return result
    
    def pass_turn(self, player: Player) -> TurnResult:
        """玩家跳过"""
        # 只有不是出牌者才能跳过
        if self.last_play and self.last_play.player == player:
            return TurnResult(player, GameAction.PLAY, [], None)
        
        self.turn_pass_count += 1
        return TurnResult(player, GameAction.PASS, [])
    
    def next_turn(self) -> int:
        """进入下一回合"""
        self.current_turn = (self.current_turn + 1) % 3
        
        # 如果连续两人跳过（上家出牌后），恢复自由出牌
        # 注意：不需要等三人，跳过两次且上次有出牌即可
        if self.turn_pass_count >= 2 and self.last_play and self.last_play.action == GameAction.PLAY:
            self.last_play = None
            self.turn_pass_count = 0
        
        return self.current_turn
    
    def check_game_over(self) -> Optional[Player]:
        """检查游戏是否结束"""
        for player in self.players:
            if len(player.cards) == 0:
                return player
        return None
    
    def get_winner(self) -> Optional[Player]:
        """获取获胜者"""
        winner = self.check_game_over()
        if winner:
            # 地主获胜
            if winner.is_landlord:
                return winner
            # 农民获胜 - 返回第一个农民
            return self.players[1] if not winner.is_landlord else self.players[2]
        return None
    
    def get_valid_plays(self, player: Player) -> List[List[Card]]:
        """获取玩家可以出的所有合法牌型组合"""
        valid_plays = []
        
        # 如果没有上家出牌，可以出任何合法牌型
        if not self.last_play or self.last_play.player != player:
            from itertools import combinations
            # 遍历所有可能的出牌组合
            for length in range(1, len(player.cards) + 1):
                for combo in combinations(player.cards, length):
                    pattern = PatternAnalyzer.analyze(list(combo))
                    if pattern:
                        # 检查是否能打过上家
                        if not self.last_play or self.last_play.action == GameAction.PASS:
                            valid_plays.append(list(combo))
                        elif PatternAnalyzer.can_beat(pattern, self.last_play.pattern):
                            valid_plays.append(list(combo))
        else:
            # 必须出比上家大的牌
            pass
        
        return valid_plays
    
    def get_smart_play(self, player: Player, is_ai: bool = True) -> Optional[List[Card]]:
        """AI智能出牌"""
        # 自由出牌（没有上家出牌或连续跳过后）
        if not self.last_play or self.last_play.player == player or self.last_play.action == GameAction.PASS:
            return self._ai_first_play(player)
        else:
            # 跟牌
            return self._ai_follow_play(player)
    
    def _ai_first_play(self, player: Player) -> Optional[List[Card]]:
        """AI先手出牌策略"""
        if len(player.cards) == 0:
            return None
        
        # 出单张最小的
        sorted_cards = CardUtils.sort_cards(player.cards, descending=False)
        
        # 尝试出顺子
        for length in range(5, 12):
            straight = self._find_smallest_straight(player.cards, length)
            if straight:
                return straight
        
        # 出对子
        counts = CardUtils.count_by_rank(player.cards)
        for val in sorted(counts.keys(), reverse=False):
            if counts[val] == 2:
                return [c for c in player.cards if c.value == val][:2]
        
        # 出三张
        for val in sorted(counts.keys(), reverse=False):
            if counts[val] == 3:
                return [c for c in player.cards if c.value == val][:3]
        
        # 出炸弹
        for val in sorted(counts.keys(), reverse=True):
            if counts[val] == 4:
                return [c for c in player.cards if c.value == val][:4]
        
        # 出单张
        return [sorted_cards[0]]
    
    def _ai_follow_play(self, player: Player) -> Optional[List[Card]]:
        """AI跟牌策略"""
        if not self.last_play or self.last_play.action == GameAction.PASS:
            return self._ai_first_play(player)
        
        target_pattern = self.last_play.pattern
        target_type = target_pattern.card_type
        target_count = len(self.last_play.cards)
        
        # 尝试炸弹
        counts = CardUtils.count_by_rank(player.cards)
        
        # 优先用炸弹炸
        for val in sorted(counts.keys(), reverse=True):
            if counts[val] == 4:
                return [c for c in player.cards if c.value == val][:4]
        
        # 火箭
        has_little = 16 in counts
        has_big = 17 in counts
        if has_little and has_big:
            return [c for c in player.cards if c.value in [16, 17]]
        
        # 根据目标牌型找牌
        player_pattern = self._find_matching_pattern(player.cards, target_pattern)
        if player_pattern:
            return player_pattern
        
        # 找不到能打过的牌，尝试出最小单张（自由出牌）
        return None
    
    def _find_smallest_straight(self, cards: List[Card], length: int) -> Optional[List[Card]]:
        """找到最小的顺子"""
        single_values = []
        for card in cards:
            if card.value <= 14:  # 顺子不含2和王
                if card.value not in single_values:
                    single_values.append(card.value)
        
        single_values.sort()
        
        for i in range(len(single_values) - length + 1):
            is_straight = True
            for j in range(length - 1):
                if single_values[i + j + 1] != single_values[i + j] + 1:
                    is_straight = False
                    break
            if is_straight:
                result = []
                for val in single_values[i:i+length]:
                    for card in cards:
                        if card.value == val and card not in result:
                            result.append(card)
                            break
                if len(result) == length:
                    return result
        return None
    
    def _find_matching_pattern(self, cards: List[Card], target: CardPattern) -> Optional[List[Card]]:
        """找到能打过目标牌型的牌"""
        counts = CardUtils.count_by_rank(cards)
        
        # 单张
        if target.card_type == CardType.SINGLE:
            for val in sorted(counts.keys()):
                if val > target.main_value:
                    for card in cards:
                        if card.value == val:
                            return [card]
        
        # 对子
        elif target.card_type == CardType.PAIR:
            for val in sorted(counts.keys()):
                if counts[val] >= 2 and val > target.main_value:
                    result = [c for c in cards if c.value == val][:2]
                    if len(result) == 2:
                        return result
        
        # 三张
        elif target.card_type == CardType.TRIPLE:
            for val in sorted(counts.keys()):
                if counts[val] >= 3 and val > target.main_value:
                    result = [c for c in cards if c.value == val][:3]
                    if len(result) == 3:
                        return result
        
        # 三带二
        elif target.card_type == CardType.THREE_WITH_TWO:
            for val in sorted(counts.keys()):
                if counts[val] >= 3 and val > target.main_value:
                    # 找一对
                    for pair_val in counts.keys():
                        if counts[pair_val] >= 2 and pair_val != val:
                            return [c for c in cards if c.value == val][:3] + [c for c in cards if c.value == pair_val][:2]
        
        # 炸弹
        elif target.card_type == CardType.BOMB:
            for val in sorted(counts.keys()):
                if counts[val] == 4 and val > target.main_value:
                    return [c for c in cards if c.value == val][:4]
        
        return None


if __name__ == "__main__":
    # 测试游戏
    game = LandlordsGame()
    game.initialize()
    players, landlord_cards = game.deal_cards()
    
    print("发牌结果:")
    for i, player in enumerate(players):
        print(f"玩家{i+1} {player.name}: {player.cards}")
    print(f"底牌: {landlord_cards}")