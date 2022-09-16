#!/usr/bin/env python3

# from cv2 import FileNode_UNIFORM
import random
import shutil
import numpy as np
import pandas as pd
import utm
from ott_utils.deprecated import OSMHandler
import glob
import os
from .log import WKLogger
import xml.etree.ElementTree as et

import time

UTM_zone_x = 52
UTM_zone_y = 'n'

lat_lon = utm.to_latlon(302551.533431,4123889.68239, 52, 's')
UTM = utm.from_latlon(lat_lon[0], lat_lon[1])

lg = WKLogger(log_path=os.getcwd(), log_level = 'debug', target=os.path.basename(__file__))


# UTM 좌표로 표기된 TXT 파일을 불러와서 numpy arr로 리턴한다.
def read_UTMmap_txt(txt_global_path):
    map_data_txt = pd.read_csv(txt_global_path, sep=',', encoding='utf-8')
    UTMmap_arr = map_data_txt.to_numpy()

    return UTMmap_arr


# UTM numpy arr을 받고 latlon numpy arr를 리턴하는 함수
def UTM_2_latlon(UTM_numpy):
    latlon_numpy_arr = []

    for node in UTM_numpy:
        latlon_numpy_arr.append(utm.to_latlon(node[0], node[1], UTM_zone_x, UTM_zone_y))

    return np.array(latlon_numpy_arr,dtype=np.float64)


# latlon numpy arr을 받고 UTM numpy arr를 리턴하는 함수
def latlon_2_UTM(UTM_numpy):
    UTM_numpy_arr = np.array([],dtype=np.float64)

    for node in UTM_numpy:
        np.append(UTM_numpy_arr,utm.from_latlon(node[0], node[1]))

    return UTM_numpy_arr


def write_osm(output_path, node):
    print(output_path)
    osm_file = open(output_path, mode='wt')

    # OSM 작성 시작
    text = ["<?xml version='1.0' encoding='UTF-8'?>\n", "<osm version='0.6' upload='false' generator='JOSM'>\n"]

    for nd in node:
        text.append("  <node id='{0}' lat='{1}' lon='{2}' />\n".format(-int(nd[0]), nd[1], nd[2]))

    rd = random.randrange(-999999, 0)
    text.append("  <way id='{}' action='modify' visible='true'>\n".format(rd))

    for nd in node:
        text.append("    <nd ref='{}' />\n".format(-int(nd[0])))

    text.append('  </way>\n')
    text.append("</osm>")

    for line in text:
        osm_file.write(line)

    osm_file.close()

def read_osm(file_name):
    # 기존 주행유도선 파일 데이터 parsing
    osm_data = OSMHandler.OSM_data(file_name)

    nodes = []
    ways = []
    way_id_lst = []

    for data in osm_data:
        if data[0] == 'node':
            nodes.append(data[1:4])

        elif data[0] == 'way':
            ways.append(data)
            way_id_lst.append(data[1])

    nodes = np.array(nodes)
    node_ids = nodes[:, 0]

    return nodes


def chk_path(path, file_type = 'txt'):
    '''
    경로를 받아서 상대경로인지, 절대경로인지, 우분투인지 윈도우인지 판단 후 return한다.

    /home/...../*.txt :: 우분투 절대경로도 되고
     ./txt :: 상대경로도 되고
    C:\\......\\txt :: 윈도우 절대경로도 되고
    윈도우 상대경로는....아직 추가 안해놨네
    /Users/ ..... / foo.txt  :: 맥 절대경로도 된다.

    Args:
        path:


    Returns:
        /home/...../*.txt
        C:\\......\\txt
    '''
    if path.startswith('/home'):
        print('startwith home')
        return '%s/*' % os.getcwd() + file_type
    if path.startswith('/Users'):
        print('startwith MacOS(Absolute path)')
        return '%s/*' % path + file_type

    elif path.startswith('C:\\'):
        print('startwith windows(Absolute path)')
        return '%s\\*' % path + file_type
    elif path.startswith('./'):
        print('startwith relative_path')
        return '%s/*' % os.path.join(os.getcwd(), path[2:]) + file_type

    else:
        print('획인된 경로 : ' + str(path))

        lg.err('절대도 아니고, 상대경로도 아닌 듯 합니다. 혹시 정상적인 경로를 지정한 게 맞나요?')
        raise Exception


