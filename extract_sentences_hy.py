import csv
import json
import random
import re
import sys
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


def process_article(sub_folders, folder):
    n = 100
    if folder == "text":
        n = 40
    for ch in sub_folders:
        if ch == "_":
            return

        if ch == "H":
            n = 34

        for i in range(n):
            if i < 10:
                i = ONES[str(i)]

            filename = f'{folder}/A{ch}/wiki_{i}'
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
    file_name = 'hy_wiki'
    threads = []

    # appending hy.wikipedia sentences in approved_sentences list
    for let_1, let_2 in [("A", "B"), ("C", "D"), ("E", "F"), ("G", "H")]:
        threads.append(Thread(target=process_article, args=([let_1, let_2],'text_ea')))

    # appending hyw.wikipedia sentences in approved_sentences list
    threads.append(Thread(target=process_article, args=(["A", "_"], "text")))

    for idx, t in enumerate(threads):
        print(f"starting thread {idx + 1}\n")
        t.start()

    for t in threads:
        t.join()

    print(f'dumping approved_sentences  (len: {len(approved_sentences)})')
    with open(f"{file_name}.txt", "w") as f:
        for sentence in approved_sentences:
            f.write(sentence+'\n')

    if len(sys.argv) > 1:
        if sys.argv[1] == "generate_sample":
            sample_size = 4103  # calculated this number from https://www.surveymonkey.com/mp/sample-size-calculator/
            print('\ngenerating random sample.....')
            sample = random.sample(approved_sentences, sample_size)

            with open(f'{file_name}.csv', 'w', newline='') as csvfile:
                empty_column = list([" "] * len(sample))
                fieldnames = ['Sentence', 'Sentence_Eval_1', 'Sentence_Eval_2', 'Sentence_Eval_3', 'Comments']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                rows = [{'Sentence': s,
                         'Sentence_Eval_1': " ",
                          'Sentence_Eval_2': " ",
                          'Sentence_Eval_3': " ",
                          'Comments': " "} for s in sample]
                writer.writerows(rows)





