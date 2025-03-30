# coding=utf-8
import pytest
from xml.etree import ElementTree as ET
from ssml_parser.base.parser import SsmlParser
from ssml_parser.base.element import (
    SsmlElement, SsmlNodeElement, SsmlLeafElement,
    Speak, Prosody, Voice, Lang,
    Break, PlainText, SayAs, Sub
)


@pytest.fixture
def parser():
    parser = SsmlParser()
    parser.init()
    return parser


def test_parse_simple_speak(parser):
    ssml_text = "<speak>Hello World</speak>"
    result = parser.parse(ssml_text)
    
    assert isinstance(result, Speak)
    assert len(result.children) == 1
    assert isinstance(result.children[0], PlainText)
    assert result.children[0].text == "Hello World"


def test_parse_nested_elements(parser):
    ssml_text = """<speak>Hello <voice name="female">World</voice></speak>"""
    result = parser.parse(ssml_text)
    
    assert isinstance(result, Speak)
    assert len(result.children) == 2
    assert isinstance(result.children[0], PlainText)
    assert result.children[0].text == "Hello "
    assert isinstance(result.children[1], Voice)
    assert result.children[1].attrs["name"] == "female"
    assert len(result.children[1].children) == 1
    assert isinstance(result.children[1].children[0], PlainText)
    assert result.children[1].children[0].text == "World"


def test_parse_attributes(parser):
    ssml_text = """<speak xmlns="http://www.w3.org/2001/10/synthesis" version="1.0">Test</speak>"""
    result = parser.parse(ssml_text)
    
    assert isinstance(result, Speak)
    assert result.attrs.get("version") == "1.0"
    assert len(result.children) == 1
    assert isinstance(result.children[0], PlainText)
    assert result.children[0].text == "Test"


def test_parse_break(parser):
    ssml_text = """<speak>Before<break time="500ms"/>After</speak>"""
    result = parser.parse(ssml_text)
    
    assert isinstance(result, Speak)
    assert len(result.children) == 3
    assert isinstance(result.children[0], PlainText)
    assert result.children[0].text == "Before"
    assert isinstance(result.children[1], Break)
    assert result.children[1].attrs["time"] == "500ms"
    assert isinstance(result.children[2], PlainText)
    assert result.children[2].text == "After"


def test_parse_say_as(parser):
    ssml_text = """<speak>Count: <say-as interpret-as="digits">12345</say-as></speak>"""
    result = parser.parse(ssml_text)
    
    assert isinstance(result, Speak)
    assert len(result.children) == 2
    assert isinstance(result.children[0], PlainText)
    assert result.children[0].text == "Count: "
    assert isinstance(result.children[1], SayAs)
    assert result.children[1].attrs["interpret-as"] == "digits"
    assert result.children[1].text == "12345"


def test_parse_sub(parser):
    ssml_text = """<speak>I love <sub alias="artificial intelligence">AI</sub></speak>"""
    result = parser.parse(ssml_text)
    
    assert isinstance(result, Speak)
    assert len(result.children) == 2
    assert isinstance(result.children[0], PlainText)
    assert result.children[0].text == "I love "
    assert isinstance(result.children[1], Sub)
    assert result.children[1].attrs["alias"] == "artificial intelligence"
    assert result.children[1].text == "AI"


def test_parse_prosody(parser):
    ssml_text = """<speak><prosody rate="slow" pitch="+10%">Slow speech</prosody></speak>"""
    result = parser.parse(ssml_text)
    
    assert isinstance(result, Speak)
    assert len(result.children) == 1
    assert isinstance(result.children[0], Prosody)
    assert result.children[0].attrs["rate"] == "slow"
    assert result.children[0].attrs["pitch"] == "+10%"
    assert len(result.children[0].children) == 1
    assert isinstance(result.children[0].children[0], PlainText)
    assert result.children[0].children[0].text == "Slow speech"


def test_parse_lang(parser):
    ssml_text = """<speak><lang xml:lang="fr-FR">Bonjour</lang></speak>"""
    result = parser.parse(ssml_text)
    
    assert isinstance(result, Speak)
    assert len(result.children) == 1
    assert isinstance(result.children[0], Lang)
    assert result.children[0].attrs["xml:lang"] == "fr-FR"
    assert len(result.children[0].children) == 1
    assert isinstance(result.children[0].children[0], PlainText)
    assert result.children[0].children[0].text == "Bonjour"


def test_parse_complex_ssml(parser):
    ssml_text = (
        """<speak>"""
        """今天是2023年10月15日，气温是25度。"""
            """<say-as interpret-as="digits">12345</say-as>"""
            """<voice name="female">"""
                """这是女声部分，包含数字987。"""
                    """<prosody rate="slow">"""
                    """这部分语速较慢，包含数字654。"""
                    """</prosody>"""
            """</voice>"""
                """<break time="500ms"/>"""
            """<sub alias="人工智能">AI</sub>技术正在快速发展。"""
        """</speak>""").strip()
    
    result = parser.parse(ssml_text)
    
    assert isinstance(result, Speak)
    assert len(result.children) > 0
    
    # 验证第一个文本节点
    assert isinstance(result.children[0], PlainText)
    assert result.children[0].text == "今天是2023年10月15日，气温是25度。"
    
    # 验证say-as节点
    assert isinstance(result.children[1], SayAs)
    assert result.children[1].attrs["interpret-as"] == "digits"
    assert result.children[1].text == "12345"
    
    # 验证voice节点
    assert isinstance(result.children[2], Voice)
    assert result.children[2].attrs["name"] == "female"
    
    # 验证break节点
    assert isinstance(result.children[3], Break)
    assert result.children[3].attrs["time"] == "500ms"
    
    # 验证sub节点
    assert isinstance(result.children[4], Sub)
    assert result.children[4].attrs["alias"] == "人工智能"
    assert result.children[4].text == "AI"
    
    # 验证最后的文本节点
    assert isinstance(result.children[5], PlainText)
    assert result.children[5].text == "技术正在快速发展。"


def test_invalid_tag(parser):
    ssml_text = """<speak><invalid>Test</invalid></speak>"""
    
    with pytest.raises(ValueError) as excinfo:
        parser.parse(ssml_text)
    
    assert "Unsupported SSML tag" in str(excinfo.value)