from playwright.sync_api import sync_playwright
import time
import pandas as pd
import json
import os
from dotenv import load_dotenv
from iframe_to_pdf import download_pdf_from_shopee_preview
from pdf_merge import pdf_merge
from datetime import datetime
#해당 코드 써줘야 env가져올 수 있음
load_dotenv()

PLAYWRIGHT_NAV_TIMEOUT_MS = int("30000")
PLAYWRIGHT_SELECTOR_TIMEOUT_MS = int("30000")

fwee_countrylist = {
    "Singapore":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=1147332494&mass_shipment_tab=201&filter.shipping_method=18063&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770266071&filter.shipping_urgency_filter.shipping_urgency=1",
    "TaiwanXiapi":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=1152063847&mass_shipment_tab=201&filter.shipping_method=38064&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770266088&filter.shipping_urgency_filter.shipping_urgency=1",
    "Thailand":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=1152063845&mass_shipment_tab=201&filter.shipping_method=78016&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770266100&filter.shipping_urgency_filter.shipping_urgency=1",
    "Malaysia":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=1152063834&mass_shipment_tab=201&filter.shipping_method=28062&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770266119&filter.shipping_urgency_filter.shipping_urgency=1",
    "Vietnam":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=1152063841&mass_shipment_tab=201&filter.shipping_method=58016&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770266159&filter.shipping_urgency_filter.shipping_urgency=1",
    "Philippines":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=1152063836&mass_shipment_tab=201&filter.shipping_method=48023&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770266188&filter.shipping_urgency_filter.shipping_urgency=1"
}

def get_parcel_count(page):
    text = page.locator("div.fix-card-container div.fix-top-content-left div.parcel-count").inner_text().strip()
    return int(text.split()[0])

country_input = input("나라를 입력하세요: ").split()
country_input = list(map(str,country_input))

# 한국 시간 설정
dt = datetime.now()
KST = dt.strftime("%Y-%m-%d")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False,
                                        )

    context = browser.new_context(storage_state="fwee_shopee_state.json",
                               viewport={"width": 1280, "height": 720})
    page = context.new_page()
    page.goto("https://seller.shopee.kr/?cnsc_shop_id=545141727",wait_until="domcontentloaded",timeout=PLAYWRIGHT_SELECTOR_TIMEOUT_MS)

    print("Page loaded")

    try:
        for country in country_input:
            page.goto(fwee_countrylist[country],timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)
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

                    while True:
                        parcel_count = get_parcel_count(page)
                        print(f"{country} 현재 처리할 송장 수: {parcel_count}")
                        if parcel_count == 0:
                            print(f"{country}/{shipping_channel} 처리할 송장 없음, 이동")
                            break
                        else:
                            # 50/page 버튼 누르기
                            page_button = page.locator("div.mass-ship-pagination div.pagination-wrapper div.page-size-dropdown-container")
                            page_button.click()
                            page.wait_for_timeout(1000)

                            # 드롭다운 생성 및 버튼 누르기
                            page_button = page.locator("div.eds-popper-container ul.eds-dropdown-menu li.eds-dropdown-item:has-text('200')").click()
                            page.wait_for_timeout(1500)

                            # 전체 상품 체크박스 누르기
                            page.locator("div.mass-ship-list-container div.mass-ship-list div.fix-card-top label.eds-checkbox").click()
                            page.wait_for_timeout(1500)

                            #Dropoff 가져오는지 확인
                            page.locator("div.mass-action-panel div.main div.button-wrapper").click()
                            page.wait_for_timeout(1500)

                            # Arrange Shipment Progress 창
                            page.locator("div.ship-process").wait_for(state="visible",timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)
                            another_win = page.locator("div.ship-process div.content")

                            # generate 버튼 누르기
                            generate_btn =another_win.locator("button:has-text('Generate')").first
                            generate_btn.wait_for(state="visible", timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)
                            generate_btn.click()
                            print(f"{country} Generate 클릭했음")
                            page.wait_for_timeout(1500)

                            dropdown = page.locator("div.eds-popper-container").last
                            dropdown.wait_for(state="attached", timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)

                            # 팝오버 안의 2번째 li 클릭
                            # 클릭
                            item = dropdown.locator("ul > li").nth(1)
                            item.wait_for(state="attached", timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)

                            with page.expect_popup(timeout=5000) as popup_info:
                                item.click()
                            pop_up = popup_info.value
                            pop_up.wait_for_load_state("domcontentloaded",timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)
                            
                            ts = datetime.now().strftime("%H%M%S")
                            saved = download_pdf_from_shopee_preview(pop_up, save_path=f"fwee_{KST}/fwee_{country}_{KST}_{ts}.pdf")
                            print(f"{country} PDF 저장 완료: {saved}")
                            pop_up.close()
                            page.wait_for_timeout(2000)
                            
                            # 팝업 닫고 새로고침
                            page.reload(wait_until="domcontentloaded",timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)

    except Exception as e:
        print(f"error: {e}")

f_path = f"./fwee_{KST}"
pdf_merge(f_path)
