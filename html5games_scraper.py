import os
import json
import time
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urljoin
import logging
import traceback
import requests
from bs4 import BeautifulSoup
import random # Added for random delay
from playwright.sync_api import sync_playwright

# Set up logging
logging.basicConfig(
    filename='html5games_scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8',  # 使用UTF-8编码
    filemode='a'  # 追加模式
)

logger = logging.getLogger(__name__)  # 创建 logger 实例

logger.info("\n" + "="*50 + "\n开始运行 html5games.com 爬虫\n" + "="*50)

# Categories to scrape with their URL slugs
CATEGORIES = {
    # 'Cards': 'Cards',
    # 'Arcade': 'Arcade',
    # 'Racing': 'Racing',
    'Sport': 'Sport',
    'Multiplayer': 'Multiplayer',
    'Jump & Run': 'Jump-Run'  # 注意：URL中可能使用连字符
}

# Create output directory if it doesn't exist
OUTPUT_DIR = 'scraped_data/html5games'
os.makedirs(OUTPUT_DIR, exist_ok=True)

class WebGameScraper:
    def __init__(self):
        # 创建存储目录
        self.base_dir = 'scraped_data/html5games'
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

    def save_game_data(self, game_data):
        """保存游戏数据到JSON文件"""
        if not game_data or not game_data.get('title'):
            return False
            
        try:
            # 获取分类名称（使用第一个分类）
            category = game_data.get('categories', ['uncategorized'])[0]
            
            # 创建分类目录
            category_dir = os.path.join(self.base_dir, category.lower().replace(' & ', '_').replace(' ', '_'))
            os.makedirs(category_dir, exist_ok=True)
            
            # 生成文件名
            safe_title = "".join(c for c in game_data['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
            filename = f"game_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(category_dir, filename)
            
            # 保存数据
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved game data to: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving game data: {str(e)}")
            return False

    def get_page_content(self, url):
        """使用Playwright获取页面内容"""
        try:
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            self.page.goto(url)
            return self.page.content()
        except Exception as e:
            logger.error(f"Error getting page content: {str(e)}")
            return None

def setup_driver(headless=True):
    """Set up and return the undetected ChromeDriver."""
    try:
        # 设置Chrome选项
        options = uc.ChromeOptions()
        if headless:
            options.add_argument('--headless=new')  # 使用新的无头模式
        
        # 基础设置
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-notifications')
        options.add_argument('--window-size=1920,1080')
        
        # 性能和稳定性优化
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        options.add_argument('--disable-features=TranslateUI')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument('--disable-site-isolation-trials')
        
        # 更真实的浏览器配置
        options.add_argument('--enable-javascript')  # 启用 JavaScript
        options.add_argument('--disable-blink-features=AutomationControlled')  # 禁用自动化标记
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 设置ChromeDriver路径
        chrome_driver_path = os.path.join(os.path.dirname(__file__), 'drivers', 'chromedriver-win64', 'chromedriver-win64', 'chromedriver.exe')
        if not os.path.exists(chrome_driver_path):
            logger.error(f"ChromeDriver not found at {chrome_driver_path}")
            # 尝试下载ChromeDriver
            download_script = os.path.join(os.path.dirname(__file__), 'scripts', 'download_chrome.py')
            if os.path.exists(download_script):
                logger.info("Attempting to download ChromeDriver...")
                os.system(f'python "{download_script}"')
            else:
                logger.error("download_chrome.py script not found")
                raise FileNotFoundError("ChromeDriver not found and cannot download")
        
        # 设置ChromeDriver路径
        os.environ['PATH'] = os.path.dirname(chrome_driver_path) + os.pathsep + os.environ['PATH']
        
        # 初始化ChromeDriver
        logger.info(f"初始化 ChromeDriver... (Headless: {headless})")
        driver = uc.Chrome(
            driver_executable_path=chrome_driver_path,
            options=options,
            version_main=138  # 使用实际的Chrome版本
        )
        
        # 设置更长的超时时间
        driver.set_page_load_timeout(60)  # 增加到60秒
        driver.set_script_timeout(600)     # 脚本执行超时也设置为60秒
        
        # 设置请求拦截器来添加自定义请求头
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "platform": "Windows"
        })
        
        logger.info("ChromeDriver 初始化成功")
        return driver
        
    except Exception as e:
        logger.error(f"初始化 ChromeDriver 失败: {str(e)}")
        logger.error(traceback.format_exc())
        raise

