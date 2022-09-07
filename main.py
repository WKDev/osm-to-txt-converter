# GUI Wrapper Script for txt_to_osm
# created 220905 by chanhyeokson
import time
from tkinter import *
from PIL import ImageTk, Image
import os
from ott_utils.point_increment import point_increment
from ott_utils.log import WKLogger
from ott_utils.txt_to_osm import txt_to_osm
from ott_utils.osm_to_txt import osm_to_txt
from ott_utils import OSMHandler

lg = WKLogger(os.path.join(os.getcwd(),'logs'))



##########parameters to modify
NODE_INT = 0.05 # Node Intervel
RAW_PATH = './point_increment/input'
DENSED_PATH = './point_increment/output'
OTT_PATH = './osm_to_txt'
TRAJECTORY_GENERATOR_PATH = './trajectory_generator/input'
#############

root = Tk()

global work_stat  # 함수 btnpress() 정의
global chkvar
global chkvar1
global chkvar2

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


def foldername_generator(pth):
    # 현재 날짜를 받아옵니다.
    curr_time = time.localtime()
    yr = str(curr_time.tm_year)[2:]

    # 날짜가 10보다 작은 경우, 앞에 0을 붙여줍니다.
    month = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_mon)
    d = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_mday)
    h = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_hour)
    _min = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_min)
    _sec = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_sec)

    folders = []

    # 점을 포함하지 않으며, 끝이 숫자로 끝나는 것들을 리스트로 반환합니다.
    for t in os.listdir(pth):
        # lg.debug(t)

        if str(t).find(".") == -1:
            if t[-1].isdigit():
                folders.append(int(t.split(sep='_')[1]))

    lg.debug('folders : ' + str(folders))

    cnt = '1' if len(folders) == 0 else str(max(folders) + 1)
    lg.debug('count : ' + cnt)

    ret = yr + month + d + 'T' + h + _min + _sec + '_' + cnt
    return ret

def txt_enhancer():
    source_dir = 'C:\\Users\\chanh\\PycharmProjects\\osm-to-txt-converter\\txt_to_osm'


    lg.info('this will turn raw txt into enhanced one.')
    txt_to_osm(source_dir)
    point_increment()





if __name__ == "__main__":
    # init_gui()
    txt_enhancer()