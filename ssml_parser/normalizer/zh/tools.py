# coding=utf-8

CN_DIGITS = {
    "0": "零",
    "1": "一",
    "2": "二",
    "3": "三",
    "4": "四",
    "5": "五",
    "6": "六",
    "7": "七",
    "8": "八",
    "9": "九",
}
CN_UNITS = {
    "十": "十",
    "百": "百",
    "千": "千",
}
CN_BIG_UNITS = {
    "万": "万",
    "亿": "亿",
    # "万亿": "万亿",
}


def integer_to_chinese(num: str):
    """
    将数字(小于1万万亿, <10^16)转换为中文表示
    """
    try:
        i_num = int(num)
    except:
        raise ValueError(f"num {num} is not an integer")
    
    result = ""
    if num[0] == "-":
        result += "负"
        num = num[1:]
    if len(num) == 1:
        return result + CN_DIGITS[num]
    if len(num) > 16:
        raise ValueError(f"num {num} is bigger than 10^16")
    
    # split num to list every 4 digits
    num = "0"*16 + num
    num = num[-16:]
    result = _i2c_8digit(num[:8])
    if result:
        result += CN_BIG_UNITS["亿"]
        if num[7] == "0" or num[8] == "0":
            result += "零"
    result += _i2c_8digit(num[8:16])
    if result:
        return _clean_normed_number(result)
    else:
        return "零"


def _i2c_4digit(num: str):
    """
    将4位以内数字转换为中文表示
    num: str, len=4
    """
    if len(num) != 4:
        num = "0000" + num
        num = num[-4:]
    result = ""
    if num[0] != "0":
        result += CN_DIGITS[num[0]]
        result += CN_UNITS["千"]
    if num[1] != "0":
        result += CN_DIGITS[num[1]]
        result += CN_UNITS["百"]
    if num[2]!= "0":
        if num[1]== "0" and num[0]!= "0":
            result += "零"
        result += CN_DIGITS[num[2]]
        result += CN_UNITS["十"]
    if num[3] != "0":
        if num[2]== "0" and not (num[0] == "0" and num[1] == "0"):
            result += "零"
        result += CN_DIGITS[num[3]]

    return result


def _i2c_8digit(num: str):
    """
    将8位以内数字转换为中文表示
    num: str, len=8
    """
    if len(num) != 8:
        num = "00000000" + num
        num = num[-8:]
    result = ""
    high, low = num[:4], num[4:]
    high_res = ""
    low_res = ""
    if high != "0000":
        result += _i2c_4digit(high)
        result += CN_BIG_UNITS["万"]
    if low != "0000":
        if result and (high[-1] == "0" or low[0] == "0"):
            result += "零"
        result += _i2c_4digit(low)
    return result


def _clean_normed_number(num_str: str):
    """
    清理正则化后的数字:
      - 开头的"十"
      - "二"替换成"两"
    """
    if num_str.startswith("一十"):
        num_str = num_str[1:]
    num_str = num_str.replace("二", "两")
    num_str = num_str.replace("十两", "十二")
    num_str = num_str.replace("两十", "二十")
    if num_str.endswith("两"):
        num_str = num_str[:-1] + "二"
    return num_str

    

        



def test():
    for test_case in [
        "0",
        "5",
        "123",
        "9009",
        "2004",
        "23400",
        "120000",
        "823000020202"
    ]:
        print(f"{test_case} -> {integer_to_chinese(test_case)}")


def test_i2c_4digit():
    for test_case in [
        "0000",
        "0001",
        "0010",
        "0023",
        "0040",
        "0101",
        "0210",
        "0111",
        "1000",
        "9001",
    ]:
        print(f"{test_case} -> {_i2c_4digit(test_case)}")

def test_i2c_8digit():
    for test_case in [
        "00000000",
        "00000001",
        "00000101",
        "00003101",
        "00010101",
        "23001234",
        "23013056"
    ]:
        print(f"{test_case} -> {_i2c_8digit(test_case)}")


if __name__ == "__main__":
    test()
    # test_i2c_4digit()
    # test_i2c_8digit()
