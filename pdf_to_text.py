import fitz
from pathlib import Path

path = "퓌_test_files"
list_text = []

def pdf_to_text(file_path):
    files = Path(file_path).glob("*.pdf")
    for file in files:
        doc = fitz.open(file)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            print(f"--- Page {page_num + 1} ---")
            for line in text.splitlines():
                line = line.replace("Order ID: ", "")
                line = line.replace("Tracking NO.: ", "")
                list_text.append(line)
            # 리스트에서 Items: 제거
            list_text.remove("Items:")
            break  # 첫 페이지만 출력
        break  # 첫 파일만 출력
print(pdf_to_text(path))
print(list_text)

