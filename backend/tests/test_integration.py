def test_fetch_erp_data():
    from app.services.integration_service import fetch_erp_data
    result = fetch_erp_data("test_endpoint")
    assert 'mock' in result
