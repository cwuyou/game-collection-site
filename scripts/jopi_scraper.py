import os
import json
import requests
from bs4 import BeautifulSoup
import logging
import sys
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jopi_scraper.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class JopiScraper:
    def __init__(self):
        self.base_url = "https://www.jopi.com/free-games-for-your-website.php"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # 确保输出目录存在
        self.output_dir = os.path.join('scraped_data', 'jopi')
        os.makedirs(self.output_dir, exist_ok=True)

    def get_page_content(self):
        """获取页面内容"""
        try:
            logger.info(f"Fetching content from {self.base_url}")
            response = requests.get(self.base_url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching page content: {str(e)}")
            return None

    def extract_game_data(self, html):
        """从HTML中提取游戏数据"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            games_data = []
            
            # 使用<hr>标签分割每个游戏块
            hr_tags = soup.find_all('hr')
            
            for hr_tag in hr_tags:
                game_data = {}
                
                # 获取游戏名称 (在<hr>后的第一个h2标签中)
                h2_tag = hr_tag.find_next('h2')
                if h2_tag:
                    game_data['name'] = h2_tag.get_text().split('-')[0].strip()
                    
                    # 获取游戏图片URL
                    img_tag = hr_tag.find_next('img')
                    if img_tag and img_tag.get('src'):
                        game_data['image_url'] = img_tag['src']
                    
                    # 获取iframe地址
                    textarea = hr_tag.find_next('textarea')
                    if textarea:
                        iframe_content = textarea.string
                        # 使用BeautifulSoup解析iframe内容以提取src
                        iframe_soup = BeautifulSoup(iframe_content, 'html.parser')
                        iframe_tag = iframe_soup.find('iframe')
                        if iframe_tag and iframe_tag.get('src'):
                            game_data['iframe_url'] = iframe_tag['src']
                    
                    # 获取<hr>到<textarea>之间的原始HTML
                    raw_html = ''
                    current = hr_tag
                    while current and not isinstance(current, type(textarea)):
                        raw_html += str(current)
                        current = current.next_element
                    raw_html += str(textarea) if textarea else ''
                    game_data['raw_html'] = raw_html
                    
                    if game_data.get('name'):  # 只添加有名称的游戏
                        games_data.append(game_data)
                        logger.info(f"Found game: {game_data['name']}")
            
            return games_data
        except Exception as e:
            logger.error(f"Error extracting game data: {str(e)}")
            return []

    def save_game_data(self, game_data):
        """保存游戏数据到JSON文件"""
        try:
            # 清理文件名（移除非法字符）
            safe_name = "".join(c for c in game_data['name'] if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"jopi_{safe_name}.json"
            filepath = os.path.join(self.output_dir, filename)
            
            # 添加抓取时间戳
            game_data['scraped_at'] = datetime.now().isoformat()
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved game data to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving game data: {str(e)}")
            return False

    def run(self):
        """运行爬虫"""
        try:
            # 获取页面内容
            html = self.get_page_content()
            if not html:
                return False
            
            # 提取游戏数据
            games_data = self.extract_game_data(html)
            logger.info(f"Found {len(games_data)} games")
            
            # 保存每个游戏的数据
            for game_data in games_data:
                self.save_game_data(game_data)
            
            return True
        except Exception as e:
            logger.error(f"Error running scraper: {str(e)}")
            return False

def main():
    scraper = JopiScraper()
    success = scraper.run()
    if success:
        logger.info("Scraping completed successfully")
    else:
        logger.error("Scraping failed")

if __name__ == "__main__":
    main() 