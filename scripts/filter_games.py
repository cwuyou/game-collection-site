import os
import json
from datetime import datetime

# 获取脚本的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SCRAPED_DATA_DIR = os.path.join(PROJECT_ROOT, 'scraped_data')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, f'multi_category_games_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')

def filter_games():
    # 只获取scraped_data根目录下的json文件
    json_files = [f for f in os.listdir(SCRAPED_DATA_DIR) 
                 if f.endswith('.json') and os.path.isfile(os.path.join(SCRAPED_DATA_DIR, f))]
    
    multi_category_games = []
    
    for json_file in json_files:
        file_path = os.path.join(SCRAPED_DATA_DIR, json_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
                
            # 获取categories并排除"2-player"
            categories = [cat for cat in game_data.get('categories', []) if cat != '2-player']
                
            # 检查剩余categories是否有2个或更多元素
            if len(categories) >= 2:
                multi_category_games.append({
                    'filename': json_file,
                    'title': game_data.get('title', 'Unknown'),
                    'categories': categories,
                    'tags': game_data.get('tags', [])
                })
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
            continue
    
    # 将结果写入文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("Games with Multiple Categories (excluding '2-player'):\n")
        f.write("=" * 80 + "\n\n")
        
        for game in multi_category_games:
            f.write(f"Filename: {game['filename']}\n")
            f.write(f"Title: {game['title']}\n")
            f.write(f"Categories: {', '.join(game['categories'])}\n")
            f.write(f"Tags: {', '.join(game['tags'])}\n")
            f.write("-" * 80 + "\n\n")
        
        f.write(f"\nTotal games found: {len(multi_category_games)}")
    
    print(f"Found {len(multi_category_games)} games with multiple categories (excluding '2-player')")
    print(f"Results have been written to: {OUTPUT_FILE}")

if __name__ == "__main__":
    filter_games() 