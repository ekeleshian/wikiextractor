import json
import sys
import pickle
import re
from threading import Thread, Lock

mutex = Lock()
approved_sentences = []

ONES = {'0': '00', '1': '01', '2': '02', '3': '03', '4': '04',
        '5': '05', "6": "06", "7": "07", "8": "08", "9": "09"}


def does_meet_criteria(text_str):
    words = text_str.split(" ")
    if len(words) < 3 or len(words) > 14:
        return False

    nums = re.findall('[0-9]+', text_str)
    if len(nums) > 0:
        return False

    upper_case_words = re.findall('([Ա-Ֆ]([ա-ֆ])+)', text_str)
    if len(upper_case_words) > 1:
        return False

    abbreviations = re.findall('[Ա-Ֆ][Ա-Ֆ]+', text_str)
    if len(abbreviations) > 0:
        return False

    non_hy = ''.join(re.findall(
        '[^\u0530-\u058F(\.)+,+-+«+»+]+', text_str)).strip()
    if len(non_hy) > 0:
        return False
    return True


def process_article(folders):
    for ch in folders:
        if ch == "_":
            return
        for i in range(100):
            if i < 10:
                i = ONES[str(i)]
            filename = f'text/A{ch}/wiki_{i}'
            with open(filename, 'r') as f:
                data = f.readlines()
                for idx, article in enumerate(data):
                    data_json = json.loads(article)
                    text = data_json['text']
                    text = text.replace(":", "։")
                    sentences = text.split("։")
                    sentences = [txt + '։' for txt in sentences]
                    count = 0
                    for sentence in sentences:
                        if count > 3:
                            break
                        sentence = sentence.replace('\n', ' ')
                        sentence = re.sub(' +', ' ', sentence)
                        sentence = sentence.strip()
                        if does_meet_criteria(sentence):
                            count += 1
                            mutex.acquire()
                            try:
                                approved_sentences.append(sentence)  # critical section
                            finally:
                                mutex.release()
        print(f"\n{ch} folder done processed.")
        print(f'\n{len(approved_sentences)} collected.')
        print("***************")


if __name__ == '__main__':

    threads = []
    for let_1, let_2 in [("A", "B"), ("C", "D"), ("E", "F"), ("G", "_")]:
        threads.append(Thread(target=process_article, args=([let_1, let_2],)))
    for idx, t in enumerate(threads):
        print(f"starting thread {idx + 1}\n")
        t.start()
    for t in threads:
        t.join()

    print(f'dumping approved_sentences  (len: {len(approved_sentences)})')
    with open("hy_wiki.txt", "w") as f:
        for sentence in approved_sentences:
            f.write(sentence+'\n')
