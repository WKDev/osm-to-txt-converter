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
if __name__ != "__main__":
    from ott_utils.log import WKLogger
    from ott_utils.deprecated import OSMHandler
else:
    import OSMHandler
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
    print(osm_data)

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

def osm_to_txt(last_folder,dir):
    src = chk_path(last_folder=last_folder, path=dir, file_type='.osm')

    lg.info('source : ' + src)

    return_path = os.path.join(dir, os.path.join(os.getcwd(), dir[2:]) if dir.startswith('./') else dir, last_folder,
                               'osm_to_txt')

    # return_path = os.path.join(dir, os.path.join(os.getcwd(), dir[2:]) if dir.startswith('./') else dir, last_folder,
    #                            'point_increment')
    lg.info('expected return path : ' + str(return_path))

    if not os.path.exists(return_path):
        os.makedirs(return_path)


    if len(glob.glob(src)) == 0 :
        lg.warn('cannot find files from the source directory. script will be terminated.')
    else:
        lg.info(glob.glob(src))

    for f in glob.glob(src):
        lg.info(f)
        new_node_latlon = read_osm(f)

        #osm 2 utm
        tmp_node_latlon = np.delete(new_node_latlon, 0, 1)

        new_node_UTM = latlon_2_UTM(tmp_node_latlon)
        new_node_UTM.astype(np.float64)

        lat_lon = utm.to_latlon(302551.533431,4123889.68239, 52, 's')
        UTM = utm.from_latlon(lat_lon[0], lat_lon[1])

        lg.debug('dirname : ' + str(last_folder))
        lg.debug('dst : ' + str(return_path))
        # shutil.copy(f, os.path.join(return_path, last_folder, 'backup'))
        lg.verbose(str(f.replace('.osm', '').split(sep='/')[-1]))
        txt_path = os.path.join(return_path,str(f.replace('.osm', '').split(sep='/')[-1])+'.txt')
        lg.info('output_destination : ' + txt_path)

        # lg.err('RETURNS : ' + str(new_node_UTM))

        write_UTM_txt(path = txt_path, UTM_numpy_arr= new_node_UTM)

        lg.info('osm_to_txt_done.')


    print("\033[32m[OSM_TO_TXT][INFO] ALL PROCESSES HAVE DONE!")


if __name__ == '__main__':

    osm_to_txt(last_folder='test',dir='./test')

    # print(os.listdir('./increased'))

    # ret.py에서 생성된 데이터를 불러옵니다.

    # ret(src='./rawdata', dst='./increased')

    