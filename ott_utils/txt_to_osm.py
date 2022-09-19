#!/usr/bin/env python3

import random
import shutil
import numpy as np
import utm
import os
from .log import WKLogger
from .common import _write_osm

UTM_zone_x = 52
UTM_zone_y = 'n'

lg = WKLogger(log_level = 'debug',log_path=os.getcwd(), target=os.path.basename(__file__))


def txt_to_osm(src, dst, save=True, return_type= 'utm', unify_endpoint = True, coord = None):
    '''
    TXT_to_OSM
    ----------
    csv스타일로 저장된 utm 데이터를 xml 형태로 저장된 osm 파일로 변환합니다.


    Args:
        src: 입력 경로
        dst: 출력 경로
        save: 저장 여부
        return_type: 반환 타입을 지정합니다. 기본적으로 utm 값을 반환하지만, 원하는 경우, WGS84로 변환도 가능합니다.

        coord : 임의의 좌표값을 받습니다. 보통 전 파일의 끝 라인을 받습니다.
        unify_endpoint : coord 파라미터로 받은 데이터를 현재 변환중인 파일의 첫 라인에 넣어줍니다.(여러 파일의 분기점을 하나로 맞추기 위함입니다.)

    Returns: 2-depth ndarray
    [[utm_x1, utm_y1], .... [utm_xn, utm_yn]]
    [[lat_x1, lon_y1], .... [lat_xn, lon_yn]]
    '''
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

        if i == 0 and coord is not None and unify_endpoint:
            if coord[0] > 200 and coord[1] > 200:
                converted = utm.to_latlon(coord[0], coord[1], UTM_zone_x, UTM_zone_y)
            tmp_latlon = np.array([[ii, converted[0], converted[1]]], dtype=np.float64)
        else:
            tmp_latlon = np.array([[ii, converted[0], converted[1]]], dtype=np.float64)

        # lg.info(latlon_line)
        latlon_nodes = np.append(latlon_nodes, tmp_latlon, axis=0)

    lg.verbose(latlon_nodes)
    # 저장 영역
    txt_path = os.path.join(dst, str(src.replace('.txt', '').split(sep='/')[-1]) + '.osm')

    if save:
        _write_osm(txt_path, latlon_nodes)


    if return_type == 'utm':
        return txt_raw

    if return_type == 'latlon':
        return latlon_nodes[:][1:]

if __name__ == '__main__':
    txt_to_osm('C:\\Users\\chanh\\PycharmProjects\\osm-to-txt-converter\\input',
                    'C:\\Users\\chanh\\PycharmProjects\\osm-to-txt-converter\\input')