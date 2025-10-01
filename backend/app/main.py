# ... [existing code above unchanged] ...
# Fix router collision
from app.api.v1.advanced_etrm import router as advanced_etrm_router
app.include_router(advanced_etrm_router, prefix="/api/v1/advanced")
