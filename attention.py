import fitz  # PyMuPDF
import cv2
import numpy as np
from PIL import Image
import os

def extract_text_areas_using_cv(pdf_path, output_folder, high_quality=True):
    doc = fitz.open(pdf_path)
    zoom = 3 if high_quality else 1.5  # 고화질을 위한 확대 설정

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

        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            if w > 200 and h > 800:  # 너무 작은 영역은 제외
                # 텍스트 영역만 잘라내기
                crop_img = img.crop((x, y, x+w, y+h))
                crop_img.save(f"{output_folder}/page_{page_number}_area_{i}.png")

    doc.close()

# 사용 예시
output_folder = "/Users/tachyon/Downloads/attention"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

extract_text_areas_using_cv("/Users/tachyon/Downloads/2024 고3 수학영역.pdf", output_folder)
