"""
斗地主游戏图形用户界面 - 欢乐斗地主风格
使用pygame库实现
"""

import pygame
import sys
from typing import List, Optional, Tuple, Dict

from .cards import Card, CardUtils, Suit, Rank
from .game import LandlordsGame, Player, PlayerPosition, TurnResult, GameAction
from .game_types import CardType, CardPattern, PatternAnalyzer
from .score import ScoreManager, PlayerScore


# 颜色定义 - 欢乐斗地主风格
class Colors:
    """颜色常量"""
    # 主色调
    GREEN = (50, 150, 50)
    DARK_GREEN = (30, 100, 30)
    LIGHT_GREEN = (80, 180, 80)
    
    # 界面色
    BROWN = (139, 90, 43)
    GOLD = (255, 215, 0)
    DARK_GOLD = (184, 134, 11)
    CREAM = (255, 243, 224)
    
    # 文字色
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    
    # 特殊色
    RED = (200, 50, 50)
    BLUE = (50, 100, 200)
    YELLOW = (255, 255, 0)
    PINK = (255, 182, 193)
    PURPLE = (128, 0, 128)
    
    # 卡牌色
    CARD_BG = (255, 255, 255)
    CARD_BORDER = (80, 80, 80)
    CARD_BACK = (0, 100, 0)
    
    # 按钮色
    BTN_GREEN = (34, 139, 34)
    BTN_GREEN_HOVER = (50, 205, 50)
    BTN_RED = (178, 34, 34)
    BTN_RED_HOVER = (220, 20, 60)


