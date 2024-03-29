import mock
import pytest

import dtale.charts.utils as chart_utils
from tests import ExitStack
from tests.dtale.test_charts import build_col_def


@pytest.mark.unit
def test_set_mapbox_token():
    with ExitStack() as stack:
        stack.enter_context(mock.patch("dtale.charts.utils.MAPBOX_TOKEN", None))

        chart_utils.set_mapbox_token("test")
        assert chart_utils.MAPBOX_TOKEN == "test"


@pytest.mark.unit
def test_valid_chart_w_invalid_map_chart():
    assert not chart_utils.valid_chart(
        "maps", map_type="choropleth", loc_mode="geojson-id", geojson=None
    )


@pytest.mark.unit
def test_valid_chart_w_invalid_candlestick_chart():
    assert not chart_utils.valid_chart("candlestick", cs_x=None)
    assert chart_utils.valid_chart(
        "candlestick",
        cs_x="x",
        cs_open="open",
        cs_close="close",
        cs_high="high",
        cs_low="low",
    )


@pytest.mark.unit
def test_valid_chart_w_invalid_treemap_chart():
    assert not chart_utils.valid_chart("treemap", treemap_value=None)
    assert not chart_utils.valid_chart("treemap", treemap_value="a", treemap_label=None)
    assert chart_utils.valid_chart("treemap", treemap_value="x", treemap_label="open")


@pytest.mark.unit
def test_convert_date_val_to_date():
    assert (
        chart_utils.convert_date_val_to_date("2020-01-01").strftime("%Y%m%d")
        == "20200101"
    )
    assert (
        chart_utils.convert_date_val_to_date(1577854800000).strftime("%Y%m%d")
        == "20200101"
    )


@pytest.mark.unit
def test_group_filter_handler():
    assert (
        chart_utils.group_filter_handler("date", "2020-01-01", "D")[0]
        == "`date` == '20200101'"
    )
    assert (
        chart_utils.group_filter_handler("date", 1577854800000, "D")[0]
        == "`date` == '20200101'"
    )


@pytest.mark.unit
def test_build_agg_data(unittest, rolling_data):
    import dtale.views as views

    df, _ = views.format_data(rolling_data)
    extended_aggregation = [
        dict(col="0", agg="mean"),
        dict(col="0", agg="sum"),
        dict(col="1", agg="mean"),
    ]
    output, code, cols = chart_utils.build_agg_data(
        df, "date", ["0", "1"], {}, None, extended_aggregation=extended_aggregation
    )
    unittest.assertEqual(
        sorted(output.columns),
        [
            build_col_def("mean", "0"),
            build_col_def("sum", "0"),
            build_col_def("mean", "1"),
            "date",
        ],
    )
    unittest.assertEqual(
        sorted(cols),
        [
            build_col_def("mean", "0"),
            build_col_def("sum", "0"),
            build_col_def("mean", "1"),
        ],
    )

    output, code, cols = chart_utils.build_agg_data(df, "date", ["0", "1"], {}, "mean")
    unittest.assertEqual(
        list(output.columns),
        ["date", build_col_def("mean", "0"), build_col_def("mean", "1")],
    )
    unittest.assertEqual(cols, [build_col_def("mean", "0"), build_col_def("mean", "1")])

    output, code, cols = chart_utils.build_agg_data(
        df, "date", ["0", "1"], {}, "drop_duplicates"
    )
    unittest.assertEqual(
        list(output.columns),
        [
            "index",
            "date",
            build_col_def("drop_duplicates", "0"),
            build_col_def("drop_duplicates", "1"),
        ],
    )
    unittest.assertEqual(
        cols,
        [build_col_def("drop_duplicates", "0"), build_col_def("drop_duplicates", "1")],
    )

    extended_aggregation = [
        dict(col="0", agg="mean"),
        dict(col="0", agg="pctsum"),
        dict(col="1", agg="mean"),
        dict(col="1", agg="first"),
    ]
    output, code, cols = chart_utils.build_agg_data(
        df, "date", ["0", "1"], {}, None, extended_aggregation=extended_aggregation
    )
    unittest.assertEqual(
        sorted(list(output.columns)),
        [
            build_col_def("mean", "0"),
            build_col_def("pctsum", "0"),
            build_col_def("first", "1"),
            build_col_def("mean", "1"),
            "date",
        ],
    )
    unittest.assertEqual(
        sorted(cols),
        [
            build_col_def("mean", "0"),
            build_col_def("pctsum", "0"),
            build_col_def("first", "1"),
            build_col_def("mean", "1"),
        ],
    )
