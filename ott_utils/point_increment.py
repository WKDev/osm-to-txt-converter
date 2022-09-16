#!/usr/bin/env python3
from ott_utils.common import _smooth
from ott_utils.deprecated import OSMHandler

import argparse
import math
import numpy as np
from haversine import haversine
import os, glob, time
from .log import WKLogger
import xml.etree.ElementTree as et
import utm

UTM_zone_x = 52
UTM_zone_y = 'n'


lg = WKLogger( target='point_increment' , log_path=None, log_level = 'info')


def point_increment(src_path = None, path_smooth = True, src_array = None, dst = None, save = True, diagnostic = True, node_interval = 0.1, filename='test'):
    '''
    point_increment
    ---------------
    두 점이 있으면, 그 사이를 일정한 간격으로 보간해줍니다.


    간단한 원리 설명
    ------------
    1. 각 라인의 점과 점 사이는 직선이라 가정합니다.
    2. 두 점으로부터, 거리를 계산하고, 직선의 방정식을 생성합니다.
    (WGS84를 기반으로 계산하는 경우, haversine 사용을 고려해야 하지만, UTM은 그냥 보간해도 됩니다.)
    3. 두 점의 거리에 node_interval 에 부합하도록 얼마나 많은 점이 들어갈 수 있을지 고려하여, 보간 좌표를 찍습니다.
    4. 다만 이경로는 방향이 존재한다는 것을 고려해야 합니다. 전 수학을 못해서 하드코딩했는데,아마 벡터 연산을 사면 더 스마트한 방식으로
    구현이 가능하지 않을까...


    Args:
        src_path: /home/abc.txt 식의 문자열을 넣어주면 거기에서 utm좌표를 불러와 점을 늘린 후, dst 경로에 반환합니다.
        path_smooth:
        src_array:
        dst: /home/output 식의 문자열을 넣어주면 처리 후 저장합니다. 단, 이 때, save=True여야 합니다.
        save: True인 경우, 실제 파일로 저장합니다. 기본값이 True입니다.
        node_interval: 촘촘하게 만들 점 주기를 설정합니다.

    Returns:

    '''


    old_cx, old_cy, new_cx, new_cy = [], [], [], [] # path_smoothing 코드 합침 220914 by chanhyeokson

    # lg.info(src)
    p_prev = None # i-1번째 점
    p_pp = None # i-2번째 점

    array_raw = np.empty((0, 3), dtype=np.float64)
    incremented = np.empty((0, 2), dtype=np.float64)

    if src_path is not None:
        txt_raw = np.loadtxt(src_path, dtype=str, delimiter=',')
        array_raw = txt_raw.astype(np.float64)
        # lg.info(txt_raw)

    if src_array is not None:
        array_raw = src_array

    for i, p in enumerate(array_raw):
        _x2 = None
        _y2 = None
        _x1 = None
        _y1 = None
        _x0 = None
        _y0 = None
        if i == 0:
            p_prev = p
            incremented = np.append(incremented, [p], axis=0)
            continue
        else:
            if i > 2 and diagnostic:
                _x0 = p_pp[0]
                _y0 = p_pp[1]

            _x2 = p[0]
            _y2 = p[1]
            _x1 = p_prev[0]
            _y1 = p_prev[1]

            # if p_prev[0] > p[0]: # x값이 감소하는 경우

            dist = np.linalg.norm(p_prev - p) # 유클리드 거리 계산
            lg.debug('dist : {} {} {} {} {}'.format(_x1, _y1, _x2, _y2,dist))
            # lg.info(p)
            # lg.info(p_prev)

            # 거리가 너무 좁으면 이 작업을 스킵합니다.
            if dist < node_interval:
                lg.warn('dist : {} is less than node interval'.format(dist))
                continue

            x_dist = abs(_x2 - _x1)
            y_dist = abs(_y2 - _y1)

            # 기울기
            _slope = lambda b2, b1, a2, a1 : (b2 - b1)/(a2 - a1)
            slope = _slope(_y2,_y1,_x2,_x1)
            lg.debug('slope : {}'.format(slope))
            # 두 점으로 만들어낸 일차함수
            _eq_y = lambda x: slope * (x - _x2) + _y2

            # 두 점사이에 추가할 수 있는 점 개수 세기
            _point_available = int(dist/node_interval) -1
            _points_to_add = np.empty((0, 2), dtype=np.float64)

            lg.debug('expected new points : {}'.format(_point_available))

            if i > 2 and diagnostic:
                # threshold = np.pi / 4  # 점이 아무리 꺾여도 pi/4 이상 꺾이면 문제가 있는겁니다.. point_increment 진행하면 더욱 더요.
                threshold = 45
                # k점과 k-1, k-1과 k-2간의 각도 구하기
                prev_slope_deg = np.rad2deg(np.arctan2(_y1-_y0, _x1-_x0))
                curr_slope_deg = np.rad2deg(np.arctan2(_y2-_y1, _x2-_x1))

                check_line_valid = True if prev_slope_deg-threshold < curr_slope_deg < threshold + prev_slope_deg else False

                lg.debug('current deg : {}, prev: {}'.format(curr_slope_deg, prev_slope_deg))

                if not check_line_valid:
                    lg.err('current deg : {}, prev: {}'.format(curr_slope_deg, prev_slope_deg))
                    if src_path is not None:
                        lg.err('invalid path moving detected at the file {}, line : {}'.format(src_path, i))
                    if src_array is not None:
                        lg.err('invalid path moving detected at filename : {}, src array line:{}, check original file.'.format(filename,i))


            if _point_available > 2:
                for t in range(_point_available):
                    tmp_point = np.empty((0, 1), dtype=np.float64)
                    t = t+1 # 0 -n --> 1-->n+1

                    if slope > 0: # 기울기가 0보다 크면 , p가 p_prev보다 크다,

                        if p_prev[0] < p[0]:
                            x_new = _x1 + x_dist * t / _point_available
                            y_new = _eq_y(x_new)
                        else:
                            x_new = _x1 - x_dist * t / _point_available
                            y_new = _eq_y(x_new)

                        # x_new = _x1 + x_dist*t / _point_available
                        # y_new = _y1 + y_dist*t / _point_available
                        tmp_point = np.array([x_new, y_new],dtype=np.float64)

                    if slope < 0: # 기울기가 0보다 크면 , p가 p_prev보다 크다,
                        if p_prev[0] < p[0]:
                            x_new = _x1 + x_dist * t / _point_available
                            y_new = _eq_y(x_new)
                        else:
                            x_new = _x1 - x_dist * t / _point_available
                            y_new = _eq_y(x_new)

                        tmp_point = np.array([x_new, y_new],dtype=np.float64)

                    _points_to_add = np.append(_points_to_add, [tmp_point], axis=0)

                incremented = np.append(incremented, _points_to_add[:-1],axis=0)

            lg.debug('incremented :')
            lg.verbose(incremented)

        incremented = np.append(incremented, [p], axis=0)

        if diagnostic:
            p_pp = p_prev
            p_prev = p

    txt_path = os.path.join(dst, filename +'.txt')
    # txt_path = os.path.join(dst, str(dst.replace('.txt', '').split(sep='/')[-1]) + '.txt')
    lg.debug('file will be saved here:  {}'.format(txt_path))


    if path_smooth:
        cx = incremented
        newpath = _smooth(cx)
        with open(txt_path, 'w') as fw:
            for coord_x, coord_y in newpath:
                # print(coord_x,coord_y)
                fw.write(str(coord_x))
                fw.write(',')
                fw.write(str(coord_y))
                fw.write('\n')
                new_cx.append(coord_x)
                new_cy.append(coord_y)

        return

    if save:
        # lg.debug(str(incremented))
        np.savetxt(txt_path, incremented, fmt='%s', delimiter=',')

            # 4m 간격 거리에 2m 간격으로 점을 추가한다면? 1개 개
            # 6m 간격에 1m 간격으로 추가하면? 5개 |-.-.-.-.-.-|
            #
            # 두 점으로부터 linear regression
            # sqrt(x^2-y^2) = node_interval
            # y-y0 = (y-y0)/(x-x0)*(x-x0)

if __name__ == '__main__':

    # ret()
    pass
