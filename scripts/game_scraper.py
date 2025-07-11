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
                # 1. 获取侧边栏的所有游戏分类名称（作为有效分类列表）
                valid_categories = set()
                sidebar = soup.find('ul', class_='navbar__menu')
                if sidebar:
                    for link in sidebar.find_all('a', href=True):
                        href = link.get('href', '')
                        if '/t/' in href:
                            category_name = link.text.strip()
                            if category_name and category_name != '2-player':  # 排除2-player作为分类
                                valid_categories.add(category_name.lower())  # 转为小写以便后续匹配
                logger.info(f"Found valid categories from sidebar: {valid_categories}")

                # 2. 获取游戏页面的分类（从"Home>"后面的文本）
                breadcrumb_category = None
                breadcrumb = soup.find('ol', class_='breadcrumb')
                if breadcrumb:
                    items = breadcrumb.find_all('li')
                    if len(items) > 1:  # 确保有"Home"之后的项目
                        last_item = items[-1].find('a')
                        if last_item:
                            category = last_item.text.strip()
                            if category != '2-player':  # 排除2-player
                                breadcrumb_category = category
                logger.info(f"Found breadcrumb category: {breadcrumb_category}")

                # 3. 从游戏描述中提取分类信息
                description_texts = []
                final_categories = []
                
                # 3.1 首先检查面包屑分类
                if breadcrumb_category:
                    bc_lower = breadcrumb_category.lower()
                    if bc_lower in valid_categories:
                        final_categories.append(breadcrumb_category)
                        logger.info(f"Found category from breadcrumb: {breadcrumb_category}")
                
                # 3.2 如果面包屑分类不匹配，则统计文本出现频率
                if not final_categories:
                    # 收集所有相关文本
                    for desc_selector in ['.game-description', 'meta[name="description"]', 'p', '.game-info', '.game-controls']:
                        elements = soup.select(desc_selector)
                        for desc in elements:
                            text = desc.get('content', '') or desc.text
                            if text:
                                description_texts.append(text.lower())
                    
                    # 获取其他相关文本
                    for section_text in ["More Games Like This", "Game Description", "How to Play", "Controls"]:
                        section = soup.find(string=lambda text: text and section_text in text)
                        if section:
                            parent = section.parent
                            if parent:
                                text = parent.get_text().lower()
                                description_texts.append(text)
                    
                    # 获取Embed URL
                    iframe = soup.find('iframe', id='gameFrame')
                    if iframe:
                        src = iframe.get('src', '').lower()
                        if src:
                            description_texts.append(src)
                    
                    # 统计每个有效分类在文本中的出现次数
                    category_counts = {}
                    for category in valid_categories:
                        count = 0
                        category_lower = category.lower()
                        
                        for text in description_texts:
                            # 处理特殊分类
                            if category_lower == 'fps':
                                count += text.count('first person shooter')
                                count += text.count('fps')
                            elif category_lower == 'strategy':
                                count += text.count('strategic')
                                count += text.count('strategy')
                            elif category_lower == 'racing':
                                count += text.count('race')
                                count += text.count('racing')
                                count += text.count('drift')
                            else:
                                count += text.count(category_lower)
                            
                            # 在URL中出现的分类给予更高权重
                            if text.startswith('http'):
                                if category_lower in text:
                                    count += 3  # URL中出现给予额外权重
                        
                        # 检查"Other ** Games"部分
                        other_games_pattern = f"Other {category.title()} Games"
                        if soup.find(string=lambda text: text and other_games_pattern in text):
                            count += 5  # 给予额外权重
                        
                        if count > 0:
                            category_counts[category] = count
                    
                    # 如果找到了出现次数最多的分类
                    if category_counts:
                        # 按出现次数降序排序
                        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
                        top_category = sorted_categories[0][0]
                        # 使用有效分类列表中的原始大小写形式
                        original_case = next(c for c in sidebar.find_all('a', href=True) 
                                          if c.text.strip().lower() == top_category)
                        final_categories.append(original_case.text.strip())
                        logger.info(f"Found category from text frequency: {original_case.text.strip()} (count: {sorted_categories[0][1]})")
                
                # 3.3 如果前两种方法都没找到分类，检查分类链接
                if not final_categories:
                    for link in soup.find_all('a', href=True):
                        href = link.get('href', '').lower()
                        if '/t/' in href:
                            # 从URL中提取分类名
                            category = href.split('/t/')[-1].strip('/').replace('-', ' ')
                            if category and category != '2-player' and category in valid_categories:
                                # 使用有效分类列表中的原始大小写形式
                                original_case = next(c for c in sidebar.find_all('a', href=True) 
                                                  if c.text.strip().lower() == category)
                                category_name = original_case.text.strip()
                                if category_name not in final_categories:
                                    final_categories.append(category_name)
                                    logger.info(f"Found category from links: {category_name}")
                                    break  # 找到一个匹配的分类就停止
                
                game_data['categories'] = final_categories
                logger.info(f"Final categories: {final_categories}")

                # 5. 获取游戏标签（从post__tags-share区域）
                tags = []
                tags_div = soup.find('div', class_='post__tags-share')
                if tags_div:
                    tag_list = tags_div.find('ul', class_='post__tag')
                    if tag_list:
                        for tag_item in tag_list.find_all('li'):
                            tag_link = tag_item.find('a')
                            if tag_link:
                                tag_text = tag_link.text.strip()
                                if tag_text:
                                    tags.append(tag_text)
                
                # 如果游戏支持2个玩家，将"2-player"添加到标签中
                if '2-player' not in tags:
                    two_player_found = False
                    # 检查面包屑
                    if breadcrumb and '2-player' in [li.text.strip() for li in breadcrumb.find_all('li')]:
                        two_player_found = True
                    # 检查描述中的链接
                    if not two_player_found:
                        for link in soup.find_all('a', href=True):
                            if '2-player' in link.text.strip():
                                two_player_found = True
                                break
                    if two_player_found:
                        tags.append('2-player')
                
                game_data['tags'] = tags
                logger.info(f"Found tags: {tags}")

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

    def calculate_category_weight(self, category, description_texts, soup):
        """
        计算分类的权重分数
        :param category: 分类名称
        :param description_texts: 描述文本列表
        :param soup: BeautifulSoup对象
        :return: 权重分数
        """
        weight = 0
        category_lower = category.lower()
        
        # 1. 统计分类名在描述文本中的出现次数
        for text in description_texts:
            # 处理特殊分类
            if category_lower == 'fps':
                weight += text.count('first person shooter') * 2
                weight += text.count('fps') * 2
            elif category_lower == 'strategy':
                weight += text.count('strategic') * 2
                weight += text.count('strategy') * 2
            elif category_lower == 'racing':
                weight += text.count('race') * 2
                weight += text.count('racing') * 2
                weight += text.count('drift') * 2
            else:
                # 直接匹配分类名
                weight += text.count(category_lower)
        
        # 2. 检查"More Games Like This"部分
        more_games_section = soup.find(string=lambda text: text and "More Games Like This" in text)
        if more_games_section:
            parent = more_games_section.parent
            if parent:
                more_games_text = parent.get_text().lower()
                if category_lower in more_games_text:
                    weight += 5  # 给予更高权重
        
        # 3. 检查"Other ** Games"部分
        other_games_pattern = f"Other {category.title()} Games"
        other_games_section = soup.find(string=lambda text: text and other_games_pattern in text)
        if other_games_section:
            weight += 5  # 给予更高权重
        
        # 4. 检查游戏链接
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').lower()
            if f'/t/{category_lower.replace(" ", "-")}' in href:
                weight += 3  # 给予适中权重
        
        return weight

    def get_weighted_categories(self, valid_categories, description_texts, soup):
        """
        获取带权重的分类列表
        :param valid_categories: 有效分类集合
        :param description_texts: 描述文本列表
        :param soup: BeautifulSoup对象
        :return: 按权重排序的分类列表
        """
        category_weights = []
        for category in valid_categories:
            weight = self.calculate_category_weight(category, description_texts, soup)
            if weight > 0:  # 只添加有权重的分类
                category_weights.append((category, weight))
        
        # 按权重降序排序
        return sorted(category_weights, key=lambda x: x[1], reverse=True)

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