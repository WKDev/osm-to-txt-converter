import random, time, os
import numpy as np
import xml.etree.ElementTree as et
import utm

def get_last_line(src:str):
    ret = np.empty((0,2), dtype=np.float64)
    nodes = np.empty((0, 2), dtype=np.float64)  # 여기에 osm파일의 모든 node 태그의 데이터를 저장합니다.
    utm_nodes = np.empty((0, 2), dtype=np.float64)  # 여기에 node 변수에 있는 latlon data를

    if src.endswith('.txt'):
        # txt_raw에 gf 경로로부터 txt파일의 경로를 읽어옵니다.
        ret = np.loadtxt(src, dtype=str, delimiter=',')
        ret = ret.astype(np.float64)

    elif src.endswith('.osm'):

        # xml parsing 수행, osm파일은 확장자만 osm이지 사실은 xml 파일이다..
        src_osm = et.parse(src)
        root = src_osm.getroot()

        # osm으로부터 태그와 attribute 불러오기
        for n in root:
            if n.tag == 'node':
                # 배열에 추가하기
                attr = n.attrib
                # lg.debug(attr)
                tmp_line = np.array([[np.float64(attr['lat']), np.float64(attr['lon'])]],
                                    dtype=np.float64)
                nodes = np.append(nodes, tmp_line, axis=0)

        # txt에서 불러온 utm을 latlon으로 변환 및 utm_nodes에 담습니다
        for n in nodes:
            utm_coord = utm.from_latlon(n[0], n[1], 52, 'n')
            tmp_utm_node = np.array([[utm_coord[0], utm_coord[1]]])
            ret = np.append(ret, tmp_utm_node, axis=0)

    # lg.info(txt_raw)

    return ret[-1, :][0], ret[-1, :][1]



def _foldername_generator(t, pth):
    # 현재 날짜를 받아옵니다.
    curr_time = t
    yr = str(curr_time.tm_year)[2:]

    # 날짜가 10보다 작은 경우, 앞에 0을 붙여줍니다.
    month = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_mon)
    d = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_mday)
    h = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_hour)
    _min = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_min)
    _sec = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_sec)

    folders = []

    # 점을 포함하지 않으며, 끝이 숫자로 끝나는 것들을 리스트로 반환합니다.
    for t in os.listdir(pth):
        # lg.debug(t)

        if not str(t).endswith('.txt'):
            # print(t[4:6])
            if t[-1].isdigit() and int(t[4:6]) == int(d) and int(t[2:4]) == int(month):
                folders.append(int(t.split(sep='_')[1]))

    # lg.verbose('folders : ' + str(folders))

    cnt = '1' if len(folders) == 0 else str(max(folders) + 1)
    # lg.verbose('count : ' + cnt)



    ret = yr + month + d + 'T' + h + _min + _sec + '_' + cnt
    return ret

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

def _write_osm(output_path, node):
    print(output_path)
    osm_file = open(output_path, mode='wt')

    # OSM 작성 시작
    text = ["<?xml version='1.0' encoding='UTF-8'?>\n",
            "<osm version='0.6' upload='false' generator='JOSM'>\n"]

    for nd in node:
        text.append("  <node id='{0}' visible = 'true' lat='{1}' lon='{2}' />\n".format(int(nd[0]), nd[1], nd[2]))

    rd = random.randrange(-999999, 0)
    text.append("  <way id='{}' action='modify' visible='true'>\n".format(rd))

    for nd in node:
        text.append("    <nd ref='{}' />\n".format(int(nd[0])))

    text.append('  </way>\n')
    text.append("</osm>")

    for line in text:
        osm_file.write(line)

    osm_file.close()


