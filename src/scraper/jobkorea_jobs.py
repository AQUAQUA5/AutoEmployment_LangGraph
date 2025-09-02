import asyncio
from playwright.async_api import async_playwright, expect, Error
import re


async def click_category(category , main_box, print_procces):
    try:
        botton =  main_box.get_by_text(text=category).filter(visible=True)
        await botton.click()
        if print_procces:
            print('직무 버튼 클릭 성공')
    except Exception as e:
        print('직무 버튼 클릭 실패 :', e)

async def click_option_1(option , main_box, print_procces):
    try:
        botton =  main_box.get_by_text(text=option, exact =True).filter(visible=True)
        await botton.nth(1).click()
    except Exception as e:
        print('직무 버튼 클릭 실패 :', e)



async def get_searchedJob( options , hide_browser = False, print_procces=True):
    SEARCH_URL = "https://www.jobkorea.co.kr/recruit/joblist?menucode=search"
    async with async_playwright() as p:
        # 페이지 접속
        try:
            browser = await p.chromium.launch(headless=hide_browser) # False는 브라우저창 보임
            page = await browser.new_page()
            page.set_default_timeout(30000)
            await page.goto(SEARCH_URL)
            if print_procces:
                print('페이지 접속 성공')
        except Exception as e:
            print('페이지 접속 실패 :', e)

        # 메인박스 탐색
        try:
            main_box =  page.locator('div').filter(has_text='채용공고 상세검색').filter(has_text='직무').filter(has_text='근무지역').filter(has_text='직급/직책/급여')
            main_box = main_box.filter(has_not_text='TOP100').filter(has_not_text='TOP 헤드라인 채용관').filter(visible=True)
            await expect(main_box).to_be_visible()
            if print_procces:
                print('메인박스 탐색 성공')
        except Exception as e:
            print('메인박스 탐색 실패 :', e)

        # 직무 버튼 클릭
        for option in options:
            await click_category(option[0], main_box, print_procces)
            await click_option_1(option[1], main_box, print_procces)
        await page.pause()
    return 1




# async def get_categories(options , hide_browser = False, print_procces=True):
#     return
#     SEARCH_URL = "https://www.jobkorea.co.kr/recruit/joblist?menucode=search"
#     async with async_playwright() as p:
#         # 페이지 접속
#         try:
#             browser = await p.chromium.launch(headless=hide_browser) # False는 브라우저창 보임
#             page = await browser.new_page()
#             page.set_default_timeout(10000)
#             await page.goto(SEARCH_URL)
#             if print_procces:
#                 print('페이지 접속 성공')
#         except Exception as e:
#             print('페이지 접속 실패 :', e)

#         # 메인박스 탐색
#         try:
#             main_box =  page.locator('div').filter(has_text='채용공고 상세검색').filter(has_text='직무').filter(has_text='근무지역').filter(has_text='직급/직책/급여')
#             main_box = main_box.filter(has_not_text='TOP100').filter(has_not_text='TOP 헤드라인 채용관').filter(visible=True)
#             await expect(main_box).to_be_visible()
#             if print_procces:
#                 print('메인박스 탐색 성공')
#         except Exception as e:
#             print('메인박스 탐색 실패 :', e)

#         # 직무 버튼 클릭
#         for option in options:
#             await click_category(option[0], main_box, print_procces)


#         # 사용자 직무 선택
#         try:
#             all_elements = await main_box.get_by_text(text=role).filter(visible=True).all()
#             button = main_box.get_by_text(text=role).filter(visible=True)
#             await button.highlight()
#             for i, element_locator in enumerate(all_elements):
#                 # 각 요소의 텍스트 내용과 HTML 내용을 출력
#                 element_text = await element_locator.inner_text()
#                 element_inner_html = await element_locator.inner_html()
#                 element_outer_html = await element_locator.evaluate("el => el.outerHTML")  # 요소 자체 포함 전체 HTML [9]

#                 print(f"\n--- {i+1}번째 요소 ---")
#                 print(f"  [텍스트 내용]: {element_text}")
#                 print(f"  [innerHTML]: {element_inner_html[:200]}...")
#                 print(f"  [outerHTML]: {element_outer_html[:200]}...")

#             await page.pause()
#             if print_procces:
#                 print('사용자 직무 선택 성공')
#         except Exception as e:
#             print('사용자 직무 선택 실패 :', e)

        
#     return all_elements