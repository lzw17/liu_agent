"""API routes for LiuAgent."""
import os
import tempfile
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from ..core import logger, get_config
from ..models.schemas import (
    ChatRequest, ChatResponse, SearchRequest, SearchResponse,
    DocumentUploadResponse, KnowledgeBaseResponse, HealthResponse, ConfigResponse
)
from ..services import (
    get_chat_service, get_knowledge_base_service, get_search_service, get_llm_service
)

router = APIRouter()

# Health check endpoint
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    config = get_config()
    
    # Check service status
    services = {}
    try:
        llm_service = get_llm_service()
        services["llm"] = "ok"
    except Exception as e:
        services["llm"] = f"error: {str(e)}"
    
    try:
        kb_service = get_knowledge_base_service()
        services["knowledge_base"] = "ok"
    except Exception as e:
        services["knowledge_base"] = f"error: {str(e)}"
    
    try:
        search_service = get_search_service()
        services["search"] = "ok"
    except Exception as e:
        services["search"] = f"error: {str(e)}"
    
    return HealthResponse(
        status="healthy" if all("ok" in status for status in services.values()) else "degraded",
        version="1.0.0",
        services=services
    )

# Configuration endpoint
@router.get("/config", response_model=ConfigResponse)
async def get_config_info():
    """Get configuration information."""
    config = get_config()
    llm_service = get_llm_service()
    search_service = get_search_service()
    
    return ConfigResponse(
        llm_providers=llm_service.get_available_providers(),
        search_engines=search_service.get_available_engines(),
        max_file_size=config.upload.max_file_size,
        allowed_extensions=config.upload.allowed_extensions
    )

# Chat endpoints
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the AI agent."""
    try:
        chat_service = get_chat_service()
        response = await chat_service.chat(request)
        return response
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat/stream")
async def stream_chat(request: ChatRequest):
    """Stream chat with the AI agent."""
    try:
        chat_service = get_chat_service()
        
        async def generate():
            # 先发送一个初始 ping，确保SSE通道建立
            import json as _json
            yield f"data: {_json.dumps({'type': 'ping'})}\n\n"
            async for chunk_data in chat_service.stream_chat(request):
                if "error" in chunk_data:
                    import json
                    yield f"data: {json.dumps({'error': chunk_data['error']}, ensure_ascii=False)}\n\n"
                    break
                else:
                    import json
                    yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            generate(), 
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    except Exception as e:
        logger.error(f"Stream chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Search endpoints
@router.post("/search", response_model=SearchResponse)
async def web_search(request: SearchRequest):
    """Perform web search."""
    try:
        search_service = get_search_service()
        results = await search_service.search(
            request.query,
            max_results=request.max_results or 10,
            engine=request.engine
        )
        
        return SearchResponse(
            results=results,
            query=request.query,
            total_results=len(results)
        )
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Knowledge base endpoints
@router.post("/upload-pdf", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and process a document."""
    try:
        config = get_config()
        
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in config.upload.allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_ext} not allowed. Allowed types: {config.upload.allowed_extensions}"
            )
        
        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > config.upload.max_file_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {config.upload.max_file_size} bytes"
            )
        
        # Create upload directory
        upload_dir = Path(config.upload.upload_path)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process document
            kb_service = get_knowledge_base_service()
            result = await kb_service.upload_document(temp_file_path, file.filename)
            
            # Clean up temp file in background
            background_tasks.add_task(os.unlink, temp_file_path)
            
            return result
            
        except Exception as e:
            # Clean up temp file on error
            os.unlink(temp_file_path)
            raise
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge-base", response_model=KnowledgeBaseResponse)
async def get_knowledge_base():
    """Get knowledge base documents."""
    try:
        kb_service = get_knowledge_base_service()
        documents = await kb_service.get_documents()
        
        return KnowledgeBaseResponse(
            documents=documents,
            total_documents=len(documents)
        )
    except Exception as e:
        logger.error(f"Knowledge base endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/knowledge-base/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from knowledge base."""
    try:
        kb_service = get_knowledge_base_service()
        success = await kb_service.delete_document(document_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete document endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Search knowledge base
@router.post("/knowledge-base/search")
async def search_knowledge_base(request: SearchRequest):
    """Search in knowledge base."""
    try:
        kb_service = get_knowledge_base_service()
        results = await kb_service.search_documents(
            request.query,
            max_results=request.max_results or 5
        )
        
        return {
            "results": results,
            "query": request.query,
            "total_results": len(results)
        }
    except Exception as e:
        logger.error(f"Knowledge base search endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
