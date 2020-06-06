import romanify
import re

def roman_to_int(input):
    """ Convert a Roman numeral to an integer. """

    input = input.upper()
    nums = {'M': 1000, 'D': 500, 'C': 100, 'L': 50, 'X': 10, 'V': 5, 'I': 1}
    sum = 0
    for i in range(len(input)):
        value = nums[input[i]]
        # If the next place holds a larger number, this value is negative
        if i+1 < len(input) and nums[input[i+1]] > value:
            sum -= value
        else:
            sum += value
    return sum

def unquote(text):
    #text = re.sub(r"^(\")+", "", text)
    #text = re.sub(r"(\")+$", "", text)
    #return re.sub(r"(\")+", "\"", text)
    text = re.sub(r"^([^А-Яа-я1-9])+", "", text, flags=re.I | re.DOTALL | re.UNICODE)
    text = re.sub(r"([^А-Яа-я1-9])+$", "", text, flags=re.I | re.DOTALL | re.UNICODE)
    return re.sub(r"([^А-Яа-я0-9 ]){2,}", "", text, flags=re.I | re.DOTALL | re.UNICODE)

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




#address = str(input("Адрес: "))
address = "\"\"\"0, Россия г. Москва, м. ВДНХ, ул. Ленинская Слобода, д. XII помещение XIII КОМ. 27\""
print(f"Входная строка: {address}")

matches = re.findall(r"[MDCXVLImdcxvli]+", address)
#print(Arabicification.roman_to_int("XV"))
for i in range(0, len(matches)):
    address = re.sub(r"{}".format(matches[i]), str(roman_to_int(matches[i])), address, 1)

address = unquote(address)

address = re.sub(r",", " ,", address)
#address = re.sub(r"\"", " \" ", address)
lexems = re.split(r"[ .\"]+", address)
print(lexems)

keys = {"г": "city", "гор": "city", "город": "city", "с": "city", "п": "city", "пос": "city", "поселок": "city", "пгт": "city",
        "улица": "street", "ул": "street", "проспект": "street", "пр": "street", "пр-кт": "street", "бульвар": "street",
        "б-р": "street", "аллея": "street", "шоссе": "street", "шос": "street", "ш": "street", "площадь": "street",
        "пл": "street",
        "дом": "house", "д": "house",
        "м": "metro", "метро": "metro"}

isShort = ["г", "гор", "с", "п", "пос", "пгт", "ул", "пр", "шос", "ш", "пл", "д", "м", ]

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
        types[i] = curType

    types[i] = curType
    i += 1


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

print(types)
print(lexems)
print(address)


