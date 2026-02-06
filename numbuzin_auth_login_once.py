# 최초 1회 로그인 세션 위한 스크립트

from playwright.sync_api import sync_playwright, TimeoutError
import os
from dotenv import load_dotenv 
import sys

#해당 코드 써줘야 env가져올 수 있음
load_dotenv()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(
        "https://seller.shopee.kr/account/signin",
        wait_until="domcontentloaded",
        timeout=30000,
    )

    print("Page loaded")

    num_id = os.getenv("NUMBUZIN_ID")                                                             
    num_pw = os.getenv("NUMBUZIN_PW")  

    if not num_id or not num_pw:
        raise ValueError("Missing NUMBUZIN_ID or NUMBUZIN_PW env var")

    page.locator('input.eds-input__input[placeholder="Email/Phone/Username"]').wait_for(
        timeout=30000
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
    page.wait_for_selector("input[placeholder='Please input']", timeout=60000)      
                                                                                    
    if len(sys.argv) > 1:                                                           
        code = sys.argv[1]                                           
    else:                                                                           
        code = input("인증코드 입력: ").strip()                                     
                                                                                    
    page.locator("input[placeholder='Please input']").type(code, delay=120)         
    # 인증코드 자동 입력 후 클릭 버튼
    page.locator("button.eds-button--normal:has-text('Confirm')").click()
    page.wait_for_selector("div.todo-list-container",timeout=30000)

    page.wait_for_timeout(5000)

    context.storage_state(path="numbuzin_shopee_state.json")
    print("Login state saved to numbuzin_shopee_state.json")
    # 브라우저 닫기
    browser.close()