def txt_to_osm(source, destinations):
    readed_utm_map = np.empty(shape=(0, 2))

    src = chk_path(path=source, file_type='.txt')

    new_folder_name = foldername_generator(time.localtime(), pth=destinations)
    backup_dir = os.path.join(destinations, new_folder_name, 'backup')

    if not os.path.isdir(backup_dir):
        os.makedirs(backup_dir)


    for f in glob.glob(src):
        lg.info(f)
        # txt맵 데이터를 nparray에 담음
        utm_np_arr = np.vstack((readed_utm_map, read_UTMmap_txt(f)))
        lg.info('UTM.txt -->nparray(UTM)')
        # lg.debug(utm_np_arr)

        # 위에서 얻은 데이터를 latlon 정보로 변환
        latlon_np_arr = UTM_2_latlon(utm_np_arr)
        lg.info('nparray(UTM)-->nparray(latlon)')
        # lg.debug(latlon_np_arr)

        # nodeid를 위한 array 생성
        node_id = np.arange(1, len(latlon_np_arr) + 1, dtype=int)
        # lg.debug(node_id)


        # nodeid와 latlon 정보 결합
        # [id] + [lat, lon] = [id,lat,lon]
        # [id] + [lat, lon] = [id, lat, lon]
        # [id] + [lat, lon] = [id, lat, lon]
        # [id] + [lat, lon] = [id, lat, lon]

        node = np.hstack((node_id.reshape(-1, 1), latlon_np_arr))
        # lg.debug(node_id.reshape(-1, 1))
        # lg.debug(node)

        node_pooling = np.array(node[0])
        # lg.debug(node_pooling)

        for i, row in enumerate(node):
            # lg.debug('{}th iteration'.format(i))

            if not (i % 1 != 0 or i == 0):
                # lg.debug('{}th iteration, pass'.format(i))
                pass

            else:
                node_pooling = np.vstack((node_pooling, row))
            node_pooling = np.vstack((node_pooling, row))

        ##########################

        lg.debug('dirname : ' + str(new_folder_name))
        lg.debug('dst : ' + str(destinations))
        shutil.copy(f, os.path.join(destinations, new_folder_name, 'backup'))
        osm_path = os.path.join(destinations, new_folder_name, str(f.replace('.txt', '').split(sep='/')[-1]) + '.osm')
        lg.info('output_destination : ' + osm_path)

        write_osm(output_path=osm_path, node=node_pooling)
        lg.info('txt_to_osm_done.')





def txt_to_osm_new(src, dst, save=True, return_type= 'utm'):

        # txt_raw에 gf 경로로부터 txt파일의 경로를 읽어옵니다.
        txt_raw = np.loadtxt(src, dtype=str,delimiter=',')
        txt_raw = txt_raw.astype(np.float64)
        # lg.info(txt_raw)

        latlon_nodes = np.empty((0, 3), dtype=np.float64)


        # 위에서 얻은 데이터를 latlon 정보로 변환
        # latlon_np_arr = UTM_2_latlon(utm_np_arr)
        lg.info('nparray(UTM)-->nparray(latlon)')
        # lg.debug(latlon_np_arr)

        for i, t in enumerate(txt_raw):
            ii = -1-i # node id를 -1부터 -방향으로 커지도록 변경합니다.
            converted = utm.to_latlon(t[0],t[1], UTM_zone_x, UTM_zone_y)
            # lg.info(latlon_line)
            tmp_latlon = np.array([[ii, converted[0], converted[1]]], dtype=np.float64)

            latlon_nodes = np.append(latlon_nodes, tmp_latlon, axis=0)

        lg.verbose(latlon_nodes)
        # 저장 영역
        txt_path = os.path.join(dst, str(src.replace('.txt', '').split(sep='/')[-1]) + '.osm')

        if save:
            write_osm(txt_path, latlon_nodes)


        if return_type == 'utm':
            return txt_raw

        if return_type == 'latlon':
            return latlon_nodes[:][1:]


def foldername_generator(t, pth):
    # 현재 날짜를 받아옵니다.
    curr_time = t
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

        if not str(t).endswith('.txt'):
            # print(t[4:6])
            if t[-1].isdigit() and int(t[4:6]) == int(d) and int(t[2:4]) == int(month):
                folders.append(int(t.split(sep='_')[1]))

    lg.verbose('folders : ' + str(folders))

    cnt = '1' if len(folders) == 0 else str(max(folders) + 1)
    lg.verbose('count : ' + cnt)



    ret = yr + month + d + 'T' + h + _min + _sec + '_' + cnt
    return ret


if __name__ == '__main__':
    txt_to_osm('C:\\Users\\chanh\\PycharmProjects\\osm-to-txt-converter\\input',
                    'C:\\Users\\chanh\\PycharmProjects\\osm-to-txt-converter\\input',
                    'C:\\Users\\chanh\\PycharmProjects\\osm-to-txt-converter\\input\\output')