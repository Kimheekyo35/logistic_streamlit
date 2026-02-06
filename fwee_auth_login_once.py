from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(
        "https://seller.shopee.kr/account/signin",
        wait_until="domcontentloaded",
        timeout=30000)
    
    print("Page loaded")

    fwee_id = os.getenv("FWEE_ID")
    fwee_pw = os.getenv("FWEE_PW")

    if not fwee_id or not fwee_pw:
        raise ValueError("Missing FWEE_ID or FWEE_PW env var")
    
    page.locator('input.eds-input__input[placeholder="Email/Phone/Username"]').wait_for(
        timeout=30000)
    page.locator('input.eds-input__input[placeholder="Email/Phone/Username"]').type(
        fwee_id, delay=120)
    page.locator('input.eds-input__input[placeholder="Password"]').type(
        fwee_pw, delay=120)
    
    page.locator("button.submit-btn:has-text('Log In')").click()

    # 인증코드 직접 입력
    code = input("인증코드 입력: ").strip()
    page.locator('input.eds-input__input[placeholder="Please input"]').type(code, delay=120)

    # 인증코드 자동 입력 후 클릭 버튼
    page.locator("button.eds-button--normal:has-text('Confirm')").click()
    page.wait_for_selector("div.todo-list-container",timeout=30000) 

    page.wait_for_timeout(10000)

    context.storage_state(path="fwee_shopee_state.json")
    print("Login state saved to fwee_shopee_state.json")

    # 브라우저 닫기
    browser.close()