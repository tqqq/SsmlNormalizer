# coding=utf-8
from xml.etree import ElementTree as ET
import re
from .element import (
    SsmlElement, SsmlNodeElement, SsmlLeafElement,
    Speak, Prosody, Voice, Lang,
    Break, PlainText, SayAs, Sub
)


class SsmlParser:
    def __init__(self):
        self.tags = {}
        self.namespaces = [
            {"http://www.w3.org/XML/1998/namespace": "xml"}
        ]

    def init(self):
        for tag in [Speak, Prosody, Voice, Lang, Break, PlainText, SayAs, Sub]:
            self.tags[tag.__tagname__] = tag

    def parse(self, text: str) -> SsmlElement:
        root = ET.fromstring(text)
        # 获取speak标签的xmlns属性
        speak_tag = re.findall(f"<speak.*?>", text)[0]
        xmlns = re.findall(f'xmlns="(.*?)"', speak_tag)
        if xmlns:
            self.namespaces[0][xmlns[0]] = ""

        return self._parse_element(None, root)

    def _parse_element(self, parent: SsmlElement | None, root: ET.Element) -> SsmlElement:
        tag = root.tag
        # 收集命名空间映射
        cur_ns = {}
        for prefix, url in root.nsmap.items() if hasattr(root, 'nsmap') else []:
            if prefix is None:
                prefix = ''  # 处理默认命名空间
            cur_ns[url] = prefix

        # 从xmlns属性中收集额外的命名空间
        for attr, value in root.attrib.items():
            if attr.startswith('xmlns:'):
                prefix = attr.split(':')[1]
                cur_ns[value] = prefix
        self.namespaces.append(cur_ns)
        if tag.startswith('{'):
            tag = self._get_prefixed_name(tag)
        if tag not in self.tags:
            raise ValueError(f"Unsupported SSML tag: {tag}")


        # 解析属性
        attrs = {}
        for attr, value in root.attrib.items():
            if attr.startswith('{'):
                attr = self._get_prefixed_name(attr)
            attrs[attr] = value
        # 创建元素实例
        element_class = self.tags[tag]
        if issubclass(element_class, SsmlLeafElement):
            element = element_class(parent=parent, attrs=attrs, text=root.text)
            return element

        element = element_class(parent=parent, attrs=attrs)
        # 解析子节点
        # children = []
        if root.text:  # and root.text.strip():
            text_element = PlainText(parent=element, attrs={}, text=root.text)
            element.children.append(text_element)

        for child_node in root:
            child = self._parse_element(element, child_node)
            element.children.append(child)
            if child_node.tail:  # and child_node.tail.strip():
                tail_element = PlainText(parent=element, attrs={}, text=child_node.tail)
                element.children.append(tail_element)
        self.namespaces.pop(-1)
        return element

    def _get_prefixed_name(self, full_name):
        """将完整的URL形式的标签名转换为带前缀的形式
        ctx_ns example:
        [
            {
                "http://www.w3.org/XML/1998/namespace": "xml",
                ""URL_ADDRESS.com/my_namespace": "my"
            },
            {},
            {},
            {
                "URL_ADDRESS.com/my_namespace": "my2"
            },
        ]
        """
        if '}' not in full_name:
            return full_name
        namespace, tag = full_name[1:].split('}')
        # 倒序查询namespaces
        for ns in reversed(self.namespaces):
            if namespace in ns:
                prefix = ns[namespace]
                return f"{prefix}:{tag}" if prefix else tag
        raise ValueError(f"Namespace not found for tag: {full_name}")


# def print_node(node: SsmlElement, spaces = 0):

#     if isinstance(node, SsmlLeafElement):
#         print(" "*spaces + f"{node.tag_name()}({node.attrs}): {node.text}")
#     else:
#         print(" "*spaces + f"{node.tag_name()}({node.attrs})")
#         spaces += 2
#         for child in node.children:
#             print_node(child, spaces)



def test():

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
    parser = SsmlParser()
    parser.init()
    # root = ET.fromstring(ssml_text)
    result = parser.parse(ssml_text)
    print_node(result)




if __name__ == '__main__':
    test()

