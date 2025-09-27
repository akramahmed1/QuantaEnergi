def test_quantum_optimize():
    from app.services.ai_service import quantum_optimize_portfolio
    assert 'optimal_weights' in quantum_optimize_portfolio([0.1,0.2], [0.05,0.1])

def test_forecast_load():
    from app.services.ai_service import forecast_load
    result = forecast_load([1.0, 2.0, 3.0])
    assert 'predicted' in result

def test_ensemble_forecast():
    from app.services.ai_service import ensemble_forecast
    result = ensemble_forecast([1.0, 2.0, 3.0])
    assert 'pred' in result and 'accuracy' in result
