def generate_invoice(trade_id: int, region: str) -> dict:
    currencies = {'us': 'USD', 'me': 'AED', 'eu': 'EUR'}
    amount = 80500.0
    
    # CBAM flag for EU region
    if region == 'eu':
        return {
            'id': trade_id, 
            'amount': amount, 
            'currency': currencies.get(region, 'USD'),
            'warning': 'Carbon tax apply'
        }
    
    return {'id': trade_id, 'amount': amount, 'currency': currencies.get(region, 'USD')}
