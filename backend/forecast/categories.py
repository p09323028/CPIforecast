"""14 類別的中→英對應，與 notebook 完全一致。"""
from __future__ import annotations

CATEGORIES: dict[str, str] = {
    "一.食物類": "Food",
    "17.外食費": "FAFH",
    "2.肉類": "meats",
    "11豬肉": "pork",
    "13牛肉、牛內臟": "beef",
    "15雞肉": "poultry",
    "5.水產品": "seafood",
    "4.蛋類": "eggs",
    "20雞蛋": "egg",
    "11.乳類": "dairy",
    "121鮮奶": "milk",
    "7.蔬菜": "vegetable",
    "9.水果": "fruit",
    "12.食用油": "oils",
}

DISPLAY_ZH: dict[str, str] = {
    "Food": "食物類",
    "FAFH": "外食費",
    "meats": "肉類",
    "pork": "豬肉",
    "beef": "牛肉",
    "poultry": "雞肉",
    "seafood": "水產品",
    "eggs": "蛋類",
    "egg": "雞蛋",
    "dairy": "乳類",
    "milk": "鮮乳",
    "vegetable": "蔬菜",
    "fruit": "水果",
    "oils": "食用油",
}


def english_names() -> list[str]:
    return list(CATEGORIES.values())


def display_pairs() -> list[dict[str, str]]:
    return [{"en": en, "zh": DISPLAY_ZH[en]} for en in english_names()]
