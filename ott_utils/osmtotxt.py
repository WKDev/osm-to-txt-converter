#!/usr/bin/env python3

# osmtotxt.py

# created : 
# modified : chanhyeokson

# 220903 : (chanhyeokson) added folder check syntax, 
# now user is able to convert osm to txt by executing this script at once.

# 220902 : got scripts from kimhyeonseo

from distutils.command.config import LANG_EXT
from genericpath import isfile
from re import U
import numpy as np
import pandas as pd
import utm
from . import OSMHandler

import os
import shutil
import glob

import time

# from point_increment import point_increment

UTM_zone_x = 52
UTM_zone_y = 'n'

INPUT_FOLDER = 'increased'
OUTPUT_FOLDER = 'ret'

#새로 만드는 id가 기존의 id와 겹치지 않게 조정하는 함수
def check_new_id(nid, id_list):
    if np.isin(-nid, id_list): #
        nid += 1
        return check_new_id(nid, id_list)

    else:
        return nid





# UTM 좌표로 표기된 TXT 파일을 불러와서 numpy arr로 리턴한다.
def read_UTMmap_txt(txt_file_name):
    map_data_txt = pd.read_csv(txt_file_name, sep=',', encoding='utf-8')
    UTMmap_arr= map_data_txt.to_numpy()

    return UTMmap_arr


# UTM numpy arr을 받고 latlon numpy arr를 리턴하는 함수
def UTM_2_latlon(UTM_numpy):
    latlon_numpy_arr = []
    
    for node in UTM_numpy:
        latlon_numpy_arr.append(utm.to_latlon(node[0], node[1], UTM_zone_x, UTM_zone_y))

    return np.array(latlon_numpy_arr)

# latlon numpy arr을 받고 UTM numpy arr를 리턴하는 함수
def latlon_2_UTM(UTM_numpy):
    UTM_numpy_arr = []
    
    for node in UTM_numpy:
        UTM_numpy_arr.append(utm.from_latlon(node[0], node[1]))
    
    return np.array(UTM_numpy_arr)[:,0:2]


def write_osm(node):
    # osm_file = open(output_txt_path, mode='wt')

    # OSM 작성 시작
    text = ["<?xml version='1.0' encoding='UTF-8'?>\n", "<osm version='0.6' upload='false' generator='JOSM'>\n"]

    for nd in node:
        text.append("  <node id='{0}' lat='{1}' lon='{2}' />\n".format(-int(nd[0]), nd[1], nd[2]))

    text.append("</osm>")

    # for line in text:
    #     osm_file.write(line)

    # osm_file.close()

def write_UTM_txt(path,UTM_numpy_arr):
    np.savetxt(path, UTM_numpy_arr, fmt='%s', delimiter=',')


def read_osm(file_name):
    #기존 주행유도선 파일 데이터 parsing
    osm_data = OSMHandler.OSM_data(file_name)

    nodes = []
    ways = []
    way_id_lst = []

    for data in osm_data:
        if data[0] == 'node' :
            nodes.append(data[1:4])

        elif data[0] == 'way' :
            ways.append(data)
            way_id_lst.append(data[1])

    nodes = np.array(nodes)    
    node_ids = nodes[:,0]

    return nodes

def osm_to_txt(src, dst):


    try:
        if not os.path.isdir(src):
            raise FileNotFoundError
      
        pth = os.listdir(src)

        if len(pth) == 0:
            raise IndexError
        pth.sort()

    except FileNotFoundError as e:
        print('\033[31m[OSMtoTXT][ERROR] input 폴더 : '+ src +' 가 존재하지 않습니다. ')
        quit()

    except IndexError:
        print('\033[31m[OSMtoTXT][ERROR] '+src + ' 폴더 내부에 파일이 존재하지 않습니다. ')
        quit()

    for f in pth:
        if not f.split(sep='.')[2] == 'osm':
            print('\033[31m[OSMtoTXT][WARN] skipped file / folder :'+f + '.')


        

    # OUTPUT_FOLDER 경로가 없으면 경로를 새로 만듭니다.
    if not os.path.isdir(dst):
        os.mkdir(os.path.join(os.getcwd(),dst[2:]))

    # print(os.path.isfile(os.path.join(os.getcwd(),'ret')))
    # print(len(glob.glob(pathname='./ret/*.txt')))

    # 현재 날짜를 받아옵니다.
    curr_time = time.localtime()
    yr = str(curr_time.tm_year)[2:]

    # 날짜가 10보다 작은 경우, 앞에 0을 붙여줍니다.
    month = (lambda x : '0' + str(x) if x < 10 else str(x))(curr_time.tm_mon)
    d = (lambda x : '0' + str(x) if x < 10 else str(x))(curr_time.tm_mday)
    h = (lambda x : '0' + str(x) if x < 10 else str(x))(curr_time.tm_hour)
    min = (lambda x : '0' + str(x) if x < 10 else str(x))(curr_time.tm_min)
    sec = (lambda x : '0' + str(x) if x < 10 else str(x))(curr_time.tm_sec)

    foldername = yr + month + d + '_'+h +'_'+min + '_'+sec

    # if len(glob.glob(pathname=dst+'/*.txt')) != 0:
    #     print('[OSM_TO_TXT][VERBOSE] Previous file would be moved into subdirectory :' + foldername)
    #     os.mkdir(os.path.join(os.getcwd(),dst[2:],foldername))
        
    #     # OUTPUT_FOLDER 경로에 데이터가 존재하면, 백업을 진행합니다.
    #     existed = os.listdir(os.path.join(os.getcwd(),dst[2:]))
    #     for f in existed:
    #         if f.endswith('.txt'):
    #             # print('existed file : ' + f)
    #             shutil.move(src=os.path.join(os.getcwd(),dst[2:],f), dst=os.path.join(os.getcwd(),dst[2:],foldername,f))
    os.mkdir(os.path.join(os.getcwd(),dst[2:],foldername))       
    for p in pth:
        #생성된 데이터를 저장할 경로를 지정합니다.
        txt_pth = p[:-3] + "txt"
        # print(txt_pth)

        #파일 이름에서 주석을 제거합니다.
        txt_pth = txt_pth.split(sep='.')[0]+ '.' + txt_pth.split(sep='.')[2]
        print("\033[0m[OSM_TO_TXT][VERBOSE]" + str(txt_pth))


        #increased 이하 폴더에 있는 osm 파일을 읽습니다.
        new_node_latlon = read_osm(os.path.join(os.getcwd(),src,p)) # 촘촘하게 만든 파일 불러오기

        #osm 2 utm
        tmp_node_latlon = np.delete(new_node_latlon, 0, 1)
        
        new_node_UTM = latlon_2_UTM(tmp_node_latlon)
        new_node_UTM.astype(np.float32)

        # ret 폴더에 osm--> txt, latlon --> utm으로 변환된 txt 파일을 저장합니다.
        write_UTM_txt(path = os.path.join(os.getcwd(),dst[2:],foldername,txt_pth), UTM_numpy_arr= new_node_UTM)

    lat_lon = utm.to_latlon(302551.533431,4123889.68239, 52, 's')
    UTM = utm.from_latlon(lat_lon[0], lat_lon[1])


    print("\033[32m[OSM_TO_TXT][INFO] ALL PROCESSES HAVE DONE!")


if __name__ == '__main__':
    # print(os.listdir('./increased'))

    # point_increment.py에서 생성된 데이터를 불러옵니다.

    # point_increment(src='./rawdata', dst='./increased')
    osm_to_txt(src='./increased', dst='./ret')

    