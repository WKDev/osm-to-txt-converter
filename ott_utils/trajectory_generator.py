#trajectory_generator
# txt파일로부터 osm으로 역생성된 파일은 way 태그가 없습니다. 
# 이렇게 되면 JOSM에서 확인이 되지 않고, 보간 역시 어렵기에, way태그 생성이 필요한데, 
# trajectory_generator는 way 태그를 추가해줍니다.
# created : 220904 chanhyeokson

import random
from xml.dom.minidom import Element
import xml.etree.ElementTree as et
import os

LOG_TITLE = '[TRAJECTORY_GENERATOR] '
INPUT_PATH = './trajectory_generator/input'

def check_path_valid(src):
    """입력 경로의 유효성을 체크합니다. 경로가 잘못된 경우, 에러를 반환합니다.

    Args:
        src (_type_): _description_

    Raises:
        Exception: _description_
        Exception: _description_
    """
    if not os.path.exists(src):
        os.makedirs(os.path.join(os.getcwd(),src[2:]))
        raise Exception(LOG_TITLE + '\033[31m[WARN] '+src+' 경로가 존재하지 않습니다. 경로를 만들어둘테니, 데이터를 넣어주세요')

    if len(os.listdir(src)) == 0:
        raise Exception(LOG_TITLE + '\033[31m[ERROR]input 경로내에 파일이 없습니다..')

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
            

def trajectory_generator(src):
    
    #input 경로 유효성을 체크합니다.
    check_path_valid(src=src)

    flist = os.listdir(src)

    for f in flist:
        print(LOG_TITLE + '[INFO] File : ' + f)

        src_osm = et.parse(os.path.join(src, f))
        root = src_osm.getroot()

        rd = random.randrange(-999999,0)

        # way태그가 이미 존재하는지 확인
        for k in root:
            if k.tag == 'way':
                print('\033[33m'+LOG_TITLE + '[WARN] way태그가 이미 존재합니다. 일단 무시하고 계속합니다.')

        way = et.SubElement(root, 'way')

        way.set('id',str(rd))
        way.set('action','modify')
        way.set('visible','true')
        # 모든 라인과 태그를 검색합니다.

        for x in root:
            if x.tag == 'node':
                #way 태그 아래에 node태그 id를 nd 태그에 담습니다
                et.SubElement(way, 'nd').set('ref', x.attrib['id'])

        _pretty_print(root)

        tree = et.ElementTree(root)
        with open(os.path.join(src, f), "wb") as file:  
            tree.write(file, encoding='utf-8', xml_declaration=True)                                    

    print('\033[32m' + LOG_TITLE +'[INFO] everything is done.')



if __name__ == "__main__":
    check_path_valid(INPUT_PATH)

    trajectory_generator(INPUT_PATH)
    




