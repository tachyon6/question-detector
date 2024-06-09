import os
import re
from time import sleep
import win32com.client as win32

project_root = os.getcwd()
basic_hwp_path = os.path.join(project_root, "test", "basic_quark.hwp")

_jsonInput = {
    "문제번호": 12,
    "line1": "$a_{2}=-4$이고 공차가 $0$이 아닌 등차수열 ${ a _{n}}$에 대하여",
    "line2": "수열 ${ b _{n}}$을 $b _{n} = a _{n} + a _{n+1} ( n GEQ 1 )$이라 하고, 두 집합 $A,  B$를",
    "line3": "$A= LEFT { a _{1},  a _{2},  a _{3},  a _{4}, a _{5} RIGHT }$, $B= LEFT { b _{1},  b _{2},  b _{3},  b _{4},  b _{5} RIGHT }$",
    "line4": "라 하자. $n( A SMALLINTER B ) = 3$이 되도록 하는 모든 수열 ${ a _{n}}$에",
    "line5": "대하여 $a _{20}$의 값의 합은? [ 4 점 ]",
    "선지": "① 30 ② 34 ③ 38 ④ 42 ⑤ 46"
}

def init_hwp():
    """
    아래아한글을 시작하는 함수
    """
    hwp = win32.gencache.EnsureDispatch("hwpframe.hwpobject")
    hwp.XHwpWindows.Item(0).Visible = True
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
    return hwp

# 스타일 변경하는 함수
def set_style(style_num):
    Act = hwp.CreateAction("Style")
    Set = Act.CreateSet()
    Act.GetDefault(Set)
    Set.SetItem("Apply", style_num)  # "개요 n"으로 변경
    Act.Execute(Set)

def insert_text(text):
    """
    텍스트를 넣는 함수
    """
    hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
    hwp.HParameterSet.HInsertText.Text = text
    hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)

def insert_equation(equation):
    """
    수식을 넣는 함수
    """
    hwp.HAction.GetDefault("EquationCreate", hwp.HParameterSet.HEqEdit.HSet)
    hwp.HParameterSet.HEqEdit.EqFontName = "HYhwpEQ"
    hwp.HParameterSet.HEqEdit.string = equation
    hwp.HParameterSet.HEqEdit.BaseUnit = hwp.PointToHwpUnit(11.0)
    hwp.HAction.Execute("EquationCreate", hwp.HParameterSet.HEqEdit.HSet)
    sleep(1)

    hwp.FindCtrl()
    hwp.HAction.GetDefault("EquationPropertyDialog", hwp.HParameterSet.HShapeObject.HSet)
    hwp.HParameterSet.HShapeObject.HSet.SetItem("ShapeType", 3)
    hwp.HParameterSet.HShapeObject.Version = "Equation Version 60"
    hwp.HParameterSet.HShapeObject.EqFontName = "HYhwpEQ"
    hwp.HParameterSet.HShapeObject.HSet.SetItem("ApplyTo", 1)
    hwp.HParameterSet.HShapeObject.HSet.SetItem("TreatAsChar", 1)
    hwp.HAction.Execute("EquationPropertyDialog", hwp.HParameterSet.HShapeObject.HSet)
    hwp.Run("Cancel")

def move_cursor_to_end():
    hwp.Run("MoveLineEnd")

def change_line():
    hwp.Run("BreakLine")

def change_para():
    hwp.Run("BreakPara")

def process_line(line):
    """
    텍스트와 수식을 처리하는 함수
    """
    parts = re.split(r'(\$.*?\$)', line)
    only_equation = True  # 한글이 포함되었는지 확인하는 플래그
    for part in parts:
        if part.startswith('$') and part.endswith('$'):
            insert_equation(part[1:-1])
            print("equation: ", part[1:-1])
        else:
            if part.strip():  # 공백이 아닌 텍스트가 있다면
                only_equation = False
            else:
                continue
            insert_text(part)
            print("text: ", part)
    
    move_cursor_to_end()

    if only_equation:
        change_para()
    else:
        change_line()

if __name__ == '__main__':
    hwp = init_hwp()
    hwp.Open(basic_hwp_path)
    set_style(1)
    for key in ["line1", "line2", "line3", "line4"]:
        if key in _jsonInput:
            process_line(_jsonInput[key])

