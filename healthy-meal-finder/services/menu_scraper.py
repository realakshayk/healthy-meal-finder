# services/menu_scraper.py

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from playwright.async_api import async_playwright, Browser, Page
import re
from urllib.parse import urljoin, urlparse
import time

logger = logging.getLogger(__name__)

class MenuScraper:
    """
    Web scraper for extracting menu text from restaurant websites using Playwright.
    
    This service handles:
    - Browser automation with Playwright
    - Menu text extraction from various website structures
    - Error handling for failed scraping attempts
    - Rate limiting and respectful scraping
    """
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.playwright = None
        self.timeout = 10000  # 10 seconds timeout
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
    async def initialize(self):
        """Initialize the Playwright browser instance."""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            logger.info("✅ Playwright browser initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Playwright: {e}")
            raise
    
    async def close(self):
        """Close the browser and cleanup resources."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("✅ Playwright browser closed")
    
    async def scrape_restaurant_menu(self, restaurant_info: Dict) -> Optional[str]:
        """
        Scrape menu text from a restaurant's website.
        
        Args:
            restaurant_info: Dictionary containing restaurant information including website URL
            
        Returns:
            Extracted menu text or None if scraping failed
        """
        if not self.browser:
            await self.initialize()
        
        website_url = restaurant_info.get('website')
        if not website_url:
            logger.warning(f"No website URL found for restaurant: {restaurant_info.get('name', 'Unknown')}")
            return None
        
        # Normalize the URL
        if not website_url.startswith(('http://', 'https://')):
            website_url = 'https://' + website_url
        
        try:
            page = await self.browser.new_page()
            await page.set_user_agent(self.user_agent)
            
            # Set viewport and timeout
            await page.set_viewport_size({"width": 1280, "height": 720})
            page.set_default_timeout(self.timeout)
            
            logger.info(f"🌐 Scraping menu from: {website_url}")
            
            # Navigate to the website
            await page.goto(website_url, wait_until="domcontentloaded")
            
            # Wait a bit for dynamic content to load
            await asyncio.sleep(2)
            
            # Extract menu text using multiple strategies
            menu_text = await self._extract_menu_text(page)
            
            if menu_text:
                logger.info(f"✅ Successfully scraped menu from {website_url} ({len(menu_text)} characters)")
                return menu_text
            else:
                logger.warning(f"⚠️ No menu text found on {website_url}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to scrape {website_url}: {e}")
            return None
        finally:
            if 'page' in locals():
                await page.close()
    
    async def _extract_menu_text(self, page: Page) -> Optional[str]:
        """
        Extract menu text from a webpage using multiple strategies.
        
        Args:
            page: Playwright page object
            
        Returns:
            Extracted menu text or None
        """
        # Strategy 1: Look for common menu selectors
        menu_selectors = [
            '[class*="menu"]',
            '[id*="menu"]',
            '[class*="food"]',
            '[id*="food"]',
            '[class*="dish"]',
            '[id*="dish"]',
            '[class*="item"]',
            '[id*="item"]',
            'nav',
            'main',
            'section'
        ]
        
        for selector in menu_selectors:
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    text = await element.text_content()
                    if text and self._is_menu_content(text):
                        return self._clean_text(text)
            except Exception:
                continue
        
        # Strategy 2: Extract all text and filter for menu-like content
        try:
            all_text = await page.text_content('body')
            if all_text:
                # Look for menu-like patterns
                menu_sections = self._extract_menu_sections(all_text)
                if menu_sections:
                    return '\n'.join(menu_sections)
        except Exception:
            pass
        
        # Strategy 3: Fallback to main content
        try:
            main_content = await page.text_content('main') or await page.text_content('article')
            if main_content and self._is_menu_content(main_content):
                return self._clean_text(main_content)
        except Exception:
            pass
        
        return None
    
    def _is_menu_content(self, text: str) -> bool:
        """
        Determine if text content looks like a menu.
        
        Args:
            text: Text content to analyze
            
        Returns:
            True if content appears to be menu-like
        """
        if not text or len(text.strip()) < 50:
            return False
        
        # Menu indicators
        menu_keywords = [
            'menu', 'food', 'dish', 'meal', 'entree', 'appetizer', 'dessert',
            'breakfast', 'lunch', 'dinner', 'special', 'price', '$', '€', '£',
            'calories', 'protein', 'carbs', 'fat', 'vegetarian', 'vegan', 'gluten'
        ]
        
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in menu_keywords if keyword in text_lower)
        
        # Price patterns
        price_pattern = r'\$[\d,]+\.?\d*'
        price_count = len(re.findall(price_pattern, text))
        
        # Menu-like structure indicators
        has_prices = price_count > 0
        has_keywords = keyword_count >= 3
        has_structure = len(text.split('\n')) > 5
        
        return has_prices or (has_keywords and has_structure)
    
    def _extract_menu_sections(self, text: str) -> List[str]:
        """
        Extract menu-like sections from full page text.
        
        Args:
            text: Full page text
            
        Returns:
            List of menu-like text sections
        """
        lines = text.split('\n')
        menu_sections = []
        current_section = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line looks like menu content
            if self._is_menu_line(line):
                current_section.append(line)
            elif current_section:
                # End of menu section
                if len(current_section) > 2:  # At least 3 lines
                    menu_sections.append('\n'.join(current_section))
                current_section = []
        
        # Add final section if it exists
        if current_section and len(current_section) > 2:
            menu_sections.append('\n'.join(current_section))
        
        return menu_sections
    
    def _is_menu_line(self, line: str) -> bool:
        """
        Determine if a single line looks like menu content.
        
        Args:
            line: Single line of text
            
        Returns:
            True if line appears to be menu content
        """
        if not line or len(line) < 3:
            return False
        
        # Menu line indicators
        has_price = bool(re.search(r'\$[\d,]+\.?\d*', line))
        has_food_words = any(word in line.lower() for word in [
            'chicken', 'beef', 'salmon', 'pasta', 'salad', 'soup', 'burger',
            'pizza', 'steak', 'fish', 'vegetable', 'rice', 'quinoa', 'tofu'
        ])
        has_description = len(line) > 10 and any(word in line.lower() for word in [
            'with', 'and', 'served', 'topped', 'dressed', 'grilled', 'roasted'
        ])
        
        return has_price or has_food_words or has_description
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common web artifacts
        text = re.sub(r'(Menu|Home|About|Contact|Order|Reserve|Book)', '', text, flags=re.IGNORECASE)
        
        # Remove navigation elements
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 2:
                # Skip navigation-like lines
                if not any(nav_word in line.lower() for nav_word in [
                    'home', 'about', 'contact', 'order', 'reserve', 'book', 'login', 'sign up'
                ]):
                    cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    async def scrape_multiple_restaurants(self, restaurants: List[Dict]) -> Dict[str, str]:
        """
        Scrape menus from multiple restaurants concurrently.
        
        Args:
            restaurants: List of restaurant dictionaries
            
        Returns:
            Dictionary mapping restaurant names to menu text
        """
        if not self.browser:
            await self.initialize()
        
        results = {}
        
        # Scrape restaurants concurrently (with rate limiting)
        semaphore = asyncio.Semaphore(3)  # Limit concurrent requests
        
        async def scrape_single(restaurant):
            async with semaphore:
                menu_text = await self.scrape_restaurant_menu(restaurant)
                if menu_text:
                    results[restaurant['name']] = menu_text
                # Rate limiting - wait between requests
                await asyncio.sleep(1)
        
        # Create tasks for all restaurants
        tasks = [scrape_single(restaurant) for restaurant in restaurants]
        
        # Execute all scraping tasks
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info(f"✅ Scraped menus from {len(results)} out of {len(restaurants)} restaurants")
        return results

# Global scraper instance
menu_scraper = MenuScraper() 