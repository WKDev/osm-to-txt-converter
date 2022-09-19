# OSM to txt
## 개요
- java openstreetmap osm(xml)을 다루는 툴입니다.

## Features
- osm --> txt
- txt --> osm
- GPS 좌표간의 점을 보간합니다. 
- 경로를 부드럽게 만들어줍니다.(기존 path_smoothing 통합)
- 각 텍스트파일의 끝점과 시작점을 동일하게 만들어줍니다.
- (beta)비정상적인 경로(북쪽으로 쭉 가야 하는데 갑자기 남쪽 뜬금없는 곳에 점이 찍힌다든지) 를 탐지해 알려줍니다.


### point_increment.py
- osm파일 내부에 존재하는 점의 개수를 늘려줍니다. 앞서 언급한 대부분의 기능은 이 안에 정의되어 있습니다.

### osm_to_txt.py 
- convert osm to txt from files in the increase folder created by point_increment.py

### txt_to_osm.py 
- convert osm to txt from files in the increase folder created by point_increment.py


### 실행순서
python3 main.py

### Prequisites

python3 -m venv venv : 가상환경 생성
pip3 install -r requirements.txt : 필요한 모듈들 설치

### Getting Started
1. JOSM에서 생성한 데이터 혹은 직접 만든 txt파일을 input 파일에 넣어주세요
2. python3 main.py을 적절히 수정하세요. 아마 주석 처리만 적당히 하면 될겁니다.
3. 처리된 데이터는 output 폴더에 저장됩니다.

더 자세한 내용은 각 파일의 함수에 작성된 docstring을 참조하세요,

### About

22/09/16 K-BUB 손찬혁 / 대부분의 코드 새로 제작 및 기능들 추가

22/09/05 K-BUB 손찬혁 / 기존 오픈소스 기반으로 프로토타입 구성


