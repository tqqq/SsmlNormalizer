# coding=utf-8
import re


CARDINAL = re.compile(r"-?\d+(?:,\d{3})*(?:\.\d+)?")
NUMBERS = re.compile(r"\d+")