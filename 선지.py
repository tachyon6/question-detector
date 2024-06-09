import os
import re
from time import sleep
import win32com.client as win32

project_root = os.getcwd()
basic_hwp_path = os.path.join(project_root, "test", "basic_quark.hwp")

선지1 = "① 30 ② 34 ③ 38 ④ 42 ⑤ 46"
선지2 = "① $30$ ② $34$ ③ $38$ ④ $42$ ⑤ $46$"
선지3 = "① $30$ ② $34$ ③ $38$\n ④ $42$ ⑤ $46$"

def init_hwp():
    hwp = win32.gencache.EnsureDispatch("hwpframe.hwpobject")
    hwp.XHwpWindows.Item(0).Visible = True
    hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
    return hwp

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
        hwp.Run("MoveRight")
    except Exception as e:
        print(f"Error inserting equation: {equation}, Error: {str(e)}")

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

def change_para(hwp):
    hwp.Run("BreakPara")

if __name__ == "__main__":
    hwp = init_hwp()
    hwp.Open(basic_hwp_path)

    process_choices(hwp, 선지1)
    change_para(hwp)
