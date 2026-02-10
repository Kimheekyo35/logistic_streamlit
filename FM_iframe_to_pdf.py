import base64
from pathlib import Path
from playwright.sync_api import Page

from pathlib import Path
from playwright.sync_api import Page

def download_pdf(popup: Page, save_path: str, timeout_ms: int = 30000) -> str:
    out = Path(save_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # 1) 팝업 로드 대기
    popup.wait_for_load_state("domcontentloaded", timeout=timeout_ms)

    # 2) "팝업 URL 자체가 PDF" 인 경우: 제일 쉬운 루트 (쿠키/세션 포함해서 요청)
    url = popup.url
    try:
        resp = popup.request.get(url, timeout=timeout_ms)
        ct = (resp.headers.get("content-type") or "").lower()
        if resp.ok and "application/pdf" in ct:
            out.write_bytes(resp.body())
            return str(out)
    except Exception:
        pass

    # 3) 팝업 로딩 과정에서 PDF 요청이 따로 발생하는 경우: response로 잡기
    def is_pdf_response(r):
        try:
            ct = (r.headers.get("content-type") or "").lower()
            return "application/pdf" in ct
        except Exception:
            return False

    pdf_resp = popup.wait_for_response(is_pdf_response, timeout=timeout_ms)
    out.write_bytes(pdf_resp.body())
    return str(out)