class CardRenderer:
    """卡牌渲染器 - 欢乐斗地主风格"""
    
    CARD_WIDTH = 75
    CARD_HEIGHT = 110
    FONT_SIZE = 18
    
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.font = pygame.font.SysFont('SimHei', self.FONT_SIZE)
        self.small_font = pygame.font.SysFont('SimHei', 12)
        self.large_font = pygame.font.SysFont('SimHei', 36)
    
    def draw_card(self, card: Card, x: int, y: int, selected: bool = False, face_down: bool = False):
        """绘制单张卡牌"""
        rect = pygame.Rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT)
        
        # 选中效果
        if selected:
            y -= 15
        
        # 绘制背景
        if face_down:
            self._draw_card_back(x, y)
        else:
            self._draw_card_front(card, x, y)
        
        # 选中时的发光效果
        if selected:
            pygame.draw.rect(self.screen, Colors.YELLOW, rect.move(0, -15), 3, border_radius=6)
    
    def _draw_card_back(self, x: int, y: int):
        """绘制卡牌背面"""
        rect = pygame.Rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT)
        
        # 白色背景
        pygame.draw.rect(self.screen, Colors.CARD_BG, rect, border_radius=8)
        pygame.draw.rect(self.screen, Colors.CARD_BORDER, rect, 2, border_radius=8)
        
        # 深绿色填充
        inner_rect = pygame.Rect(x+4, y+4, self.CARD_WIDTH-8, self.CARD_HEIGHT-8)
        pygame.draw.rect(self.screen, Colors.DARK_GREEN, inner_rect, border_radius=4)
        
        # 花纹图案
        center_x = x + self.CARD_WIDTH // 2
        center_y = y + self.CARD_HEIGHT // 2
        
        # 绘制菱形花纹
        for i in range(-1, 2):
            for j in range(-1, 2):
                cx = center_x + i * 20
                cy = center_y + j * 25
                if 0 <= cx - x <= self.CARD_WIDTH and 0 <= cy - y <= self.CARD_HEIGHT:
                    pygame.draw.circle(self.screen, Colors.GOLD, (cx, cy), 4)
        
        # 中间大花纹
        pygame.draw.circle(self.screen, Colors.GOLD, (center_x, center_y), 15, 2)
    
    def _draw_card_front(self, card: Card, x: int, y: int):
        """绘制卡牌正面"""
        rect = pygame.Rect(x, y, self.CARD_WIDTH, self.CARD_HEIGHT)
        
        # 白色背景
        pygame.draw.rect(self.screen, Colors.CARD_BG, rect, border_radius=8)
        pygame.draw.rect(self.screen, Colors.CARD_BORDER, rect, 2, border_radius=8)
        
        # 花色颜色
        if card.suit in (Suit.HEART, Suit.DIAMOND):
            color = Colors.RED
        else:
            color = Colors.BLACK
        
        # 左上角
        rank_text = self.font.render(card.rank_symbol, True, color)
        self.screen.blit(rank_text, (x + 6, y + 4))
        
        suit_small = self.small_font.render(card.suit_symbol, True, color)
        self.screen.blit(suit_small, (x + 8, y + 24))
        
        # 中间大花色
        large_suit = self.large_font.render(card.suit_symbol, True, color)
        suit_rect = large_suit.get_rect(center=(x + self.CARD_WIDTH//2, y + self.CARD_HEIGHT//2 + 5))
        self.screen.blit(large_suit, suit_rect)
        
        # 右下角（旋转180度显示）
        rank_bottom = self.font.render(card.rank_symbol, True, color)
        rank_rect = rank_bottom.get_rect(bottomright=(x + self.CARD_WIDTH - 6, y + self.CARD_HEIGHT - 4))
        self.screen.blit(rank_bottom, rank_rect)
        
        suit_bottom = self.small_font.render(card.suit_symbol, True, color)
        self.screen.blit(suit_bottom, (x + self.CARD_WIDTH - 20, y + self.CARD_HEIGHT - 22))
    
    def draw_back(self, x: int, y: int):
        """绘制背面卡牌"""
        self._draw_card_back(x, y)


class Button:
    """按钮类"""
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple, hover_color: Tuple):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        
        # 按钮边框
        pygame.draw.rect(screen, Colors.WHITE, self.rect, 2, border_radius=10)
        
        font = pygame.font.SysFont('SimHei', 22)
        text_surf = font.render(self.text, True, Colors.WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def check_hover(self, pos: Tuple[int, int]):
        self.is_hovered = self.rect.collidepoint(pos)


class LandlordsUI:
    """斗地主游戏界面 - 欢乐斗地主风格"""
    
    WINDOW_WIDTH = 1100
    WINDOW_HEIGHT = 700
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("欢乐斗地主 - Happy Landlords")
        
        self.card_renderer = CardRenderer(self.screen)
        self.game = LandlordsGame()
        self.score_manager = ScoreManager()
        self.clock = pygame.time.Clock()
        
        # UI状态
        self.selected_cards: List[int] = []
        self.ai_thinking = False
        self.message = ""
        self.message_timer = 0
        self.phase = "start"  # start, select_rounds, bidding, playing, round_end, game_over
        self.total_rounds = 3  # 默认3回合
        self.current_round = 0
        
        # 按钮
        self.buttons: Dict[str, Button] = {}
        self._init_buttons()
        
        # 玩家积分
        self.player_scores = [1000, 1000, 1000]
        self.round_score_data = None
    
    def _init_buttons(self):
        """初始化按钮"""
        center_x = self.WINDOW_WIDTH // 2
        center_y = self.WINDOW_HEIGHT // 2
        
        # 开始界面按钮
        self.buttons = {
            'start': Button(center_x - 100, center_y + 80, 200, 55, "开始游戏", Colors.BTN_GREEN, Colors.BTN_GREEN_HOVER),
            'round_3': Button(center_x - 230, center_y - 30, 140, 50, "3回合", Colors.BTN_GREEN, Colors.BTN_GREEN_HOVER),
            'round_5': Button(center_x - 70, center_y - 30, 140, 50, "5回合", Colors.BTN_GREEN, Colors.BTN_GREEN_HOVER),
            'round_10': Button(center_x + 90, center_y - 30, 140, 50, "10回合", Colors.BTN_GREEN, Colors.BTN_GREEN_HOVER),
            'bid_yes': Button(center_x - 160, center_y + 100, 140, 50, "叫地主", Colors.BTN_RED, Colors.BTN_RED_HOVER),
            'bid_no': Button(center_x + 20, center_y + 100, 140, 50, "不叫", Colors.GRAY, Colors.LIGHT_GRAY),
            'play': Button(center_x - 160, center_y + 80, 140, 50, "出牌", Colors.BTN_GREEN, Colors.BTN_GREEN_HOVER),
            'pass': Button(center_x + 20, center_y + 80, 140, 50, "不出", Colors.GRAY, Colors.LIGHT_GRAY),
            'continue': Button(center_x - 100, center_y + 80, 200, 55, "继续", Colors.BTN_GREEN, Colors.BTN_GREEN_HOVER),
        }
    
    def draw_background(self):
        """绘制背景 - 欢乐斗地主风格"""
        # 主背景渐变
        for i in range(self.WINDOW_HEIGHT):
            ratio = i / self.WINDOW_HEIGHT
            r = int(50 + ratio * 20)
            g = int(150 + ratio * 30)
            b = int(50 + ratio * 20)
            pygame.draw.line(self.screen, (r, g, b), (0, i), (self.WINDOW_WIDTH, i))
        
        # 桌面区域
        table_rect = pygame.Rect(60, 80, self.WINDOW_WIDTH - 120, self.WINDOW_HEIGHT - 160)
        pygame.draw.ellipse(self.screen, Colors.DARK_GREEN, table_rect)
        pygame.draw.ellipse(self.screen, Colors.BROWN, table_rect, 4)
        
        # 装饰角落
        corner_size = 30
        for x, y in [(80, 100), (self.WINDOW_WIDTH - 80 - corner_size, 100), 
                     (80, self.WINDOW_HEIGHT - 100 - corner_size), 
                     (self.WINDOW_WIDTH - 80 - corner_size, self.WINDOW_HEIGHT - 100 - corner_size)]:
            pygame.draw.rect(self.screen, Colors.GOLD, (x, y, corner_size, corner_size), border_radius=5)
    
    def draw_player_info(self, player_idx: int, x: int, y: int):
        """绘制玩家信息面板"""
        player = self.game.players[player_idx]
        is_current = (self.game.current_turn == player_idx) and self.phase == "playing"
        
        # 面板背景
        panel_width = 180
        panel_height = 70
        panel_rect = pygame.Rect(x, y, panel_width, panel_height)
        
        # 高亮当前玩家
        if is_current:
            pygame.draw.rect(self.screen, Colors.GOLD, panel_rect, border_radius=10)
        else:
            pygame.draw.rect(self.screen, (50, 50, 50), panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, Colors.WHITE, panel_rect, 2, border_radius=10)
        
        # 玩家名称
        font = pygame.font.SysFont('SimHei', 18)
        name = player.name
        if player.is_landlord:
            name += " 房东"
        name_text = font.render(name, True, Colors.WHITE)
        self.screen.blit(name_text, (x + 10, y + 8))
        
        # 积分
        score = self.player_scores[player_idx]
        score_text = font.render(f"积分: {score}", True, Colors.YELLOW)
        self.screen.blit(score_text, (x + 10, y + 35))
        
        # 卡牌数量
        count_text = font.render(f"{len(player.cards)}张", True, Colors.LIGHT_GRAY)
        self.screen.blit(count_text, (x + 100, y + 8))
    
    def draw_landlord_cards(self):
        """绘制底牌"""
        if not self.game.landlord_cards:
            return
            
        font = pygame.font.SysFont('SimHei', 16)
        text = font.render("底牌:", True, Colors.WHITE)
        self.screen.blit(text, (self.WINDOW_WIDTH // 2 - 80, 90))
        
        for i, card in enumerate(self.game.landlord_cards):
            self.card_renderer.draw_card(card, self.WINDOW_WIDTH // 2 - 80 + i * 85, 85)
    
    def draw_player_cards(self):
        """绘制玩家手牌（底部）"""
        player = self.game.players[1]
        if not player.cards:
            return
            
        y = self.WINDOW_HEIGHT - self.card_renderer.CARD_HEIGHT - 50
        total_width = len(player.cards) * 80
        x = (self.WINDOW_WIDTH - total_width) // 2
        
        for i, card in enumerate(player.cards):
            y_offset = -15 if i in self.selected_cards else 0
            self.card_renderer.draw_card(card, x + i * 80, y + y_offset, i in self.selected_cards)
    
    def draw_last_play_cards(self):
        """绘制上家出的牌"""
        if not self.game.last_play or self.game.last_play.action == GameAction.PASS:
            return
        
        result = self.game.last_play
        cards = result.cards
        
        # 确定位置（左侧或右侧）
        if result.player.player_id == 0:
            x, y = 200, 250
        else:
            x, y = self.WINDOW_WIDTH - 200 - len(cards) * 80, 250
        
        # 绘制标签
        font = pygame.font.SysFont('SimHei', 14)
        label = font.render(f"{result.player.name}出牌:", True, Colors.YELLOW)
        self.screen.blit(label, (x, y - 20))
        
        # 绘制卡牌
        for i, card in enumerate(cards):
            self.card_renderer.draw_card(card, x + i * 80, y)
    
    def draw_score_board(self):
        """绘制积分面板"""
        font = pygame.font.SysFont('SimHei', 16)
        
        # 回合信息
        round_text = font.render(f"回合 {self.current_round + 1}/{self.total_rounds}", True, Colors.WHITE)
        self.screen.blit(round_text, (self.WINDOW_WIDTH // 2 - 50, 30))
        
        # 炸弹和王炸统计
        if self.game.bombs_count > 0:
            bomb_text = font.render(f"炸弹 x{self.game.bombs_count}", True, Colors.RED)
            self.screen.blit(bomb_text, (self.WINDOW_WIDTH - 120, 30))
        
        if self.game.rockets_count > 0:
            rocket_text = font.render(f"王炸 x{self.game.rockets_count}", True, Colors.PURPLE)
            self.screen.blit(rocket_text, (self.WINDOW_WIDTH - 220, 30))
    
    def draw_message(self):
        """绘制消息提示"""
        if self.message:
            font = pygame.font.SysFont('SimHei', 28)
            text = font.render(self.message, True, Colors.YELLOW)
            text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 100))
            
            # 背景
            bg_rect = text_rect.inflate(40, 20)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect, border_radius=10)
            pygame.draw.rect(self.screen, Colors.GOLD, bg_rect, 2, border_radius=10)
            
            self.screen.blit(text, text_rect)
    
    def draw_round_result(self):
        """绘制回合结算"""
        if not self.round_score_data:
            return
        
        # 半透明遮罩
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # 结算面板
        panel_w, panel_h = 500, 350
        panel_x = (self.WINDOW_WIDTH - panel_w) // 2
        panel_y = (self.WINDOW_HEIGHT - panel_h) // 2
        
        pygame.draw.rect(self.screen, (50, 50, 50), (panel_x, panel_y, panel_w, panel_h), border_radius=15)
        pygame.draw.rect(self.screen, Colors.GOLD, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=15)
        
        # 标题
        font_title = pygame.font.SysFont('SimHei', 32)
        title = "本回合结算"
        title_surf = font_title.render(title, True, Colors.GOLD)
        self.screen.blit(title_surf, (panel_x + panel_w//2 - title_surf.get_width()//2, panel_y + 20))
        
        # 结果
        font = pygame.font.SysFont('SimHei', 22)
        landlord_win = self.round_score_data['landlord_win']
        result_text = "地主获胜!" if landlord_win else "农民获胜!"
        result_color = Colors.RED if landlord_win else Colors.BLUE
        result_surf = font.render(result_text, True, result_color)
        self.screen.blit(result_surf, (panel_x + panel_w//2 - result_surf.get_width()//2, panel_y + 70))
        
        # 详细信息
        font_detail = pygame.font.SysFont('SimHei', 18)
        details = [
            f"叫分: {self.round_score_data['landlord_bid']}",
            f"炸弹: {self.round_score_data['bombs']}个 (×{2**self.round_score_data['bombs']})",
            f"王炸: {self.round_score_data['rockets']}个 (×{4**self.round_score_data['rockets']})",
            f"倍率: ×{self.round_score_data['multiplier']}",
        ]
        
        y_offset = 110
        for detail in details:
            detail_surf = font_detail.render(detail, True, Colors.WHITE)
            self.screen.blit(detail_surf, (panel_x + 50, panel_y + y_offset))
            y_offset += 30
        
        # 积分变化
        y_offset += 10
        font_score = pygame.font.SysFont('SimHei', 20)
        
        landlord_change = self.round_score_data['landlord_change']
        peasants_change = self.round_score_data['peasants_change']
        
        # 地主
        landlord_name = self.game.players[self.game.current_landlord_id].name
        change_text = f"{landlord_name}: {landlord_change:+d}"
        color = Colors.GREEN if landlord_change > 0 else Colors.RED
        change_surf = font_score.render(change_text, True, color)
        self.screen.blit(change_surf, (panel_x + 50, panel_y + y_offset))
        
        # 农民
        for pid in range(3):
            if pid != self.game.current_landlord_id:
                peasant_name = self.game.players[pid].name
                change_text = f"{peasant_name}: {peasants_change:+d}"
                color = Colors.GREEN if peasants_change > 0 else Colors.RED
                change_surf = font_score.render(change_text, True, color)
                self.screen.blit(change_surf, (panel_x + 50, panel_y + y_offset + 30))
        
        # 继续按钮
        self.buttons['continue'].draw(self.screen)
    
    def draw_game_over(self):
        """绘制游戏结束界面"""
        # 半透明遮罩
        overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # 结算面板
        panel_w, panel_h = 600, 450
        panel_x = (self.WINDOW_WIDTH - panel_w) // 2
        panel_y = (self.WINDOW_HEIGHT - panel_h) // 2
        
        pygame.draw.rect(self.screen, (30, 30, 30), (panel_x, panel_y, panel_w, panel_h), border_radius=15)
        pygame.draw.rect(self.screen, Colors.GOLD, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=15)
        
        # 标题
        font_title = pygame.font.SysFont('SimHei', 36)
        title = "游戏结束"
        title_surf = font_title.render(title, True, Colors.GOLD)
        self.screen.blit(title_surf, (panel_x + panel_w//2 - title_surf.get_width()//2, panel_y + 20))
        
        # 排行榜
        font = pygame.font.SysFont('SimHei', 22)
        font_name = pygame.font.SysFont('SimHei', 24)
        
        # 按积分排序
        scores = [(i, self.player_scores[i]) for i in range(3)]
        scores.sort(key=lambda x: x[1], reverse=True)
        
        y_offset = 80
        medals = ["1st", "2nd", "3rd"]
        
        for rank, (pid, score) in enumerate(scores):
            player = self.game.players[pid]
            player_name = player.name
            
            # 排名
            rank_text = f"{medals[rank]} {player_name}"
            if pid == self.game.current_landlord_id:
                rank_text += " (房东)"
            
            name_surf = font_name.render(rank_text, True, Colors.WHITE)
            score_surf = font.render(f"{score} 分", True, Colors.YELLOW)
            
            self.screen.blit(name_surf, (panel_x + 80, panel_y + y_offset))
            self.screen.blit(score_surf, (panel_x + 400, panel_y + y_offset))
            
            y_offset += 50
        
        # 胜负判定
        winner_id = scores[0][0]
        player_is_winner = (winner_id == 1)
        
        if player_is_winner:
            result = "** 恭喜你获胜! **"
            result_color = Colors.GOLD
        else:
            result = "** 再接再厉! **"
            result_color = Colors.LIGHT_GRAY
        
        font_result = pygame.font.SysFont('SimHei', 28)
        result_surf = font_result.render(result, True, result_color)
        self.screen.blit(result_surf, (panel_x + panel_w//2 - result_surf.get_width()//2, panel_y + 260))
        
        # 重新开始按钮
        self.buttons['start'].draw(self.screen)
    
    def show_start_screen(self):
        """显示开始界面"""
        self.draw_background()
        
        # 标题
        font_title = pygame.font.SysFont('SimHei', 72)
        title = font_title.render("欢乐斗地主", True, Colors.GOLD)
        title_rect = title.get_rect(center=(self.WINDOW_WIDTH // 2, 150))
        
        # 标题阴影
        shadow = font_title.render("欢乐斗地主", True, Colors.BROWN)
        self.screen.blit(shadow, (title_rect.x + 4, title_rect.y + 4))
        self.screen.blit(title, title_rect)
        
        # 副标题
        font = pygame.font.SysFont('SimHei', 24)
        subtitle = font.render("HAPPY LANDLORDS", True, Colors.WHITE)
        subtitle_rect = subtitle.get_rect(center=(self.WINDOW_WIDTH // 2, 220))
        self.screen.blit(subtitle, subtitle_rect)
        
        # 回合选择提示
        tip_font = pygame.font.SysFont('SimHei', 22)
        tip = tip_font.render("选择回合数:", True, Colors.YELLOW)
        self.screen.blit(tip, (self.WINDOW_WIDTH // 2 - tip.get_width() // 2, 280))
        
        # 回合按钮
        for btn_key in ['round_3', 'round_5', 'round_10']:
            self.buttons[btn_key].draw(self.screen)
        
        # 版本信息
        font_version = pygame.font.SysFont('SimHei', 14)
        version = font_version.render("v1.1 - 多回合对战 | 炸弹计分 | 王炸翻倍", True, Colors.LIGHT_GRAY)
        self.screen.blit(version, (self.WINDOW_WIDTH // 2 - version.get_width() // 2, self.WINDOW_HEIGHT - 50))
        
        pygame.display.flip()
    
    def show_playing_phase(self):
        """显示游戏阶段"""
        self.draw_background()
        
        # 绘制玩家信息
        self.draw_player_info(0, 50, 100)
        self.draw_player_info(2, self.WINDOW_WIDTH - 230, 100)
        self.draw_player_info(1, self.WINDOW_WIDTH // 2 - 90, self.WINDOW_HEIGHT - 130)
        
        # 绘制底牌
        self.draw_landlord_cards()
        
        # 绘制玩家手牌
        self.draw_player_cards()
        
        # 绘制上家出的牌
        self.draw_last_play_cards()
        
        # 绘制积分面板
        self.draw_score_board()
        
        # 显示出牌按钮
        if self.game.current_turn == 1:
            if self.game.last_play and self.game.last_play.player.player_id != 1:
                self.buttons['pass'].draw(self.screen)
            if self.selected_cards:
                self.buttons['play'].draw(self.screen)
        
        # 当前提示
        current = self.game.players[self.game.current_turn]
        font = pygame.font.SysFont('SimHei', 18)
        tip = f"轮到: {current.name}"
        tip_surf = font.render(tip, True, Colors.YELLOW)
        self.screen.blit(tip_surf, (self.WINDOW_WIDTH // 2 - tip_surf.get_width() // 2, 170))
        
        # 绘制消息
        self.draw_message()
        
        pygame.display.flip()
    
    def show_round_end(self):
        """显示回合结束"""
        self.draw_background()
        self.draw_player_info(0, 50, 100)
        self.draw_player_info(2, self.WINDOW_WIDTH - 230, 100)
        self.draw_player_info(1, self.WINDOW_WIDTH // 2 - 90, self.WINDOW_HEIGHT - 130)
        self.draw_round_result()
        pygame.display.flip()
    
    def show_game_over_screen(self):
        """显示游戏结束"""
        self.draw_background()
        self.draw_game_over()
        pygame.display.flip()
    
    def handle_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """处理点击事件"""
        # 更新按钮悬停状态
        for btn in self.buttons.values():
            btn.check_hover(pos)
        
        # 检查按钮点击
        for btn_key, btn in self.buttons.items():
            if btn.rect.collidepoint(pos):
                return btn_key
        
        # 检查卡牌点击
        if self.phase == "playing" and self.game.current_turn == 1:
            player = self.game.players[1]
            y = self.WINDOW_HEIGHT - self.card_renderer.CARD_HEIGHT - 50
            total_width = len(player.cards) * 80
            x = (self.WINDOW_WIDTH - total_width) // 2
            
            for i, card in enumerate(player.cards):
                card_x = x + i * 80
                y_offset = -15 if i in self.selected_cards else 0
                card_rect = pygame.Rect(card_x, y + y_offset, 75, self.card_renderer.CARD_HEIGHT)
                if card_rect.collidepoint(pos):
                    if i in self.selected_cards:
                        self.selected_cards.remove(i)
                    else:
                        self.selected_cards.append(i)
                    return None
        
        return None
    
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
                    self._process_action(action)
            
            # 根据游戏阶段渲染
            if self.phase == "start":
                self.show_start_screen()
            elif self.phase in ["bidding", "playing"]:
                self.show_playing_phase()
                if self.phase == "playing" and self.game.current_turn != 1 and not self.ai_thinking:
                    self.ai_thinking = True
                    auto_play_timer = 25
            elif self.phase == "round_end":
                self.show_round_end()
            elif self.phase == "game_over":
                self.show_game_over_screen()
            
            # AI自动出牌
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
    
    def _process_action(self, action: Optional[str]):
        """处理动作"""
        if action is None:
            return
        
        if action == "start":
            self._start_game()
        elif action in ["round_3", "round_5", "round_10"]:
            self.total_rounds = int(action.split('_')[1])
            self._start_game()
        elif action == "bid_yes":
            self._process_bid(True)
        elif action == "bid_no":
            self._process_bid(False)
        elif action == "play":
            self._player_play_cards()
        elif action == "pass":
            self._player_pass()
        elif action == "continue":
            self._next_round()
    
    def _start_game(self):
        """开始新游戏"""
        self.game.initialize()
        self.game.deal_cards()
        self.selected_cards = []
        self.current_round = 0
        self.player_scores = [1000, 1000, 1000]
        self.phase = "bidding"
        self.game.current_turn = 0
    
    def _process_bid(self, is_bid: bool):
        """处理叫地主"""
        if is_bid:
            self.game.set_landlord(self.game.current_turn, bid=1)
            self.message = f"{self.game.players[self.game.current_landlord_id].name}成为房东!"
            self.message_timer = 60
            self.phase = "playing"
        else:
            self.game.current_turn = (self.game.current_turn + 1) % 3
            if self.game.current_turn != 1:
                self._ai_bid()
            else:
                # 玩家轮到，自动叫地主
                self._process_bid(True)
    
    def _ai_bid(self):
        """AI叫地主"""
        import random
        player = self.game.players[self.game.current_turn]
        good_cards = sum(1 for c in player.cards if c.value >= 15)
        if good_cards >= 2 or random.random() > 0.3:
            self._process_bid(True)
        else:
            self._process_bid(False)
    
    def _player_play_cards(self):
        """玩家出牌"""
        if not self.selected_cards:
            return
        
        selected_cards = [self.game.players[1].cards[i] for i in sorted(self.selected_cards)]
        
        if self.game.can_play_cards(self.game.players[1], selected_cards):
            self.game.play_cards(self.game.players[1], selected_cards)
            self.selected_cards = []
            self._check_round_end()
        else:
            self.message = "不能出这些牌!"
            self.message_timer = 30
    
    def _player_pass(self):
        """玩家跳过"""
        if self.game.last_play and self.game.last_play.player.player_id == 1:
            return
        self.game.pass_turn(self.game.players[1])
        self._advance_turn()
    
    def _ai_turn(self):
        """AI出牌"""
        current = self.game.get_player_at_turn(self.game.current_turn)
        cards = self.game.get_smart_play(current)
        
        if cards:
            self.game.play_cards(current, cards)
            self._check_round_end()
        else:
            self.game.pass_turn(current)
        
        self._advance_turn()
    
    def _advance_turn(self):
        """进入下一回合"""
        self.game.next_turn()
    
    def _check_round_end(self):
        """检查回合结束"""
        if self.game.check_game_over():
            # 计算积分
            self.round_score_data = self.game.calculate_round_score()
            
            # 更新积分
            landlord_id = self.game.current_landlord_id
            self.player_scores[landlord_id] += self.round_score_data['landlord_change']
            for pid in range(3):
                if pid != landlord_id:
                    self.player_scores[pid] += self.round_score_data['peasants_change']
            
            self.current_round += 1
            
            if self.current_round >= self.total_rounds:
                self.phase = "game_over"
            else:
                self.phase = "round_end"
    
    def _next_round(self):
        """下一回合"""
        self.game.initialize()
        self.game.deal_cards()
        self.selected_cards = []
        self.round_score_data = None
        self.phase = "bidding"
        self.game.current_turn = 0


def main():
    """主函数"""
    game = LandlordsUI()
    game.run()


if __name__ == "__main__":
    main()