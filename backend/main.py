from fastapi import FastAPI, APIRouter
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from scalar_fastapi import get_scalar_api_reference
from config import config
import json
import uvicorn
import logging
import zotero
import llm
import database

logger = logging.getLogger("backend")
app = FastAPI(title="Zotero Assistant API")
router = APIRouter(prefix="/api")


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        title=app.title,
        openapi_url=app.openapi_url,
    )


@router.get("/collections")
def get_collections():
    """获取所有文献集"""
    return zotero.get_collections()


@router.get("/collection")
def get_collection(collection_key):
    """获取指定文献集中的所有文献"""
    return zotero.get_items_in_collection(collection_key)


@router.post("/embedding_text")
def embedding_text(text: str):
    """获取文本的嵌入表示"""
    return llm.get_text_embedding(text)


@router.post("/index_collections")
def index_collections(collections: list[str]):
    """索引指定文献集中的所有文献"""
    # return database.index_collections(collections)
    return StreamingResponse(database.index_collections(collections), media_type="text/event-stream")


@router.post("/semantic_search")
def semantic_search(query: list[str], collections: list[str], n_results: int = 10):
    """语义搜索"""
    return database.semantic_search(query, collections, n_results)


@router.post("/fulltext_search")
def fulltext_search(query: list[str], collections: list[str], ignore_case: bool = True):
    """全文搜索"""
    return database.fulltext_search(query, collections, ignore_case)


@router.post("/get_full_prompt")
def get_full_prompt(query: str, collections: list[str]):
    """根据用户查询生成完整提示词"""
    enhanced_query = llm.enhance_query(query)
    knowledge = database.semantic_search(enhanced_query, collections, n_results=10)
    return {"prompt": llm.get_full_prompt(query, json.dumps(knowledge, ensure_ascii=False))}


@router.get("/get_document")
def get_document(key: str):
    """根据key获取文档内容"""
    return database.get_document_by_key(key)


@router.get("/item/{key}")
def get_item_info(key: str):
    """根据key获取文献的详细信息"""
    return zotero.get_item_info(key)


@router.get("/open/{key}")
def open_pdf(key: str):
    """使用用户默认的PDF阅读器打开PDF文件"""
    zotero.open_pdf(key)
    return {"message": f"Opened PDF {key}"}


@router.get("/export/{key}")
def export_document(key: str):
    """导出PDF文件"""
    path = zotero.export_pdf(key)
    return {"message": f"Exported PDF {key} to {path}"}


@router.get("/open_export_path")
def open_export_path():
    """打开导出文件夹"""
    zotero.open_export_path()
    return {"message": "Opened export path"}


@router.post("/completion")
def chat_completion(messages: list[dict], temperature: float = 0.8, top_p: float = 0.9) -> StreamingResponse:
    """获取聊天补全"""
    return StreamingResponse(
        llm.streaming_chat_completion(messages, temperature, top_p), media_type="text/event-stream"
    )


@app.get("/", include_in_schema=False)
def serve_index():
    """主页"""
    return FileResponse(config["static_path"] + "/index.html")


# include the API router
app.include_router(router)
# Mount static files for serving Vue app
app.mount("/", StaticFiles(directory=config["static_path"]), name="static")


@app.exception_handler(404)
def catch_all(request, exc):
    """Catch-all route to serve Vue Router paths."""
    return FileResponse(config["static_path"] + "/index.html")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARN, format="%(asctime)s [%(levelname)s] %(message)s")
    logger.setLevel(logging.INFO)
    uvicorn.run(app, host="127.0.0.1", port=8000)
