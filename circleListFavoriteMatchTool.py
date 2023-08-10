import sys
import requests
from bs4 import BeautifulSoup
import csv
import unicodedata
import re

def normalize(str):
    """文字列のUnicode正規化"""
    return unicodedata.normalize('NFKC', str)


def make_unique_list(seq):
    """リストの重複要素を削除"""
    seen = []
    return [x for x in seq if x not in seen and not seen.append(x)]


def parse_circle_list_comitia(soup):
    """コミティアのサークルリストを抽出"""
    circlelist = []
    
    alltr = soup.main.table.find_all('tr')
    for tr in alltr:
        if tr.td.has_attr('colspan'):
            # ブロック文字行は飛ばす
            continue
        alltd = tr.find_all('td')
        # 比較のため正規化したサークル名も取得
        # 作家名は記載なしのため空を設定
        circlelist.append({'location': alltd[0].string,
                           'circleName': alltd[1].string,
                           'normalizedCircleName': normalize(alltd[1].string),
                           'author': ''})
    return circlelist


def parse_circle_list_sdf(soup):
    """SDFのサークルリストを抽出"""
    circlelist = []
    
    alltr = soup.find_all('tr')
    for tr in alltr:
        alltd = tr.find_all('td')
        if len(alltd) != 2:
            # サークル情報以外(カットなど)は飛ばす
            continue

        # サークル情報（先頭にサークル名、末尾に配置、途中はイベント名等）
        infos = list(str.strip() for str in alltd[0].strings)
        author = alltd[1].string

        circlelist.append({'location': infos[-1],
                           'circleName': infos[0],
                           'normalizedCircleName': normalize(infos[0]),
                           'author': author
                           })

    return circlelist


def parse_circle_list_bsmatsuri(soup):
    """BS祭のサークルリストを抽出"""
    circlelist = []
    
    alltr = soup.find_all('tr')
    for tr in alltr:
        alltd = tr.find_all('td')
        if len(alltd) != 6:
            # サークル情報以外(イベントタイトル)は飛ばす
            continue
        if alltd[0].string == "配置ジャンル" or alltd[1].string is None:
            # 見出し行は飛ばす
            continue
        # サークル情報（イベント名、サークル名、ふりがな、ペンネーム、サイト情報、配置番号）
        circlelist.append({'location': alltd[5].string,
                           'circleName': alltd[1].string,
                           'normalizedCircleName': normalize(alltd[1].string),
                           'author': alltd[3].string
                           })

    return circlelist


def parse_circle_list_puniket(soup):
    """ぷにケットのサークルリストを抽出"""
    circlelist = []
    
    alltr = soup.find_all('tr')
    for tr in alltr:
        alltd = tr.find_all('td')
        if len(alltd) != 7:
            # サークル情報以外(イベントタイトル)は飛ばす
            continue
        if not (alltd[2].text.strip()):
            # 見出し行は飛ばす
            continue
        # サークル情報（サークル名、ペンネーム、配置番号、サークルURL、twitter、Pixiv、参加イベント）
        circlelist.append({'location': alltd[2].text,
                           'circleName': alltd[0].text, \
                           'normalizedCircleName': normalize(alltd[0].text),
                           'author': alltd[1].text
                           })
    return circlelist


def parse_circle_list_kobekawasaki(soup):
    """神戸かわさき造船これくしょんのサークルリストを抽出"""
    circlelist = []
    
    alltr = soup.table.tbody.find_all('tr')
    for tr in alltr:
        alltd = tr.find_all('td')
        # サークル情報（SP、SP番号、サークル名、サークル名カナ、ペンネーム、ペンネームカナ、スペース数）
        circlelist.append({'location': alltd[0].text + alltd[1].text,
                           'circleName': alltd[2].text,
                           'normalizedCircleName': normalize(alltd[2].text),
                           'author': alltd[4].text
                           })
    return circlelist


def get_circle_list(url):
    """サークルリストページのデータを取得し、リストを抽出する"""
    response = requests.get(url)
    
    # 文字コード判定はBeautifulSoupで行うため、バイト列で渡す
    soup = BeautifulSoup(response.content, 'html.parser')
    
    parsefuncs = [
        ('.*comitia.*', parse_circle_list_comitia),
        ('.*sdf-event.*', parse_circle_list_sdf),
        ('.*bs-fes.*', parse_circle_list_bsmatsuri),
        ('.*puniket\.com*', parse_circle_list_puniket),
        ('.*kobe-kancolle\.info.*', parse_circle_list_kobekawasaki),
    ]
    
    for parsefunc in parsefuncs:
        if re.match(parsefunc[0], url):
            return parsefunc[1](soup)
    
    print('未対応のサイトです。')
    return None


def match_circle_list(circlelist, favoritefilepath):
    """お気に入りサークルリストファイルの内容を取得し、サークルリストとマッチングする"""
    with open(favoritefilepath, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        # サークルリストの比較
        checklist = []
        for row in reader:
            if row[0] == 'Circle':
                name = normalize(row[10])
            elif row[0] == 'UnKnown':
                name = normalize(row[1])
            else:
                continue

            for circle in circlelist:
                if name == circle['normalizedCircleName']:
                    checklist.append(circle)
    checklist = make_unique_list(checklist)
    return checklist


def print_check_list(checklist):
    """チェックリストを出力"""
    checklist = sorted(checklist, key=lambda circle: normalize(circle['location']))

    print('location\tcircleName\tauthor')
    for c in checklist:
        print(f"{c['location']}\t{c['circleName']}\t{c['author']}") 

if len(sys.argv) != 3:
    print('下記の引数で実行してください。')
    print('$ circleListFavoriteMatchTool.py <サークルリストのURL> <お気に入りリストのファイルパス>')
    quit()

circlelist = get_circle_list(sys.argv[1])
checklist = match_circle_list(circlelist, sys.argv[2])
print_check_list(checklist)
