from playwright.sync_api import sync_playwright
import time
import pandas as pd
import json
import os
from dotenv import load_dotenv

#해당 코드 써줘야 env가져올 수 있음
load_dotenv()

PLAYWRIGHT_NAV_TIMEOUT_MS = int("30000")
PLAYWRIGHT_SELECTOR_TIMEOUT_MS = int("30000")

numbuzin_country = {
    "Singapore":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=358623637&mass_shipment_tab=201&filter.shipping_method=18063&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770187020&filter.shipping_urgency_filter.shipping_urgency=1",
    "Taiwan Xiapi":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=545141727&mass_shipment_tab=201&filter.shipping_method=38064&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770187057&filter.shipping_urgency_filter.shipping_urgency=1",
    "Malaysia":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=372445559&mass_shipment_tab=201&filter.shipping_method=28050&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770187159&filter.shipping_urgency_filter.shipping_urgency=1",
    "Vietnam":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=989076281&mass_shipment_tab=201&filter.shipping_method=0&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770187213&filter.shipping_urgency_filter.shipping_urgency=1",
    "Philippines":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=832134646&mass_shipment_tab=201&filter.shipping_method=0&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770187241&filter.shipping_urgency_filter.shipping_urgency=1"
}

country_input = input("나라를 입력하세요: ").split()
country_input = list(map(str,country_input))

fwee_country_list = ["Singapore","Taiwan Xiapi","Thailand","Malaysia","Vietnam","Philippines"]
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False,
                                proxy={
                                            "server": os.getenv("PROXY_SERVER"),
                                            "username": os.getenv("PROXY_USER"),
                                            "password": os.getenv("PROXY_PASSWORD")
                                        }
                                        )

    page = browser.new_page()
    page.goto(
        "https://seller.shopee.kr/account/signin",
        wait_until="domcontentloaded",
        timeout=PLAYWRIGHT_SELECTOR_TIMEOUT_MS,
    )

    print("Page loaded")

    num_id = os.getenv("NUMBUZIN_ID")                                                             
    num_pw = os.getenv("NUMBUZIN_PW")  

    if not num_id or not num_pw:
        raise ValueError("Missing NUMBUZIN_ID or NUMBUZIN_PW env var")

    page.locator('input.eds-input__input[placeholder="Email/Phone/Username"]').wait_for(
        timeout=PLAYWRIGHT_SELECTOR_TIMEOUT_MS
    )
    page.locator('input.eds-input__input[placeholder="Email/Phone/Username"]').type(
        num_id, delay=120
    )
    page.locator('input.eds-input__input[placeholder="Password"]').type(
        num_pw, delay=120
    )

    # 버튼 클릭 후, 다음 페이지 나올 때까지 기다리기
    # expect_navigation은 “그 블록 안의 클릭 1회”에만 대응
    page.locator("button.submit-btn:has-text('Log In')").click()
    
    # 인증코드 직접 입력
    code = input("인증코드 입력: ").strip()
    page.locator('input.eds-input__input[placeholder="Please input"]').type(code, delay=120)

    # 인증코드 자동 입력 후 클릭 버튼
    page.locator("button.eds-button--normal:has-text('Confirm')").click()
    page.wait_for_selector("div.todo-list-container",timeout=30000)

    # 메인 메뉴 화면으로 들어감
    # 공백 제거
    try:
        for country in country_input:
            page.goto(numbuzin_country[country],timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)
            print(f"{country} 열었음")
            page.wait_for_timeout(5000)

            # Shipping Channel 제대로 가져오는지 체크
            shipping_channel = page.locator("div.shipping-channel-filter div.mass-ship-filter-item div.content")

            group = shipping_channel.locator("div.radio-button-wrapper div.eds-radio-group")
            labels = group.locator("label.eds-radio-button")
            label_cnt = labels.count()
            page.wait_for_timeout(1000)

            for i in range(label_cnt):
                label_button = labels.nth(i)
                zero_up = label_button.locator("span.meta").inner_text().strip()
                per_count = int(zero_up.strip("()"))
                if per_count >= 1:
                    label_button.click()
                    page.wait_for_timeout(1000)

                    # 50/page 버튼 누르기
                    page_button = page.locator("div.mass-ship-pagination div.pagination-wrapper div.page-size-dropdown-container")
                    page_button.click()
                    page.wait_for_timeout(1000)

                    # 드롭다운 생성 및 버튼 누르기
                    page_button = page.locator("div.eds-popper-container ul.eds-dropdown-menu li.eds-dropdown-item").nth(5).click()
                    page.wait_for_timeout(1500)

                    # 전체 상품 체크박스 누르기
                    page.locator("div.mass-ship-list-container div.mass-ship-list div.fix-card-top label.eds-checkbox").click()
                    page.wait_for_timeout(1500)


                    


    except TimeoutError as e:
        print(f"error: {e}")
