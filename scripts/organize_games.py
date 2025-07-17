import os
import json
import shutil
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('organize_games.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def organize_games():
    # 获取项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html5games_dir = os.path.join(project_root, 'scraped_data', 'html5games')
    
    # 确保html5games目录存在
    if not os.path.exists(html5games_dir):
        logger.error(f"目录不存在: {html5games_dir}")
        return
    
    # 获取所有json文件
    json_files = [f for f in os.listdir(html5games_dir) 
                 if f.endswith('.json') and os.path.isfile(os.path.join(html5games_dir, f))]
    
    if not json_files:
        logger.info("没有找到需要整理的JSON文件")
        return
    
    logger.info(f"找到 {len(json_files)} 个JSON文件需要整理")
    
    # 处理每个文件
    for json_file in json_files:
        try:
            file_path = os.path.join(html5games_dir, json_file)
            
            # 读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as f:
                game_data = json.load(f)
            
            # 获取分类列表
            categories = game_data.get('categories', [])
            if not categories:
                logger.warning(f"文件 {json_file} 没有categories信息，跳过")
                continue
            
            # 如果categories不是列表，转换为列表
            if isinstance(categories, str):
                categories = [categories]
            
            # 为每个分类创建副本
            for category in categories:
                try:
                    # 创建分类目录
                    category_dir = os.path.join(
                        html5games_dir, 
                        category.lower().replace(' & ', '_').replace(' ', '_')
                    )
                    os.makedirs(category_dir, exist_ok=True)
                    
                    # 生成新的文件名
                    title = game_data.get('title', 'untitled')
                    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                    new_filename = f"game_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    new_file_path = os.path.join(category_dir, new_filename)
                    
                    # 更新游戏数据中的category字段
                    game_data_copy = game_data.copy()
                    game_data_copy['category'] = category
                    
                    # 保存到新位置
                    with open(new_file_path, 'w', encoding='utf-8') as f:
                        json.dump(game_data_copy, f, ensure_ascii=False, indent=2)
                    logger.info(f"已复制 {json_file} 到分类 {category}")
                    
                except Exception as e:
                    logger.error(f"处理文件 {json_file} 的分类 {category} 时出错: {str(e)}")
                    continue
            
            # 删除原始文件
            os.remove(file_path)
            logger.info(f"已删除原始文件 {json_file}")
            
        except Exception as e:
            logger.error(f"处理文件 {json_file} 时出错: {str(e)}")
            continue
    
    logger.info("文件整理完成")

if __name__ == '__main__':
    organize_games() 