# coding=utf-8

import pynini
from pynini.lib import pynutil
from .tools import integer_to_chinese
from pynini.lib import pynutil

class DateFst:
    """
    日期FST
    """
    def __init__(self):
        y2, y4 = self._init_year_fst()
        self.fst_list = {
            "m": self._init_month_fst(),
            "d": self._init_day_fst(),
            "y": y2,
            "Y": y4,
        }
        self.symbols_fst = self._init_symbols_fst()
        self.default_fst = self._init_default_fst()

    def _init_month_fst(self):
        number_to_month = {
            "1": ["一月", "1月", "1", "01"], 
            "2": ["二月", "2月", "2", "02"],
            "3": ["三月", "3月", "3", "03"],
            "4": ["四月", "4月", "4", "04"],
            "5": ["五月", "5月", "5", "05"],
            "6": ["六月", "6月", "6", "06"],
            "7": ["七月", "7月", "7", "07"],
            "8": ["八月", "8月", "8", "08"],
            "9": ["九月", "9月", "9", "09"],
            "10": ["十月", "10月", "10"],
            "11": ["十一月", "11月", "11",],
            "12": ["十二月", "12月", "12"]
        }
        month_to_number = {}
        for k, v in number_to_month.items():
            for x in v:
                month_to_number[x] = k
        month_map_fst = pynini.string_map(month_to_number.items())
        return month_map_fst.optimize()

    def _init_day_fst(self):
        day_to_number = {}
        for k in range(1, 32):
            day_to_number[str(k)] = str(k)
            day_to_number[integer_to_chinese(str(k))] = str(k)
            day_to_number[f"{k:02}"] = str(k)

        day_suffix  ={
            "日": "",
            "号": "",
        }
        day_map_fst = pynini.string_map(day_to_number.items()) + pynini.string_map(day_suffix.items()).ques
        return day_map_fst.optimize()

    def _init_year_fst(self):
        digit_to_number = {}
        for i in range(10):
            digit_to_number[str(i)] = str(i)
            digit_to_number[integer_to_chinese(str(i))] = str(i)
        # digit_fst = pynini.string_map(digit_to_number.items())
        year_2_fst = pynini.string_map(digit_to_number.items()).closure(2, 2) + pynini.cross("年", "").ques
        year_4_fst = pynini.string_map(digit_to_number.items()).closure(4, 4) + pynini.cross("年", "").ques
        return year_2_fst.optimize(), year_4_fst.optimize()

    def _init_symbols_fst(self):
        symbols_fst = pynini.string_map({
            " ": "",
            "-": "",
            "/": "",
            ".": "",
            "," : "",
            "\t": "",
        }.items())
        return symbols_fst.optimize()

    def _init_default_fst(self):

        digit_to_number = {}
        for i in range(10):
            digit_to_number[str(i)] = str(i)
            digit_to_number[integer_to_chinese(str(i))] = str(i)
        year_2_fst = pynini.string_map(digit_to_number.items()).closure(2, 2) + pynini.cross("年", "").ques
        year_4_fst = pynini.string_map(digit_to_number.items()).closure(4, 4) + pynini.cross("年", "").ques
        year_fst = pynini.union(year_2_fst, year_4_fst) + self._init_symbols_fst().ques
        default_fst = (
            pynutil.add_weight(year_fst, 2).ques +
            pynutil.insert(" - ") +
            pynutil.add_weight((self._init_month_fst() + self._init_symbols_fst().ques), 0.9).ques +
            pynutil.insert(" - ") +
            pynutil.add_weight(self._init_day_fst(), 1).ques
        )
        return default_fst.optimize()

    def build_fst(self, dformat: str):
        for c in dformat:
            if c not in self.fst_list:
                raise ValueError(f"Unsupported date format: {dformat}")

        result = self.fst_list[dformat[0]]
        for c in dformat[1:]:
            result = result + self.symbols_fst.star + pynutil.insert('-') + self.fst_list[c]
        return result + self.symbols_fst.star


class TimeFst:
    """
    时间FST
    """
    def __init__(self):
        self.fst_list = {
            "h": self._init_hour_fst(),
            "M": self._init_minute_fst(),
            "s": self._init_second_fst(),
            "I": self._init_period_fst()
        }
        self.symbols_fst = self._init_symbols_fst()
        self.default_fst = self._init_default_fst()

    def _init_hour_fst(self):
        # 支持12/24小时制（含中文和数字）
        hour_map = {}
        for h in range(0, 25):
            hour_map[str(h)] = str(h)
            hour_map[f"{h}点"] = str(h)
            hour_map[f"{h}时"] = str(h)
            hour_map[f"{h:02}"] = str(h)
            hour_map[f"{h:02}点"] = str(h)
            hour_map[f"{h:02}时"] = str(h)
            h_c = integer_to_chinese(str(h))
            hour_map[h_c] = str(h)
            hour_map[f"{h_c}点"] = str(h)
            hour_map[f"{h_c}时"] = str(h)
        return pynini.string_map(hour_map.items()).optimize()

    def _init_minute_fst(self):
        # 处理分钟（00-59）
        minute_map = {}
        for m in range(0, 60):
            minute_map[str(m)] = str(m)
            minute_map[f"{m:02}"] = str(m)
            minute_map[f"{m:02}分"] = str(m)
            m_c = integer_to_chinese(str(m))
            minute_map[m_c] = str(m)
            minute_map[m_c + "分"] = str(m)
        return pynini.string_map(minute_map.items()).optimize()

    def _init_second_fst(self):
        # 处理秒钟（00-59）
        second_map = {}
        for s in range(0, 60):
            second_map[str(s)] = str(s)
            second_map[f"{s:02}"] = str(s)
            second_map[f"{s:02}秒"] = str(s)
            s_c = integer_to_chinese(str(s))
            second_map[s_c] = str(s)
        return pynini.string_map(second_map.items()).optimize()

    def _init_period_fst(self):
        # 处理上午/下午标记
        am_fst = pynini.union("a", "A") + pynini.union(".", " ").ques + pynini.union("m", "M")
        am_fst = pynini.cross(am_fst.union("上午"), "AM")
        
        pm_fst = pynini.union("p", "P") + pynini.union(".", " ").ques + pynini.union("m", "M")
        pm_fst = pynini.cross(pm_fst.union("下午"), "PM")

        return pynini.union(am_fst, pm_fst).optimize()

    def _init_symbols_fst(self):
        # 处理时间分隔符
        symbols = {
            ":": "",
            ".": "",
            " ": "",
        }
        return pynini.string_map(symbols.items()).optimize()

    def _init_default_fst(self):
        # 默认格式 h:MM(:ss)( period)
        time_fst = (
            (self._init_period_fst() + self._init_symbols_fst().ques).ques +
            pynutil.insert(" : ") +
            (self._init_hour_fst() + self._init_symbols_fst().ques).ques +
            pynutil.insert(" : ") +
            (self._init_minute_fst() + self._init_symbols_fst().ques).ques +
            pynutil.insert(" : ") +
            pynutil.add_weight(
                (self._init_second_fst() + self._init_symbols_fst().ques), 1.1
            ).ques +
            pynutil.insert(" : ") +
            self._init_period_fst().ques
        )
        return time_fst.optimize()

    def build_fst(self, tformat: str):
        # 与DateFst相同的构建逻辑
        for c in tformat:
            if c not in self.fst_list:
                raise ValueError(f"Unsupported time format: {tformat}")

        result = self.fst_list[tformat[0]]
        for c in tformat[1:]:
            result = result + self.symbols_fst.star + pynutil.insert(' : ') + self.fst_list[c]
        return result + self.symbols_fst.star


