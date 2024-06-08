import base64
import requests
from dotenv import load_dotenv
import os
import json

load_dotenv()

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Path to your image
image_path = "/Users/tachyon/Downloads/test/2/page_4_question_14.png"

# Getting the base64 string
base64_image = encode_image(image_path)

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_KEY}"
}

instructions = """
다음 문제를 인식해서 아래와 같은 형식에 맞춰서 답변해줘
json 형식으로 출력하고, 각 key는 문제번호, line{n}, 이미지, 선지로 구성돼.
인식되는 각 줄마다 line{n}으로 취급해서 출력해줘. 문장 기준이 아니라 줄 기준으로 출력해줘.
문단이 이미지 너비의 직사각형 박스로 감싸져있는 경우만 "조건"이라 하고 출력해줘. 조건은 박스 안에 들어있는 것만을 포함해야해. 조건 안에 여러 줄이 있을 경우 {} 안에 line을 사용해서 출력해. 문제에 해당 직사각형 박스가 있는 경우에만 해당돼. 없을 수도 있어
수식은 latex 그리고 $으로 감싸 표시해. 한글을 제외한 숫자(점수를 제외한)와 영문자는 모두 수식으로 표현하고, 영문자는 라틴체와 이탤릭체를 구분해줘.
이미지(도형, 그래프)가 존재하면 해당 위치에 "이미지" 를 추가해줘.이미지가 없다면 아예 출력하지 않아도 돼. line, 선지와의 위치를 고려하여 순서를 맞춰서 출력해줘.
선지는 ①②③④⑤에 각각 어떤 값이 써있고, 줄바꿈이 존재하는지(한 줄에 다 있는지, 두 줄에 나눠 존재하는지)를 토대로 출력해줘. 두줄에 나눠있다면 줄바꿈 문자로 표현해줘. 선지가 없다면 "no"라 해줘. 
모든 요소는 읽는 순서에 맞게 출력해줘.

문제번호 예시) "문제번호" : 28

line 예시1)
        "line1": "양수 $a$에 대하여 최고차항의 계수가 $1$인 함수 $f(x)$는",
        "line2": "$f(x)=\\frac{x^2-ax}{e^x}$",
        "line3": "이다. 실수 $t$에 대하여 $x$에 대한 방정식",
        "line4": "$f(x)=f'(t)(x-t)+f(t)$",
        "line5": "의 서로 다른 실근의 개수를 $g(t)$라 하자.",
    예시2)
       "line1": "그림과 같이 중심이 $O$이고 길이가 $2$인 선분 $AB$를",
       "line2": "지름으로 하는 반원 위에 $\\angle AOC = \\frac{\\pi}{2}$인 점 $C$가 있다.",
       "line3": "호 $BC$ 위에 점 $P$와 호 $CA$ 위에 점 $Q$를 $\\overline{PB} = \\overline{QC}$가 되도록",
       "line4": "잡고, 선분 $AP$ 위에 점 $R$을 $\\angle CQR = \\frac{\\pi}{2}$가 되도록 잡는다."
조건 예시)
    "조건": {
        "line1": "주사위를 한 번 던져 나온 눈의 수가",
        "line2": "$6$의 약수이면 점 $P$를 양의 방향으로 $1$만큼 이동시키고,",
        "line3": "$6$의 약수가 아니면 점 $P$를 이동시키지 않는다."
    }
    "조건": {
        "line1": "(가) 모든 실수 $x$에 대하여",
        "line2": "$f(x) = f(1) + (x - 1) f\'(g(x))$이다.",
        "line3": "(나) 함수 $g(x)$의 최소값은 $\\frac{5}{2}$이다.",
        "line4": "(다) $f(0) = -3$, $f(g(1)) = 6$"
        }
    (가, 나, 다 에는 수식표현 $을 사용하면 안된다)
이미지, 선지 예시1)
    "이미지": "이미지",
    "선지": "① $-1$ ② $0$ ③ $1$ ④ $2$ ⑤ $3$"

    예시 2)
    "선지" : "① $-1$ ② $0$ ③ $1$\n ④ $2$ ⑤ $3$",
    "이미지" : "그래프"
"""

payload = {
    "model": "gpt-4o",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": instructions},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high"
                    },
                },
            ],
        }
    ],
    "max_tokens": 1500
}

response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
content = response.json().get("choices")[0].get("message").get("content")

print(content)