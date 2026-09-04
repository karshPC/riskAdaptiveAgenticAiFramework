import numpy as np
import pandas as pd

from experiments.run_empirical_extensions import threshold_cost_analysis


def test_cost_analysis_selects_lowest_cost_threshold():
    result = threshold_cost_analysis(
        pd.Series([0, 0, 1, 1]),
        np.array([0.1, 0.4, 0.6, 0.9]),
        false_block_cost=5,
        false_allow_cost=1,
    )

    assert result["optimum"]["cost"] == min(item["cost"] for item in result["curve"])
    assert result["cost_matrix"] == {"false_block": 5, "false_allow": 1}
