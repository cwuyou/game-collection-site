import os
import json
from pathlib import Path

def get_all_categories():
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    scraped_data_dir = project_root / 'scraped_data'
    
    # 存储所有分类
    categories = set()
    
    # 遍历所有json文件
    for subdir in ['1000webgames', 'jopi']:
        dir_path = scraped_data_dir / subdir
        if dir_path.exists():
            for file in dir_path.glob('*.json'):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if 'categories' in data:
                            categories.update(data['categories'])
                except Exception as e:
                    print(f"Error reading {file}: {e}")
    
    # 检查根目录下的json文件
    for file in scraped_data_dir.glob('*.json'):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'categories' in data:
                    categories.update(data['categories'])
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    # 转换为列表并排序
    categories_list = sorted(list(categories), key=lambda x: (not x[0].isdigit(), x.lower()))
    
    # 为每个分类分配序号
    categories_with_numbers = {cat: idx + 1 for idx, cat in enumerate(categories_list)}
    
    return categories_with_numbers

def get_category_icon(category):
    """
    根据分类名获取对应的图标
    返回Lucide图标名称（参考：https://lucide.dev/icons/）
    """
    # 分类名到图标的映射
    icon_mapping = {
        # 数字开头的分类
        "2-player": "users",
        "3d": "cube",
        # 字母开头的分类
        "action": "swords",
        "adventure": "map",
        "arcade": "gamepad-2",
        "board": "layout-grid",
        "card": "cards",
        "casual": "dices",
        "drawing": "pencil",
        "dress up": "shirt",
        "fighting": "sword",
        "fps": "crosshair",
        "hidden objects": "search",
        "horror": "skull",
        "io games": "globe",
        "logic": "brain",
        "mahjong": "grid-2x2",
        "matching": "puzzle",
        "multiplayer": "users",
        "puzzle": "puzzle",
        "racing": "car",
        "shooting": "target",
        "simulation": "monitor",
        "sports": "trophy",
        "strategy": "chess-knight",
        "tower defense": "castle",
        "word": "text",
    }
    
    # 返回对应的图标，如果没有映射则返回默认图标
    return icon_mapping.get(category.lower(), "gamepad")

if __name__ == "__main__":
    # 获取所有分类及其序号
    categories = get_all_categories()
    
    # 打印结果
    print("\nCategories with numbers:")
    for cat, num in categories.items():
        icon = get_category_icon(cat)
        print(f"{num}. {cat} (Icon: {icon})") 