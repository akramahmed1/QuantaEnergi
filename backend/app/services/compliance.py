"""
Compliance Service - Sanctions screening
"""

def screen_trade(trade_region: str) -> bool:
    """
    Sanctions screening - OFAC/CBAM rules
    """
    rules = {
        'me': True,   # Middle East - allowed
        'eu': False,  # EU - blocked (CBAM)
        'us': True,   # US - allowed
        'uk': True,   # UK - allowed
        'guyana': True  # Guyana - allowed
    }
    return rules.get(trade_region, True)  # Default to allowed
