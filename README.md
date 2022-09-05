# OSM to txt
## 개요
java openstreetmap osm 데이터를 kbub에 사용할 수 있도록 txt파일로 변환합니다

### point_increment.py
osm파일 내부에 존재하는 점의 개수를 늘려줍니다.

### osmtotxt.py 
convert osm to txt from files in the increase folder created by point_increment.py

### 실행순서

python3 point_increment.py

osmtotxt.py

### Prequisites
python3 -m venv venv : 가상환경 생성
pip3 install -r requirements.txt : 필요한 모듈들 설치

### Getting Started

1. JOSM에서 생성한 데이터를 rawdata 파일에 넣어주세요
2. python3 osmtotxt.py 를 실행하면 increased 폴더에 촘촘해진 osm 파일이 자동으로 생성되고,ret 폴더에 txt파일이 일괄 저장됩니다. 이 때, txt파일의 이름은 원본이 어찌 되었든, 숫자만 저장됩니다.
3. ret폴더에 있는걸 필요한 파트에 배포하면 끝...!


