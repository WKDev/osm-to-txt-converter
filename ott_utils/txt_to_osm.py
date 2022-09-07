#!/usr/bin/env python3

# from cv2 import FileNode_UNIFORM
import random
from re import U
import numpy as np
import pandas as pd
import utm
from . import OSMHandler
import glob
import os
from .log import WKLogger

import time

UTM_zone_x = 52
UTM_zone_y = 'n'

lat_lon = utm.to_latlon(302551.533431,4123889.68239, 52, 's')
UTM = utm.from_latlon(lat_lon[0], lat_lon[1])

lg = WKLogger(log_path=os.getcwd(), log_level = 'debug')


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

    return np.array(latlon_numpy_arr)


# latlon numpy arr을 받고 UTM numpy arr를 리턴하는 함수
def latlon_2_UTM(UTM_numpy):
    UTM_numpy_arr = []

    for node in UTM_numpy:
        UTM_numpy_arr.append(utm.from_latlon(node[0], node[1]))

    return np.array(UTM_numpy_arr)[:, 0:2]


def write_osm(output_path, node):
    osm_file = open(output_path, mode='wt')

    # OSM 작성 시작
    text = ["<?xml version='1.0' encoding='UTF-8'?>\n", "<osm version='0.6' upload='false' generator='JOSM'>\n"]

    for nd in node:
        text.append("  <node id='{0}' lat='{1}' lon='{2}' />\n".format(-int(nd[0]), nd[1], nd[2]))

    rd = random.randrange(-999999, 0)
    text.append("  <way id='{}' action='modify' visible='true'>".format(rd))

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
        return '%s\\*.txt' % path
    elif path.startswith('./'):
        print('startwith relative_path')
        return '%s/*.txt' % os.path.join(os.getcwd(), path[2:])

    else:
        print('획인된 경로 : ' + str(path))

        lg.err('절대도 아니고, 상대경로도 아닌 듯 합니다. 혹시 정상적인 경로를 지정한 게 맞나요?')
        raise Exception


def txt_to_osm(source, *destinations):
    readed_utm_map = np.empty(shape=(0, 2))

    src = chk_path(path=source)
    # print(src)

    for f in glob.glob(src):
        # txt맵 데이터를 nparray에 담음
        utm_np_arr = np.vstack((readed_utm_map, read_UTMmap_txt(f)))
        lg.info('UTM.txt -->nparray(UTM)')
        lg.debug(utm_np_arr)

        # 위에서 얻은 데이터를 latlon 정보로 변환
        latlon_np_arr = UTM_2_latlon(utm_np_arr)
        lg.info('nparray(UTM)-->nparray(latlon)')
        lg.debug(latlon_np_arr)

        # nodeid를 위한 array 생성
        node_id = np.arange(1, len(latlon_np_arr) + 1, dtype=int)
        lg.debug(node_id)


        # nodeid와 latlon 정보 결합
        # [id] + [lat, lon] = [id,lat,lon]
        # [id] + [lat, lon] = [id, lat, lon]
        # [id] + [lat, lon] = [id, lat, lon]
        # [id] + [lat, lon] = [id, lat, lon]

        node = np.hstack((node_id.reshape(-1, 1), latlon_np_arr))
        lg.debug(node_id.reshape(-1, 1))
        lg.debug(node)

        node_pooling = np.array(node[0])
        lg.debug(node_pooling)

        for i, row in enumerate(node):
            # lg.debug('{}th iteration'.format(i))

            # if not (i % 1 != 0 or i == 0):
            #     lg.debug('{}th iteration, pass'.format(i))
            #     pass
            #
            # else:
            #     node_pooling = np.vstack((node_pooling, row))
            node_pooling = np.vstack((node_pooling, row))

        ##########################

        for dst in destinations:
            dirname = foldername_generator(dst)
            os.mkdir((os.path.join(dst, dirname)))
            lg.debug(str(f.split(sep='.')[-1]))
            lg.info('output_destination : ' + os.path.join(dst, dirname, str(f.split(sep='.')[-2]) + '.osm'))

            write_osm(output_path=os.path.join(dst, dirname, str(f.split(sep='.')[-2]) + '.osm'), node=node_pooling)
            lg.info('txt_to_osm_done.')


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


if __name__ == '__main__':
    txt_to_osm('C:\\Users\\chanh\\PycharmProjects\\osm-to-txt-converter\\txt_to_osm',
                    'C:\\Users\\chanh\\PycharmProjects\\osm-to-txt-converter\\txt_to_osm',
                    'C:\\Users\\chanh\\PycharmProjects\\osm-to-txt-converter\\txt_to_osm\\output')