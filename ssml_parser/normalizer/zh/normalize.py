# coding=utf-8

import pynini
import pynini.lib.pynutil
import string
import re

from tn.chinese.normalizer import Normalizer as ZhNormalizer
from .fst import DateFst, TimeFst
from .tools import integer_to_chinese
from . import regex


date_fst = DateFst()
time_fst = TimeFst()
zh_tn_model = ZhNormalizer(remove_erhua=True)


def normalize(text: str, interpret_as: str="", attrs: dict = None):
    """
    Normalize text
    """
    if interpret_as == "date":
        return date_normalize(text, dformat=attrs.get("format"))
    elif interpret_as == "time":
        return time_normalize(text, dformat=attrs.get("format"))
    elif interpret_as == "phone":
        return telephone_normalize(text)
    elif interpret_as == "nominal":
        return nominal_normalize(text)
    elif interpret_as == "cardinal":
        return cardinal_normalize(text)
    elif interpret_as == "ordinal":
        return ordinal_normalize(text)
    elif interpret_as == "email":
        return email_normalize(text)
    else:
        return plain_normalize(text)


def date_normalize(text: str, dformat: str = ""):
    """
    Normalize text
    """
    if dformat:
        result = date_normalize_with_format(text, dformat)
        if result:
            items = result.split("-")
            date_map = dict(zip(list(dformat), items))
            year = date_map.get("Y", date_map.get("y", ""))
            month = date_map.get("m")
            day = date_map.get("d")
            try:
                return build_date_str(year, month, day)
            except ValueError:
                return plain_normalize(text)

    # normalize date without format
    try:
        result = pynini.accep(text) @ date_fst.default_fst
        result = pynini.shortestpath(result).string()
        if result:
            items = result.split("-")
            year, month, day = (c.strip() for c in items)
            try:
                return build_date_str(year, month, day)
            except ValueError:
                return plain_normalize(text)
    except pynini.FstOpError:
        pass
    return plain_normalize(text)


def time_normalize(text: str, dformat: str = ""):
    """
    Normalize text for time expressions
    """
    if dformat:
        result = time_normalize_with_format(text, dformat)
        if result:
            items = result.split(":")
            time_map = dict(zip(list(dformat), items))
            hour = time_map.get("h", "")
            minute = time_map.get("M", "")
            second = time_map.get("s", "")
            period = time_map.get("I", "")
            try:
                return build_time_str(hour, minute, second, period)
            except ValueError:
                return plain_normalize(text)

    # normalize time without format
    try:
        result = pynini.accep(text) @ time_fst.default_fst
        result = pynini.shortestpath(result).string()
        if result:
            items = result.split(" : ")
            # 根据默认FST的顺序解析结果
            period_prefix, hour, minute, second, period_suffix = items
            period = period_prefix or period_suffix
            try:
                return build_time_str(hour, minute, second, period)
            except ValueError:
                return plain_normalize(text)
    except pynini.FstOpError:
        pass
    return plain_normalize(text)


def telephone_normalize(text: str):
    """
    Normalize text
    read by group
    """
    numbers = regex.NUMBERS.findall(text)
    result = " ".join(_phone_normalize(num).strip() for num in numbers)
    result = result.replace("一", "幺")
    return result
    # return zh_tn_model.normalize(text)


def nominal_normalize(text: str):
    """
    Normalize text
    """
    result = ""
    for c in list(text):
        if c.isdigit():
            result += integer_to_chinese(c)
        elif c.lower() in "qwertyuiopasdfghjklzxcvbnm":
            result += f" {c} "
        elif c in string.punctuation:
            result += f" "
        else:
            result += c
    result = re.sub(r"\s+", " ", result)
    result = result.replace("一", "幺")
    return result

    # return " ".join(integer_to_chinese(c) if c.isdigit() else c for c in list(text))


def cardinal_normalize(text: str):
    """
    Normalize text
    """
    try:
        return regex.CARDINAL.sub(lambda x: _cardinal_normalize(x.group(0)), text)
    except ValueError:
        return plain_normalize(text)


