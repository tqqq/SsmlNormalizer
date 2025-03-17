# coding=utf-8
from tn.chinese.normalizer import Normalizer as ZhNormalizer


zh_tn_model = ZhNormalizer(remove_erhua=True)


def plain_normalize(text: str):
    """
    Normalize text
    """
    return zh_tn_model.normalize(text)


# def date_normalize(text: str, dformat: str = None):
#     """
#     Normalize date text
#     """
#     return text



