# GUI Wrapper Script for input
# created 220905 by chanhyeokson
import glob
import time
import os
from natsort import natsorted
from ott_utils.common import get_last_line
from ott_utils.point_increment import point_increment
from ott_utils.log import WKLogger
from ott_utils.osm_to_txt import osm_to_txt
from ott_utils.txt_to_osm import txt_to_osm
import sys

lg = WKLogger(log_path=os.path.join(os.getcwd(),'logs'),target=os.path.basename(__file__), log_level='verbose')

input_dir = '/Users/chanhyeokson/osm-to-txt-converter/input'
output_dir = '/Users/chanhyeokson/osm-to-txt-converter/output'

def from_osm_to_txt():
    source = glob.glob(input_dir + '/*.osm')
    source = natsorted(source)

    # 전체 경로의 안정성을 위해, input 의 각 파일의 마지막 좌표를 저장합니다.
    # 그리고 이를 osm_to_txt의 coord 파라미터로 넘겨주어, k번째 파일의 끝점과 k-1번째 파일의 시작점이 일치하도록 합니다.
    last_coord = None

    for i, f in enumerate(source):

        # f는 절대경로 형식입니다. 여기에서 파일 이름만 뽑아냅니다. point_increment가 최종 파일을 저장할 때, input과 동일한 이름을 가지게
        # 하기 위함입니다.
        get_filename = lambda n: n.split('/')[-1].replace('.osm', '').replace('.txt', '')

        utm_arr = osm_to_txt(src=f, dst=output_dir, save=True, coord=last_coord, unify_endpoint=False)
        # utm_arr = txt_to_osm(src=f, dst=output_dir, unify_endpoint=True, coord=last_coord, save=True)

        point_increment(
                        # src_path=f, # 입력을 파일 경로로 받습니다.
                        src_array=utm_arr, # 입력을 배열로 받습니다.
                        path_smooth=True, # path_smooting을 진행할 지 결정합니다.
                        dst=output_dir, # 저장할 때 파일 저장 경로를 지정합니다.
                        save=True, # 저장할지 여부를 선택합니다.
                        diagnostic=True, # 경로가 정상적인지를 판단합니다.
                        node_interval=0.05, # 점 간격을 지정합니다.
                        filename=get_filename(f))
        print('point_increment : {} / {} done. '.format(i+1 ,len(source)))

        if i == 0:
            continue
        else:
            last_coord = get_last_line(src=f)


def from_txt_to_osm():
    source = glob.glob(input_dir + '/*.txt')
    source = natsorted(source)

    last_coord = None

    for i, f in enumerate(source):
        get_filename = lambda n: n.split('/')[-1].replace('.osm', '').replace('.txt', '')
        # utm_arr = osm_to_txt(src=f, dst=output_dir, save=True, coord=last_coord, unify_endpoint=False)
        utm_arr = txt_to_osm(src=f, dst=output_dir, unify_endpoint=True, coord=last_coord, save=True)

        point_increment(
            # src_path=f, # 입력을 파일 경로로 받습니다.
            src_array=utm_arr,  # 입력을 배열로 받습니다.
            path_smooth=True,  # path_smooting을 진행할 지 결정합니다.
            dst=output_dir,  # 저장할 때 파일 저장 경로를 지정합니다.
            save=True,  # 저장할지 여부를 선택합니다.
            diagnostic=True,  # 경로가 정상적인지를 판단합니다.
            node_interval=0.05,  # 점 간격을 지정합니다.
            filename=get_filename(f))
        print('point_increment : {} / {} done. '.format(i + 1, len(source)))

        if i == 0:
            continue
        else:
            last_coord = get_last_line(src=f)


if __name__ == "__main__":
    # 미리 말씀드리는데, 이 코드는 사상누각입니다...!
    # 더 나은 방법이 머리속에 떠올랐지만, 돌이키기에는 너무 먼 길을 돌아왔기에 그냥 쓰는 것 뿐입니다.
    # 일단 파이썬 기본 recursion limit을 1000--->10000으로 조정합니다. recursion issue 발생할경우 다시 조정하세요.
    print(sys.setrecursionlimit(10000))

    # from_txt_to_osm()
    from_osm_to_txt()



