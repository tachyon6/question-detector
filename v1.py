import fitz  # PyMuPDF
from PIL import Image
import os


def extract_blocks_as_images(pdf_path, output_folder, high_quality=True):
    doc = fitz.open(pdf_path)
    zoom = 2 if high_quality else 1  # 고화질을 위한 확대 설정
    
    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        blocks = page.get_text("dict")["blocks"]  # 모든 블록을 가져옵니다.
        
        for i, block in enumerate(blocks):
            if "lines" in block or "image" in block:  # 텍스트 라인 또는 이미지가 포함된 블록인지 확인
                rect = fitz.Rect(block["bbox"])  # 블록의 경계 추출
                # 페이지의 해당 영역을 이미지로 변환, zoom을 통해 해상도 조정
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=rect) 
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img.save(f"{output_folder}/page_{page_number}_block_{i}.png")  # 이미지 파일로 저장

    doc.close()

# 사용 예시
output_folder = "/Users/tachyon/Downloads/img1"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    
extract_blocks_as_images("/Users/tachyon/Downloads/2024 고3 수학영역.pdf", output_folder)
