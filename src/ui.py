"""
斗地主游戏图形用户界面
使用pygame库实现
"""

import pygame
import sys
from typing import List, Optional, Tuple

from .cards import Card, CardUtils, Suit, Rank
from .game import LandlordsGame, Player, PlayerPosition, TurnResult, GameAction
from .game_types import CardType, CardPattern, PatternAnalyzer


# 颜色定义
class Colors:
    """颜色常量"""
    GREEN = (50, 150, 50)
    DARK_GREEN = (30, 100, 30)
    LIGHT_GREEN = (80, 180, 80)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    RED = (200, 50, 50)
    BLUE = (50, 100, 200)
    YELLOW = (255, 255, 0)
    GOLD = (255, 215, 0)
    CARD_BG = (240, 240, 240)
    CARD_BORDER = (100, 100, 100)


class CardRenderer:
    """卡牌渲染器"""
    
    CARD_WIDTH = 80
    CARD_HEIGHT = 120
    FONT_SIZE = 20
    
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.font = pygame.font.SysFont('SimHei', self.FONT_SIZE)
        self.small_font = pygame.font.SysFont('SimHei', 14)
    
    def draw_card(self, card: Card, x: int, y: int, selected: bool = False, face_down: bool = False):
        """绘制单张卡牌"""
        rect = pygame.Rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT)
        
        # 绘制背景
        bg_color = Colors.GOLD if selected else Colors.CARD_BG
        pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
        pygame.draw.rect(self.screen, Colors.CARD_BORDER, rect, 2, border_radius=8)
        
        if face_down:
            # 背面
            pygame.draw.rect(self.screen, Colors.DARK_GREEN, 
                          (x+5, y+5, self.CARD_WIDTH-10, self.CARD_HEIGHT-10), border_radius=4)
            # 绘制花纹
            for i in range(3):
                for j in range(3):
                    cx = x + 20 + i * 20
                    cy = y + 30 + j * 30
                    pygame.draw.circle(self.screen, Colors.GOLD, (cx, cy), 5)
        else:
            # 正面
            self._draw_card_content(card, x, y)
    
    def _draw_card_content(self, card: Card, x: int, y: int):
        """绘制卡牌内容"""
        # 花色颜色
        if card.suit in (Suit.HEART, Suit.DIAMOND):
            color = Colors.RED
        else:
            color = Colors.BLACK
        
        # 牌值
        rank_text = self.font.render(card.rank_symbol, True, color)
        self.screen.blit(rank_text, (x + 8, y + 8))
        
        # 花色符号
        suit_text = self.small_font.render(card.suit_symbol, True, color)
        self.screen.blit(suit_text, (x + 12, y + 32))
        
        # 中间的大花色符号
        large_suit = pygame.font.SysFont('SimHei', 40).render(card.suit_symbol, True, color)
        suit_rect = large_suit.get_rect(center=(x + self.CARD_WIDTH//2, y + self.CARD_HEIGHT//2))
        self.screen.blit(large_suit, suit_rect)
        
        # 底角
        suit_text_bottom = self.small_font.render(card.suit_symbol, True, color)
        self.screen.blit(suit_text_bottom, (x + self.CARD_WIDTH - 20, y + self.CARD_HEIGHT - 25))
        
        rank_bottom = self.font.render(card.rank_symbol, True, color)
        rank_rect = rank_bottom.get_rect(bottomright=(x + self.CARD_WIDTH - 8, y + self.CARD_HEIGHT - 8))
        self.screen.blit(rank_bottom, rank_rect)
    
    def draw_back(self, x: int, y: int):
        """绘制背面卡牌"""
        self.draw_card(Card(Suit.SPADE, Rank.THREE), x, y, face_down=True)
    
    def draw_card_list(self, cards: List[Card], x: int, y: int, selected_indices: List[int] = None, vertical: bool = False):
        """绘制卡牌列表"""
        if selected_indices is None:
            selected_indices = []
        
        if vertical:
            for i, card in enumerate(cards):
                self.draw_card(card, x, y + i * (self.CARD_HEIGHT + 5), i in selected_indices)
        else:
            for i, card in enumerate(cards):
                self.draw_card(card, x + i * (self.CARD_WIDTH + 5), y, i in selected_indices)


class LandlordsUI:
    """斗地主游戏界面"""
    
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("斗地主 - Landlords Card Game")
        
        self.card_renderer = CardRenderer(self.screen)
        self.game = LandlordsGame()
        self.clock = pygame.time.Clock()
        
        # UI状态
        self.selected_cards: List[int] = []  # 选中的卡牌索引
        self.ai_thinking = False
        self.message = ""
        self.message_timer = 0
        self.phase = "start"  # start, bidding, playing, game_over
        
        # 按钮
        self.buttons = []
        self._init_buttons()
    
    def _init_buttons(self):
        """初始化按钮"""
        self.buttons = [
            {"text": "开始游戏", "rect": pygame.Rect(500, 350, 200, 60), "action": "start"},
            {"text": "叫地主", "rect": pygame.Rect(400, 500, 150, 50), "action": "bid_yes"},
            {"text": "不叫", "rect": pygame.Rect(650, 500, 150, 50), "action": "bid_no"},
            {"text": "出牌", "rect": pygame.Rect(400, 650, 150, 50), "action": "play"},
            {"text": "不出", "rect": pygame.Rect(650, 650, 150, 50), "action": "pass"},
        ]
    
    def _draw_button(self, button: dict, hover: bool = False):
        """绘制按钮"""
        color = Colors.GREEN if hover else Colors.DARK_GREEN
        pygame.draw.rect(self.screen, color, button["rect"], border_radius=10)
        pygame.draw.rect(self.screen, Colors.GOLD, button["rect"], 2, border_radius=10)
        
        font = pygame.font.SysFont('SimHei', 24)
        text = font.render(button["text"], True, Colors.WHITE)
        text_rect = text.get_rect(center=button["rect"].center)
        self.screen.blit(text, text_rect)
    
    def _get_button_at_pos(self, pos: Tuple[int, int]) -> Optional[dict]:
        """获取指定位置的按钮"""
        for button in self.buttons:
            if button["rect"].collidepoint(pos):
                return button
        return None
    
    def draw_background(self):
        """绘制背景"""
        self.screen.fill(Colors.GREEN)
        
        # 绘制桌面区域
        pygame.draw.ellipse(self.screen, Colors.DARK_GREEN, 
                          (100, 100, self.WINDOW_WIDTH - 200, self.WINDOW_HEIGHT - 200))
    
    def draw_player_area(self, player_idx: int, x: int, y: int, horizontal: bool = True):
        """绘制玩家区域"""
        player = self.game.players[player_idx]
        is_current = (self.game.current_turn == player_idx)
        
        # 玩家名称和状态
        font = pygame.font.SysFont('SimHei', 20)
        
        # 背景框
        bg_rect = pygame.Rect(x, y, 250, 40)
        bg_color = Colors.GOLD if is_current else Colors.DARK_GREEN
        pygame.draw.rect(self.screen, bg_color, bg_rect, border_radius=8)
        
        # 名称
        name_text = f"{player.name} ({len(player.cards)}张)"
        text = font.render(name_text, True, Colors.WHITE)
        self.screen.blit(text, (x + 10, y + 10))
        
        # 地主标识
        if player.is_landlord:
            lord_text = font.render("地主", True, Colors.RED)
            self.screen.blit(lord_text, (x + 180, y + 10))
    
    def draw_landlord_cards(self):
        """绘制底牌"""
        font = pygame.font.SysFont('SimHei', 18)
        text = font.render("底牌:", True, Colors.WHITE)
        self.screen.blit(text, (500, 20))
        
        for i, card in enumerate(self.game.landlord_cards):
            self.card_renderer.draw_card(card, 550 + i * 90, 10, face_down=False)
    
    def draw_player_cards(self, player_idx: int):
        """绘制玩家手牌"""
        player = self.game.players[player_idx]
        cards = player.cards
        
        if player_idx == 1:  # 玩家在底部
            y = self.WINDOW_HEIGHT - CardRenderer.CARD_HEIGHT - 30
            x = (self.WINDOW_WIDTH - len(cards) * 85) // 2
            
            for i, card in enumerate(cards):
                y_offset = -20 if i in self.selected_cards else 0
                self.card_renderer.draw_card(card, x + i * 85, y + y_offset, i in self.selected_cards)
    
    def draw_message(self):
        """绘制消息"""
        if self.message:
            font = pygame.font.SysFont('SimHei', 28)
            text = font.render(self.message, True, Colors.YELLOW)
            text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 150))
            
            # 背景
            bg_rect = text_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, Colors.BLACK, bg_rect, border_radius=10)
            pygame.draw.rect(self.screen, Colors.GOLD, bg_rect, 2, border_radius=10)
            
            self.screen.blit(text, text_rect)
    
    def handle_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """处理点击事件"""
        # 检查按钮点击
        button = self._get_button_at_pos(pos)
        if button:
            return button["action"]
        
        # 检查卡牌点击（玩家区域）
        if self.game.current_turn == 1:  # 玩家回合
            player = self.game.players[1]
            y = self.WINDOW_HEIGHT - CardRenderer.CARD_HEIGHT - 30
            x = (self.WINDOW_WIDTH - len(player.cards) * 85) // 2
            
            for i, card in enumerate(player.cards):
                card_x = x + i * 85
                card_rect = pygame.Rect(card_x, y - 20, 80, CardRenderer.CARD_HEIGHT + 20)
                if card_rect.collidepoint(pos):
                    if i in self.selected_cards:
                        self.selected_cards.remove(i)
                    else:
                        self.selected_cards.append(i)
                    return None
        
        return None
    
    def show_start_screen(self):
        """显示开始界面"""
        self.draw_background()
        
        # 标题
        font = pygame.font.SysFont('SimHei', 60)
        title = font.render("斗 地 主", True, Colors.GOLD)
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # 副标题
        font = pygame.font.SysFont('SimHei', 24)
        subtitle = font.render("Landlords Card Game", True, Colors.WHITE)
        subtitle_rect = subtitle.get_rect(center=(self.WINDOW_WIDTH // 2, 210))
        self.screen.blit(subtitle, subtitle_rect)
        
        # 按钮
        for button in self.buttons[:1]:  # 只显示开始游戏按钮
            self._draw_button(button, button["rect"].collidepoint(pygame.mouse.get_pos()))
        
        # 说明
        font = pygame.font.SysFont('SimHei', 18)
        info = "点击\"开始游戏\"开始新游戏\n玩家(底部)对抗两个电脑玩家"
        lines = info.split('\n')
        for i, line in enumerate(lines):
            text = font.render(line, True, Colors.LIGHT_GREEN)
            self.screen.blit(text, (self.WINDOW_WIDTH // 2 - text.get_width() // 2, 450 + i * 30))
        
        pygame.display.flip()
    
    def show_bidding_phase(self):
        """显示叫地主阶段"""
        self.draw_background()
        
        # 绘制玩家区域
        self.draw_player_area(0, 50, 50, horizontal=True)
        self.draw_player_area(2, self.WINDOW_WIDTH - 300, 50, horizontal=True)
        self.draw_player_area(1, self.WINDOW_WIDTH // 2 - 125, self.WINDOW_HEIGHT - 100, horizontal=False)
        
        # 绘制底牌（背面）
        font = pygame.font.SysFont('SimHei', 18)
        text = font.render("底牌(3张):", True, Colors.WHITE)
        self.screen.blit(text, (self.WINDOW_WIDTH // 2 - 100, self.WINDOW_HEIGHT // 2 - 60))
        
        for i in range(3):
            self.card_renderer.draw_back(self.WINDOW_WIDTH // 2 - 100 + i * 90, self.WINDOW_HEIGHT // 2 - 40)
        
        # 显示按钮
        self._draw_button(self.buttons[1])  # 叫地主
        self._draw_button(self.buttons[2])  # 不叫
        
        # 当前提示
        current_player = self.game.get_player_at_turn(self.game.current_turn)
        font = pygame.font.SysFont('SimHei', 22)
        tip = f"{current_player.name}请叫地主"
        text = font.render(tip, True, Colors.YELLOW)
        self.screen.blit(text, (self.WINDOW_WIDTH // 2 - text.get_width() // 2, self.WINDOW_HEIGHT // 2 + 150))
        
        pygame.display.flip()
    
    def show_playing_phase(self):
        """显示游戏阶段"""
        self.draw_background()
        
        # 绘制三个玩家区域
        self.draw_player_area(0, 50, 50, horizontal=True)
        self.draw_player_area(2, self.WINDOW_WIDTH - 300, 50, horizontal=True)
        self.draw_player_area(1, self.WINDOW_WIDTH // 2 - 125, self.WINDOW_HEIGHT - 100, horizontal=False)
        
        # 绘制底牌
        self.draw_landlord_cards()
        
        # 绘制玩家手牌
        self.draw_player_cards(1)
        
        # 绘制出牌区域
        self._draw_last_play()
        
        # 显示出牌按钮
        if self.game.current_turn == 1:
            if self.game.last_play and self.game.last_play.player != self.game.players[1]:
                self._draw_button(self.buttons[4])  # 不出
            if self.selected_cards:
                self._draw_button(self.buttons[3])  # 出牌
        
        # 提示
        font = pygame.font.SysFont('SimHei', 20)
        current = self.game.players[self.game.current_turn]
        tip = f"轮到: {current.name}"
        text = font.render(tip, True, Colors.YELLOW)
        self.screen.blit(text, (self.WINDOW_WIDTH // 2 - text.get_width() // 2, self.WINDOW_HEIGHT // 2 - 150))
        
        pygame.display.flip()
    
    def _draw_last_play(self):
        """绘制上次出牌"""
        if not self.game.last_play or self.game.last_play.action == GameAction.PASS:
            return
        
        result = self.game.last_play
        cards = result.cards
        
        # 确定绘制位置
        if result.player.position == PlayerPosition.PEASANT1:
            x, y = 50, 150
        elif result.player.position == PlayerPosition.PEASANT2:
            x, y = self.WINDOW_WIDTH - 350, 150
        else:
            return
        
        # 绘制卡牌
        for i, card in enumerate(cards):
            self.card_renderer.draw_card(card, x + i * 85, y)
    
    def show_game_over(self):
        """显示游戏结束界面"""
        self.draw_background()
        
        winner = self.game.get_winner()
        font = pygame.font.SysFont('SimHei', 40)
        
        if winner:
            msg = f"{winner.name}获胜!"
            color = Colors.RED if winner.is_landlord else Colors.BLUE
        else:
            msg = "游戏结束!"
            color = Colors.YELLOW
        
        text = font.render(msg, True, color)
        text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, 200))
        self.screen.blit(text, text_rect)
        
        # 重新开始按钮
        self._draw_button(self.buttons[0])
        
        pygame.display.flip()
    
    def run(self):
        """主循环"""
        running = True
        auto_play_timer = 0
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    action = self.handle_click(event.pos)
                    if action == "start":
                        self._start_game()
                    elif action == "bid_yes":
                        self._process_bid(True)
                    elif action == "bid_no":
                        self._process_bid(False)
                    elif action == "play":
                        self._player_play_cards()
                    elif action == "pass":
                        self._player_pass()
            
            # 根据游戏阶段渲染
            if self.phase == "start":
                self.show_start_screen()
            elif self.phase == "bidding":
                self.show_bidding_phase()
            elif self.phase == "playing":
                self.show_playing_phase()
                # AI回合
                if self.game.current_turn != 1 and not self.ai_thinking:
                    self.ai_thinking = True
                    auto_play_timer = 30  # 延迟以显示AI思考
            elif self.phase == "game_over":
                self.show_game_over()
            
            # AI自动出牌计时器
            if self.phase == "playing" and self.ai_thinking:
                auto_play_timer -= 1
                if auto_play_timer <= 0:
                    self._ai_turn()
                    self.ai_thinking = False
            
            # 消息定时器
            if self.message_timer > 0:
                self.message_timer -= 1
                if self.message_timer <= 0:
                    self.message = ""
            
            pygame.display.flip()
            self.clock.tick(30)
        
        pygame.quit()
    
    def _start_game(self):
        """开始新游戏"""
        self.game.initialize()
        self.game.deal_cards()
        self.selected_cards = []
        self.phase = "bidding"
        self.game.current_turn = 0  # 从第一个玩家开始叫地主
    
    def _process_bid(self, is_bid: bool):
        """处理叫地主"""
        if is_bid:
            # 叫地主成功
            self.game.set_landlord(self.game.current_turn)
            self.message = f"{self.game.current_landlord.name}成为地主!"
            self.message_timer = 60
            self.phase = "playing"
        else:
            # 下一家
            self.game.current_turn = (self.game.current_turn + 1) % 3
            
            # 简单策略：随机决定是否叫地主
            # 这里可以让AI自动叫地主
            if self.game.current_turn != 1:  # AI
                self._ai_bid()
    
    def _ai_bid(self):
        """AI叫地主"""
        import random
        player = self.game.players[self.game.current_turn]
        
        # AI策略：牌好就叫
        good_cards = sum(1 for c in player.cards if c.value >= 15)  # 有王或2
        if good_cards >= 2 or len(player.cards) > 0:
            if random.random() > 0.3:  # 70%概率叫
                self.game.set_landlord(self.game.current_turn)
                self.message = f"{self.game.current_landlord.name}成为地主!"
                self.message_timer = 60
                self.phase = "playing"
                return
        
        # 不叫
        self.game.current_turn = (self.game.current_turn + 1) % 3
        if self.game.current_turn == 0:  # 回到第一个玩家重新开始叫地主流程
            self._ai_bid()  # 递归处理
    
    def _player_play_cards(self):
        """玩家出牌"""
        if not self.selected_cards:
            return
        
        selected_cards = [self.game.players[1].cards[i] for i in sorted(self.selected_cards)]
        
        # 检查是否能出
        if self.game.can_play_cards(self.game.players[1], selected_cards):
            result = self.game.play_cards(self.game.players[1], selected_cards)
            self.selected_cards = []
            self._check_game_end()
        else:
            self.message = "不能出这些牌!"
            self.message_timer = 30
    
    def _player_pass(self):
        """玩家跳过"""
        if self.game.last_play and self.game.last_play.player == self.game.players[1]:
            return  # 不能跳过
        
        self.game.pass_turn(self.game.players[1])
        self._advance_turn()
    
    def _ai_turn(self):
        """AI出牌"""
        current = self.game.get_player_at_turn(self.game.current_turn)
        if not current or current.position == PlayerPosition.LANDLORD and current.is_landlord:
            pass
        
        cards = self.game.get_smart_play(current, is_ai=True)
        
        if cards:
            result = self.game.play_cards(current, cards)
            self._check_game_end()
        else:
            self.game.pass_turn(current)
        
        self._advance_turn()
    
    def _advance_turn(self):
        """进入下一回合"""
        self.game.next_turn()
        
        # 检查游戏结束
        winner = self.game.get_winner()
        if winner:
            self.phase = "game_over"
    
    def _check_game_end(self):
        """检查游戏结束"""
        winner = self.game.get_winner()
        if winner:
            self.phase = "game_over"


def main():
    """主函数"""
    game = LandlordsUI()
    game.run()


if __name__ == "__main__":
    main()