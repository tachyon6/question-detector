import fitz  # PyMuPDF
from PIL import Image
import os
import re

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def extract_blocks_as_images(pdf_path, output_folder, high_quality=True):
    doc = fitz.open(pdf_path)
    zoom = 2 if high_quality else 1  # 고화질을 위한 확대 설정
    question_pattern = re.compile(r"^\d+\.")
    question_number = 1

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        blocks = page.get_text("dict")["blocks"]  # 모든 블록을 가져옵니다.
        
        current_question_blocks = []
        last_question_number = question_number

        for block in blocks:
            if "lines" in block or "image" in block:  # 텍스트 라인 또는 이미지가 포함된 블록인지 확인
                block_text = "".join(span["text"] for line in block.get("lines", []) for span in line.get("spans", []))
                if question_pattern.match(block_text.strip()):
                    if current_question_blocks:
                        # 이전 문제 이미지 저장
                        save_question_image(current_question_blocks, page, zoom, output_folder, page_number, last_question_number)
                        last_question_number = question_number
                        question_number += 1
                        current_question_blocks = []

                current_question_blocks.append(block)

        # 마지막 문제 저장
        if current_question_blocks:
            save_question_image(current_question_blocks, page, zoom, output_folder, page_number, last_question_number)

    doc.close()

def save_question_image(blocks, page, zoom, output_folder, page_number, question_number):
    min_x = min(block["bbox"][0] for block in blocks)
    max_x = max(block["bbox"][2] for block in blocks)
    min_y = min(block["bbox"][1] for block in blocks)
    max_y = max(block["bbox"][3] for block in blocks)
    rect = fitz.Rect(min_x, min_y, max_x, max_y)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=rect)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    ensure_directory(output_folder)
    img.save(f"{output_folder}/page_{page_number}_question_{question_number}.png")

output_folder = "/Users/tachyon/Downloads/img3"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

extract_blocks_as_images("/Users/tachyon/Downloads/2024 고3 수학영역.pdf", output_folder)
