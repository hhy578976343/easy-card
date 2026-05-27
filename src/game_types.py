"""
牌型模块 - 定义斗地主的各种牌型及其大小比较
"""

from enum import Enum
from typing import List, Optional, Tuple
from dataclasses import dataclass
from .cards import Card, Rank


class CardType(Enum):
    """牌型枚举"""
    SINGLE = 1           # 单张
    PAIR = 2             # 对子
    TRIPLE = 3          # 三张
    BOMB = 4             # 炸弹
    ROCKET = 5           # 火箭（王炸）
    STRAIGHT = 6         # 顺子
    DOUBLE_STRAIGHT = 7  # 双顺
    TRIPLE_STRAIGHT = 8  # 三顺
    PLANE = 9            # 飞机（带翅膀不带牌）
    PLANE_WITH_WINGS = 10 # 飞机带单翅膀
    THREE_WITH_TWO = 11  # 三带二


@dataclass
class CardPattern:
    """牌型结构"""
    card_type: CardType
    main_value: int  # 主牌值（用于比较大小）
    cards: List[Card]  # 原始卡牌列表
    
    def __repr__(self):
        return f"{self.card_type.name}(value={self.main_value}, cards={len(self.cards)})"


class PatternAnalyzer:
    """牌型分析器"""
    
    @staticmethod
    def analyze(cards: List[Card]) -> Optional[CardPattern]:
        """分析一组卡牌返回牌型"""
        if not cards:
            return None
        
        # 按牌值排序
        sorted_cards = sorted(cards, key=lambda c: c.value, reverse=True)
        counts = {}
        for card in sorted_cards:
            counts[card.value] = counts.get(card.value, 0) + 1
        
        count_values = sorted(counts.keys(), reverse=True)
        count_buckets = {}
        for v in count_values:
            cnt = counts[v]
            if cnt not in count_buckets:
                count_buckets[cnt] = []
            count_buckets[cnt].append(v)
        
        # 分析各种牌型
        # 单张
        if len(cards) == 1:
            return CardPattern(CardType.SINGLE, sorted_cards[0].value, cards)
        
        # 对子
        if len(cards) == 2:
            if counts[count_values[0]] == 2:
                return CardPattern(CardType.PAIR, count_values[0], cards)
            # 火箭
            if len(count_values) == 2 and set(count_values) == {16, 17}:
                return CardPattern(CardType.ROCKET, 18, cards)
            return None
        
        # 三张
        if len(cards) == 3:
            if counts[count_values[0]] == 3:
                return CardPattern(CardType.TRIPLE, count_values[0], cards)
            return None
        
        # 三带二
        if len(cards) == 5:
            if 3 in count_buckets and 2 in count_buckets:
                if len(count_buckets[3]) == 1 and len(count_buckets[2]) == 1:
                    triple_val = count_buckets[3][0]
                    return CardPattern(CardType.THREE_WITH_TWO, triple_val, cards)
            # 顺子检查
            result = PatternAnalyzer._check_straight(sorted_cards, counts, 5)
            if result:
                return result
            return None
        
        # 炸弹
        if len(cards) == 4:
            if counts[count_values[0]] == 4:
                return CardPattern(CardType.BOMB, count_values[0], cards)
            return None
        
        # 更多牌型检查
        n = len(cards)
        
        # 顺子 (5张以上连续单牌)
        if n >= 5:
            result = PatternAnalyzer._check_straight(sorted_cards, counts, n)
            if result:
                return result
        
        # 双顺 (3对以上连续对子)
        if n >= 6 and n % 2 == 0:
            result = PatternAnalyzer._check_double_straight(count_values, counts, n // 2)
            if result:
                return result
        
        # 三顺 (2组以上连续三张)
        if n >= 6 and n % 3 == 0:
            result = PatternAnalyzer._check_triple_straight(count_values, counts, n // 3)
            if result:
                return result
        
        return None
    
    @staticmethod
    def _check_straight(sorted_cards: List[Card], counts: dict, required_len: int) -> Optional[CardPattern]:
        """检查顺子"""
        # 只考虑单张牌值
        single_values = [v for v, c in counts.items() if c == 1]
        single_values.sort(reverse=True)
        
        if len(single_values) < required_len:
            return None
        
        # 顺子不能包含2和王
        max_val = max(single_values)
        if max_val > 14:  # A (14) 是顺子最大的
            return None
        
        # 查找最长的顺子
        for i in range(len(single_values) - required_len + 1):
            is_straight = True
            for j in range(required_len - 1):
                if single_values[i + j] - single_values[i + j + 1] != 1:
                    is_straight = False
                    break
            if is_straight:
                # 取出顺子的牌
                straight_cards = []
                for card in sorted_cards:
                    if card.value in single_values[i:i+required_len] and card not in straight_cards:
                        straight_cards.append(card)
                        if len(straight_cards) == required_len:
                            break
                return CardPattern(CardType.STRAIGHT, single_values[i], straight_cards)
        
        return None
    
    @staticmethod
    def _check_double_straight(count_values: list, counts: dict, pairs_needed: int) -> Optional[CardPattern]:
        """检查双顺"""
        # 找出所有对子的值
        pair_values = [v for v in count_values if counts[v] >= 2]
        if len(pair_values) < pairs_needed:
            return None
        
        # 检查是否连续
        pair_values.sort(reverse=True)
        for i in range(len(pair_values) - pairs_needed + 1):
            is_straight = True
            for j in range(pairs_needed - 1):
                if pair_values[i + j] - pair_values[i + j + 1] != 1:
                    is_straight = False
                    break
            if is_straight:
                return CardPattern(CardType.DOUBLE_STRAIGHT, pair_values[i], [])
        
        return None
    
    @staticmethod
    def _check_triple_straight(count_values: list, counts: dict, triples_needed: int) -> Optional[CardPattern]:
        """检查三顺"""
        triple_values = [v for v in count_values if counts[v] >= 3]
        if len(triple_values) < triples_needed:
            return None
        
        triple_values.sort(reverse=True)
        for i in range(len(triple_values) - triples_needed + 1):
            is_straight = True
            for j in range(triples_needed - 1):
                if triple_values[i + j] - triple_values[i + j + 1] != 1:
                    is_straight = False
                    break
            if is_straight:
                return CardPattern(CardType.TRIPLE_STRAIGHT, triple_values[i], [])
        
        return None
    
    @staticmethod
    def compare(p1: CardPattern, p2: CardPattern) -> int:
        """比较两个牌型的大小
        返回: 1 p1 > p2, -1 p1 < p2, 0 相等
        """
        # 不同牌型之间的比较
        type_order = {
            CardType.SINGLE: 1, CardType.PAIR: 2, CardType.TRIPLE: 3,
            CardType.STRAIGHT: 4, CardType.DOUBLE_STRAIGHT: 5, CardType.TRIPLE_STRAIGHT: 6,
            CardType.PLANE: 7, CardType.PLANE_WITH_WINGS: 8, CardType.THREE_WITH_TWO: 9,
            CardType.BOMB: 10, CardType.ROCKET: 11
        }
        
        t1 = type_order.get(p1.card_type, 0)
        t2 = type_order.get(p2.card_type, 0)
        
        # 火箭最大
        if p1.card_type == CardType.ROCKET:
            return 1
        if p2.card_type == CardType.ROCKET:
            return -1
        
        # 炸弹比普通牌型大
        if p1.card_type == CardType.BOMB and t2 < 10:
            return 1
        if p2.card_type == CardType.BOMB and t1 < 10:
            return -1
        
        # 同类型比较
        if p1.card_type == p2.card_type:
            return 1 if p1.main_value > p2.main_value else (-1 if p1.main_value < p2.main_value else 0)
        
        # 不同牌型无法比较
        return 0
    
    @staticmethod
    def can_beat(patter: CardPattern, target: CardPattern) -> bool:
        """检查是否能打过目标牌型"""
        result = PatternAnalyzer.compare(patter, target)
        return result > 0


class PatternValidator:
    """牌型验证器"""
    
    @staticmethod
    def is_valid(cards: List[Card]) -> bool:
        """验证是否是有效的牌型"""
        return PatternAnalyzer.analyze(cards) is not None


if __name__ == "__main__":
    from .cards import CardUtils, Suit
    
    # 测试牌型分析
    cards = [Card(Suit.HEART, Rank.FIVE), Card(Suit.SPADE, Rank.SIX), 
             Card(Suit.DIAMOND, Rank.SEVEN), Card(Suit.CLUB, Rank.EIGHT),
             Card(Suit.HEART, Rank.NINE)]
    pattern = PatternAnalyzer.analyze(cards)
    print(f"顺子测试: {pattern}")