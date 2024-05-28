import os
import subprocess
from PIL import Image
import pytesseract

def convert_pdf_to_svgs(pdf_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    command = f'pdf2svg "{pdf_path}" "{output_folder}/page_%d.svg" all'
    subprocess.run(command, shell=True)

def extract_text_from_svg(svg_path):
    # Inkscape를 사용하여 SVG를 PNG로 변환
    png_path = svg_path.replace('.svg', '.png')
    command = f'inkscape "{svg_path}" --export-type="png" -o "{png_path}"'
    subprocess.run(command, shell=True)
    # Tesseract를 사용하여 이미지에서 텍스트를 추출
    text = pytesseract.image_to_string(Image.open(png_path), lang='kor+eng')
    return text

# 사용 예시
pdf_path = "/Users/tachyon/Downloads/2024 고3 수학영역.pdf"
output_folder = "/Users/tachyon/Downloads/전처리_svg"

convert_pdf_to_svgs(pdf_path, output_folder)

