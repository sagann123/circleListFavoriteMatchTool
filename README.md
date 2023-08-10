# circleListFavoriteMatchTool
同人イベントサイトのサークルリストからお気に入りサークル情報を抽出するPythonスクリプト  
男性向けの同人イベントに参加する人向けのツールです。  
コミケ以外の同人イベントのサイトにて公開されているサークルリストページからサークル情報を抽出し、コミケWebカタログからダウンロードしたお気に入りデータCSV内のサークル名とマッチしたサークル情報を出力します。  
あらかじめ、コミケWebカタログの有料機能であるお気に入りデータ機能よりお気に入りデータCSVをダウンロードしておく必要があります。  
python3で動作します。

# Requirement
* Python 3
* Beautiful Soup 4
* Requests

# Installation
```bash
pip install beautifulsoup4
pip install requests
```
※作者はvenvにて動作させています。

# Usage
```bash
python3 circleListFavoriteMatchTool.py　[URL] [お気に入りデータcsv]
```

# Author
* sagann
* https://sagann123.github.io/

# License
circleListFavoriteMatchTool is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).
