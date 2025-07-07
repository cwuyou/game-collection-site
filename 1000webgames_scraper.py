import os
import json
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import sys
import time
import random
from playwright.sync_api import sync_playwright
import requests

# 获取脚本的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('1000webgames_scraper.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WebGameScraper:
    def __init__(self):
        # 创建存储目录
        self.base_dir = 'scraped_data/1000webgames'
        os.makedirs(self.base_dir, exist_ok=True)
        
        # 初始化Playwright
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False,  # 显示浏览器窗口以便调试
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--lang=en-US,en;q=0.9'
            ]
        )
        
        # 创建上下文
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            geolocation={'latitude': 40.7128, 'longitude': -74.0060},
            permissions=['geolocation'],
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'DNT': '1'
            }
        )
        
        # 基础URL
        self.base_url = 'https://1000webgames.com'
        
    def get_proxy(self):
        """获取代理服务器"""
        try:
            # 这里使用免费代理API
            response = requests.get('https://proxylist.geonode.com/api/proxy-list?limit=1&page=1&sort_by=lastChecked&sort_type=desc&protocols=http%2Chttps&anonymityLevel=elite&filterUpTime=90')
            data = response.json()
            if data['data']:
                proxy = data['data'][0]
                return f"{proxy['ip']}:{proxy['port']}"
            return None
        except Exception as e:
            logger.error(f"Error getting proxy: {str(e)}")
            return None
            
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

    def get_page_content(self, url):
        """获取页面内容"""
        page = None
        try:
            page = self.context.new_page()
            page.set_default_timeout(30000)  # 30秒超时
            
            # 设置浏览器特征
            page.add_init_script("""
                // 覆盖 WebDriver
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // 覆盖 Chrome
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // 覆盖 Permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // 添加语言
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // 添加插件
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {
                            0: {type: "application/x-google-chrome-pdf"},
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        }
                    ]
                });
            """)
            
            logger.info(f"Navigating to {url}")
            
            # 设置请求拦截
            page.route("**/*", lambda route: route.continue_())
            
            response = page.goto(
                url,
                wait_until='domcontentloaded',
                timeout=30000
            )
            
            if not response:
                logger.error("Failed to get response from page")
                return None
                
            if response.status >= 400:
                logger.error(f"Got HTTP status {response.status} for {url}")
                return None
            
            # 等待页面加载
            try:
                # 等待body元素可见
                page.wait_for_selector('body', timeout=10000)
                # 模拟人类行为
                page.mouse.move(random.randint(100, 500), random.randint(100, 500))
                page.mouse.wheel(delta_y=random.randint(-100, 100))
                # 短暂等待以确保动态内容加载
                page.wait_for_timeout(random.randint(1000, 2000))
            except Exception as e:
                logger.warning(f"Timeout waiting for content: {str(e)}")
            
            content = page.content()
            
            # 保存调试截图
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

    def parse_game_page(self, url):
        """解析游戏页面"""
        content = self.get_page_content(url)
        if not content:
            return None
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # 保存解析后的HTML结构用于调试
        debug_path = os.path.join(PROJECT_ROOT, f'debug_parsed_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
        with open(debug_path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        logger.info(f"Saved parsed HTML to {debug_path}")
        
        # 提取游戏信息
        game_data = {
            'url': url,
            'title': '',
            'description': '',
            'iframe_url': '',
            'preview_image': '',
            'categories': [],
            'tags': [],
            'scraped_at': datetime.now().isoformat()
        }
        
        try:
            # 获取标题
            title_elem = soup.find('title')  # 使用title标签
            if title_elem:
                game_data['title'] = title_elem.text.strip().replace(' - 1000 Web Games', '')
                logger.info(f"Found title: {game_data['title']}")
            
            # 获取描述
            # 尝试多种可能的描述元素
            desc_candidates = [
                soup.find('meta', {'name': 'description'}),  # meta描述
                soup.find('meta', {'property': 'og:description'}),  # Open Graph描述
                soup.find('div', class_='game-description'),  # 游戏描述div
                soup.find('div', class_='description'),  # 描述div
                soup.find('p', class_='description'),  # 描述段落
                soup.find('div', {'id': 'about'}),  # about区域
                soup.find('div', {'id': 'description'})  # description区域
            ]
            
            for desc_elem in desc_candidates:
                if desc_elem:
                    if desc_elem.name == 'meta':
                        desc_text = desc_elem.get('content', '')
                    else:
                        desc_text = desc_elem.text
                    if desc_text and len(desc_text.strip()) > 0:
                        game_data['description'] = desc_text.strip()
                        logger.info(f"Found description: {game_data['description'][:100]}...")
                        break
            
            # 获取iframe URL
            # 尝试多种可能的iframe
            iframe_candidates = [
                soup.find('iframe', id='gameFrame'),  # 游戏框架
                soup.find('iframe', class_='game-iframe'),  # 游戏iframe
                soup.find('iframe', {'data-type': 'game'}),  # 游戏类型iframe
                soup.find('iframe', {'name': 'game'}),  # 游戏名称iframe
                soup.find('iframe', {'title': lambda x: x and 'game' in x.lower()}),  # 标题包含game的iframe
                soup.find('iframe')  # 任何iframe
            ]
            
            for iframe_elem in iframe_candidates:
                if iframe_elem and 'src' in iframe_elem.attrs:
                    src = iframe_elem['src']
                    # 确保是完整的URL
                    if not src.startswith(('http://', 'https://')):
                        src = f"{self.base_url}/{src.lstrip('/')}"
                    game_data['iframe_url'] = src
                    logger.info(f"Found iframe URL: {game_data['iframe_url']}")
                    break
            
            # 获取预览图片
            # 尝试多种可能的图片元素
            img_candidates = [
                soup.find('meta', {'property': 'og:image'}),  # Open Graph图片
                soup.find('img', class_='game-preview'),  # 游戏预览图
                soup.find('img', class_='preview'),  # 预览图
                soup.find('img', {'alt': lambda x: x and game_data['title'].lower() in x.lower()}),  # alt包含游戏名的图片
                soup.find('img', src=True)  # 任何图片
            ]
            
            for img_elem in img_candidates:
                if img_elem:
                    if img_elem.name == 'meta':
                        src = img_elem.get('content', '')
                    else:
                        src = img_elem.get('src', '')
                    if src:
                        if not src.startswith(('http://', 'https://')):
                            src = f"{self.base_url}/{src.lstrip('/')}"
                        game_data['preview_image'] = src
                        logger.info(f"Found preview image: {game_data['preview_image']}")
                        break
            
            # 获取分类和标签
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'category=' in href or 'tag=' in href or 'cat=' in href:
                    tag = link.text.strip()
                    if tag:
                        if 'category=' in href or 'cat=' in href:
                            game_data['categories'].append(tag)
                        else:
                            game_data['tags'].append(tag)
            
            if game_data['categories']:
                logger.info(f"Found categories: {game_data['categories']}")
            if game_data['tags']:
                logger.info(f"Found tags: {game_data['tags']}")
                
        except Exception as e:
            logger.error(f"Error parsing game page: {str(e)}")
            return None
            
        return game_data
        
    def save_game_data(self, game_data):
        """保存游戏数据到JSON文件"""
        if not game_data or not game_data.get('title'):
            return False
            
        try:
            # 生成文件名
            filename = f"{game_data['title'].strip().replace(' ', '_')}.json"
            filepath = os.path.join(self.base_dir, filename)
            
            # 保存数据
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved game data to: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving game data: {str(e)}")
            return False
            
    def get_game_links(self):
        """获取游戏链接"""
        try:
            logger.info("Getting game links from homepage")
            content = self.get_page_content(self.base_url)
            if not content:
                return []
                
            soup = BeautifulSoup(content, 'html.parser')
            game_links = []
            
            # 查找游戏链接
            for link in soup.find_all('a', href=True):
                href = link['href']
                if not href.startswith(('http://', 'https://')):
                    href = f"{self.base_url}/{href.lstrip('/')}"
                
                if '1000webgames.com/play-' in href and href not in game_links:
                    game_links.append(href)
                    logger.info(f"Found game link: {href}")
                
            game_links = list(set(game_links))  # 去重
            logger.info(f"Found {len(game_links)} unique game links")
            return game_links
            
        except Exception as e:
            logger.error(f"Error getting game links: {str(e)}")
            return []
        
    def scrape_games(self):
        """开始爬取游戏"""
        try:
            # 获取游戏链接
            game_links = self.get_game_links()
            if not game_links:
                logger.error("No game links found")
                return
                
            logger.info(f"Starting to scrape {len(game_links)} games")
            
            # 爬取每个游戏页面
            for link in game_links:
                try:
                    logger.info(f"Scraping game: {link}")
                    game_data = self.parse_game_page(link)
                    
                    if game_data:
                        self.save_game_data(game_data)
                    
                    # 随机延迟
                    delay = random.uniform(2, 5)
                    logger.info(f"Waiting {delay:.2f} seconds before next request")
                    time.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"Error processing game {link}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error in scrape_games: {str(e)}")
        finally:
            self.__del__()  # 确保资源被清理

def main():
    scraper = WebGameScraper()
    scraper.scrape_games()

if __name__ == "__main__":
    main()