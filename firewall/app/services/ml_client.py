import asyncio

class MLClient:
    async def analyze(self, prompt: str):
        # Mock ML service
        # In a real scenario, this would call the ML service
        await asyncio.sleep(0.01)
        return {"ml_score": 0.0}
