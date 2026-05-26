#!/usr/bin/env python3
"""
斗地主游戏入口
Landlords Card Game - Main Entry Point
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ui import main


if __name__ == "__main__":
    print("=" * 50)
    print("        斗地主 - Landlords Card Game")
    print("=" * 50)
    print()
    print("游戏说明:")
    print("- 点击卡牌选中")
    print("- 点击\"出牌\"按钮出牌")
    print("- 点击\"不出\"跳过")
    print("- 地主先出牌")
    print()
    print("祝你玩得愉快!")
    print()
    
    main()