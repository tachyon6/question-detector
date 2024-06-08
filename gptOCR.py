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
image_path = "/Users/tachyon/Downloads/test/2/page_27_question_68.png"

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
수식은 latex으로 인식해 hwp수식형식으로 바꾸고 $$으로 감싸 표시해. 한글을 제외한 모든 숫자(점수를 제외한)와 영문자는 모두 수식으로 표현하고, 도형의 점에 해당하는 영대문자 앞에는 rm을 붙이고 그 다음 영문자부터는 it를 붙여줘.
이미지(도형, 그래프)가 존재하면 해당 위치에 "이미지" 를 추가해줘.이미지가 없다면 아예 출력하지 않아도 돼. line, 선지와의 위치를 고려하여 순서를 맞춰서 출력해줘.
선지는 ①②③④⑤에 각각 어떤 값이 써있고, 줄바꿈이 존재하는지(한 줄에 다 있는지, 두 줄에 나눠 존재하는지)를 토대로 출력해줘. 두줄에 나눠있다면 줄바꿈 문자로 표현해줘. 선지가 없다면 "no"라 해줘. 
모든 요소는 읽는 순서에 맞게 출력해줘.

latex -> hwp 변환형식)
1. 
   - LaTeX format: `\( a_{n+1} = \begin{cases} 2^{a_n} & \text{if } a_n \text{이 홀수인 경우} \\ \frac{1}{2} a_n & \text{if } a_n \text{이 짝수인 경우} \end{cases} \)`
   - HWP format: `a _{n+1} = {cases{pile{#} 2 ^{a _{n}}&`````` LEFT ( a _{n} 이```홀수인```경우 RIGHT )#pile{#} {1} over {2} a _{n} ````&`````` LEFT ( a _{n} 이```짝수인```경우 RIGHT )}}`

2. 
   - LaTeX format: `\( g(x) = \begin{cases} x + 3 & \text{if } x < -1 \\ x^2 & \text{if } -1 \leq x < a \\ x + k & \text{if } x \geq a \end{cases} \)`
   - HWP format: `g LEFT ( x RIGHT ) = {cases{eqalign{` pile{#} x+3 pile{#} ~` LEFT ( x< it -1 RIGHT )# ` pile{#} x ^{2} pile{#} ~``````````` LEFT ( -1 LEQ  x<a RIGHT )}&eqalign{#}#` pile{#} x+k pile{#} ~` LEFT ( x GEQ  a RIGHT )&}}`

3. 
   - LaTeX format: `\( \left\{ x \mid \text{모든 자연수 } x \text{에 대하여 } \frac{y}{x} > 1 \text{이다.} \right\} \)`
   - HWP format: `LEFT { x LEFT | 모든```자연수``x에```대하여``` {y} over {x} >1이다. RIGHT . RIGHT }`

4. 
   - LaTeX format: `\( a^b + \sqrt{c} - d_1 \times f'(x) \div \lim_{{x \to 1^+}} \frac{f(x)}{g(x)} \pm \sum_{{n=1}}^{\infty} (\overline{A} \neq \vec{A}) \theta \leq \int_{{0}}^{{-1}} \frac{|x|}{y} \geq X \cdots X[z] y\{z\} 90^\circ \)`
   - HWP format: `a ^{b} + sqrt {c} -d _{1} TIMES f` prime LEFT ( x RIGHT ) DIVIDE lim _{x` rarrow `1+} {{f LEFT ( x RIGHT )} over {g LEFT ( x RIGHT )}} +- sum _{n=1} ^{INF } LEFT ( {bar{A}} != {vec{rm A}} RIGHT ) theta LEQ int _{0} ^{-1} {{LEFT | x RIGHT |} over {it y}} GEQ X CDOTS ` rm X LEFT [ it z RIGHT ] y LEFT { z RIGHT } 90 DEG`

5. 
   - LaTeX format: `\( 3\vec{a} + k\vec{b} = (a, b) \)`
   - HWP format: `3 {vec{a}} `+k {vec{b}} `= LEFT ( a,```b RIGHT )`

6. 
   - LaTeX format: `\( \left| \overrightarrow{CX} \right| = \frac{1}{2} \overrightarrow{CP} + \overrightarrow{CQ} \cdot \overrightarrow{PQ} = \overline{AB} + \overline{CD} \)`
   - HWP format: `LEFT | {vec{rm CX}} RIGHT | = {1} over {2} {vec{rm CP}} + {vec{rm CQ}} CDOT  {vec{rm PQ}} = {bar{rm AB}} + {bar{rm CD}}`

7. 
   - LaTeX format: `\( A(c, d) \)`
   - HWP format: `rmA LEFT ( it c,```d RIGHT )`


문제번호 예시) "문제번호" : 28

line 예시1)
    "line1": "양수 $a$에 대하여 최고차항의 계수가 자연수 $k$인 함수 $f(x)$는",
    "line2": "$LEFT | f LEFT ( x RIGHT ) RIGHT | = {x ^{2} - ax} over {e ^{x}}$",
    "line3": "이다. 실수 $t$에 대하여 $x$에 대한 방정식",
    "line4": "$f LEFT ( x RIGHT ) = f` prime LEFT ( t RIGHT ) ( x - t ) + f LEFT ( t RIGHT )$",
    "line5": "의 서로 다른 실근의 개수를 $g(t)$라 하자."
    예시2)
    "line1": "그림과 같이 중심이 $rmO$이고 길이가 $2$인 선분 $rmAB$를",
    "line2": "지름으로 하는 반원 위에 $angle rmAOC = {pi} over {2}$인 점 $C$가 있다.",
    "line3": "호 $rmBC$ 위에 점 $rmP$와 호 $rmCA$ 위에 점 $rmQ$를 $bar{rmPB} = bar{rmQC}$가 되도록",
    "line4": "잡고, 선분 $rmAP$ 위에 점 $rmR$을 $angle rmCQR = {it k} over {2}$가 되도록 잡는다."
    "line5": "${vec{rm AB}} CDOT {vec{rm PR}}$의 값이 $0$이 되도록 하는 $k$의 값은"
조건 예시)
    "조건": {
        "line1": "주사위를 한 번 던져 나온 눈의 수가",
        "line2": "$6$의 약수이면 점 $P$를 양의 방향으로 $1$만큼 이동시키고,",
        "line3": "$6$의 약수가 아니면 점 $P$를 이동시키지 않는다."
    }
    "조건": {
        "line1": "(가) 모든 실수 $x$에 대하여",
        "line2": "$f LEFT ( x RIGHT ) = f LEFT ( 1 RIGHT ) + ( x - 1 ) f` prime LEFT ( g LEFT ( x RIGHT ) RIGHT )$이다.",
        "line3": "(나) 함수 $g(x)$의 최소값은 ${5} over {2}$이다.",
        "line4": "(다) $f LEFT ( 0 RIGHT ) = -3$, $f LEFT ( g LEFT ( 1 RIGHT ) RIGHT ) = 6$"
    }
    "조건" : {
        "line1": "$LEFT [ 0,```12 RIGHT ]$에서 $f LEFT ( x RIGHT ) =x`$, $g LEFT ( x RIGHT ) = it -x`$",
        "line2": "이다."
    }
(가), (나), (다) 에는 수식표현 $에 들어가지 않는다.
","는 수식표현 $에 들어가지 않는다. =, <, > 뒤에 -가 올때 중간에 it를 넣어줘야한다.

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
            "role": "system",
            "content": "이전 대화는 무시하고 질문에 맞는 답변을 해주세요."
        },
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

print(response.json())
print(content)