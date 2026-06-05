import pandas as pd

from forecast import data as data_mod
from forecast.categories import FLDID_TO_EN


def _fixture() -> dict:
    """Minimal SDMX-JSON: 2 categories (fldid 2=Food, 18=pork) x 2 months."""
    return {
        "data": {
            "structure": {
                "dimensions": {
                    "series": [
                        {
                            "values": [
                                {"id": "2", "name": "食物類"},
                                {"id": "18", "name": "豬肉"},
                            ]
                        }
                    ],
                    "observation": [
                        {"values": [{"id": "2026-M4"}, {"id": "2026-M5"}]}
                    ],
                }
            },
            "dataSets": [
                {
                    "series": {
                        "0": {"observations": {"0": [100.0], "1": [101.5]}},
                        "1": {"observations": {"0": [130.0], "1": [129.5]}},
                    }
                }
            ],
        }
    }


def test_parse_maps_fldid_to_english():
    wide = data_mod.parse_sdmx_json(_fixture())
    assert list(wide.columns) == ["Food", "pork"]
    assert list(wide.index) == [pd.Timestamp("2026-04-01"), pd.Timestamp("2026-05-01")]
    assert wide.loc["2026-05-01", "Food"] == 101.5
    assert wide.loc["2026-04-01", "pork"] == 130.0


def test_parse_treats_zero_as_missing():
    """Unpublished future months come back as [0]; CPI index is always >0."""
    payload = _fixture()
    payload["data"]["structure"]["dimensions"]["observation"][0]["values"].append(
        {"id": "2026-M6"}
    )
    payload["data"]["dataSets"][0]["series"]["0"]["observations"]["2"] = [0]
    payload["data"]["dataSets"][0]["series"]["1"]["observations"]["2"] = [0]
    wide = data_mod.parse_sdmx_json(payload)
    assert pd.isna(wide.loc["2026-06-01", "Food"])
    assert wide.dropna(how="any").index.max() == pd.Timestamp("2026-05-01")


def test_parse_skips_unknown_fldid():
    payload = _fixture()
    payload["data"]["structure"]["dimensions"]["series"][0]["values"].append(
        {"id": "99999", "name": "未知"}
    )
    payload["data"]["dataSets"][0]["series"]["2"] = {
        "observations": {"0": [1.0], "1": [2.0]}
    }
    wide = data_mod.parse_sdmx_json(payload)
    assert list(wide.columns) == ["Food", "pork"]


def test_build_url_contains_all_14_fldids():
    url = data_mod.build_url(end_period="2026-M5")
    for fldid in FLDID_TO_EN:
        assert f"{fldid}" in url
    assert "endTime=2026-M5" in url
    assert "startTime=1981-M1" in url
    assert data_mod.DATASET_ID in url


def test_fldid_and_categories_agree():
    from forecast.categories import CATEGORIES

    assert set(FLDID_TO_EN.values()) == set(CATEGORIES.values())
    assert len(FLDID_TO_EN) == 14
