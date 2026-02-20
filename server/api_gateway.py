from fastapi import FastAPI, Request, Response, HTTPException
import httpx

app = FastAPI()

ROUTE_MAP = {
    "/api/auth": "http://127.0.0.1:8001",
    "/api/user": "http://127.0.0.1:8001",
    "/api/transactions": "http://127.0.0.1:8002",
    "/api/dashboard": "http://127.0.0.1:8002",
    "/api/budget": "http://127.0.0.1:8002",
    "/api/receipts": "http://127.0.0.1:8003",
    "/api/ai": "http://127.0.0.1:8003"
}

async def forward_request(request: Request, target_url: str):
    async with httpx.AsyncClient(timeout=500.0) as client:
        headers = dict(request.headers)
        headers.pop("host", None)
        headers.pop("content-length", None)
        
        body = await request.body()
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
        except Exception as e:
            print(f"Gateway Error: {e}")
            raise HTTPException(status_code=503, detail="Service unavailable")

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(request: Request, path: str):
    request_path = f"/{path}"
    target_base = None
    
    for prefix, service_url in ROUTE_MAP.items():
        if request_path.startswith(prefix):
            target_base = service_url
            break
            
    if not target_base:
        raise HTTPException(status_code=404)
        
    target_url = f"{target_base}{request_path}"
    return await forward_request(request, target_url)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)