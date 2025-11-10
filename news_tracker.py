"""
News Tracker - Monitors Georgian news sources for parenting-related content
"""
import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime, timedelta
import json
import os
import config

class NewsTracker:
    def __init__(self):
        self.sources = config.NEWS_SOURCES
        self.keywords = [
            'მშობელი', 'მშობლობა', 'ბავშვი', 'ბავშვები', 
            'სკოლა', 'განათლება', 'აღზრდა', 'ფსიქოლოგია',
            'დაბადება', 'სკოლამდელი', 'ბაღი', 'მასწავლებელი',
            'კრიმინალი ბავშვები', 'ძალადობა ბავშვებზე'
        ]
        self.cache_file = f'{config.DATA_DIR}/news_cache.json'
        self.load_cache()
    
    def load_cache(self):
        """Load cached news to avoid duplicates"""
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
        except:
            self.cache = {'seen_urls': [], 'last_check': None}
    
    def save_cache(self):
        """Save news cache"""
        os.makedirs(config.DATA_DIR, exist_ok=True)
        self.cache['last_check'] = datetime.now().isoformat()
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def check_news(self):
        """Check all sources for relevant news"""
        all_news = []
        
        # Check InterPressNews
        ipn_news = self._check_interpressnews()
        all_news.extend(ipn_news)
        
        # Check Netgazeti
        ng_news = self._check_netgazeti()
        all_news.extend(ng_news)
        
        # Check Formula
        formula_news = self._check_formula()
        all_news.extend(formula_news)
        
        # Check ON.ge
        on_news = self._check_onge()
        all_news.extend(on_news)
        
        # Filter out already seen news
        new_news = [n for n in all_news if n['url'] not in self.cache['seen_urls']]
        
        # Add to cache
        for news in new_news:
            self.cache['seen_urls'].append(news['url'])
        
        # Keep cache size manageable (last 500 URLs)
        if len(self.cache['seen_urls']) > 500:
            self.cache['seen_urls'] = self.cache['seen_urls'][-500:]
        
        self.save_cache()
        
        return new_news[:10]  # Return top 10 most relevant
    
    def _check_interpressnews(self):
        """Check InterPressNews.ge"""
        news = []
        try:
            # Try education section
            url = 'https://www.interpressnews.ge/ka/sections/1-sazogadoeba/'
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('article', limit=20)
            for article in articles:
                title_elem = article.find('h3') or article.find('h2')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if self._is_relevant(title):
                        link_elem = title_elem.find('a')
                        if link_elem:
                            link = 'https://www.interpressnews.ge' + link_elem.get('href', '')
                            news.append({
                                'title': title,
                                'url': link,
                                'source': 'InterPressNews',
                                'date': datetime.now().isoformat()
                            })
        except Exception as e:
            print(f"Error checking InterPressNews: {e}")
        
        return news
    
    def _check_netgazeti(self):
        """Check Netgazeti.ge"""
        news = []
        try:
            url = 'https://www.netgazeti.ge/life/'
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('div', class_='article-item', limit=20)
            for article in articles:
                title_elem = article.find('h3') or article.find('h2')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if self._is_relevant(title):
                        link_elem = article.find('a')
                        if link_elem:
                            link = link_elem.get('href', '')
                            if not link.startswith('http'):
                                link = 'https://www.netgazeti.ge' + link
                            news.append({
                                'title': title,
                                'url': link,
                                'source': 'Netgazeti',
                                'date': datetime.now().isoformat()
                            })
        except Exception as e:
            print(f"Error checking Netgazeti: {e}")
        
        return news
    
    def _check_formula(self):
        """Check Formula.ge"""
        news = []
        try:
            url = 'https://www.formula.ge/kategoria/sazogadoeba'
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all('article', limit=20)
            for article in articles:
                title_elem = article.find('h3') or article.find('h2')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if self._is_relevant(title):
                        link_elem = article.find('a')
                        if link_elem:
                            link = link_elem.get('href', '')
                            if not link.startswith('http'):
                                link = 'https://www.formula.ge' + link
                            news.append({
                                'title': title,
                                'url': link,
                                'source': 'Formula',
                                'date': datetime.now().isoformat()
                            })
        except Exception as e:
            print(f"Error checking Formula: {e}")
        
        return news
    
    def _check_onge(self):
        """Check ON.ge"""
        news = []
        try:
            url = 'https://on.ge/story'
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = soup.find_all(['article', 'div'], class_=['story', 'news-item'], limit=20)
            for article in articles:
                title_elem = article.find(['h1', 'h2', 'h3'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if self._is_relevant(title):
                        link_elem = article.find('a')
                        if link_elem:
                            link = link_elem.get('href', '')
                            if not link.startswith('http'):
                                link = 'https://on.ge' + link
                            news.append({
                                'title': title,
                                'url': link,
                                'source': 'ON.ge',
                                'date': datetime.now().isoformat()
                            })
        except Exception as e:
            print(f"Error checking ON.ge: {e}")
        
        return news
    
    def _is_relevant(self, text):
        """Check if text contains relevant keywords"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.keywords)
    
    def format_news_context(self, news_list):
        """Format news for Claude API context"""
        if not news_list:
            return None
        
        context = "ბოლოდროინდელი ნიუსები:\n\n"
        for idx, news in enumerate(news_list[:5], 1):
            context += f"{idx}. {news['title']}\n"
            context += f"   წყარო: {news['source']}\n"
            context += f"   ლინკი: {news['url']}\n\n"
        
        return context
    
    def should_check_news_today(self):
        """Determine if we should check news today"""
        today = datetime.now()
        weekday = today.weekday()  # 0=Monday, 6=Sunday
        
        return weekday in config.NEWS_CHECK_DAYS
