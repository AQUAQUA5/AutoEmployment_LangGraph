import asyncio
from playwright.async_api import async_playwright, expect
import re

async def get_role_sub_categories( role , hide_browser = False, print_procces=True):
    SEARCH_URL = "https://www.jobkorea.co.kr/recruit/joblist?menucode=search"
    async with async_playwright() as p:
        # 페이지 접속
        try:
            browser = await p.chromium.launch(headless=hide_browser) # False는 브라우저창 보임
            page = await browser.new_page()
            page.set_default_timeout(10000)
            await page.goto(SEARCH_URL)
            if print_procces:
                print('페이지 접속 성공')
        except Exception as e:
            print('페이지 접속 실패 :', e)

        # 메인박스 탐색
        try:
            main_box =  page.locator('div').filter(has_text='채용공고 상세검색').filter(has_text='직무').filter(has_text='근무지역').filter(has_text='직급/직책/급여')
            main_box = main_box.filter(has_not_text='TOP100').filter(has_not_text='TOP 헤드라인 채용관')
            await expect(main_box).to_be_visible()
            if print_procces:
                print('메인박스 탐색 성공')
        except Exception as e:
            print('메인박스 탐색 실패 :', e)

        # 직무 버튼 클릭
        try:
            botton =  main_box.get_by_text(text='직무').filter(visible=True)
            await botton.click()
            if print_procces:
                print('직무 버튼 클릭 성공')
        except Exception as e:
            print('직무 버튼 클릭 실패 :', e)

        # 서브 카테고리 추출
        try:
            if role !='기획·전략':
                


            await page.pause()
        except Exception as e:
            print('오류 발생', e)
        return 