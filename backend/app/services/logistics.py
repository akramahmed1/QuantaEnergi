class InventoryTracker:
    def __init__(self):
        self.deliveries = []
    
    def track_delivery(self, location: str, volume: float) -> str:
        self.deliveries.append(f'{volume} to {location}')
        return 'Tracked'
