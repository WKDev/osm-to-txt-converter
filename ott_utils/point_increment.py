#!/usr/bin/env python3
from . import OSMHandler

import argparse
import math
import numpy as np
from haversine import haversine
import os

#Arguments Parsing
parser = argparse.ArgumentParser()
parser.add_argument('--file', '-f', nargs='*', help='file_names', default=[], dest='file_names')
parser.add_argument('--option', '-o', nargs='*', help='options', default=[], dest='options')

filename_input = parser.parse_args().file_names
option_input = parser.parse_args().options

# if len(filename_input) == 0:
#
#     # lane_file_name = "/home/kroad/HDMap_data/HDMap_UTMK_osm/B2_SURFACELINEMARK.osm"
#     #print("----------ARTIV_OSM_FORMATTER----------")
#     #print('LINK File : "A2_LINK.osm"')
#     #print('LANE File : "B2_SURFACELINEMARK.osm"')
#     #print('Output File : "A2_LINK_output.osm"')
#     print("")
# else:
#     raise Exception('Invalid Arguments')
#

if len(option_input) == 0:
    node_interval = 0.05  # 점과 점사이 간격 (단위:m)
    lane_change_nodes = 20


elif len(option_input) == 1:
    node_interval = float(option_input[0])
    lane_change_nodes = 20

elif len(option_input) == 2:
    node_interval = float(option_input[0])
    lane_change_nodes = int(option_input[1])

else:
    raise Exception('Invalid Arguments')




#새로 만드는 id가 기존의 id와 겹치지 않게 조정하는 함수
def check_new_id(nid, id_list):
    if np.isin(-nid, id_list):
        nid += 1

    else:
        return nid

    return check_new_id(nid, id_list)

