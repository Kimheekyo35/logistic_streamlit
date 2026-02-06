from PyPDF2 import PdfReader, PdfWriter
import os

path = "./test_file"

# 해당 경로에 있는 파일들 리스트로 만들기
file_list = os.listdir(path)
merger = PdfWriter()

for file in file_list:
    file_path = os.path.join(path, file)
    if file_path.endswith(".pdf"):
        # PDF 파일 열기
        with open(file_path, "rb") as f:
            pdf_reader = PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                # pdf 병합하기
                merger.add_page(page)

# 새로운 파일에 저장
with open(os.path.join(path, "merged_output.pdf"), "wb") as output_pdf:
    merger.write(output_pdf)
