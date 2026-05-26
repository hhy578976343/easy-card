"""
卡牌模块 - 定义卡牌的数据结构和基本操作
"""

from enum import Enum
from typing import List, Tuple, Optional


class Suit(Enum):
    """花色枚举"""
    SPADE = 0    # 黑桃 ♠
    HEART = 1    # 红心 ♥
    CLUB = 2     # 梅花 ♣
    DIAMOND = 3  # 方块 ♦


class Rank(Enum):
    """牌值枚举 - 从3到王"""
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
    TWO = 15
    LITTLE_JOKER = 16   # 小王
    BIG_JOKER = 17      # 大王


class Card:
    """卡牌类"""
    
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
    
    @property
    def value(self) -> int:
        """卡牌的实际价值（用于排序和比较）"""
        return self.rank.value
    
    @property
    def suit_symbol(self) -> str:
        """花色符号"""
        symbols = {Suit.SPADE: '♠', Suit.HEART: '♥', Suit.CLUB: '♣', Suit.DIAMOND: '♦'}
        return symbols[self.suit]
    
    @property
    def rank_symbol(self) -> str:
        """牌值符号"""
        rank_symbols = {
            Rank.THREE: '3', Rank.FOUR: '4', Rank.FIVE: '5',
            Rank.SIX: '6', Rank.SEVEN: '7', Rank.EIGHT: '8',
            Rank.NINE: '9', Rank.TEN: '10', Rank.JACK: 'J',
            Rank.QUEEN: 'Q', Rank.KING: 'K', Rank.ACE: 'A',
            Rank.TWO: '2', Rank.LITTLE_JOKER: 'joker',
            Rank.BIG_JOKER: 'JOKER'
        }
        return rank_symbols.get(self.rank, str(self.rank.value))
    
    @property
    def display_name(self) -> str:
        """显示名称"""
        if self.rank in (Rank.LITTLE_JOKER, Rank.BIG_JOKER):
            return self.rank_symbol.upper() if self.rank == Rank.BIG_JOKER else self.rank_symbol
        return f"{self.suit_symbol}{self.rank_symbol}"
    
    def __repr__(self):
        return self.display_name
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank
    
    def __hash__(self):
        return hash((self.suit, self.rank))


class CardUtils:
    """卡牌工具类"""
    
    @staticmethod
    def create_standard_deck() -> List[Card]:
        """创建一副标准的54张牌"""
        cards = []
        # 52张普通牌
        for suit in Suit:
            for rank in [Rank.THREE, Rank.FOUR, Rank.FIVE, Rank.SIX, Rank.SEVEN,
                        Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN,
                        Rank.KING, Rank.ACE, Rank.TWO]:
                cards.append(Card(suit, rank))
        # 2张王牌
        cards.append(Card(Suit.SPADE, Rank.LITTLE_JOKER))  # 小王
        cards.append(Card(Suit.SPADE, Rank.BIG_JOKER))      # 大王
        return cards
    
    @staticmethod
    def sort_cards(cards: List[Card], descending: bool = True) -> List[Card]:
        """排序卡牌，默认按值降序"""
        return sorted(cards, key=lambda c: c.value, reverse=descending)
    
    @staticmethod
    def group_by_rank(cards: List[Card]) -> dict:
        """按牌值分组"""
        groups = {}
        for card in cards:
            if card.value not in groups:
                groups[card.value] = []
            groups[card.value].append(card)
        return groups
    
    @staticmethod
    def count_by_rank(cards: List[Card]) -> dict:
        """统计每个牌值的数量"""
        counts = {}
        for card in cards:
            counts[card.value] = counts.get(card.value, 0) + 1
        return counts


if __name__ == "__main__":
    # 测试卡牌创建
    deck = CardUtils.create_standard_deck()
    print(f"创建了 {len(deck)} 张牌")
    print("牌堆示例:", deck[:5])