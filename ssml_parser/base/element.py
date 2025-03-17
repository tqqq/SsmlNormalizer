# coding=utf-8
import abc

# from pydantic import BaseModel, Field
from typing import ClassVar
from .normalizer import Normalizer

class SsmlElement:
    __tagname__: ClassVar[str] = ""

    def __init__(self, parent: "SsmlElement", attrs: dict):
        # super().__init__(parent=parent, attrs=attrs)
        self.parent = parent
        self.attrs = attrs or {}

    def tag_name(self) -> str:
        return self.__tagname__

    def can_merge(self, element: "SsmlElement") -> bool:
        return False

    def merge(self, element: "SsmlElement") -> "SsmlElement":
        return self

    def normalize(self, normalizers: dict[str, Normalizer]):
        pass

    def _get_attr_in_path(self, name):
        node = self
        while node is not None:
            if name in node.attrs:
                return node.attrs[name]
            node = node.parent
        return None


class SsmlNodeElement(SsmlElement, abc.ABC):
    def __init__(self, parent: "SsmlElement", attrs:dict):
        super().__init__(parent=parent, attrs=attrs)
        self.children = []

    def normalize(self, normalizers: dict[str, Normalizer]):
        for child in self.children:
            child.normalize(normalizers)
    
    def merge_children(self):
        for child in self.children:
            if isinstance(child, SsmlNodeElement):
                child.merge_children()

        if len(self.children) == 0:
            return
        new_children = []
        current_child = self.children[0]
        for child in self.children[1:]:
            if current_child.can_merge(child):
                current_child = current_child.merge(child)
            else:
                new_children.append(current_child)
                current_child = child
        new_children.append(current_child)
        self.children = new_children


class SsmlLeafElement(SsmlElement, abc.ABC):
    def __init__(self, parent: "SsmlElement", attrs: dict, text: str):
        super().__init__(parent=parent, attrs=attrs)
        self.text = text or ""

    def normalize(self, normalizers: dict[str, Normalizer]):
        lang = self._get_attr_in_path("xml:lang")
        if lang in normalizers:
            self.text = normalizers[lang].normalize(text=self.text, attrs=self.attrs)


class Speak(SsmlNodeElement):
    __tagname__: ClassVar[str] = "speak"


class Prosody(SsmlNodeElement):
    __tagname__: ClassVar[str] = "prosody"


class Voice(SsmlNodeElement):
    __tagname__: ClassVar[str] = "voice"


class Lang(SsmlNodeElement):
    __tagname__: ClassVar[str] = "lang"


class Break(SsmlLeafElement):
    __tagname__: ClassVar[str] = "break"

    def normalize(self, normalizers: dict[str, Normalizer]):
        self.text = ""
   

class PlainText(SsmlLeafElement):
    __tagname__: ClassVar[str] = "_plain"
    
    def can_merge(self, element: "SsmlElement") -> bool:
        return element.tag_name() in ["_plain", "say-as", "sub"]

    def merge(self, element: "SsmlElement") -> "SsmlElement":
        if not isinstance(element, SsmlLeafElement):
            raise ValueError(f"Can not merge tag [{self.tag_name()}] with [{element.tag_name()}]")
        self.text += element.text
        return self


class SayAs(SsmlLeafElement):
    __tagname__: ClassVar[str] = "say-as"
    
    def can_merge(self, element: "SsmlElement") -> bool:
        return element.tag_name() in ["_plain", "say-as", "sub"]

    def merge(self, element: "SsmlElement") -> "SsmlElement":
        if not isinstance(element, SsmlLeafElement):
            raise ValueError(f"Can not merge tag [{self.tag_name()}] with [{element.tag_name()}]")
        return PlainText(parent=self.parent, attrs={}, text=self.text + element.text)


class Sub(SsmlLeafElement):
    __tagname__: ClassVar[str] = "sub"
    
    def can_merge(self, element: "SsmlElement") -> bool:
        return element.tag_name() in ["_plain", "say-as", "sub"]

    def merge(self, element: "SsmlElement") -> "SsmlElement":
        if not isinstance(element, SsmlLeafElement):
            raise ValueError(f"Can not merge tag [{self.tag_name()}] with [{element.tag_name()}]")
        # self.text += element.text
        return PlainText(parent=self.parent, attrs={}, text=self.text + element.text)

    def normalize(self, normalizers: dict[str, Normalizer]):
        self.text = self.attrs.get("alias", self.text)
    
    

    




    