def point_increment(node_interval, src,dst):
    """_summary_

    Args:
        src (string): JOSM으로 생성한 raw data 경로
        dst (string): 촘촘하게 만든 출력 경로

    Raises:
        FileNotFoundError: src 파라미터로 입력받은 경로가 존재하지 않습니다.
        IndexError: _description_
        IndexError: _description_
    """

    print('[DENSE][INFO] Node Interval :', node_interval, 'meter(s)')
    print('[DENSE][INFO] # of Lane Change Nodes :', lane_change_nodes)
    print("")

    #기존 주행유도선 파일 데이터 parsing
    try:
        if not os.path.isdir(src):
            print(src)
            raise FileNotFoundError
        
        files = os.listdir(src)
        print('[DENSE][INFO] detected files:')
        print('[DENSE][INFO]'+ str(files))


        if len(files) == 0:
            raise IndexError
        files.sort()

        if not os.path.isdir(dst):
            print('[DENSE][INFO]' + os.listdir(dst))
            raise FileNotFoundError
            
        files.sort()

    except FileNotFoundError as e:
        print('\033[31m[DENSE][ERROR] input/output 폴더가 존재하지 않습니다. ')
        print('\033[31m[DENSE][ERROR] input folder : '+ os.path.join(os.getcwd(),src[2:]))
        print('\033[31m[DENSE][ERROR] output folder : '+ os.path.join(os.getcwd(),dst[2:]))

        quit()

    except IndexError:
        print('\033[31m[DENSE][ERROR] '+ src + ' 폴더 내부에 파일이 존재하지 않습니다. ')
        quit()

    for f in files:
        print(os.path.join(dst,f))
        output = open(os.path.join(os.getcwd(),dst[2:],f), mode='wt')  # 촘촘하게 작성

        file_name = os.path.join(src,f)

        osm_data = OSMHandler.OSM_data(file_name)

        nodes = []
        ways = []
        new_nodes = []
        way_id_lst = []

        for data in osm_data:
            if data[0] == 'node' :
                nodes.append(data[1:4])

            elif data[0] == 'way' :
                ways.append(data)
                way_id_lst.append(data[1])


        nodes = np.array(nodes)
        node_ids = nodes[:,0]

        #node 세분화
        id_count = 1 #새로 만드는 node ID는 200000부터 시작

        for way in ways:
            ref_nodes = way[2] #way를 구성하는 nodes

            cnt = 0
            ref_nodes_num = len(ref_nodes)
            every_nodes_for_each_way = []

            #node 간격 파악 후 세분화
            while cnt < ref_nodes_num - 1:
                id1, id2 = ref_nodes[cnt], ref_nodes[cnt+1]

                temp_nodes = dict()

                id1_idx = np.where(nodes[:,0] == id1)
                temp_nodes['id1'] = nodes[id1_idx][0][1:]

                id2_idx = np.where(nodes[:,0] == id2)
                temp_nodes['id2'] = nodes[id2_idx][0][1:]

                #node 간 거리를 haversine 공식으로 계산
                temp_dist = haversine(temp_nodes['id1'], temp_nodes['id2'], unit = 'm')

                #설정한 간격 이하로 노드 간격을 맞추기 위해 필요한 노드의 개수
                n = math.ceil((1/node_interval)*temp_dist + 1)

                #새로운 nodes 형성
                temp_new_nodes = []

                temp_point_x = (temp_nodes['id1'][0])
                temp_point_y = (temp_nodes['id1'][1])
                temp_new_nodes.append([id1, temp_point_x,temp_point_y])

                for k in range(1,n-1):
                    temp_point_x = (temp_nodes['id1'][0]*(n-1-k) + temp_nodes['id2'][0]*k)/(n-1)
                    temp_point_y = (temp_nodes['id1'][1]*(n-1-k) + temp_nodes['id2'][1]*k)/(n-1)
                    temp_new_nodes.append([0, temp_point_x,temp_point_y])

                every_nodes_for_each_way.extend(np.array(temp_new_nodes))


                cnt += 1

                #way내 마지막 node
                if cnt == ref_nodes_num - 1:
                    every_nodes_for_each_way.append(np.array([id2, temp_nodes['id2'][0],temp_nodes['id2'][1]]))
            every_nodes_for_each_way = np.array(every_nodes_for_each_way)
            #print(every_nodes_for_each_way)


            #새로운 nodes에 id 부여
            ## try and except    added by Wontae
            try:
                no_id_idx = np.isin(every_nodes_for_each_way[:,0], 0)
            except IndexError as e:
                print("\033[31m[DENSE][ERROR] Please check ((( action= delete ))) in .osm file")
                raise IndexError(e)


            for i, tf in enumerate(no_id_idx):
                if tf:
                    id_count = check_new_id(id_count, node_ids)
                    every_nodes_for_each_way[i][0] = -id_count
                    id_count += 1

            #way에 새로 만들어진 node들을 추가
            temp_id_list = every_nodes_for_each_way[:,0]
            temp_id_list = list(temp_id_list.astype(int))


            way[2] = temp_id_list

            #pyroutelib3 사용을 위해 way에 태그 추가
            way[3] += 1
            way[4]['highway'] = 'trunk'

            new_nodes.extend(every_nodes_for_each_way)

        #중복 노드 제거
        new_nodes = np.array(new_nodes)

        nodes_uni = [tuple(row) for row in new_nodes]
        nodes_uni = list(set(nodes_uni))
        nodes_uni.sort(reverse=True)


        nodes_np = np.array(nodes_uni)

        # OSM 작성 시작
        text = ["<?xml version='1.0' encoding='UTF-8'?>\n", "<osm version='0.6' upload='false' generator='JOSM'>\n"]

        for nd in nodes_uni:
            text.append("  <node id='{0}' lat='{1}' lon='{2}' />\n".format(int(nd[0]), nd[1], nd[2]))

        for w in ways:
            text.append("  <way id='{0}' action='modify'>\n".format(w[1]))
            for nd in w[2]:
                text.append("    <nd ref='{0}' />\n".format(nd))
            keys=[]
            keys = w[4].keys()
            for key in keys:
                text.append("    <tag k='{0}' v='{1}' />\n".format(key, w[4][key]))
            text.append("  </way>\n")

        text.append("</osm>")

        for line in text:
            output.write(line)

    output.close()

    print("\033[32m[DENSE][INFO] All processes have ended!")


if __name__ == '__main__':

    # point_increment()
    pass
