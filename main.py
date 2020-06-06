import re
import time
import pandas as pd

def roman_to_int(input):
    input = input.upper()
    nums = {'M': 1000, 'D': 500, 'C': 100, 'L': 50, 'X': 10, 'V': 5, 'I': 1}
    sum = 0
    for i in range(len(input)):
        value = nums[input[i]]
        if i + 1 < len(input) and nums[input[i+1]] > value:
            sum -= value
        else:
            sum += value
    return sum

def clear(text):
    return re.sub(r"(^[^А-Яа-я1-9]+(?=[А-Яа-я0-9]))|([A-Za-z]+)|([^А-Яа-я0-9 ,.]{2,})|(\(.{0,}\))|([ .-][.-]+,)|((?<=(Москва ))и(?=( МО)))",
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



addressData = pd.read_csv("data.csv", encoding='utf-8', sep=";", error_bad_lines=False, quoting=3)
result = []
addresses = pd.DataFrame(addressData)
print("Size: " + str(len(addressData)))
result_file = open("C:/result.csv", "w")

st = time.time()

iter = 0
for address in addresses["address"]:
    #print(f"Входная строка: {address}")

    matches = re.findall(r"[MDCXVLImdcxvli]+", address)
    for i in range(0, len(matches)):
        address = re.sub(r"{}".format(matches[i]), str(roman_to_int(matches[i])), address, 1)

    address = clear(address)
    #print(f"Регулярки: {address}")

    address = re.sub(r",", " , ", address)
    #address = re.sub(r"\.", " . ", address)
    lexems = re.split(r"[ \"]+", address)

    #print(lexems)

    keys = {"г": "city", "гор": "city", "город": "city", "с": "city", "п": "city", "пос": "city", "поселок": "city", "пгт": "city",
            "улица": "street", "ул": "street", "проспект": "street", "пр": "street", "пр-кт": "street", "бульвар": "street",
            "б-р": "street", "аллея": "street", "шоссе": "street", "шос": "street", "ш": "street", "площадь": "street",
            "пл": "street",
            "дом": "house", "д": "house",
            "м": "metro", "метро": "metro"}

    isShort = ["г", "гор", "с", "п", "пос", "пгт", "ул", "пр", "шос", "ш", "пл", "д", "м", ]

    delete = ["м", "метро"]

    isDone = False
    curType = "none"

    types = list(range(0, len(lexems)))
    meaning = list(range(0, len(lexems))) #none, value, trigger
    for i in range(len(lexems)):
        types[i] = "none"
        meaning[i] = "none"


    i = 0
    while i < len(lexems):
        if i >= len(lexems):
            break
        if (lexems[i] == "0"):
            curType = "trash"
        elif (isPostIndex(lexems[i])):
            curType = "post_index"
        elif lexems[i].lower() == "россия":
            curType = "country"
        elif lexems[i] == ',':
            curType = "comma"
        elif lexems[i].lower() in keys:
            type = keys[lexems[i].lower()]
            curType = keys[lexems[i].lower()]

            types[i] = type
        else:
            if len(types) > 0 and types[i - 1] == "comma":
                curType = "none"
                types[i] = curType

            types[i] = curType

        types[i] = curType
        i += 1

    #print(types)

    lastType = "none"
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

    address = ""
    for i in range(len(lexems)):
        address += lexems[i]

        if i < len(lexems) - 1 and not types[i + 1] == 'comma':
            address += " "

    #print(types)
    #print(lexems)
    #print(address)
    #print("")
    if iter % 5000 == 0:
        print(iter)

    result.append(address)
    result_file.write(f"{addresses.id[iter]};{addresses.address[iter]};{address}\n")
    iter += 1

ft = time.time()
print("Time: " + str((ft - st) * 1000) + " msec")
result_file.close()
