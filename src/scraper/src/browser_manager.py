from rebrowser_playwright.async_api import async_playwright, expect, BrowserContext, Page
from typing import Dict
from src.scraper.src.profiles1 import USER_PROFILE, BROWSER_ARGS, get_fingerprint_script

class BrowserManager:
    def __init__(self, profile: Dict = None, hide_browser: bool = False):
        self.profile = profile or USER_PROFILE
        self.hide_browser = hide_browser
        self.playwright = None
        self.browser = None
        self.context = None
    
    async def __aenter__(self):
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def start(self) -> BrowserContext:
        self.playwright = await async_playwright().start()
        
        launch_options = {
            'headless': self.hide_browser,
            'args': BROWSER_ARGS,
            'channel': 'chrome',
        }
        
        self.browser = await self.playwright.chromium.launch(**launch_options)
        
        self.context = await self._create_context()
        
        return self.context
    
    async def _create_context(self) -> BrowserContext:
        context_options = {
            'viewport': self.profile['viewport'],
            'user_agent': self.profile['user_agent'],
            'locale': self.profile['locale'],
            'timezone_id': self.profile['timezone_id'],
            'geolocation': self.profile['geolocation'],
            'permissions': self.profile['permissions'],
            'extra_http_headers': self.profile['extra_http_headers'],
            'device_scale_factor': self.profile['device_scale_factor'],
            'is_mobile': self.profile['is_mobile'],
            'has_touch': self.profile['has_touch']
        }
        
        context = await self.browser.new_context(**context_options)
        
        # 수정된 fingerprint script 적용
        await context.add_init_script(get_fingerprint_script())
        
        return context
    
    async def new_page(self) -> Page:
        """새 페이지 생성"""
        if not self.context:
            raise RuntimeError("브라우저가 시작되지 않았습니다. start() 메서드를 먼저 호출하세요.")
        
        page = await self.context.new_page()
        
        # 추가적인 페이지 설정 (자연스러운 행동을 위해)
        await self._setup_page(page)
        
        return page
    
    async def _setup_page(self, page: Page):
        """페이지별 추가 설정 - 자연스러운 사용자 행동 시뮬레이션"""
        # 페이지 로드 타임아웃 설정
        page.set_default_timeout(30000)  # 30초
        
        # 자연스러운 지연 시간 추가
        await page.wait_for_timeout(500)
        
        # 자연스러운 마우스 움직임 (실제 사용자 행동 모방)
        try:
            # 페이지 중앙 근처로 마우스 이동
            viewport = self.profile['viewport']
            center_x = viewport['width'] // 2
            center_y = viewport['height'] // 2
            
            # 자연스러운 마우스 움직임
            await page.mouse.move(center_x - 50, center_y - 30)
            await page.wait_for_timeout(100)
            await page.mouse.move(center_x + 20, center_y + 10)
            await page.wait_for_timeout(150)
            
        except Exception:
            # 마우스 움직임 실패 시 무시 (중요하지 않음)
            pass
    
    async def close(self):
        """브라우저 종료"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()