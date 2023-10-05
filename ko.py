
import requests
import urllib3
import re
import time
import pandas
import sys
import os
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def eraseDoubleSpace(inputText):
    while "  " in inputText:
        inputText = inputText.replace("  ", " ")

    return inputText

def start():

    if getattr(sys, 'frozen', False):
        thisDir = os.path.dirname(sys.executable)
    elif __file__:
        thisDir = os.path.dirname(os.path.realpath(__file__))

    dfHeaders = [
        "단어", "한자", "발음", "품사", "No.", "영어 단어", "한국어의미", "영어의미", "예시문장"
    ]
    df = pandas.DataFrame(columns=dfHeaders)

    with open(os.path.join(thisDir, "input.txt"), 'r', encoding='utf-8') as f:
        keywords = list(map(lambda x:x.strip(), f.readlines()))

    for keyword in keywords:

        params = {
            "nation" : "eng",
            "nationCode" : "6",
            "ParaWordNo": "",
            "mainSearchWord" : keyword
        }

        tryCount = 0
        while tryCount < 20:
            try:
                res = requests.get("https://krdict.korean.go.kr/eng/dicSearch/search", params=params, verify=False)
                break
            except Exception as e:
                tryCount += 1
                time.sleep(10)
                print("인터넷 오류로 인해 잠시 멈추고 다시 시작합니다")

        soup = BeautifulSoup(res.text, 'html5lib')

        for searchResult in soup.select("div.search_result > dl"):

            tempDct = {}

            # get word
            word = searchResult.select_one("span.word_type1_17").getText().replace("\n", "").replace("\t", "")
            wordNumber = "" if searchResult.select_one("span.word_type1_17 > sup") is None else searchResult.select_one("span.word_type1_17 > sup").getText().strip()
            word = word.replace(wordNumber, "")

            # if not the same word skip
            if word != keyword:
                continue

            wordId = searchResult.select_one("a[title='Advanced View']")['href'].split("checkSubmit('")[1].split("'")[0]
            wordParams = {
                "ParaWordNo" : wordId,
                "nation" : "eng"
            }
            tryCount = 0
            while tryCount < 20:
                try:
                    wordRes = requests.get("https://krdict.korean.go.kr/eng/dicSearch/SearchView", params=wordParams, verify=False)
                    break
                except Exception as e:
                    tryCount += 1
                    time.sleep(10)
                    print("인터넷 오류로 인해 잠시 멈추고 다시 시작합니다")
            wordSoup = BeautifulSoup(wordRes.text, 'html5lib')

            # hanja
            hanja = wordSoup.select_one('a.chi_info')
            if hanja is not None:
                hanja = hanja.getText().replace("(", "").replace(")", "").strip()
            else:
                hanja = ""

            # pronounciation
            pro = wordSoup.select_one('dt.manyLang6 + dd > span.search_sub')
            if pro is not None:
                pro = pro.getText().replace("듣기]", "]").strip()
            else:
                pro = ""

            pos = wordSoup.select_one('dt.manyLang6 + dd > span.word_att_type1')
            if pos is not None:
                pos = pos.getText().replace("듣기]", "]").replace("\n", "").replace("\t", "").replace(" ", "").strip()
            else:
                pos = ""

            # print("##########")
            print(word, wordNumber)      
            # print(hanja)
            # print(pro)
            # print(pos)

            tempDct["단어"] = word + wordNumber
            tempDct["한자"] = hanja
            tempDct["발음"] = pro
            tempDct["품사"] = pos

            explainList = wordSoup.select('div.detail_list > div.explain_list')

            for i, explain in enumerate(explainList):
                num = i+1

                # English Word
                if explain.select_one('p.multiTrans') is None:
                    englishWord = ""
                else:
                    englishWord = re.sub("\d.", "", explain.select_one('p.multiTrans').getText()).strip()
                    englishWord = eraseDoubleSpace(englishWord)
                # Korean Meaning
                if explain.select_one('p.senseDef') is None:
                    koreanMeaning = ""
                else:
                    koreanMeaning = re.sub("\d.", "", explain.select_one('p.senseDef').getText()).strip()
                    koreanMeaning = eraseDoubleSpace(koreanMeaning)
                # English Meaning
                if explain.select_one('p.multiSenseDef') is None:
                    englishMeaning = ""
                else:
                    englishMeaning = explain.select_one('p.multiSenseDef').getText().strip()
                    englishMeaning = eraseDoubleSpace(englishMeaning)
                # Examples
                examples = " ".join(map(lambda x:eraseDoubleSpace(x.getText().replace("\n", "").replace("\t", "").strip()),explain.select('ul.printArea > li')))

                tempDct["No."] = num
                tempDct["영어 단어"] = englishWord
                tempDct["한국어의미"] = koreanMeaning
                tempDct["영어의미"] = englishMeaning
                tempDct["예시문장"] = examples

                df = df.append(tempDct, ignore_index=True)

    num = 1
    while os.path.isfile(os.path.join(thisDir, f"result{num}.xlsx")):
        num += 1

    while True:
        try:
            df.to_excel(os.path.join(thisDir, f"result{num}.xlsx"), engine='xlsxwriter', index=False)
            break
        except PermissionError as e:
            print(f"result{num}.xlsx 엑셀파일을 닫아주세요")
            time.sleep(5)

    input("크롤링이 완료되었습니다 (아무키를 눌러서 종료해주세요...)")


if __name__ == "__main__":
    
    start()
        # time.sleep(0.2)


        # 2:46