# web_service.py
"""
简单的web服务：使用真实的demo核心功能
"""
import json
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

# 导入真实的诊断核心
from diagnosis_core import DiagnosisService


class ChatRequest(BaseModel):
    message: str
    user_id: str = None


# 创建FastAPI应用
app = FastAPI(title="故障诊断AI服务", description="基于真实demo核心的web服务")

# 添加CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "故障诊断AI服务", "version": "real-demo"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "故障诊断AI"}


# 创建诊断服务实例
diagnosis_service = DiagnosisService(verbose=False)


@app.post("/chat")
async def chat(request: ChatRequest):
    """同步聊天接口"""
    try:
        result = await diagnosis_service.diagnose(request.message)
        return {
            "response": result,
            "status": "success"
        }
    except Exception as e:
        return {
            "response": f"诊断出错: {str(e)}",
            "status": "error"
        }


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """流式聊天接口"""
    async def generate():
        try:
            async for chunk in diagnosis_service.diagnose_stream(request.message):
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        except Exception as e:
            error_chunk = {
                "type": "error",
                "message": str(e),
                "status": "failed"
            }
            yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)