# web_service.py
"""
Web控制器层：处理HTTP请求和响应
"""
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .diagnosis_core import DiagnosisService


# 请求模型
class ChatRequest(BaseModel):
    message: str
    user_id: str = None


# 响应模型
class ChatResponse(BaseModel):
    response: str
    status: str


class HealthResponse(BaseModel):
    status: str
    service: str


# 创建路由器
router = APIRouter(prefix="/api", tags=["chat"])

# 创建诊断服务实例
diagnosis_service = DiagnosisService(verbose=False)


@router.get("/", summary="根路径")
async def root():
    """根路径，返回服务信息"""
    return {"message": "故障诊断AI服务", "version": "v1.0"}


@router.get("/health", response_model=HealthResponse, summary="健康检查")
async def health():
    """健康检查接口"""
    return HealthResponse(status="healthy", service="故障诊断AI")


@router.post("/chat", response_model=ChatResponse, summary="同步聊天")
async def chat(request: ChatRequest):
    """
    同步聊天接口

    - **message**: 用户输入的问题
    - **user_id**: 用户ID（可选）
    """
    try:
        result = await diagnosis_service.diagnose(request.message)
        return ChatResponse(response=result, status="success")
    except Exception as e:
        return ChatResponse(response=f"诊断出错: {str(e)}", status="error")


@router.post("/chat/stream", summary="流式聊天")
async def chat_stream(request: ChatRequest):
    """
    流式聊天接口，返回Server-Sent Events

    - **message**: 用户输入的问题
    - **user_id**: 用户ID（可选）
    """
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