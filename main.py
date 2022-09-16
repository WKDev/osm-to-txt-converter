# GUI Wrapper Script for input
# created 220905 by chanhyeokson
import glob
import time
import os
from natsort import natsorted
from haversine import haversine
import xml.etree.ElementTree as et

from ott_utils.common import get_last_line
from ott_utils.point_increment import point_increment
from ott_utils.log import WKLogger
from ott_utils.osm_to_txt import osm_to_txt
from ott_utils.txt_to_osm import txt_to_osm
import sys

lg = WKLogger(log_path=os.path.join(os.getcwd(),'logs'),target=os.path.basename(__file__), log_level='verbose')

if __name__ == "__main__":
    # 미리 말씀드리는데, 이 코드는 사상누각입니다...!
    # 더 나은 방법이 머리속에 떠올랐지만, 돌이키기에는 너무 먼 길을 돌아왔기에 그냥 쓰는 것 뿐입니다.

    # osm 파일을 받아서 점 개수만 늘려줍니다.
    # 일단 파이썬 기본 recursion limit을 1000--->10000으로 조정합니다. recursion issue 발생할경우 다시 조정하세요.
    print(sys.setrecursionlimit(10000))

    input_dir = '/Users/chanhyeokson/osm-to-txt-converter/input'
    output_dir = '/Users/chanhyeokson/osm-to-txt-converter/output'

    source = glob.glob(input_dir + '/*.osm')
    source = natsorted(source)

    last_coord = None
    for i, f in enumerate(source):
        get_filename = lambda n: n.split('/')[-1].replace('.osm', '').replace('.txt', '')
        utm_arr = osm_to_txt(src=f, dst=output_dir, save=True, coord=last_coord, unify_endpoint=True)
        # utm_arr = txt_to_osm(src=f, dst=output_dir, unify_endpoint=True, coord=last_coord, save=True)


        point_increment(
                        # src_path=f,
                        src_array=utm_arr,
                        path_smooth=False,
                        dst=output_dir,
                        save=True,
                        diagnostic=True,
                        node_interval=0.,
                        filename=get_filename(f))
        print('point_increment : {} / {} done. '.format(i+1 ,len(source)))

        if i == 0:
            continue
        else:
            last_coord = get_last_line(src=f)

