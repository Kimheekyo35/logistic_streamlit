import base64
from playwright.sync_api import Page
from pathlib import Path

def download_pdf_from_shopee_preview(page: Page, save_path: str) -> str:
    # 1) PDF iframe이 붙을 때까지 기다리기 (blob: src)
    iframe = page.locator("iframe[type='application/pdf'][src^='blob:'], iframe[src^='blob:']").first
    iframe.wait_for(state="attached", timeout=60000)

    # 2) iframe src가 blob:로 채워질 때까지 대기
    page.wait_for_function("""
      () => {
        const f = document.querySelector("iframe[src^='blob:']");
        return !!f && typeof f.getAttribute("src") === "string" && f.getAttribute("src").startsWith("blob:");
      }
    """, timeout=60000)

    # 3) blob PDF를 fetch해서 base64로 반환
    js = r"""
    async () => {
      const f = document.querySelector("iframe[src^='blob:']");
      if (!f) throw new Error("blob iframe 없음");

      const blobUrl = (f.getAttribute("src") || "").split("#")[0];
      const res = await fetch(blobUrl);
      if (!res.ok) throw new Error("fetch 실패: " + res.status);

      const blob = await res.blob();
      const buf = await blob.arrayBuffer();

      let binary = "";
      const bytes = new Uint8Array(buf);
      const chunkSize = 0x8000;
      for (let i = 0; i < bytes.length; i += chunkSize) {
        binary += String.fromCharCode(...bytes.subarray(i, i + chunkSize));
      }
      const b64 = btoa(binary);

      return { b64, type: blob.type || "", size: blob.size };
    }
    """

    result = page.evaluate(js)

    if result.get("type") and "pdf" not in result["type"]:
        pass

    out = Path(save_path)
    # 상위 폴더 없으면 생성
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(result["b64"]))

    return str(out)

