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

lg = WKLogger(log_level = 'debug', target=os.path.basename(__file__))


def txt_to_osm(src, dst, save=True, return_type= 'utm', unify_endpoint = True, coord = None):
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
                tmp_latlon = np.array([[ii+100000, converted[0], converted[1]]], dtype=np.float64)
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