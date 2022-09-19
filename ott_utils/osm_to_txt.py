#!/usr/bin/env python3

# point_increment.py

# created : 
# modified : chanhyeokson

# 220903 : (chanhyeokson) added folder check syntax, 
# now user is able to convert osm to txt by executing this script at once.

# 220902 : got scripts from kimhyeonseo
import random

import numpy as np
import utm
import os
import xml.etree.ElementTree as et
import pandas as pd
import glob

if __name__ != "__main__":
    from .log import WKLogger
    from .common import _pretty_print
else:
    from log import WKLogger
    from common import _pretty_print


UTM_zone_x = 52
UTM_zone_y = 'n'

lg = WKLogger( log_level = 'info', target=os.path.basename(__file__),log_path=os.getcwd())

def osm_to_txt(src, dst, save = True, return_type ='utm', coord = None, unify_endpoint=True):
    '''
     OSM 파일을 읽어들여, utm으로 변환합니다. \n
     파라미터에 따라 txt파일로 내보낼 수도, ndarray로 내보낼 수도 있습니다.\n
     np.float64를 적용하여 보다 정확한 계산값을 돌려줍니다.\n
     자세한 사용법은 args를 참조하세요.\n

    Args:
        src: 입력 osm파일 경로를 지정합니다. 경로는 절대경로여야 하며, glob 모듈 사용을 추천합니다.
        dst: 출력 경로를 지정합니다. 경로의 파일 이름까지 지정할 필요는 없습니다. 입력물과 출력물의 경로는 똑같습니다.
        save: True인 경우, 실제 파일로 저장합니다. 기본값이 True입니다.
        return_type: 반환 타입을 지정합니다. 기본적으로 utm 값을 반환하지만, 원하는 경우, WGS84로 변환도 가능합니다.
        coord : 임의의 좌표값을 받습니다. 보통 전 파일의 끝 라인을 받습니다.
        unify_endpoint : coord 파라미터로 받은 데이터를 현재 변환중인 파일의 첫 라인에 넣어줍니다.(여러 파일의 분기점을 하나로 맞추기 위함입니다.)

    Returns: 2-depth ndarray
    [[utm_x1, utm_y1], .... [utm_xn, utm_yn]]
    [[utm_x1, utm_y1], .... [utm_xn, utm_yn]]

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
    for i, n in enumerate(nodes):
        lg.verbose('n : '+str(n))

        utm_coord = utm.from_latlon(n[1], n[2],UTM_zone_x,UTM_zone_y)
        lg.verbose(str(utm.from_latlon(n[1], n[2],UTM_zone_x,UTM_zone_y)))

        tmp_utm_node = np.array([[n[0], utm_coord[0], utm_coord[1]]])
        utm_nodes = np.append(utm_nodes, tmp_utm_node, axis=0)

    if coord is not None and unify_endpoint:
        tmp_utm_node = np.array([[-int(random.random()), coord[0], coord[1]]])
        utm_nodes = np.append(tmp_utm_node, utm_nodes[1:, :], axis=0)

    # lg.info(latlon_line)

    lg.verbose('UTM converted array : '+str(utm_nodes))

    # 저장 영역
    txt_path = os.path.join(dst, str(src.replace('.osm', '').split(sep='/')[-1]) + '.txt')

    if save:
        lg.verbose(str(utm_nodes[:, 1:]))
        np.savetxt(txt_path, utm_nodes[:, 1:], fmt='%s', delimiter=',')


    if return_type == 'latlon':
        return nodes

    if return_type == 'utm':
        # print(type(utm_nodes))
        return utm_nodes[:,1:]


if __name__ == '__main__':
    pass