# coding=utf-8

from ssml_parser.normalizer.zh.fst import DateFst, TimeFst
import time
import pynini


def test_time():
    time_fst = TimeFst()
    for test_case in [
        "下午3点",
        "12:05",
        "23:12",
        "17.30.23",
        "17点30分23秒",
        "12 pm",
        "12:34 am",
    ]:
        pass
        # print(f"{test_case} -> {time_fst.normalize(test_case)}")
        # c = pynini.accep(test_case) @ time_fst.default_fst
        #
        # print(f"{test_case} -> {pynini.shortestpath(c).string()}")
        # print(pynini.shortestpath(c).string())
    for test_case in [
            ("下午3点", "Ih"),
            ("12:05", "hM"),
            ("23:12","Ms"),
            ("17.30.23", "hMs"),
            ("17点30分23秒", "hMs"),
            ("12 pm", "hI"),
            ("12:34 am", "hMI"),
    ]:
        fst = time_fst.build_fst(test_case[1])
        c = pynini.accep(test_case[0]) @ fst
        print(f"{test_case[0]} {test_case[1]}-> {pynini.shortestpath(c).string()}")


def main():
    test_time()


if __name__ == "__main__":
    main()


