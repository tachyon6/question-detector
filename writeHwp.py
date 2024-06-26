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
    hwp = win32.gencache.EnsureDispatch("hwpframe.hwpobject")
    hwp.XHwpWindows.Item(0).Visible = True
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
    return hwp

def set_style(hwp, style_num):
    Act = hwp.CreateAction("Style")
    Set = Act.CreateSet()
    Act.GetDefault(Set)
    Set.SetItem("Apply", style_num)
    Act.Execute(Set)

def insert_text(hwp, text):
    try:
        for char in text:
            hwp.HAction.GetDefault("InsertText", hwp.HParameterSet.HInsertText.HSet)
            hwp.HParameterSet.HInsertText.Text = char
            hwp.HAction.Execute("InsertText", hwp.HParameterSet.HInsertText.HSet)
            sleep(0.05)
    except Exception as e:
        print(f"Error inserting text: {text}, Error: {str(e)}")

def process_equation(equation):
    equation = re.sub(r'(?<![A-Za-z])([A-Z])(?![A-Za-z])', r'\1`', equation)
    equation = equation.replace(',', ',```')
    equation += '`'
    return equation

def insert_equation(hwp, equation):
    try:
        equation = process_equation(equation)
        hwp.HAction.GetDefault("EquationCreate", hwp.HParameterSet.HEqEdit.HSet)
        hwp.HParameterSet.HEqEdit.EqFontName = "HYhwpEQ"
        hwp.HParameterSet.HEqEdit.string = equation
        hwp.HParameterSet.HEqEdit.BaseUnit = hwp.PointToHwpUnit(11.0)
        hwp.HAction.Execute("EquationCreate", hwp.HParameterSet.HEqEdit.HSet)

        hwp.FindCtrl()
        shape_object = hwp.HParameterSet.HShapeObject
        hwp.HAction.GetDefault("EquationPropertyDialog", shape_object.HSet)
        shape_object.HSet.SetItem("ShapeType", 3)
        shape_object.Version = "Equation Version 60"
        shape_object.EqFontName = "HYhwpEQ"
        shape_object.HSet.SetItem("ApplyTo", 1)
        shape_object.HSet.SetItem("TreatAsChar", 1)
        hwp.HAction.Execute("EquationPropertyDialog", shape_object.HSet)
        hwp.Run("Cancel")
        move_cursor_to_end(hwp)
    except Exception as e:
        print(f"Error inserting equation: {equation}, Error: {str(e)}")

def move_cursor_to_end(hwp):
    hwp.Run("MoveLineEnd")
    sleep(0.5)

def change_line(hwp):
    hwp.Run("BreakLine")
    sleep(0.5)

def change_para(hwp):
    hwp.Run("BreakPara")

def is_korean(text):
    return any('\uac00' <= char <= '\ud7a3' for char in text)

def process_line(hwp, line):
    parts = re.split(r'(\$.*?\$)', line)
    for part in parts:
        if part.startswith('$') and part.endswith('$'):
            insert_equation(hwp, part[1:-1])
        else:
            if is_korean(part):
                only_equation = False
            words = part.split()
            for word in words:
                for char in word:
                    insert_text(hwp, char)
                insert_text(hwp, ' ')

    move_cursor_to_end(hwp)

def process_choices(hwp, choices):
    equations = re.findall(r'\$(.*?)\$', choices)
    if not equations:
        equations = re.findall(r'(\d+)', choices)
    
    if '\n' in choices:
        idiom_path = "C:\\Users\\송준혁\\AppData\\Roaming\\HNC\\User\\Hwp\\60\\IDIOM\\c120c9c00032.HWPX"
    else:
        idiom_path = "C:\\Users\\송준혁\\AppData\\Roaming\\HNC\\User\\Hwp\\60\\IDIOM\\c120c9c0.HWPX"
    
    hwp.HAction.GetDefault("Idiom", hwp.HParameterSet.HIdiom.HSet)
    hwp.HParameterSet.HIdiom.InputText = idiom_path
    hwp.HParameterSet.HIdiom.InputType = 2
    hwp.HParameterSet.HIdiom.BlockMode = 0
    hwp.HParameterSet.HIdiom.StartIistID = 0
    hwp.HParameterSet.HIdiom.StartParaID = 5
    hwp.HParameterSet.HIdiom.StartPos = 0
    hwp.HParameterSet.HIdiom.StartFlags = 0
    hwp.HParameterSet.HIdiom.EndIistID = 0
    hwp.HParameterSet.HIdiom.EndParaID = 5
    hwp.HParameterSet.HIdiom.EndPos = 2
    hwp.HParameterSet.HIdiom.EndFlags = 0
    hwp.HAction.Execute("Idiom", hwp.HParameterSet.HIdiom.HSet)

    hwp.HAction.Run("MovePrevParaBegin")
    '''
    hwp.HAction.Run("MoveRight")
    hwp.HAction.Run("MoveRight")
    if '\n' in choices:
        hwp.HAction.Run("MoveRight")
    
    for equation in equations:
        insert_equation(hwp, equation)
        hwp.HAction.Run("MoveRight")
        hwp.HAction.Run("MoveRight")
        hwp.HAction.Run("MoveRight")
    
    if '\n' in choices:
        hwp.HAction.Run("MoveRight")
        hwp.HAction.Run("MoveParaEnd")
        '''

def main():
    hwp = init_hwp()
    hwp.Open(basic_hwp_path)
    set_style(hwp, 1)

    lines = ["line1", "line2", "line3", "line4", "line5"]
    korean_flags = [is_korean(_jsonInput[key]) for key in lines]

    for i, key in enumerate(lines):
        print(f"Processing {key}: {_jsonInput[key]}")
        if i > 0 and korean_flags[i - 1] and not korean_flags[i]:
            change_para(hwp)
            hwp.HAction.Run("RightShiftBlock")
            hwp.HAction.Run("RightShiftBlock")
            set_style(hwp, 2)
        process_line(hwp, _jsonInput[key])
        if not korean_flags[i]:
            change_para(hwp)
            set_style(hwp, 2)
            hwp.HAction.Run("RightShiftBlock")
        if i < len(lines) - 1 and korean_flags[i] and korean_flags[i + 1]:
            change_line(hwp)

    if "선지" in _jsonInput:
        change_para(hwp)
        process_choices(hwp, _jsonInput["선지"])

if __name__ == '__main__':
    main()
