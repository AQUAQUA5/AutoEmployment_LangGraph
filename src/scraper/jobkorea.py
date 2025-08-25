import asyncio
from playwright.async_api import async_playwright, Page, expect, TimeoutError, Error
import re

async def click_available_element(page: Page, selector: str, text: str):      # 여러개중 가능한 객체 클릭
    base_locator = page.locator(f'{selector}:has-text("{text}")')
    try:
        await base_locator.nth(0).click(timeout=1000)
        return 
    except Error as e:
        pass
    try:
        await base_locator.nth(1).click(timeout=1000)
        return 
    except Error as e:
        raise e
    
async def initialize_and_goto(url: str) -> Page:        # 페이지 초기화
    p = await async_playwright().start()
    browser = await p.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(url, wait_until="domcontentloaded")
    return page

async def click_job_button_on_page(page: Page, info1, info2):       # 검색
    for con in info1:   # 2단계 검색
        await page.locator(f'p.btn_tit:has-text("{con[0]}"), button.btn_tit:has-text("{con[0]}")').click() # 둘중하나로 카테고리 선택
        await click_available_element(page=page, selector='span.radiWrap', text=con[1] )
        await click_available_element(page=page, selector='span.radiWrap', text=con[2] )

    for con in info2:
        await page.locator(f'p.btn_tit:has-text("{con[0]}"), button.btn_tit:has-text("{con[0]}")').click() # 둘중하나로 카테고리 선택
        await click_available_element(page=page, selector='span.radiWrap', text=con[1] )
            
    # 검색
    search_button = page.get_by_role("button", name="선택된 조건 검색하기")
    await search_button.click()
    
    # 검색 완료 대기
    await page.locator('#dev-btn-search[disabled]:has-text("검색완료")').wait_for(state="visible", timeout=15000)


async def search_job_list(info1, info2 ): # 최종 리스트 반환
    SEARCH_URL = "https://www.jobkorea.co.kr/recruit/joblist?menucode=search"
    job_data = []
    async with async_playwright() as p:
        page = await initialize_and_goto(SEARCH_URL)
        
        async with page.expect_response("https://www.jobkorea.co.kr/Recruit/Home/_GI_List/") as response_info:
            await click_job_button_on_page(page, info1, info2)

        
        job_num = await page.locator("#anchorGICnt_1 > li.on > button > span").text_content()

        table_locator = page.locator('#dev-gi-list > div > div.tplList.tplJobList > table')
        rows = table_locator.locator("tbody > tr")

        for row_locator in await rows.all():


            company_name = await row_locator.locator("td.tplCo > a").text_content()
            company_link = await row_locator.locator("td.tplCo > a").get_attribute("href")

            job_content = await row_locator.locator("td.tplTit > div.titBx > strong > a").text_content()
            job_link = await row_locator.locator("td.tplTit > div.titBx > strong > a").get_attribute("href")

            job_data.append([company_name, company_link, job_content, job_link])
    return job_num, job_data




async def get_role_sub_categories( main_category ): # 최종 리스트 반환
    SEARCH_URL = "https://www.jobkorea.co.kr/recruit/joblist?menucode=search"
    categories = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # False로 설정하면 브라우저 창이 보입니다.
        page = await browser.new_page()
        try:
            await page.goto(SEARCH_URL)
            await page.locator(f'p.btn_tit:has-text("직무"), button.btn_tit:has-text("직무")').click()
            await click_available_element(page=page, selector='span.radiWrap', text=main_category)
            await page.wait_for_selector('div.nano-content.dev-sub')
            n = 0 if main_category == '기획·전략' else 1
            data = page.locator('div.nano-content.dev-sub').nth(0).locator('> *').nth(n).locator('li')
            for li_locator in await data.all():
                a = await li_locator.locator("input").get_attribute("data-name")
                categories.append(a)
            return categories
        finally:
            await browser.close()
    return categories

       



