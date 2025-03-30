# coding=utf-8

import pytest
from ssml_parser.normalizer.zh.normalize import (
    normalize, date_normalize, time_normalize, telephone_normalize,
    nominal_normalize, cardinal_normalize, ordinal_normalize,
    email_normalize, plain_normalize
)


class TestNormalize:
    
    @pytest.mark.parametrize("text, interpret_as, attrs, expected", [
        ("2023-10-15", "date", {}, "二零二三年一十月一十五日"),
        ("12:30", "time", {}, "一十二点三十分"),
        ("13912345678", "phone", {}, "幺三九 幺二三 四五六 七八"),
        ("123", "nominal", {}, "幺二三"),
        ("123", "cardinal", {}, "一百二十三"),
        ("第123章", "ordinal", {}, "第一百二十三章"),
        ("test@example.com", "email", {}, "test@example.com"),  # 假设邮箱保持不变
        ("普通文本123", "", {}, "普通文本一百二十三"),  # 默认使用 plain_normalize
    ])
    def test_normalize(self, text, interpret_as, attrs, expected):
        if attrs is None:
            attrs = {}
        result = normalize(text, interpret_as, attrs)
        assert result == expected


class TestDateNormalize:
    
    @pytest.mark.parametrize("text, dformat, expected", [
        ("2023-10-15", "", "二零二三年一十月一十五日"),
        ("20231015", "Ymd", "二零二三年一十月一十五日"),
        ("15/10/2023", "d/m/Y", "二零二三年一十月一十五日"),
        ("10/15/2023", "m/d/Y", "二零二三年一十月一十五日"),
        ("2023年10月15日", "", "二零二三年一十月一十五日"),
        ("23-10-15", "", "二零二三年一十月一十五日"),  # 假设能识别简短年份
        ("10-15", "", "一十月一十五日"),  # 只有月日
        ("无效日期", "", "无效日期"),  # 无法解析的日期返回原文本
    ])
    def test_date_normalize(self, text, dformat, expected):
        result = date_normalize(text, dformat)
        assert result == expected
    
    @pytest.mark.parametrize("text, dformat", [
        ("2023-13-15", ""),  # 无效月份
        ("2023-10-32", ""),  # 无效日期
    ])
    def test_date_normalize_invalid(self, text, dformat):
        # 对于无效日期，应该返回原始文本的标准化形式
        result = date_normalize(text, dformat)
        assert result == plain_normalize(text)


class TestTimeNormalize:
    
    @pytest.mark.parametrize("text, tformat, expected", [
        ("12:30", "", "一十二点三十分"),
        ("12:30:45", "", "一十二点三十分四十五秒"),
        ("01:05", "", "一点零五分"),
        ("01:00", "", "一点整"),
        ("12:00:00", "", "一十二点整"),
        ("12:00:05", "", "一十二点零分零五秒"),
        ("123000", "hMs", "一十二点三十分"),
        ("AM 08:30", "", "上午八点三十分"),
        ("PM 02:30", "", "下午二点三十分"),
    ])
    def test_time_normalize(self, text, tformat, expected):
        result = time_normalize(text, tformat)
        assert result == expected
    
    @pytest.mark.parametrize("text, tformat", [
        ("12:60", ""),  # 无效分钟
        ("12:30:60", ""),  # 无效秒数
    ])
    def test_time_normalize_invalid(self, text, tformat):
        # 对于无效时间，应该返回原始文本的标准化形式
        result = time_normalize(text, tformat)
        assert result == plain_normalize(text)


class TestTelephoneNormalize:
    
    @pytest.mark.parametrize("text, expected", [
        ("13912345678", "幺三九 幺二三 四五六 七八"),
        ("021-12345678", "零二幺 幺二三 四五六 七八"),
        ("400-123-4567", "四零零 幺二三 四五六 七"),
        ("12345", "幺二三四五"),  # 短号码
        ("123 456 789", "幺二三 四五六 七八九"),  # 带空格的号码
    ])
    def test_telephone_normalize(self, text, expected):
        result = telephone_normalize(text)
        assert result == expected


class TestNominalNormalize:
    
    @pytest.mark.parametrize("text, expected", [
        ("123", "幺二三"),
        ("ABC123", "A B C 幺二三"),
        ("123ABC", "幺二三 A B C"),
        ("A1B2C3", "A 幺 B 二 C 三"),
        ("测试123", "测试幺二三"),
        ("123测试", "幺二三测试"),
        ("A-B-C", "A B C"),  # 标点符号被替换为空格
    ])
    def test_nominal_normalize(self, text, expected):
        result = nominal_normalize(text)
        assert result == expected


class TestCardinalNormalize:
    
    @pytest.mark.parametrize("text, expected", [
        ("123", "一百二十三"),
        ("1,234", "一千二百三十四"),
        ("1,234,567", "一百二十三万四千五百六十七"),
        ("123.45", "一百二十三点四五"),
        ("-123", "负一百二十三"),
        ("测试123测试", "测试一百二十三测试"),  # 文本中的数字
        ("123.450", "一百二十三点四五"),  # 小数点后的尾随零被去除
    ])
    def test_cardinal_normalize(self, text, expected):
        result = cardinal_normalize(text)
        assert result == expected


class TestOrdinalNormalize:
    
    @pytest.mark.parametrize("text, expected", [
        ("第1章", "第一章"),
        ("第123节", "第一百二十三节"),
        ("第一百二十三节", "第一百二十三节"),  # 已经是中文的情况
    ])
    def test_ordinal_normalize(self, text, expected):
        # 注意：这里假设 zh_tn_model.normalize 能正确处理序数词
        # 如果实际行为不同，需要调整测试用例
        result = ordinal_normalize(text)
        assert result == expected


class TestEmailNormalize:
    
    @pytest.mark.parametrize("text, expected", [
        ("test@example.com", "test@example.com"),
        ("user.name123@company-domain.co.uk", "user.name123@company-domain.co.uk"),
    ])
    def test_email_normalize(self, text, expected):
        # 注意：这里假设邮箱地址保持不变
        # 如果实际行为不同，需要调整测试用例
        result = email_normalize(text)
        assert result == expected


class TestPlainNormalize:
    
    @pytest.mark.parametrize("text, expected", [
        ("普通文本", "普通文本"),
        ("文本123", "文本一百二十三"),
        ("文本123.45", "文本一百二十三点四五"),
    ])
    def test_plain_normalize(self, text, expected):
        # 注意：这里假设 zh_tn_model.normalize 的行为
        # 如果实际行为不同，需要调整测试用例
        result = plain_normalize(text)
        assert result == expected