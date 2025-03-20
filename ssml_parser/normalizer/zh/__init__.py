# coding=utf-8

from ssml_parser.base.normalizer import Normalizer
from .normalize import normalize

class ZhNormalizer(Normalizer):
    language = "zh-CN"

    def normalize(self, text: str, attrs: dict = None):
        # TODO: interpret-as
        return normalize(text, attrs.get("interpret-as"), attrs)

