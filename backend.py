from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
app = FastAPI(title="Backend application")

class StockRequest(BaseModel):
    symbol: str

@app.get("/get_stock")
async def get_stock(data: StockRequest):
    return {"symbol":data.symbol, "price":100.0}



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000):


