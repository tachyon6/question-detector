import cv2
import pytesseract
import os

# 이미지 파일 경로
image_path = "/Users/tachyon/Downloads/전처리/page_1_processed.png"
# 이미지 로드
image = cv2.imread(image_path)

# 이미지가 제대로 로드되었는지 확인
if image is None:
    raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {image_path}")

# 이미지를 그레이스케일로 변환
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 텍스트 영역을 찾기 위해 임계처리
_, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

# 텍스트 인식을 위해 pytesseract 설정
custom_config = r'--oem 3 --psm 6'
d = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT, config=custom_config)

# 각 텍스트 박스의 좌표를 저장
coordinates = []
n_boxes = len(d['level'])
for i in range(n_boxes):
    x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
    text = d['text'][i]
    if text.strip():  # 텍스트가 비어있지 않을 경우만
        coordinates.append((text, (x, y, w, h)))

# 문제 영역을 캡처하여 저장
problem_areas = [("문제 5", 0, 140, 860, 350), ("문제 6", 0, 380, 860, 590), ("문제 7", 860, 140, 1720, 350)]

for idx, (name, x, y, w, h) in enumerate(problem_areas):
    crop_img = image[y:y+h, x:x+w]
    output_crop_path = f'/Users/tachyon/Downloads/좌표캡처/{name}.png'
    if not os.path.exists(output_crop_path):
        os.makedirs(output_crop_path)
    cv2.imwrite(output_crop_path, crop_img)

print("문제 영역 캡처 완료.")
