import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import os
import re

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def extract_text_area_coordinates(pdf_path, high_quality=True):
    doc = fitz.open(pdf_path)
    zoom = 4 if high_quality else 1.5  # 고화질을 위한 확대 설정
    coordinates = {}

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        # 페이지를 이미지로 변환
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img_np = np.array(img)  # 이미지를 NumPy 배열로 변환
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)  # 회색조 이미지로 변환

        # OpenCV를 사용하여 텍스트 영역 찾기
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        page_coordinates = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 200 and h > 800:  # 너무 작은 영역은 제외
                page_coordinates.append((x / zoom, y / zoom, (x + w) / zoom, (y + h) / zoom))

        coordinates[page_number] = page_coordinates

    doc.close()
    return coordinates

def extract_blocks_as_images(pdf_path, output_folder, coordinates, high_quality=True, block_distance_threshold=200):
    doc = fitz.open(pdf_path)
    zoom = 2 if high_quality else 1  # 고화질을 위한 확대 설정
    question_pattern = re.compile(r"^\d+\.")
    question_number = 1

    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]

    contains_a_or_b = 'A' in base_filename or 'B' in base_filename

    for page_number in range(len(doc)):
        if page_number not in coordinates:
            continue
        page = doc.load_page(page_number)
        blocks = page.get_text("dict")["blocks"]  # 모든 블록을 가져옵니다.
        
        for coord in coordinates[page_number]:
            min_x, min_y, max_x, max_y = coord
            save_single_block_image({"bbox": [min_x, min_y, max_x, max_y]}, page, zoom, output_folder, page_number, question_number)
            if page_number == 0:
                print(f"Page {page_number} has coordinates: (min_x: {min_x}, min_y: {min_y}, max_x: {max_x}, max_y: {max_y})")
            current_question_blocks = []
            last_question_number = question_number
            last_block_bottom = 0

            for block in blocks:
                if "lines" in block or "image" in block:  # 텍스트 라인 또는 이미지가 포함된 블록인지 확인
                    block_text = "".join(span["text"] for line in block.get("lines", []) for span in line.get("spans", []))
                    block_height = block["bbox"][3] - block["bbox"][1]
                    
                    if block["bbox"][3] < min_y:
                        continue  # 지정된 영역 외부에 있는 블록 제외

                    if question_pattern.match(block_text.strip()):
                        if current_question_blocks:
                            save_question_image(current_question_blocks, page, zoom, output_folder, page_number, last_question_number, base_filename, contains_a_or_b)
                            last_question_number = question_number
                            question_number += 1
                            current_question_blocks = []

                    if current_question_blocks and (block["bbox"][1] - last_block_bottom) > block_distance_threshold:
                        break
                        
                    if current_question_blocks and (last_block_bottom - block["bbox"][3]) > block_distance_threshold:
                        continue

                    current_question_blocks.append(block)
                    last_block_bottom = block["bbox"][3]

            if current_question_blocks:
                save_question_image(current_question_blocks, page, zoom, output_folder, page_number, last_question_number, base_filename, contains_a_or_b)
                for i, block in enumerate(current_question_blocks):
                    save_single_block_image(block, page, zoom, output_folder, page_number, i)

    doc.close()

def save_single_block_image(block, page, zoom, output_folder, page_number, block_number):
    min_x, min_y, max_x, max_y = block["bbox"]
    rect = fitz.Rect(min_x, min_y, max_x, max_y)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=rect)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    ensure_directory(output_folder)
    log_folder = os.path.join(output_folder, "logs")
    ensure_directory(log_folder)
    img.save(f"{log_folder}/page_{page_number}_block_{block_number}.png")
    print(f"Block {block_number} on page {page_number} has coordinates: (min_x: {min_x}, min_y: {min_y}, max_x: {max_x}, max_y: {max_y})")

def save_question_image(blocks, page, zoom, output_folder, page_number, question_number, base_filename, contains_a_or_b):
    min_x = min(block["bbox"][0] for block in blocks)
    max_x = max(block["bbox"][2] for block in blocks)
    min_y = min(block["bbox"][1] for block in blocks)
    max_y = max(block["bbox"][3] for block in blocks)
    rect = fitz.Rect(min_x, min_y, max_x, max_y)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=rect)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    ensure_directory(output_folder)
    
    # 파일명 지정 로직 추가
    question_label = f"{question_number:02}"  # 두 자리 숫자 형식으로 변환
    if contains_a_or_b:
        filename = f"{base_filename}{question_label}.png"
    else:
        if question_number >= 23 and question_number <= 30:
            question_label += 'A'
        elif question_number >= 31 and question_number <= 38:
            question_label += 'B'
        elif question_number >= 39 and question_number <= 46:
            question_label += 'C'
        
        filename = f"{base_filename}{question_label}.png"
    
    img.save(f"{output_folder}/{filename}")

# 사용 예시
output_folder = "/Users/tachyon/Downloads/2406"

if not os.path.exists(output_folder): 
    os.makedirs(output_folder)

coordinates = extract_text_area_coordinates("/Users/tachyon/Desktop/2406.pdf")
extract_blocks_as_images("/Users/tachyon/Desktop/2406.pdf", output_folder, coordinates)