def wait_for_element(driver, selector, timeout=20):
    """等待元素出现并可见"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        # 额外检查元素是否可见
        if element.is_displayed():
            return element
        return None
    except:
        return None

def get_game_data(driver, game_url, category, retry_with_visible=True):
    """从游戏页面提取游戏数据"""
    global logger  # 添加全局 logger 声明
    max_retries = 3  # 最大重试次数
    retry_count = 0
    current_driver = driver
    
    while retry_count < max_retries:
        try:
            logger.info(f"正在访问游戏页面 (尝试 {retry_count + 1}/{max_retries}): {game_url}")
            
            # 在每次请求之间添加随机延迟
            time.sleep(random.uniform(3, 7))  # 增加延迟时间
            
            # 使用标准的页面加载方式
            current_driver.get(game_url)
            
            # 等待页面加载完成
            WebDriverWait(current_driver, 30).until(  # 增加等待时间
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 检查页面是否加载完成
            ready_state = current_driver.execute_script("return document.readyState")
            if ready_state != "complete":
                time.sleep(5)  # 增加等待时间
            
            # 获取游戏标题
            title = None
            for selector in ['.game-title', '.game-name', 'h1', '.title']:
                try:
                    element = WebDriverWait(current_driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if element and element.is_displayed():
                        title = element.text.strip()
                        if title:
                            logger.info(f"找到游戏标题: {title}")
                            break
                except:
                    continue
            
            if not title:
                logger.warning("未找到游戏标题")
                if retry_count < max_retries - 1:
                    retry_count += 1
                    time.sleep(5)  # 等待5秒后重试
                    continue
            
            # 获取游戏描述
            description = ""
            for selector in ['.game-description', '.description', '.game-info p', 'meta[name="description"]']:
                try:
                    element = current_driver.find_element(By.CSS_SELECTOR, selector)
                    if selector == 'meta[name="description"]':
                        description = element.get_attribute('content').strip()
                    else:
                        description = element.text.strip()
                    if description:
                        logger.info("找到游戏描述")
                        break
                except:
                    continue
            
            # 获取游戏链接
            iframe_url = ""
            try:
                # 等待textarea-autogrow区域加载
                autogrow_div = WebDriverWait(current_driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.textarea-autogrow'))
                )
                
                # 尝试不同方式获取链接
                try:
                    textarea = autogrow_div.find_element(By.CSS_SELECTOR, 'textarea.aff-iliate-link')
                    iframe_url = textarea.get_attribute('value') or textarea.text
                except:
                    try:
                        shadow_div = autogrow_div.find_element(By.CSS_SELECTOR, 'div.shadow')
                        iframe_url = shadow_div.text
                    except:
                        pass
                
                if iframe_url:
                    logger.info(f"找到游戏iframe链接: {iframe_url}")
                else:
                    logger.warning("未找到游戏链接")
                    
            except Exception as e:
                logger.error(f"获取游戏iframe链接时出错: {str(e)}")
            
            # 获取游戏预览图片
            preview_image = ""
            try:
                # 等待图片区域加载
                WebDriverWait(current_driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'figure[style*="width: 180px"]'))
                )
                
                # 查找180px宽度的figure中的img
                figures = current_driver.find_elements(By.CSS_SELECTOR, 'figure[style*="width: 180px"]')
                for figure in figures:
                    try:
                        img = figure.find_element(By.TAG_NAME, 'img')
                        preview_image = img.get_attribute('src')
                        if preview_image:
                            logger.info(f"找到游戏预览图片: {preview_image}")
                            break
                    except:
                        continue
                
                # 如果没找到180px的图片，尝试其他尺寸
                if not preview_image:
                    figures = current_driver.find_elements(By.CSS_SELECTOR, 'figure img')
                    if figures:
                        preview_image = figures[0].get_attribute('src')
                        if preview_image:
                            logger.info(f"找到备选预览图片: {preview_image}")
                
            except Exception as e:
                logger.error(f"获取游戏预览图片时出错: {str(e)}")
            
            # 如果获取到了必要的数据，返回结果
            if title or iframe_url:
                # 创建游戏数据
                game_data = {
                    'title': title,
                    'description': description,
                    'iframe_url': iframe_url,
                    'preview_image': preview_image,  # 添加预览图片字段
                    'categories': [category],  # 保持与现有JSON一致，使用复数形式
                    'url': game_url,
                    'scraped_at': datetime.now().isoformat()
                }
                
                return game_data
            
            # 如果数据不完整且还有重试机会，继续重试
            if retry_count < max_retries - 1:
                retry_count += 1
                time.sleep(5)
                continue
                
        except Exception as e:
            logger.error(f"抓取游戏数据时出错 {game_url}: {str(e)}")
            if retry_count < max_retries - 1:
                retry_count += 1
                
                # 如果是最后一次重试且允许切换到有头模式
                if retry_with_visible and retry_count == max_retries - 1:
                    logger.warning("无头模式失败，尝试切换到有头模式...")
                    try:
                        current_driver.quit()  # 确保关闭旧的driver
                    except:
                        pass
                    current_driver = setup_driver(headless=False)
                    retry_count = 0  # 重置重试计数
                
                time.sleep(5)  # 等待5秒后重试
                continue
            else:
                # 所有重试都失败，返回None
                return None
                
    return None  # 如果所有尝试都失败，返回None

def get_game_links(driver, url):
    """从页面获取游戏链接"""
    game_urls = set()
    
    # 等待页面加载完成
    time.sleep(5)
    
    try:
        # 等待游戏卡片加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a[href^='/Game/']"))
        )
        
        # 获取所有游戏链接
        game_elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='/Game/']")
        base_url = "https://html5games.com"
        
        for element in game_elements:
            try:
                # 获取相对链接
                href = element.get_attribute('href')
                if not href:
                    # 如果href为空，尝试获取相对路径
                    href = element.get_attribute('pathname')
                    if href:
                        href = base_url + href
                
                if href:
                    # 获取游戏名称用于日志
                    try:
                        name_element = element.find_element(By.CSS_SELECTOR, "div.name")
                        game_name = name_element.text.strip()
                    except:
                        game_name = "未知游戏"
                    
                    # 确保链接是完整的URL
                    if href.startswith('/'):
                        href = base_url + href
                    
                    game_urls.add(href)
                    logger.info(f"找到游戏链接: [{game_name}] -> {href}")
            except Exception as e:
                logger.warning(f"处理游戏链接时出错: {str(e)}")
                continue
        
        logger.info(f"在页面 {url} 上总共找到 {len(game_urls)} 个游戏链接")
    
    except TimeoutException:
        logger.error(f"等待游戏卡片加载超时: {url}")
    except Exception as e:
        logger.error(f"获取游戏链接时出错: {str(e)}")
    
    # 如果没有找到任何游戏链接，记录页面源码以供调试
    if not game_urls:
        logger.error(f"在页面上未找到游戏链接: {url}")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        debug_file = f'debug_list_{timestamp}.html'
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        logger.error(f"页面源码已保存到 {debug_file}")
        
        # 保存页面截图
        screenshot_file = f'debug_screenshot_{timestamp}.png'
        driver.save_screenshot(screenshot_file)
        logger.error(f"截图已保存到 {screenshot_file}")
    
    return list(game_urls)

def get_category_url(driver, category_name):
    """通过分类名获取真实的分类URL"""
    try:
        # 访问首页
        logger.info(f"访问网站首页，查找分类: {category_name}")
        driver.get("https://html5games.com")
        time.sleep(5)  # 等待页面加载
        
        # 等待header加载完成
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "header.main .main-section"))
            )
        except TimeoutException:
            logger.error("等待页面加载超时")
            return None
            
        # 查找所有分类链接
        try:
            # 首先尝试在header.main中查找
            links = driver.find_elements(By.CSS_SELECTOR, "header.main .main-section li a")
            
            # 遍历所有链接
            for link in links:
                try:
                    link_text = link.text.strip()
                    href = link.get_attribute('href')
                    logger.info(f"找到链接: [{link_text}] -> {href}")
                    
                    # 检查链接文本或URL中是否包含分类名（不区分大小写）
                    if (category_name.lower() in link_text.lower() or 
                        f"/{category_name}/" in href):
                        logger.info(f"找到分类 {category_name} 的链接: {href}")
                        return href
                except Exception as e:
                    logger.warning(f"处理链接时出错: {str(e)}")
                    continue
            
            # 如果通过文本和href都没找到，尝试直接查找特定格式的链接
            specific_links = driver.find_elements(By.CSS_SELECTOR, f"a[href*='/{category_name}/']")
            for link in specific_links:
                try:
                    href = link.get_attribute('href')
                    if href:
                        logger.info(f"通过href找到分类 {category_name} 的链接: {href}")
                        return href
                except Exception as e:
                    logger.warning(f"处理特定链接时出错: {str(e)}")
                    continue
            
            logger.error(f"在导航菜单中未找到分类 {category_name}")
            
            # 保存页面源码以供调试
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            debug_file = f'debug_nav_{timestamp}.html'
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.error(f"导航菜单HTML已保存到 {debug_file}")
            
            return None
            
        except Exception as e:
            logger.error(f"查找分类链接时出错: {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"获取分类URL时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def scrape_category(driver, category, category_slug):
    """抓取分类中的所有游戏"""
    # 获取分类的真实URL
    category_url = get_category_url(driver, category)
    if not category_url:
        logger.error(f"无法获取分类 {category} 的URL，跳过该分类")
        return
        
    try:
        logger.info(f"访问分类页面: {category_url}")
        driver.get(category_url)
        time.sleep(5)  # 给JavaScript更多执行时间
        
        # 获取游戏链接
        game_urls = set()
        urls = get_game_links(driver, category_url)
        if urls:
            logger.info(f"在 {category_url} 找到 {len(urls)} 个游戏")
            game_urls.update(urls)
        
        # 尝试加载更多游戏
        load_more_selectors = [
            'button.load-more',
            'a.next-page',
            'button[class*="load"]',
            'div.pagination a'
        ]
        
        for selector in load_more_selectors:
            try:
                while True:
                    load_more = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    if not load_more.is_displayed():
                        break
                        
                    driver.execute_script("arguments[0].scrollIntoView(true);", load_more)
                    time.sleep(1)
                    load_more.click()
                    time.sleep(3)
                    
                    new_urls = get_game_links(driver, category_url)
                    if new_urls:
                        game_urls.update(new_urls)
                        logger.info(f"加载更多游戏，当前总共有 {len(game_urls)} 个唯一URL")
            except TimeoutException:
                logger.info(f"使用选择器 {selector} 没有更多游戏可加载")
                continue
            except Exception as e:
                logger.warning(f"加载更多游戏时出错: {str(e)}")
                continue
    
    except Exception as e:
        logger.error(f"访问 {category_url} 时出错: {str(e)}")
        return
    
    if not game_urls:
        logger.error(f"在分类 {category} 中未找到游戏")
        return
    
    logger.info(f"在分类 {category} 中总共找到 {len(game_urls)} 个游戏")
    
    for game_url in game_urls:
        # 跳过已经抓取的游戏
        if is_game_processed(game_url, category):
            logger.info(f"跳过已抓取的游戏: {game_url}")
            continue
        
        # 获取游戏数据
        game_data = get_game_data(driver, game_url, category)
        if game_data:
            # 创建 WebGameScraper 实例并保存数据
            scraper = WebGameScraper()
            scraper.save_game_data(game_data)
            scraper.__del__()  # 清理资源
            
        # 请求之间添加延迟
        time.sleep(3)

def main():
    """主函数"""
    try:
        # 初始化 ChromeDriver
        driver = setup_driver(headless=True)
        scraper = WebGameScraper()  # 创建 WebGameScraper 实例
        
        # 遍历每个分类
        for category_name, category_slug in CATEGORIES.items():
            try:
                logger.info(f"开始处理分类: {category_name}")
                
                # 获取分类URL
                category_url = get_category_url(driver, category_slug)
                if not category_url:
                    logger.error(f"无法获取分类 {category_name} 的URL")
                    continue
                
                # 获取游戏链接
                game_links = get_game_links(driver, category_url)
                if not game_links:
                    logger.error(f"在分类 {category_name} 中没有找到游戏链接")
                    continue
                
                # 处理每个游戏链接
                for link in game_links:
                    try:
                        # 检查是否已经处理过该游戏
                        if is_game_processed(link, category_name):
                            logger.info(f"游戏 {link} 已经处理过，跳过")
                            continue
                            
                        game_data = get_game_data(driver, link, category_name)
                        if game_data:
                            scraper.save_game_data(game_data)  # 使用 WebGameScraper 的 save_game_data 方法
                            mark_game_processed(link, category_name)
                            time.sleep(random.uniform(3, 7))  # 增加延迟
                    except Exception as e:
                        logger.error(f"处理游戏 {link} 时出错: {str(e)}")
                        continue
                        
            except Exception as e:
                logger.error(f"处理分类 {category_name} 时出错: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"主程序出错: {str(e)}")
    finally:
        try:
            driver.quit()
            scraper.__del__()  # 清理 WebGameScraper 资源
        except:
            pass

def is_game_processed(game_url, category):
    """检查游戏是否已经处理过"""
    try:
        category_dir = os.path.join(OUTPUT_DIR, category.lower().replace(' & ', '_').replace(' ', '_'))
        if not os.path.exists(category_dir):
            return False
            
        # 获取所有已处理的游戏文件
        processed_files = os.listdir(category_dir)
        for file in processed_files:
            if file.endswith('.json'):
                with open(os.path.join(category_dir, file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('url') == game_url:
                        return True
        return False
    except Exception as e:
        logger.error(f"检查游戏处理状态时出错: {str(e)}")
        return False

def mark_game_processed(game_url, category):
    """标记游戏为已处理"""
    # 这个函数可以为空，因为我们通过保存游戏数据来标记处理状态
    pass

if __name__ == "__main__":
    main() 