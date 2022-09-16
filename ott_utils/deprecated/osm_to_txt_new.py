#!/usr/bin/env python3

# point_increment.py

# created : 
# modified : chanhyeokson

# 220903 : (chanhyeokson) added folder check syntax, 
# now user is able to convert osm to txt by executing this script at once.

# 220902 : got scripts from kimhyeonseo

import numpy as np
import pandas as pd
import utm
import os
import glob
import xml.etree.ElementTree as et

if __name__ != "__main__":
    from .log import WKLogger
    from ott_utils.deprecated import OSMHandler
else:
    from log import WKLogger

# from ret import ret

UTM_zone_x = 52
UTM_zone_y = 'n'

INPUT_FOLDER = 'increased'
OUTPUT_FOLDER = 'ret'

lg = WKLogger(log_path=os.getcwd(), log_level = 'debug', target=os.path.basename(__file__))


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

    return np.array(UTM_numpy_arr)[:, 0:2]


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
    # print(osm_data)

    nodes = np.array([], dtype=np.float64)
    ways =np.array([],dtype=np.float64)
    way_id_lst = np.array([],dtype=np.float64)

    for data in osm_data:
        if data[0] == 'node' :
            np.append(nodes, data[1:4])

        elif data[0] == 'way' :
            np.append(ways, data)
            np.append(way_id_lst, data[1])

    # nodes = np.array(nodes)
    # node_ids = nodes[:,0]
    lg.debug(str(nodes))

    return nodes


def chk_path(last_folder, path, file_type):
    '''
    경로를 받아서 상대경로인지, 절대경로인지, 우분투인지 윈도우인지 판단
    Args:
        path:

    Returns:
        /home/...../*.txt
        C:\\......\\txt
    '''
    if path.startswith('/home'):
        print('startwith ubuntu')
        return '%s/*/*.osm' % os.getcwd()

    if path.startswith('/Users'):
        print('startwith MacOS(Absolute path)')
        return '%s/*' % os.path.join(path, last_folder,'point_increment') + file_type

    elif path.startswith('C:\\'):
        print('startwith windows(Absolute path)')
        return '%s\\*' % os.path.join(path, last_folder,'point_increment') + file_type
    elif path.startswith('./'):
        print('startwith relative_path')
        if __name__ == "__main__":
            return '%s/*' % os.path.join(os.getcwd(),path[2:].replace('.osm','')) + file_type
        else:
            return '%s/*' % os.path.join(os.getcwd(),path[2:].replace('.osm',''), last_folder,'point_increment') + file_type

    else:
        print('획인된 경로 : ' + str(path))

        lg.err('절대도 아니고, 상대경로도 아닌 듯 합니다. 혹시 정상적인 경로를 지정한 게 맞나요?')
        raise Exception


def _pretty_print(current, parent=None, index=-1, depth=0):
    """코드를 보기 좋게 만들어줍니다.

    Args:
        current (_type_): _description_
        parent (_type_, optional): _description_. Defaults to None.
        index (int, optional): _description_. Defaults to -1.
        depth (int, optional): _description_. Defaults to 0.
    """
    # https://codechacha.com/ko/python-create-and-write-xml/
    for i, node in enumerate(current):
        _pretty_print(node, current, i, depth + 1)
    if parent is not None:
        if index == 0:
            parent.text = '\n' + ('\t' * depth)
        else:
            parent[index - 1].tail = '\n' + ('\t' * depth)
        if index == len(parent) - 1:
            current.tail = '\n' + ('\t' * (depth - 1))



def osm_to_txt_new(src, dst, save = True, return_type = 'utm'):
    '''
    OSM 파일을 읽어들여, utm으로 변환합니다. 파라미터에 따라 txt파일로 내보낼 수도, ndarray로 내보낼 수도 있습니다.

    np.float64를 적용하여 보다 정확한 계산값을 돌려줍니다.

    자세한 사용법은 args를 참조하세요

    Args:
        last_folder:
        dir:
        save:
        return_type:

    Returns:

    '''

    # lg.info('source : ' + src)
    lg.info('return path : ' + str(dst))

    if not os.path.exists(dst):
        os.makedirs(dst)


    # if len(glob.glob(source)) == 0 :
        lg.warn('cannot find files from the source directory. script will be terminated.')
    # else:
        # lg.info(glob.glob(src))


    # 파일별로 데이터 읽어오기
    # for f in glob.glob(source):
    lg.info('File : {}'.format(src))

    # 이번엔 np.float64로 했으니 절대 계산 오류같은거는 안날거다...
    nodes = np.empty((0, 3), dtype=np.float64) # 여기에 osm파일의 모든 node 태그의 데이터를 저장합니다.
    utm_nodes =np.empty((0, 3), dtype=np.float64) # 여기에 node 변수에 있는 latlon data를
    # nodes  = [[node_id, lat, lon]]
    # utm_nodes  = [[node_id, x, y]]


    # xml parsing 수행, osm파일은 확장자만 osm이지 사실은 xml 파일이다..
    src_osm = et.parse(src)
    root = src_osm.getroot()

    # osm으로부터 태그와 attribute 불러오기
    for n in root:
        if n.tag == 'node':
            # 배열에 추가하기
            attr = n.attrib
            # lg.debug(attr)
            tmp_line = np.array([[np.float64(attr['id']),np.float64(attr['lat']),np.float64(attr['lon'])]], dtype=np.float64)
            nodes = np.append(nodes,tmp_line, axis=0)


    # txt에서 불러온 utm을 latlon으로 변환 및 utm_nodes에 담습니다
    for n in nodes:
        lg.verbose('n : '+str(n))

        utm_coord = utm.from_latlon(n[1], n[2],UTM_zone_x,UTM_zone_y)
        lg.verbose(str(utm.from_latlon(n[1], n[2],UTM_zone_x,UTM_zone_y)))

        tmp_utm_node = np.array([[n[0], utm_coord[0], utm_coord[1]]])
        utm_nodes = np.append(utm_nodes, tmp_utm_node, axis=0)

    lg.debug('UTM converted array : '+str(utm_nodes))

    # 저장 영역
    txt_path = os.path.join(dst, str(src.replace('.osm', '').split(sep='/')[-1]) + '.txt')

    if save:
        lg.debug(str(utm_nodes[:, 1:]))
        np.savetxt(txt_path, utm_nodes[:, 1:], fmt='%s', delimiter=',')


    if return_type == 'latlon':
        return nodes

    if return_type == 'utm':
        print(type(utm_nodes))
        return utm_nodes


if __name__ == '__main__':
    pass