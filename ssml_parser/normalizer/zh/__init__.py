# coding=utf-8

from ssml_parser.base.normalizer import Normalizer
from .normalize import plain_normalize

class ZhNormalizer(Normalizer):
    language = "zh-CN"

    def normalize(self, text: str, attrs: dict = None):
        # TODO: interpret-as
        if "interpret-as" in attrs:
            text = plain_normalize(text)
        else:
            text = plain_normalize(text)
        return text

