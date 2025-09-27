def test_calculate_carbon_footprint():
    from app.services.esg_service import calculate_carbon_footprint
    from app.models.trade import Trade
    trade = Trade(quantity=100, asset="renewable_energy")
    assert calculate_carbon_footprint(trade)['co2'] > 0
