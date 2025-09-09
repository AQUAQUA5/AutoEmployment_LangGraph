from src.scraper.src.browser_manager import BrowserManager
from rebrowser_playwright.async_api import expect
import re

async def get_searchedJob(options, hide_browser=False, print_procces=True):
    SEARCH_URL = "https://www.jobkorea.co.kr/recruit/joblist?menucode=search"
    PRINT_PROCCES = True
    async with BrowserManager(hide_browser=hide_browser) as browser_manager:
        # 페이지 접속
        try:
            page = await browser_manager.new_page()
            page.set_default_timeout(30000)
            await page.goto(SEARCH_URL, wait_until="domcontentloaded")
            if print_procces:
                print('페이지 접속 성공')
        except Exception as e:
            print('페이지 접속 실패 :', e)
            await browser_manager.close()
            return False

        # 메인박스 탐색
        main_box = await search_mainbox(page, print_procces)
        # 직무 버튼 클릭
        try:
            for key, values in options.items():
                if key=='우대전공':
                    continue
                    
                if not values:
                    continue
                await click_option_not_exact(key, main_box, print_procces)
                for val in values:
                    if type(val)==str:
                        await click_option_not_exact(val, main_box, print_procces)
                    else:
                        await click_option_not_exact(val['대분류'], main_box, print_procces)
                        for mc in val['중분류']:
                            await click_option_not_exact(mc, main_box, print_procces)
        
            await page.pause()
            await browser_manager.close()
            
        except Exception as e:
            print('크롤링 중 오류 발생:', e)
            return False

    return True

async def search_major()

async def search_mainbox(page, print_procces):
    try:
        main_box =  page.locator('div').filter(has_text='채용공고 상세검색').filter(has_text='직무').filter(has_text='근무지역').filter(has_text='직급/직책/급여')
        main_box = main_box.filter(has_not_text='TOP100').filter(has_not_text='TOP 헤드라인 채용관').filter(visible=True)
        await expect(main_box).to_be_visible()
        if print_procces:
            print('메인박스 탐색 성공')
        return main_box
    except Exception as e:
        print('메인박스 탐색 실패 :', e)

async def click_category(category , main_box, print_procces):
    try:
        botton =  main_box.get_by_text(text=category).filter(visible=True)
        await botton.click()
        if print_procces:
            print(f'{category} 버튼 클릭 성공')
    except Exception as e:
        print(f'{category} 버튼 클릭 실패', e)

async def click_option_exact(option , main_box, print_procces):
    clean_option = re.escape(option)
    pattern = re.compile(rf'^[\s\'"]*{clean_option}[\s\'"]*$', re.IGNORECASE)
    try:
        botton =  main_box.get_by_text(text=pattern, exact = True).filter(visible=True)
        cnt = await botton.count()
        print(f'{option} 버튼수 : {cnt}')
        if cnt == 0:
            raise RuntimeError(f"{option} 탐색 실패")
        elif cnt == 1:
            await botton.first.click()
        else:
            try:
                await botton.nth(1).click(timeout=1000)
            except:
                for i in range(cnt):
                    try:
                        await botton.nth(i).click(timeout=1000)
                        break
                    except:
                        pass
                raise RuntimeError(f"{option} 클릭 실패")
        if print_procces:
            print(f"{option} 버튼 클릭 성공")
    except Exception as e:
        print(f"{option} 버튼 클릭 실패 :", e)

async def click_option_not_exact(option , main_box, print_procces):
    try:
        botton =  main_box.get_by_text(text=option).filter(visible=True)
        cnt = await botton.count()
        print(f'{option} 버튼수 : {cnt}')
        if cnt == 0:
            raise RuntimeError(f"{option} 탐색 실패")
        elif cnt == 1:
            await botton.first.click()
        else:
            try:
                await botton.nth(1).click(timeout=1000)
            except:
                for i in range(cnt):
                    try:
                        await botton.nth(i).click(timeout=1000)
                        break
                    except:
                        pass
                raise RuntimeError(f"{option} 클릭 실패")
        if print_procces:
            print(f"{option} 버튼 클릭 성공")
    except Exception as e:
        print(f"{option} 버튼 클릭 실패 :", e)

