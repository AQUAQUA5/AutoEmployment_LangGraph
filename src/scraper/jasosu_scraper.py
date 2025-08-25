import asyncio
from playwright.async_api import async_playwright, Page, expect, TimeoutError, Error
import re

async def get_jasosu( role ): 
    SEARCH_URL = "https://www.jobkorea.co.kr/starter/passassay"
    links = []
    if isinstance(role, list) and role:
        role = role[0]
    else:
        role = role
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # False로 설정하면 브라우저 창이 보입니다.
        page = await browser.new_page()
        try:
            await page.goto(SEARCH_URL)
            await page.locator('body > div.toolTipCont.fullLy.firstPopUp > div > button').click()
            await page.locator(f'li.itemCheck[data-type="Jobtype_B"][data-value*="{role}"]').click()
            await page.locator(f'li.itemCheck.allCheck[data-type="Jobtype"][data-value*="{role}-전체"]').locator('label > i').click()
            async with page.expect_response("https://asia.creativecdn.com/tags/v2?type=json") as response_info:
                search_button = page.get_by_role("button", name="선택 조건으로 검색")
                await search_button.click()
            data = page.locator('#container > div.stContainer > div.starListsWrap.ctTarget > ul').locator('li')
            for li_locator in await data.all():
                a = await li_locator.locator("a").nth(0).get_attribute("href")
                links.append(a)
        finally:
            await browser.close()
    return links

async def get_jasosu_context( url ):
    SEARCH_URL = "https://www.jobkorea.co.kr/" + url
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # False로 설정하면 브라우저 창이 보입니다.
        page = await browser.new_page()
        try:
            await page.goto(SEARCH_URL)
            title = await page.locator('#container > div.stContainer > div.selfTopBx > div.viewTitWrap > h2 > strong > a').text_content()
            q1 = await page.locator('#container > div.stContainer > div.selfQnaWrap > dl > dt:nth-child(1) > button > span.tx').text_content()
            a1 = await page.locator('#container > div.stContainer > div.selfQnaWrap > dl > dd:nth-child(2) > div').text_content()
            q2 = await page.locator('#container > div.stContainer > div.selfQnaWrap > dl > dt:nth-child(3) > button > span.tx').text_content()
            a2 = await page.locator('#container > div.stContainer > div.selfQnaWrap > dl > dd:nth-child(4) > div').text_content()

            # q3 = await page.locator('#container > div.stContainer > div.selfQnaWrap > dl > dt.next.on > button > span.tx').text_content()
            # q3 = await page.locator('#container > div.stContainer > div.selfQnaWrap > dl > dt.next.on > button > span.tx').click()
            # a3 = await page.locator('#container > div.stContainer > div.selfQnaWrap > dl > dd:nth-child(6) > div').text_content()

            # q4 = await page.locator('#container > div.stContainer > div.selfQnaWrap > dl > dt.next.on > button > span.tx').text_content()
            # a4 = await page.locator('#container > div.stContainer > div.selfQnaWrap > dl > dt.next.on > button > span.tx').click()
            # a4 = await page.locator('#container > div.stContainer > div.selfQnaWrap > dl > dd:nth-child(6) > div').text_content()
            contents = 'title:' + title + ' Q1:' + q1 + ' A1:' + a1 + ' Q2:' + q2 + ' A2:' + a2
        finally:
            await browser.close()
    return contents






