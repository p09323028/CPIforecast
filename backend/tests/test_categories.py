from forecast.categories import CATEGORIES, DISPLAY_ZH, english_names


def test_14_categories():
    assert len(CATEGORIES) == 14
    assert len(english_names()) == 14
    # every english name has a zh display label
    for en in english_names():
        assert en in DISPLAY_ZH


def test_unique_english_names():
    en = list(CATEGORIES.values())
    assert len(en) == len(set(en))
