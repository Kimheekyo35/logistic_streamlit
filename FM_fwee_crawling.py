from playwright.sync_api import sync_playwright, Page
from pathlib import Path
import time
import os
from dotenv import load_dotenv
from datetime import datetime
import sys
from FM_iframe_to_pdf import download_pdf

load_dotenv()

PLAYWRIGHT_NAV_TIMEOUT_MS = int("30000")
PLAYWRIGHT_SELECTOR_TIMEOUT_MS = int("30000")

fwee_countrylist = {
    "Singapore" : "https://seller.shopee.kr/portal/sale/order/pre-declare/generate?cnsc_shop_id=1147332494",
    "TaiwanXiapi" : "https://seller.shopee.kr/portal/sale/order/pre-declare/generate?cnsc_shop_id=1152063847",
    "Thailand" : "https://seller.shopee.kr/portal/sale/order/pre-declare/generate?cnsc_shop_id=1152063845",
    "Malaysia" : "https://seller.shopee.kr/portal/sale/order/pre-declare/generate?cnsc_shop_id=1152063834",
    "Philippines": "https://seller.shopee.kr/portal/sale/order/pre-declare/generate?cnsc_shop_id=1152063836"
}

dt = datetime.now()
KST = dt.strftime("%Y_%m_%d")
KST_hs = dt.strftime("%H%M%S")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(storage_state="fwee_shopee_state.json")
    page = context.new_page()
    page.goto("https://seller.shopee.kr/?cnsc_shop_id=1152063836",wait_until="domcontentloaded",timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)

    country = input()

    try:
        if country in fwee_countrylist:
            page.goto(fwee_countrylist[country],timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)
            print(f"{country} 열었음")
            page.wait_for_timeout(5000)

            number = str(1)
            # Daily quantity에 1입력
            page.locator("input.eds-input__input[placeholder='Input number']").type(number,delay=110)
            
            # Submit 버튼 누르기
            submit = page.locator("div.first-mile-generate > button")
            print(submit.inner_text().strip())

            # pickup_code 가져오기
            pickup_code_rt = page.locator("div.eds-scrollbar__content > table > tbody > tr").nth(0)
            pickup_code = pickup_code_rt.locator("td").nth(3).inner_text()
            print(pickup_code)

            download = pickup_code_rt.locator("td").last
            with page.expect_popup(timeout=10000) as popup_info:
                download.locator("div.eds-table__cell button").click()
            pop_up = popup_info.value
            pop_up.wait_for_load_state("domcontentloaded",timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)
            saved = download_pdf(pop_up,save_path=f"FWEE_FM_{KST}/FWEE_FM_{country}_{KST}.pdf") 
            print(f"{country} 저장 완료: {saved}")
            pop_up.close()

            # url 변경
            def change(url):
                origin_url = url.split("/")[7]
                cnsc_shop = origin_url.split("?")[1]
                own_number = cnsc_shop.split("=")[1]
                change_url = "/".join(url.split("/")[:7])+"/link?type=1&cnsc_shop_id="+own_number
                return change_url

            change_url = change(fwee_countrylist[country])
            page.goto(change_url,wait_until="load",timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)
            page.wait_for_timeout(3000)

            while True:
                empty = page.locator("div.eds-table__empty div.eds-default-page__content:has-text('No Orders Found')")
                if empty.is_visible():
                    print("데이터 없음")
                    break

                else:
                    # 새로고침 후에 너무 빨라서 클릭이 제대로 안 됨 -> timeout 주기
                    page.wait_for_timeout(3000)

                    # select All 버튼 클릭
                    select_all = page.locator("div.eds-table-scrollX-left div.eds-table__main-header tr th").nth(0).locator("label.eds-checkbox > span")
                    select_all.wait_for(state="attached")
                    select_all.click()

                    # Bind 어쩌고 버튼 클릭 
                    bind_button = page.locator("div.inline-fixed div.eds-popover__ref button").inner_text().strip()
                    print(bind_button)

                    date = page.locator("div.eds-table__body-container div.eds-scrollbar__content tbody tr").first.locator("td").nth(6).inner_text().strip()
                    date = date.split()[0].split("/")[-1]

                    if country == "Vietnam" and date == "2025":
                        break
                    
                    break

                page.reload(wait_until="load",timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)












    except Exception as e:
        print(e) 
