# GUI Wrapper Script for txt_to_osm
# created 220905 by chanhyeokson

from tkinter import *
from PIL import ImageTk, Image
import os
from ott_utils.osmtotxt import osm_to_txt
from ott_utils.point_increment import point_increment
from ott_utils.trajectory_generator import trajectory_generator


##########parameters to modify
NODE_INT = 0.05 # Node Intervel
RAW_PATH = './point_increment/input'
DENSED_PATH = './point_increment/output'
OTT_PATH = './osm_to_txt'
TRAJECTORY_GENERATOR_PATH = './trajectory_generator/input'
#############

curr_raw_path = RAW_PATH
curr_densed_path = DENSED_PATH
curr_osm_to_txt_path = OTT_PATH
curr_trajectory_generator_path = TRAJECTORY_GENERATOR_PATH
node_int = NODE_INT

root = Tk()

global work_stat  # 함수 btnpress() 정의
global chkvar
global chkvar1
global chkvar2


# def dense_ask():
#     curr_densed_path = filedialog.askdirectory()
#     #root.file = filedialog.askopenfile(initialdir='path', title='select file', filetypes=(('jpeg files', '*.jgp'), ('all files', '*.*')))
    
#     print (curr_densed_path)
#     pinc_txt.configure(text="pwd: " + curr_densed_path)



def Runner():  
    global work_stat                 # 함수 btnpress() 정의
    global chkvar
    global chkvar1
    global chkvar2
    a = []
    if chkvar.get() == 1:         # 체크박스가 체크 되었는지 확인
        point_increment(node_interval=node_int,src=curr_raw_path, dst=curr_densed_path)

    if chkvar1.get() == 1:
        osm_to_txt(src=curr_densed_path, dst=curr_osm_to_txt_path)
    if chkvar2.get() == 1:
        trajectory_generator(src=curr_trajectory_generator_path)  
    
    work_stat.config(text='status : Done')

    work_stat.grid(row=8,column=0)

def init_gui():
    global work_stat  # 함수 btnpress() 정의
    global chkvar
    global chkvar1
    global chkvar2

    root.title("OSM <-> TXT Toolkit")
    root.geometry("540x400+100+100")
    root.resizable(True, True)

    pinc_txt = Label(root, text='Node interval : ' + str(node_int) + 'm\n\n')
    pinc_txt.grid(row=0, column=0)

    curr_txt = Label(root, text='current_path : ' + str(os.getcwd()) + '\n\n')
    curr_txt.grid(row=1, column=0)

    txt = Label(root, text=" ")
    txt.grid(row=2, column=0)

    chkvar = IntVar()  # chkvar에 int 형으로 값을 저장
    chkbox = Checkbutton(root, variable=chkvar)  # root라는 창에 체크박스 생성
    chkbox.config(text="point_increment")
    chkbox.select()  # 체크박스 내용 설정
    chkbox.grid(row=3, column=0)  # 체크박스 배치

    chkvar1 = IntVar()  # chkvar1에 int 형으로 값을 저장
    chkbox1 = Checkbutton(root, variable=chkvar1)  # root라는 창에 체크박스 생성
    chkbox1.config(text="osm_to_txt")
    chkbox1.select()  # 체크박스 내용 설정
    chkbox1.grid(row=4, column=0)  # 체크박스 배치

    chkvar2 = IntVar()  # chkvar2 에 int 형으로 값을 저장
    chkbox2 = Checkbutton(root, variable=chkvar2)  # root라는 창에 체크박스 생성
    chkbox2.config(text="trajectory_generator")  # 체크박스 내용 설정
    chkbox2.select()
    chkbox2.grid(row=5, column=0)  # 체크박스 배치

    btn = Button(root)  # root라는 창에 버튼 생성
    btn.config(text="Run")  # 버튼 내용
    btn.config(width=10)  # 버튼 크기
    btn.config(command=Runner)  # 버튼 기능 (btnpree() 함수 호출)
    btn.grid(row=6, column=0)

    text = Text(master=root, height=10)

    text.insert(CURRENT, "tool 설명\n")
    text.insert(CURRENT, "point_increment : JSOM으로 생성한 경로 파일의 점 개수를 늘려줍니다.\n")
    text.insert(CURRENT, "osmtotxt : .osm 파일의 latlon 데이터를 UTM txt로 변환합니다.\n")
    text.insert(CURRENT, "trajectory_generator : UTM txt에서 osm으로 변환된 파일의 누락된 way 태그를 만들어줍니다..\n")
    text.insert(CURRENT, "(working)txt_to_osm : txt파일을 osm으로 변환합니다. \n")

    text.grid(row=7, column=0)

    work_stat = Label(root, text="status : ready")
    work_stat.grid(row=8, column=0)

    work_stat = Label(root, text="2022 K-BUB Chanhyeokson")
    work_stat.grid(row=8, column=0)

    root.mainloop()

if __name__ == "__main__":
    init_gui()
