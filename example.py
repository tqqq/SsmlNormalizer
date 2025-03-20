# coding=utf-8

import sys
import os

from ssml_parser.base.parser import SsmlParser, SsmlElement, SsmlLeafElement
# from example.simple_normalizer import SimpleTextNormalizer
from ssml_parser.normalizer.zh import ZhNormalizer


def print_node(node, indent=0):
    if isinstance(node, SsmlLeafElement):
        print(" " * indent + f"<{node.__tagname__} {str(node.attrs)}>: {node.text}")
        return
    print(" " * indent + f"<{node.__tagname__} {str(node.attrs)}>")
    for child in node.children:
        print_node(child, indent + 2)


def main():
    # 创建SSML解析器
    parser = SsmlParser()
    parser.init()

    # 示例SSML文本
    ssml_text = (
        """<speak xml:lang="zh-CN">"""
        """今天是2023年10月15日，气温是25度。"""
        """<say-as interpret-as="date" format="ym">2023-12</say-as>"""
        """<say-as interpret-as="date" format="ym">23-12</say-as>"""
        """<say-as interpret-as="date" format="Ymd">2023-12-23</say-as>"""
        """<say-as>2019-02-03</say-as>"""
        """<say-as>190203</say-as>"""
        """<voice name="female">"""
        """这是女声部分，包含数字987。"""
        """<prosody rate="slow">"""
        """这部分语速较慢，包含数字654。"""
        """</prosody>"""
        """</voice>"""
        """<break time="500ms"/>"""
        """<sub alias="人工智能">AI</sub>技术正在快速发展。"""
        """</speak>"""
    )

    # 处理SSML文本
    result = parser.parse(ssml_text)

    # 打印结果
    print_node(result)
    result.normalize({"zh-CN": ZhNormalizer()})
    result.merge_children()
    print_node(result)

    
    

if __name__ == "__main__":
    main()