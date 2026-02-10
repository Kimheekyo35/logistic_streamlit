# 전체 pdf를 merge 한 후에 1200개씩 잘라서 다시 저장하기 

from PyPDF2 import PdfReader, PdfWriter
import os
from datetime import datetime

KST = datetime.now().strftime("%Y%m%d")

# 출력 확인 코드
def print_result(name,name_cnt):
    print(f"{name}_merged_{name_cnt}.pdf 생성 완료" )
    
# Build a merged PDF in chunks to cap output size.
def pdf_merge(path):
    file_list = sorted(os.listdir(path))
    merger = PdfWriter()
    name_cnt = 1
    name = path.split("_")[0]
    page_count = 0
    # def write_chunk(writer,idx):
    #     output_name = f"{name}_merged_output_{KST}_part{idx:03d}.pdf"
    #     output_path = os.path.join(path, output_name)
    #     with open(output_path,"wb") as output_pdf:
    #         writer.write(output_pdf)
    #     print(f"PDF merge complete: {output_path}")

    for file in file_list:
        file_path = os.path.join(path, file)
        if file_path.endswith(".pdf"):
            # Read PDF and append pages to current chunk.
            with open(file_path, "rb") as f:
                pdf_reader = PdfReader(f)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    merger.add_page(page)
                    page_count += 1
                    if page_count % 1200 == 0:
                        with open(os.path.join(path,f"{name}_merged_{name_cnt}.pdf"),"wb") as output_pdf :
                            merger.write(output_pdf)
                            print_result(name,name_cnt)
                        name_cnt += 1
                        merger = PdfWriter()
                        page_count = 0

    if page_count > 0:
        out_path = os.path.join(path, f"{name}_merged_{name_cnt}.pdf")     
        with open(out_path,"wb") as output_f:
            merger.write(output_f)
            print_result(name,name_cnt)


    print("전체 PDF 병합 완료")

pdf_merge("퓌_test_files")

