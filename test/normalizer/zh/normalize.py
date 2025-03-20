# coding=utf-8
from ssml_parser.normalizer.zh.normalize import (
    date_normalize, time_normalize, cardinal_normalize, nominal_normalize, telephone_normalize
)


def test_date_normalize():
    for text, df, in [
        ("2023-10", ""),
        ("2023-10-12", ""),
        ("23-12", ""),
        ("12-11", ""),
        ("12年一月12号", ""),
        ("190203", ""),  # bad case
        ("20121201", ""),
        ("2012111", ""),
        ("19-01-02", "ydm"),
        ("19-01-02", "ydd"),
    ]:
        print(f"{text}  {df} -> {date_normalize(text, df)}")

def test_time_normalize():
    for text, df, in [
        # ("2023-10", ""),
        ("下午3点", "Ih"),
        ("12:05", "hM"),
        ("23:12", "Ms"),
        ("17.30.23", "hMs"),
        ("12.00.23", "hMs"),
        ("13.00.00", "hMs"),
        ("17点30分23秒", "hMs"),
        ("12 pm", "hI"),
        ("12:34 am", "hMI"),
    ]:
        print(f"{text}   -> {time_normalize(text, '')}")
        print(f"{text}  {df} -> {time_normalize(text, df)}")


def test_cardinal_normalize():
    for test_case in [
        "100",
        "1,234,566",
        "123243458",
        "82748357438758435493",
        "123.009",
        "12.00",
        "12.100"
    ]:
        print(f"{test_case} -> {cardinal_normalize(test_case)}")
        print(f"-{test_case} -> {cardinal_normalize('-' + test_case)}")


def test_nominal_normalize():
    for test_case in [
        "100",
        "ABC",
        "44G9J",
        "京A-12AB3"
    ]:
        print(f"{test_case} -> {nominal_normalize(test_case)}")


def test_telephone_normalize():
    for test_case in [
        "10086",
        "13688889999",
        "8613688889999",
        "023456",
        "800-810-8888",
        "+86-021-58118818"
    ]:
        print(f"{test_case} -> {telephone_normalize(test_case)}")



def main():
    # test_time_normalize()
    # test_cardinal_normalize()
    # test_nominal_normalize()
    test_telephone_normalize()

if __name__ == "__main__":
    main()


