@app.get("/grok-monitor")
async def grok_monitor():
    redis_status = "Connected" if redis_client.ping() else "Disconnected"
    return {
        "status": "ok",
        "redis_status": redis_status,
        "timestamp": "2025-06-30 11:45 CDT",  # Dynamic in production
        "message": "Grok-enhanced monitoring active"
    }
