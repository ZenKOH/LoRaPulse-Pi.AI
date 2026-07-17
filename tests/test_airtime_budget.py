from lorapulse.airtime_budget import AirTimeBudget, estimate_lora_airtime_seconds, get_region_profile


def test_higher_spreading_factor_costs_more_airtime():
    sf7 = estimate_lora_airtime_seconds(24, spreading_factor=7)
    sf12 = estimate_lora_airtime_seconds(24, spreading_factor=12)
    assert sf12 > sf7


def test_budget_records_usage():
    budget = AirTimeBudget(get_region_profile("EU868"))
    assert budget.can_send("node-1", 1.0)
    budget.record_uplink("node-1", 2.5)
    assert budget.remaining_seconds("node-1") == 27.5
