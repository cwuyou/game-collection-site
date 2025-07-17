import os
import json
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urljoin
import requests
from datetime import datetime
import urllib3
import ssl

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gamedistribution_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GameDistributionScraper:
    def __init__(self):
        self.base_url = "https://gamedistribution.com/games/"
        self.driver = None
        self.output_dir = os.path.join("scraped_data", "gamedistribution", "puzzle")
        os.makedirs(self.output_dir, exist_ok=True)

    def setup_driver(self):
        """设置Chrome浏览器驱动"""
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # 暂时关闭无头模式便于调试
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--ignore-certificate-errors')  # 忽略证书错误
        options.add_argument('--ignore-ssl-errors')  # 忽略SSL错误
        options.add_argument('--disable-web-security')  # 禁用网页安全性检查
        options.add_argument('--allow-running-insecure-content')  # 允许运行不安全内容
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_size(1920, 1080)

    def wait_for_element(self, by, value, timeout=20):  # 增加等待时间
        """等待元素加载"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            logger.error(f"等待元素超时: {value}")
            return None

    def apply_puzzle_filter(self):
        """应用Puzzle过滤器"""
        try:
            # 等待页面完全加载
            time.sleep(5)  # 增加初始等待时间
            
            # 等待并点击Filters按钮
            filters_button = self.wait_for_element(By.XPATH, "//button[text()='Filters']")
            if filters_button:
                filters_button.click()
                logger.info("点击Filters按钮")
                time.sleep(2)
            
            # 等待并点击Genres展开按钮
            genres_button = self.wait_for_element(By.XPATH, "//button[contains(@class, 'flex') and .//span[text()='Genres']]")
            if genres_button:
                genres_button.click()
                logger.info("点击Genres展开按钮")
                time.sleep(2)
            
            # 查找并点击Puzzle选项
            puzzle_option = self.wait_for_element(By.XPATH, "//div[contains(@class, 'flex')]//span[text()='Puzzle']")
            if puzzle_option:
                puzzle_option.click()
                logger.info("选择Puzzle选项")
                time.sleep(2)
            
            # 点击Apply按钮
            apply_button = self.wait_for_element(By.XPATH, "//button[text()='Apply']")
            if apply_button:
                apply_button.click()
                logger.info("点击Apply按钮")
                time.sleep(5)  # 等待页面刷新
                return True
                
            return False
        except Exception as e:
            logger.error(f"应用过滤器时出错: {str(e)}")
            return False

    def get_game_cards(self):
        """获取游戏卡片列表"""
        try:
            # 等待游戏卡片加载
            time.sleep(5)  # 增加等待时间
            
            # 使用更精确的选择器
            game_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='/games/']")
            
            # 获取href属性并过滤无效链接
            urls = []
            for link in game_links:
                href = link.get_attribute('href')
                if href and '/games/' in href and not href.endswith('/games/'):
                    full_url = urljoin("https://gamedistribution.com", href)
                    if full_url not in urls:  # 去重
                        urls.append(full_url)
            
            logger.info(f"找到 {len(urls)} 个游戏链接")
            return urls
        except Exception as e:
            logger.error(f"获取游戏卡片时出错: {str(e)}")
            return []

    def scroll_to_load_more(self):
        """滚动页面加载更多游戏"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                # 滚动到底部
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # 等待内容加载
                
                # 计算新的滚动高度
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
        except Exception as e:
            logger.error(f"滚动加载更多时出错: {str(e)}")

    def get_game_data(self, game_url):
        """获取单个游戏的详细信息"""
        try:
            self.driver.get(game_url)
            time.sleep(2)  # 等待页面加载

            # 获取游戏标题
            title = self.wait_for_element(By.CSS_SELECTOR, "h1").text

            # 获取游戏描述
            description = ""
            desc_element = self.wait_for_element(By.XPATH, "//div[contains(text(), 'DESCRIPTION')]/following-sibling::div")
            if desc_element:
                description = desc_element.text

            # 获取游戏说明
            instructions = ""
            inst_element = self.wait_for_element(By.XPATH, "//div[contains(text(), 'INSTRUCTIONS')]/following-sibling::div")
            if inst_element:
                instructions = inst_element.text

            # 获取嵌入代码
            iframe_url = ""
            embed_element = self.wait_for_element(By.XPATH, "//div[contains(text(), 'EMBED')]/following-sibling::div//iframe")
            if embed_element:
                iframe_url = embed_element.get_attribute('src')

            # 获取标签
            tags = []
            tag_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.Tags div")
            tags = [tag.text for tag in tag_elements if tag.text]

            # 获取类别
            categories = []
            genre_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.Genres div")
            categories = [genre.text for genre in genre_elements if genre.text]

            # 获取预览图片
            preview_image = ""
            img_element = self.wait_for_element(By.CSS_SELECTOR, "div.THUMBNAILS img")
            if img_element:
                preview_image = img_element.get_attribute('src')

            # 构建游戏数据
            game_data = {
                "url": game_url,
                "title": title,
                "description": description,
                "instructions": instructions,
                "iframe_url": iframe_url,
                "preview_image": preview_image,
                "categories": categories,
                "tags": tags,
                "scraped_at": datetime.now().isoformat()
            }

            return game_data
        except Exception as e:
            logger.error(f"获取游戏数据时出错 {game_url}: {str(e)}")
            return None

    def save_game_data(self, game_data):
        """保存游戏数据到JSON文件"""
        try:
            if not game_data or not game_data.get('title'):
                return False

            # 生成文件名
            filename = f"game_{game_data['title'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.output_dir, filename)

            # 保存JSON文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"保存游戏数据到文件: {filepath}")
            return True
        except Exception as e:
            logger.error(f"保存游戏数据时出错: {str(e)}")
            return False

    def run(self):
        """运行爬虫"""
        try:
            self.setup_driver()
            logger.info("启动爬虫")

            # 打开主页并等待加载
            self.driver.get(self.base_url)
            time.sleep(5)  # 增加初始等待时间
            logger.info("打开游戏列表页面")

            # 应用Puzzle过滤器
            if not self.apply_puzzle_filter():
                logger.error("应用过滤器失败")
                return

            # 滚动加载更多游戏
            self.scroll_to_load_more()

            # 获取所有游戏链接
            game_urls = self.get_game_cards()
            logger.info(f"找到 {len(game_urls)} 个游戏链接")

            # 爬取每个游戏的数据
            for url in game_urls:
                try:
                    logger.info(f"正在爬取游戏: {url}")
                    game_data = self.get_game_data(url)
                    if game_data:
                        self.save_game_data(game_data)
                    time.sleep(2)  # 增加间隔时间
                except Exception as e:
                    logger.error(f"处理游戏时出错 {url}: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"爬虫运行出错: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()
            logger.info("爬虫完成")

if __name__ == "__main__":
    scraper = GameDistributionScraper()
    scraper.run() 