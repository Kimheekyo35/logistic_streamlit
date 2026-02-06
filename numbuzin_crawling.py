
# 전체 파이프라인 : numbuzin shopee에서 배송 송장 pdf파일 크롤링 후 pdf 병합하여 하나의 파일로 저장

from playwright.sync_api import sync_playwright
import time
from datetime import datetime
import pandas as pd
import json
import os
from dotenv import load_dotenv
from iframe_to_pdf import download_pdf_from_shopee_preview
from pdf_merge import pdf_merge
import sys
#해당 코드 써줘야 env가져올 수 있음
load_dotenv()

PLAYWRIGHT_NAV_TIMEOUT_MS = int("30000")
PLAYWRIGHT_SELECTOR_TIMEOUT_MS = int("30000")

def get_parcel_count(page):
    text = page.locator("div.fix-card-container div.fix-top-content-left div.parcel-count").inner_text().strip()
    return int(text.split()[0])

numbuzin_country = {
    "Singapore":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=358623637&mass_shipment_tab=201&filter.shipping_method=18063&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770187020&filter.shipping_urgency_filter.shipping_urgency=1",
    "Taiwan Xiapi":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=545141727&mass_shipment_tab=201&filter.shipping_method=38064&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770187057&filter.shipping_urgency_filter.shipping_urgency=1",
    "Malaysia":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=372445559&mass_shipment_tab=201&filter.shipping_method=28050&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770187159&filter.shipping_urgency_filter.shipping_urgency=1",
    "Vietnam":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=989076281&mass_shipment_tab=201&filter.shipping_method=0&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770187213&filter.shipping_urgency_filter.shipping_urgency=1",
    "Philippines":"https://seller.shopee.kr/portal/sale/mass/ship?cnsc_shop_id=832134646&mass_shipment_tab=201&filter.shipping_method=0&filter.order_item_filter_type=item0&filter.order_process_status=1&filter.sort.sort_type=2&filter.sort.ascending=true&filter.pre_order=2&filter.shipping_urgency_filter.current_time=1770187241&filter.shipping_urgency_filter.shipping_urgency=1"
}

country_input = sys.argv[1:]
print(country_input)

# 한국 시간 설정
dt = datetime.now()
KST = dt.strftime("%Y-%m-%d")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False,
                                args=["--start-maximized"]
                                )
    context = browser.new_context(storage_state="numbuzin_shopee_state.json",
                                   viewport={"width": 1280, "height": 720})
    page = context.new_page()
    page.goto("https://seller.shopee.kr/?cnsc_shop_id=545141727",wait_until="domcontentloaded",timeout=PLAYWRIGHT_SELECTOR_TIMEOUT_MS)

    print("로그인 완료")

    try:
        for country in country_input:
            page.goto(numbuzin_country[country],timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)
            print(f"{country} 열었음")
            page.wait_for_timeout(5000)

            # Shipping Channel 제대로 가져오는지 체크
            shipping_channel = page.locator("div.shipping-channel-filter div.mass-ship-filter-item div.content div.radio-button-wrapper")
            
            group = shipping_channel.locator("div.eds-radio-group")
            labels = group.locator("label.eds-radio-button")
            label_cnt = labels.count()
            page.wait_for_timeout(1000)

            for i in range(label_cnt):
                label_button = labels.nth(i)
                label_name = label_button.locator("span").first.inner_text().strip().split()[:2]
                channel_name = " ".join(label_name)
                zero_up = label_button.locator("span.meta").inner_text().strip()
                per_count = int(zero_up.strip("()"))
                if per_count >= 1:
                    label_button.click()
                    page.wait_for_timeout(1000)
                    while True:
                        parcel_count = get_parcel_count(page)
                        print(f"{country}/{channel_name} 현재 처리할 송장 수: {parcel_count}")
                        if parcel_count == 0:
                            print(f"{country}/{channel_name} 처리할 송장 없음, 이동")
                            break
                        else:
                            # 50/page 버튼 누르기
                            page_button = page.locator("div.mass-ship-pagination div.pagination-wrapper div.page-size-dropdown-container button[type='button']")
                            page_button.click()
                            page.wait_for_timeout(1000)

                            # 드롭다운 생성 및 버튼 누르기
                            page_button = page.locator("div.eds-popper-container ul.eds-dropdown-menu li.eds-dropdown-item:has-text('200')").click()
                            page.wait_for_timeout(1500)

                            # 전체 상품 체크박스 누르기
                            page.locator("div.mass-ship-list-container div.mass-ship-list div.fix-card-top label.eds-checkbox").click()
                            page.wait_for_timeout(1500)

                            #Dropoff 가져오는지
                            page.locator("div.mass-action-panel div.main div.button-wrapper").click()
                            page.wait_for_timeout(1500)

                            # Arrange Shipment Progress 창에서 test
                            page.locator("div.ship-process").wait_for(state="visible",timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)
                            another_win = page.locator("div.ship-process div.content")
                            another_win_name = another_win.locator("div.header div.title").inner_text().strip()

                            # generate 버튼 누르기
                            generate_btn =another_win.locator("button:has-text('Generate')").first
                            generate_btn.wait_for(state="visible", timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)
                            generate_btn.click()
                            print(f"{country} Generate 클릭했음")
                            page.wait_for_timeout(1500)

                            # 팝오버 안의 2번째 li 클릭
                            # attach는 DOM에 있기만 하면 됨
                            dropdown = page.locator("div.eds-popper-container").last
                            dropdown.wait_for(state="attached", timeout=10000)

                            # 2번째 항목 클릭
                            item = dropdown.locator("ul > li").nth(1)
                            item.wait_for(state="attached", timeout=10000)
                            
                            with page.expect_popup(timeout=5000) as p:
                                item.click()
                            pop_up = p.value
                            pop_up.wait_for_load_state("domcontentloaded",timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)
                            print(f"{country} 팝업 떴음")

                            ts = datetime.now().strftime("%H%M%S")
                            saved = download_pdf_from_shopee_preview(pop_up, save_path=f"numbuzin_{KST}/numbuzin_{country}_{KST}_{ts}.pdf")
                            print(f"{country} PDF 저장 완료: {saved}")
                            pop_up.close()
                            page.wait_for_timeout(2000)

                            # 팝업 닫고 새로고침
                            page.reload(wait_until="domcontentloaded",timeout=PLAYWRIGHT_NAV_TIMEOUT_MS)

    except Exception as e:
        print(f"error: {e}")

n_path = f"./numbuzin_{KST}"
pdf_merge(n_path)