def ordinal_normalize(text: str):
    """
    Normalize text
    """
    return zh_tn_model.normalize(text)


def email_normalize(text: str):
    """
    Normalize text
    """
    return zh_tn_model.normalize(text)


def plain_normalize(text: str):
    """
    Normalize text
    """
    # return text
    return zh_tn_model.normalize(text)


def build_date_str(year: str, month: str, day: str):
    """
    Build date string
    """
    result = ""
    if year:
        result += "".join([integer_to_chinese(x) for x in year])
        result += "年"
    if month:
        if int(month) > 12:
            raise ValueError(f"Invalid month: {month}")
        result += integer_to_chinese(month)
        result += "月"
    if day:
        if int(day) > 31:
            raise ValueError(f"Invalid day: {day}")
        result += integer_to_chinese(day)
        result += "日"
    return result


def date_normalize_with_format(text: str, dformat: str = None):
    """
    Normalize date text
    return: xx-xx-xx
    """
    try:
        fst = date_fst.build_fst(dformat)
    except ValueError:
        return ""
    res = pynini.accep(text) @ fst
    try:
        result = pynini.shortestpath(res).string()
    except pynini.FstOpError:
        return ""
    return result


def build_time_str(hour: str, minute: str, second: str, period: str):
    """
    Build time string in Chinese format
    """
    result = ""
    hour = hour.strip()
    minute = minute.strip()
    second = second.strip()
    period = period.strip()
    
    # 处理时间段标记和小时
    if period == "AM":
        result += "上午"
    elif period == "PM":
        result += "下午"
    
    if hour:
        result += integer_to_chinese(hour)
        result += "点"
    
    if minute:
        if int(minute) > 59:
            raise ValueError(f"Invalid minute: {minute}")
        if int(minute) > 0:
            if int(minute) < 10:
                result += "零"
            result += integer_to_chinese(minute)
            result += "分"
        elif second.strip("0"):
            result += "零分"
    
    if second:
        if int(second) > 59:
            raise ValueError(f"Invalid second: {second}")
        if int(second) > 0:
            if int(second) < 10:
                result += "零"
            result += integer_to_chinese(second)
            result += "秒"

    if result.endswith("点"):
        result += "整"
    return result


def time_normalize_with_format(text: str, tformat: str = None):
    """
    Normalize time text
    return: xx : xx : xx
    """
    try:
        fst = time_fst.build_fst(tformat)
    except ValueError:
        return ""
    res = pynini.accep(text) @ fst
    try:
        result = pynini.shortestpath(res).string()
    except pynini.FstOpError:
        return ""
    return result


def _cardinal_normalize(text: str):
    """
    Normalize text
    """
    result = ""
    if text[0] == "-":
        result += "负"
        text = text[1:]
    if "." in text:
        integer_part, decimal_part = text.split(".")
    else:
        integer_part, decimal_part = text, ""
    result += integer_to_chinese(integer_part.replace(",", ""))
    decimal_part = ("1" + decimal_part).strip("0")[1:]  # strip右边的0
    if decimal_part:
        result += "点"
        result += "".join([integer_to_chinese(x) for x in decimal_part])
    return result


def _phone_normalize(text: str):
    """
    Normalize text
    """
    if len(text) <= 5:
        return "".join(integer_to_chinese(c) for c in text)
    if len(text) % 4 == 0:
        return " ".join(_phone_normalize(text[i:i+4]) for i in range(0, len(text), 4))
    if len(text) % 4 == 1:
        return "".join(integer_to_chinese(c) for c in text[:5]) + " " + _phone_normalize(text[5:])
    if len(text) % 4 == 2:
        return ("".join(integer_to_chinese(c) for c in text[:3]) + " " +
                "".join(integer_to_chinese(c) for c in text[3: 6]) + " " +
                _phone_normalize(text[6:])
        )
    return "".join(integer_to_chinese(c) for c in text[:3])  + " " + _phone_normalize(text[3:])










