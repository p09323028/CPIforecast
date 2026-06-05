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


# 主計總處 SDMX API（dataset A030101025）的 fldid 代碼 → 英文名。
# 用代碼對應比用中文品名穩健：SDMX 回傳的品名常有編碼問題，且代碼不會變。
# 注意：必須與上面 CATEGORIES 的 14 個英文名完全一致。
FLDID_TO_EN: dict[str, str] = {
    "2": "Food",        # 一.食物類
    "16": "meats",      # 2.肉類
    "18": "pork",       # 11豬肉
    "20": "beef",       # 13牛肉、牛內臟
    "23": "poultry",    # 15雞肉
    "29": "eggs",       # 4.蛋類
    "30": "egg",        # 20雞蛋
    "32": "seafood",    # 5.水產品
    "59": "vegetable",  # 7.蔬菜
    "113": "fruit",     # 9.水果
    "141": "dairy",     # 11.乳類
    "142": "milk",      # 121鮮奶
    "146": "oils",      # 12.食用油
    "179": "FAFH",      # 17.外食費
}


def english_names() -> list[str]:
    return list(CATEGORIES.values())


def display_pairs() -> list[dict[str, str]]:
    return [{"en": en, "zh": DISPLAY_ZH[en]} for en in english_names()]
