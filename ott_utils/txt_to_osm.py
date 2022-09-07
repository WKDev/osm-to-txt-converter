#!/usr/bin/env python3

# from cv2 import FileNode_UNIFORM
from re import U
import numpy as np
import pandas as pd
import utm
import OSMHandler
import glob
import os
from log import WKLogger
import xml.etree.ElementTree as et



UTM_zone_x = 52
UTM_zone_y = 'n'

lg = WKLogger(log_path=os.getcwd())

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
    osm_file = open(output_txt_path, mode='wt')

    # OSM 작성 시작
    text = ["<?xml version='1.0' encoding='UTF-8'?>\n", "<osm version='0.6' upload='false' generator='JOSM'>\n"]

    for nd in node:
        text.append("  <node id='{0}' lat='{1}' lon='{2}' />\n".format(-int(nd[0]), nd[1], nd[2]))

    text.append("</osm>")

    for line in text:
        osm_file.write(line)

    osm_file.close()

def write_UTM_txt(UTM_numpy_arr):
    np.savetxt(output_txt_path_UTM, UTM_numpy_arr, fmt='%s', delimiter=',')





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

def chk_path(path):
    '''
    경로를 받아서 상대경로인지, 절대경로인지, 우분투인지 윈도우인지 판단
    Args:
        path:

    Returns:
        /home/...../*.txt
        C:\\......\\txt
    '''
    if path.startswith('/home'):
        print('startwith home')
        return '%s/*.txt' % os.getcwd()
    elif path.startswith('C:\\'):
        print('startwith windows')
        return '%s\\*.txt' % os.getcwd()
    elif path.startswith('./'):
        print('startwith relative_path')
        return '%s/*.txt' % path

    else:
        print('획인된 경로 : ' + str(path))

        lg.err('절대도 아니고, 상대경로도 아닌 듯 합니다. 혹시 정상적인 경로를 지정한 게 맞나요?')
        raise Exception


def txt_to_osm(input):

    src = chk_path(path=input)
    print(src)

    for file_path in glob.glob(src):
        parent = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        pd.read_table(file_path, sep="," ,encoding='cp949')
        f = np.genfromtxt(fname=file_path)

        print(file_path)
        print(f)



if __name__ == '__main__':


    txt_to_osm(input='C:\\Users\\chanh\\PycharmProjects\\osm-to-txt-converter\\txt_to_osm')
    # txt 맵 수만큼 반복해서 np arr에 담는다.
#     # 1~34
#     readed_utm_map = np.empty(shape=(0,2))   ##txt to osm
#     for map_number in range(1):
#         file_name = map_file_path_generater(map_number + 1)
#         readed_utm_map = np.vstack((readed_utm_map, read_UTMmap_txt(file_name)))
#     #97, 98, 99
#     # for map_number in range(3):
#     #     file_name = map_file_path_generater(map_number + 97)
#     #     readed_utm_map = np.vstack((readed_utm_map, read_UTMmap_txt(file_name)))
#
#
#     latlon_numpy_arr = UTM_2_latlon(readed_utm_map)
#
#     node_id_np = np.arange(1, len(latlon_numpy_arr)+1, dtype=int)
#
#     node = np.hstack((node_id_np.reshape(-1, 1), latlon_numpy_arr))
#
#
#     ##########################
#     # Pooling    1/100
#
#     node_pooling = np.array(node[0])
#
#     for i, row in enumerate(node):
#         if i%1 !=0 or i == 0:
#             pass
#         else:
#             node_pooling = np.vstack((node_pooling, row))
#     ##########################
#
#
#     write_osm(node_pooling)
#
#
# lat_lon = utm.to_latlon(302551.533431,4123889.68239, 52, 's')
# UTM = utm.from_latlon(lat_lon[0], lat_lon[1])
#
#
# print("save done")