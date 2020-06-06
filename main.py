import re
import os
import time
import threading
import pandas as pd

def roman_to_int(input):
    input = input.upper()
    nums = {'M': 1000, 'D': 500, 'C': 100, 'L': 50, 'X': 10, 'V': 5, 'I': 1}
    sum = 0
    for i in range(len(input)):
        value = nums[input[i]]
        if i + 1 < len(input) and nums[input[i + 1]] > value:
            sum -= value
        else:
            sum += value
    return sum


def clear(text):
    return re.sub(
        r"(^[^А-Яа-я1-9]+(?=[А-Яа-я0-9]))|([A-Za-z]+)|([^А-Яа-я0-9 ,.]{2,})|(\(.{0,}\))|([ .-][.-]+,)|((?<=(Москва ))и(?=( МО)))",
        "", text, flags=re.I | re.DOTALL | re.UNICODE)


def isInteger(text):
    try:
        int(text)
        return True
    except ValueError:
        return False


def isPostIndex(text):
    if len(text) == 6 and isInteger(text):
        return True
    return False


def parse(addresses, resList, count=0, cpus=1):
    res = []
    for iter in range(count, len(addresses.address), cpus):

        result = addresses.address[iter]

        matches = re.findall(r"[MDCXVLImdcxvli]+", result)
        for i in range(len(matches)):
            result = re.sub(r"{}".format(matches[i]), str(roman_to_int(matches[i])), result, 1)

        result = clear(result)

        result = re.sub(r",", " , ", result)
        result = re.sub(r"\.", " . ", result)
        lexems = re.split(r"[ \"]+", result)

        keys = {"г": "city", "гор": "city", "город": "city", "с": "city", "пос": "city", "поселок": "city",
                "пгт": "city",
                "улица": "street", "ул": "street", "проспект": "street", "пр": "street", "пр-кт": "street",
                "бульвар": "street",
                "б-р": "street", "аллея": "street", "шоссе": "street", "шос": "street", "ш": "street",
                "площадь": "street",
                "пл": "street",
                "дом": "house", "д": "house",
                "м": "trash", "метро": "trash", "п": "trash"}

        curType = "none"

        types = list(range(0, len(lexems)))
        for i in range(len(lexems)):
            types[i] = "none"

        i = 0
        while i < len(lexems):
            if i >= len(lexems):
                break
            if (isPostIndex(lexems[i])):
                curType = "post_index"
            elif lexems[i].lower() == "россия":
                curType = "country"
            elif lexems[i] == ',':
                curType = "comma"
            elif lexems[i] in keys:
                curType = keys[lexems[i]]
            else:
                if len(types) > 0 and types[i - 1] == "comma":
                    curType = "none"
                    types[i] = curType

            types[i] = curType
            i += 1

        i = 0
        while True:
            if i >= len(lexems):
                break

            if types[i] == "comma":
                if i == 0 or i > 0 and types[i - 1] == "comma":
                    del types[i]
                    del lexems[i]
                    i -= 1
            if types[i] == "metro" or types[i] == "trash":
                del types[i]
                del lexems[i]
                i -= 1
            i += 1

        result = ""
        for i in range(len(lexems)):
            result += lexems[i]

            if i < len(lexems) - 1 and not types[i + 1] == 'comma':
                result += " "

        result = re.sub(r"( +\.)", ".", result)
        resList[iter] = result


addressData = pd.read_csv("data.csv", encoding='utf-8', sep=";", error_bad_lines=False, quoting=3)
addresses = pd.DataFrame(addressData)
result = list(range(len(addresses.id)))

thread_count = os.cpu_count() - 1
threads = []
for i in range(thread_count):
    threads.append(threading.Thread(target=parse, args=(addresses, result, i, thread_count)))
    threads[i].start()

for i in range(thread_count):
    threads[i].join()


result_file = open("result_odin_null_odin.csv", "w")
result_file.write(f"id;address;result\n")
for iter in range(len(addresses)):
    result_file.write(f"{addresses.id[iter]};\"{addresses.address[iter]}\";\"{result[iter]}\"\n")
result_file.close()

