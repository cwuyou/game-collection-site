import os
import json
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import sys
import time
import random
from playwright.sync_api import sync_playwright

# 获取脚本的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(PROJECT_ROOT, 'scraper.log'), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)  # 使用 stdout 而不是默认的 stderr
    ]
)
logger = logging.getLogger(__name__)

# 设置控制台输出编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

class GameScraper:
    def __init__(self):
        self.base_url = "https://www.onlinegames.io/t/embeddable-games-for-websites/"
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,  # 无头模式
            args=['--disable-blink-features=AutomationControlled']  # 禁用自动化检测
        )
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
    def __del__(self):
        """清理资源"""
        try:
            if hasattr(self, 'context'):
                self.context.close()
            if hasattr(self, 'browser'):
                self.browser.close()
            if hasattr(self, 'playwright'):
                self.playwright.stop()
        except Exception as e:
            logger.error(f"Error cleaning up resources: {str(e)}")

    def get_page_content(self, url, wait_for_selector=None):
        """获取页面内容"""
        page = None
        try:
            page = self.context.new_page()
            page.set_default_timeout(60000)  # 增加到60秒超时
            
            # 设置更多的浏览器特征
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            logger.info(f"Navigating to {url}")
            # 修改加载策略，使用 domcontentloaded 而不是 networkidle
            response = page.goto(
                url,
                wait_until='domcontentloaded',
                timeout=60000
            )
            
            if not response:
                logger.error("Failed to get response from page")
                return None
                
            if response.status >= 400:
                logger.error(f"Got HTTP status {response.status} for {url}")
                return None
            
            # 等待页面主要内容加载
            try:
                if wait_for_selector:
                    logger.info(f"Waiting for selector: {wait_for_selector}")
                    page.wait_for_selector(wait_for_selector, timeout=20000)
                else:
                    # 等待body元素可见
                    page.wait_for_selector('body', timeout=20000)
                    
                # 短暂等待以确保动态内容加载
                page.wait_for_timeout(2000)
            except Exception as e:
                logger.warning(f"Timeout waiting for content, but continuing: {str(e)}")
            
            # 获取页面内容
            content = page.content()
            
            # 保存页面截图用于调试
            screenshot_path = os.path.join(PROJECT_ROOT, f'debug_screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
            page.screenshot(path=screenshot_path)
            logger.info(f"Saved screenshot to {screenshot_path}")
            
            return content
            
        except Exception as e:
            logger.error(f"Error getting page content: {str(e)}")
            return None
        finally:
            if page:
                try:
                    page.close()
                except:
                    pass

    def get_game_links(self):
        """获取可嵌入游戏的链接"""
        try:
            logger.info(f"Getting game links from {self.base_url}")
            
            # 获取页面内容
            html = self.get_page_content(self.base_url)
            if not html:
                logger.error("Failed to get page content")
                return []
            
            # 保存 HTML 以便调试
            debug_file = os.path.join(PROJECT_ROOT, 'debug_list.html')
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Saved game list HTML to {debug_file}")
            
            soup = BeautifulSoup(html, 'html.parser')
            game_links = []
            
            # 打印页面标题以确认内容正确
            title = soup.find('title')
            if title:
                logger.info(f"Page title: {title.text}")
            
            # 找到所有游戏卡片
            game_cards = soup.find_all('article', class_='c-card')
            logger.info(f"Found {len(game_cards)} game cards")
            
            for card in game_cards:
                try:
                    # 在卡片中查找链接
                    link = card.find('a', href=True)
                    if link:
                        href = link.get('href', '')
                        # 构建完整URL
                        full_url = href if href.startswith('http') else f"https://www.onlinegames.io{href}"
                        if full_url not in game_links:
                            game_links.append(full_url)
                            # 获取游戏标题用于日志
                            title_elem = card.find('div', class_='c-card__title')
                            title_text = title_elem.text.strip() if title_elem else 'Unknown'
                            logger.info(f"Found game: {title_text} - {full_url}")
                except Exception as e:
                    logger.error(f"Error processing game card: {str(e)}")
                    continue
            
            logger.info(f"Found {len(game_links)} unique game links")
            
            # 如果没有找到任何链接，记录页面结构以便调试
            if not game_links:
                logger.warning("No game links found, dumping page structure:")
                for tag in soup.find_all(['div', 'article', 'section'], class_=True):
                    logger.info(f"Found element: {tag.name}, class: {tag.get('class', [])}")
            
            return game_links
        except Exception as e:
            logger.error(f"Error getting game links: {str(e)}")
            return []

    def scrape_game_details(self, url):
        """抓取游戏详情"""
        try:
            logger.info(f"Scraping game details from {url}")
            
            # 获取页面内容
            html = self.get_page_content(url, wait_for_selector='iframe#gameFrame')
            if not html:
                return None
            
            # 保存 HTML 以便调试
            debug_file = os.path.join(PROJECT_ROOT, f'debug_game_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(html)
            logger.info(f"Saved game page HTML to {debug_file}")
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # 获取游戏信息
            game_data = {
                'url': url,
                'title': '',
                'description': '',
                'iframe_url': '',
                'preview_image': '',
                'categories': [],
                'tags': [],
                'html_content': html,  # 保存完整HTML以供后续分析
                'scraped_at': datetime.now().isoformat()
            }
            
            # 获取标题
            for title_selector in ['h1', '.game-title', 'title']:
                try:
                    title = soup.select_one(title_selector)
                    if title:
                        game_data['title'] = title.text.strip()
                        logger.info(f"Found title: {game_data['title']}")
                        break
                except Exception as e:
                    logger.error(f"Error getting title with selector {title_selector}: {str(e)}")
                    continue
            
            # 获取描述
            for desc_selector in ['.game-description', 'meta[name="description"]', 'p']:
                try:
                    description = soup.select_one(desc_selector)
                    if description:
                        content = description.get('content', '') or description.text
                        if content:
                            game_data['description'] = content.strip()
                            logger.info(f"Found description: {game_data['description'][:100]}...")
                            break
                except Exception as e:
                    logger.error(f"Error getting description with selector {desc_selector}: {str(e)}")
                    continue
            
            # 获取 iframe URL
            try:
                iframe = soup.find('iframe', id='gameFrame')
                if iframe:
                    src = iframe.get('src', '')
                    if src:
                        game_data['iframe_url'] = src if src.startswith('http') else f"https://www.onlinegames.io{src}"
                        logger.info(f"Found iframe URL: {game_data['iframe_url']}")
                else:
                    logger.warning("No iframe with id='gameFrame' found")
            except Exception as e:
                logger.error(f"Error extracting iframe URL: {str(e)}")
            
            # 获取预览图片
            try:
                for img_selector in ['.game-image img', '.game-preview img', 'meta[property="og:image"]']:
                    img = soup.select_one(img_selector)
                    if img:
                        src = img.get('content', '') or img.get('src', '')
                        if src:
                            game_data['preview_image'] = src if src.startswith('http') else f"https://www.onlinegames.io{src}"
                            logger.info(f"Found preview image: {game_data['preview_image']}")
                            break
            except Exception as e:
                logger.error(f"Error getting preview image: {str(e)}")
            
            # 获取分类和标签
            try:
                categories = set()
                tags = set()
                
                # 查找所有链接
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    text = link.text.strip()
                    
                    if text and href:
                        if '/category/' in href or '/c/' in href:
                            categories.add(text)
                        elif '/tag/' in href or '/t/' in href:
                            tags.add(text)
                
                game_data['categories'] = list(categories)
                game_data['tags'] = list(tags)
                logger.info(f"Found categories: {game_data['categories']}")
                logger.info(f"Found tags: {game_data['tags']}")
            except Exception as e:
                logger.error(f"Error getting categories and tags: {str(e)}")
            
            logger.info(f"Successfully scraped game: {game_data['title']}")
            return game_data
        except Exception as e:
            logger.error(f"Error scraping game details: {str(e)}")
            return None

    def save_game_data(self, game_data):
        if not game_data:
            return
            
        try:
            # 创建输出目录
            output_dir = os.path.join(PROJECT_ROOT, 'scraped_data')
            os.makedirs(output_dir, exist_ok=True)
            
            # 保存游戏数据
            filename = f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Saved game data to {filepath}")
        except Exception as e:
            logger.error(f"Error saving game data: {str(e)}")

def main():
    try:
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"Python executable: {sys.executable}")
        logger.info(f"Script directory: {SCRIPT_DIR}")
        logger.info(f"Project root: {PROJECT_ROOT}")
        
        scraper = GameScraper()
        # 获取所有可嵌入游戏的链接
        game_links = scraper.get_game_links()
        
        # 抓取每个游戏的详细信息
        for link in game_links:
            try:
                game_data = scraper.scrape_game_details(link)
                if game_data and game_data['iframe_url']:  # 只保存有 iframe URL 的游戏
                    scraper.save_game_data(game_data)
                    # 随机延迟，避免请求过快
                    time.sleep(random.uniform(2, 5))
            except Exception as e:
                logger.error(f"Error processing game {link}: {str(e)}")
                continue
            
    except Exception as e:
        logger.error(f"Main process error: {str(e)}")
        
if __name__ == "__main__":
    main() 