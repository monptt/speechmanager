import re
import MeCab
import pprint
import time
import ipadic
mecab = MeCab.Tagger(ipadic.MECAB_ARGS).parse

def makeWordData(word):
    # MeCabの解析結果（単語単位）を受け取り，整形して辞書を返す
    d = {}
    d["text"] = word[0]     # 単語（書字形）
    d["pos"] = word[1]     # 品詞
    d["pos_1"] = word[2]     # 品詞細分類1
    d["pos_2"] = word[3]     # 品詞細分類2
    d["pos_3"] = word[4]    # 品詞細分類3
    d["ctype"] = word[5]    # 活用型（サ変とか）
    d["cform"] = word[6]    # 活用形（連用形とか）
    d["origin"] = word[7]   # 原形
    if(len(word)>=10):
        d["yomi"]   = word[8]   # 読み
        d["pron"]   = word[9]   # 発音
    else:   # 未知語では読みが出てこないので，書字形で代用
        d["yomi"] = d["text"]
        d["pron"] = d["text"]


    d["nmora"] = len(re.sub(r"[ァィゥェォャュョ]", "", d["pron"]))
    if(d["pos"]=="記号"):
        d["nmora"] = 0
    return d

def setDuration(textData, duration):
    # 各単語のdurationを計算して辞書の要素に追加する
    cnt_all_mora = 0
    for word in textData:
        cnt_all_mora += word["nmora"]
    
    # モーラごとの（平均）読み上げ時間
    dur_per_mora = duration/cnt_all_mora

    for word in textData:
        word["duration"] = dur_per_mora * word["nmora"]
    return textData

def makeTextData(text, duration):
    textData = []
    words = mecab(text).split("\n")
    for word in words:
        w = re.split("[\t,]", word)
        if(w[0]=="EOS"):
            break

        worddata = makeWordData(w)
        textData.append(worddata)
    
    textData = setDuration(textData, duration)

    return textData



if __name__=="__main__":
    inputtext = input("Input text here >")
    if(inputtext==""):
        inputtext = "吾輩は猫である。名前はまだ無い。どこで生れたかとんと見当がつかぬ。何でも薄暗いじめじめした所でニャーニャー泣いていた事だけは記憶している。"
    duration = float(input("Input Duration[sec] here > "))

    textData = makeTextData(inputtext)
    # 各単語の時間をセット
    setDuration(textData, duration)
    pprint.pprint(textData)

    # 確認用
    print("start")
    for word in textData:
        print(word["text"])
        time.sleep(word["duration"])    # 組み込むときは　Qtのタイマーか何かを使う
    print("EOS")