def _find_last_work(pth):
    '''
    가장 마지막으로 시작한 작업이 저장된 폴더를 반환합니다.
    Args:
        pth:

    Returns:

    '''

    # 현재 날짜를 받아옵니다.

    curr_time = time.localtime()
    yr = str(curr_time.tm_year)[2:]

    # 날짜가 10보다 작은 경우, 앞에 0을 붙여줍니다.
    month = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_mon)
    d = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_mday)
    h = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_hour)
    _min = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_min)
    _sec = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_sec)

    folders = []
    lst = []
    # 점을 포함하지 않으며, 끝이 숫자로 끝나는 것들을 리스트로 반환합니다.
    # 아 별로 스마트하지 못한 접근인데..

    for t in os.listdir(pth):
        # lg.debug(t)
        if str(t).find(".") == -1:
            if t[-1].isdigit() and int(t[4:6]) == int(d) and int(t[2:4]) == int(month):

                lst.append(int(t.split(sep='_')[-1]))
                folders.append(t)
                # lg.verbose(max(lst))

    # lg.debug(str(lst))
    if len(lst) != 0:
        last_dir_name = str(folders[lst.index(max(lst))])
        # lg.verbose(str(lst.index(max(lst))))
        #
        # lg.verbose(str(folders[int(lst.index(max(lst)))]))
        # lg.verbose(str(lst))
        #
        # lg.verbose(str(folders))
        # lg.verbose(str(last_dir_name))

        return last_dir_name

    else:
        return 'test'

def _chk_path(last_folder, path, file_type):
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
        return '%s/*' % os.path.join(path, last_folder) + file_type

    elif path.startswith('C:\\'):
        print('startwith windows(Absolute path)')
        return '%s\\*.osm' % os.path.join(path, last_folder) + file_type
    elif path.startswith('./'):
        print('startwith relative_path')
        return '%s/*.osm' % os.path.join(os.getcwd(),path[2:], last_folder) + file_type

    else:
        print('획인된 경로 : ' + str(path))

        lg.err('절대도 아니고, 상대경로도 아닌 듯 합니다. 혹시 정상적인 경로를 지정한 게 맞나요?')
        raise Exception


def foldername_generator(pth):
    # 현재 날짜를 받아옵니다.
    curr_time = time.localtime()
    yr = str(curr_time.tm_year)[2:]

    # 날짜가 10보다 작은 경우, 앞에 0을 붙여줍니다.
    month = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_mon)
    d = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_mday)
    h = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_hour)
    _min = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_min)
    _sec = (lambda x: '0' + str(x) if x < 10 else str(x))(curr_time.tm_sec)

    folders = []

    # 점을 포함하지 않으며, 끝이 숫자로 끝나는 것들을 리스트로 반환합니다.
    for t in os.listdir(pth):
        lg.debug(t)

        if not str(t).endswith('.txt'):
            print(t[4:6])
            if t[-1].isdigit() and int(t[4:6]) == int(d) and int(t[2:4]) == int(month):
                folders.append(int(t.split(sep='_')[1]))

    lg.debug('folders : ' + str(folders))


    cnt = '1' if len(folders) == 0 else str(max(folders + 1))
    lg.debug('count : ' + cnt)



    ret = yr + month + d + 'T' + h + _min + _sec + '_' + cnt
    return ret
#
# def plotter(cx, cy, title):
#     plt.figure(title)
#     plt.plot(cx, cy, '.b')
#     plt.xlabel('x')
#     plt.ylabel('y')
#     plt.axis("equal")
#     plt.grid(True)


# ------------------------------------------------
# smooth coordinates
#

def _smooth(path, weight_data=0.01, weight_smooth=0.27, tolerance=0.00001):
    # Make a deep copy of path into newpath
    newpath = [[0 for col in range(len(path[0]))] for row in range(len(path))]
    for i in range(len(path)):
        for j in range(len(path[0])):
            newpath[i][j] = path[i][j]

    #### ENTER CODE BELOW THIS LINE ###
    change = 1
    while change > tolerance:
        change = 0
        for i in range(1, len(path) - 1):
            for j in range(len(path[0])):
                ori = newpath[i][j]
                newpath[i][j] = newpath[i][j] + weight_data * (path[i][j] - newpath[i][j])
                newpath[i][j] = newpath[i][j] + weight_smooth * (
                            newpath[i + 1][j] + newpath[i - 1][j] - 2 * newpath[i][j])
                change += abs(ori - newpath[i][j])

    return newpath  # Leave this line for the grader!
