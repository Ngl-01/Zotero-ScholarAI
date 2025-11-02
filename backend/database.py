import chromadb
import zotero
import logging
import llm
import os
from tqdm import tqdm
import re

logger = logging.getLogger("backend")
client = chromadb.PersistentClient(path="./data/chroma")
collection = client.get_or_create_collection(name="zotero")


def tqdm_info(msg):
    if logger.isEnabledFor(logging.INFO):
        tqdm.write(msg)


def index_collections(collection_keys: list[str]):
    """
    索引指定文献集中的所有文献

    Args:
        collection_keys (list[str]): 文献集的唯一标识符列表
    """
    item_keys = {}
    for key in collection_keys:
        items = zotero.get_pdf_path_in_collection(key)
        item_keys.update({e["key"]: e for e in items})
    logger.info(f"Indexing collections {collection_keys} with {len(item_keys)} items")
    item_keys = list(item_keys.values())
    for i, e in tqdm(enumerate(item_keys)):
        yield f"正在索引 {i + 1}/{len(item_keys)}"
        pdf_key = e["key"]
        pdf_path = e["path"]
        mod = int(os.path.getmtime(pdf_path))
        res = collection.get(where={"key": pdf_key}, include=["metadatas"])
        ids = res["ids"]
        if ids:
            if res["metadatas"][0]["mod"] >= mod:
                continue
            else:
                collection.delete(ids=ids)
        text = zotero.get_pdf_text(pdf_path)
        chunks = llm.split_text(text)
        count = len(chunks)
        embeddings = [e["embedding"] for e in llm.get_text_embedding(chunks)]
        collection.add(
            documents=chunks,
            metadatas=[{"key": pdf_key, "mod": mod}] * count,
            
            ids=[f"{pdf_key}_{i}" for i in range(count)],
            embeddings=embeddings,
        )
    logger.info("索引完成")
    return "已完成！"


def get_document_by_key(key: str):
    """
    根据key获取文档内容和信息

    Args:
        key (str): chromadb中存储的id，格式为"{item_key}_{chunk_index}"
    Returns:
        dict: 包含文档内容和信息的字典
    """
    res = collection.get(ids=[key])
    print(res)
    item_key = key.split("_")[0]
    item = zotero.get_item_info(item_key)
    title = item["title"]
    publication = item["publication"]
    pdf_key = item["pdf_key"]
    return {
        "key": item_key,
        "pdf_key": pdf_key,
        "title": title,
        "publication": publication,
        "text": res["documents"][0],
    }


def semantic_search(queries: list[str], collections: list[str], n_results: int = 10):
    """
    语义搜索，合并所有查询结果并按距离升序排列

    Args:
        queries (list[str]): 查询文本列表
        n_results (int): 返回的结果数量

    Returns:
        list: 搜索结果
    """
    logger.info(f"获取查询的嵌入表示: {queries}")
    query_embeddings = [e["embedding"] for e in llm.get_text_embedding(queries)]
    logger.info("获取指定文献集中的所有文献")
    keys = []
    for c in collections:
        res = zotero.get_items_in_collection(c)
        keys.extend([e["key"] for e in res])
    logger.info("在数据库中查询嵌入表示")
    results = collection.query(
        query_embeddings=query_embeddings,
        where={"key": {"$in": keys}},
        n_results=n_results,
    )
    logger.info("处理查询结果")
    resmap = {}
    for i in range(len(queries)):
        ids = results["ids"][i]
        documents = results["documents"][i]
        metadatas = results["metadatas"][i]
        distances = results["distances"][i]
        for j in range(len(ids)):
            # 如果id已经存在，取距离更小的那个
            item = {
                "document": documents[j],
                "id": ids[j],
                "key": metadatas[j]["key"],
                "distance": distances[j],
            }
            if ids[j] in resmap:
                if distances[j] < resmap[ids[j]]["distance"]:
                    resmap[ids[j]] = item
            else:
                resmap[ids[j]] = item
    merged = list(resmap.values())
    logger.info(f"合并后的结果数量: {len(merged)}")
    merged.sort(key=lambda x: x["distance"])
    merged = merged[: n_results * 2]
    return merged


def get_fulltext(key: str):
    """
    根据key获取文档全文

    Args:
        key (str): 文档的唯一标识符

    Returns:
        str: 文档全文
    """
    res = collection.get(where={"key": key})
    texts = res["documents"]
    # 去掉texts[i]结尾与texts[i+1]开头重复的部分，要计算重复长度
    full_text = texts[0]
    for i in range(1, len(texts)):
        overlap_len = 0
        for j in range(1, min(len(full_text), len(texts[i]))):
            if full_text[-j:] == texts[i][:j]:
                overlap_len = j
        full_text += texts[i][overlap_len:]
    return full_text


def html_escape(text: str) -> str:
    """替换HTML特殊字符"""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _fulltext_search(
    text: str, query: str, ignore_case: bool = False, preview_length: int = 100, preview_limit: int = 20
):
    preview = []
    for match in re.finditer(query, text, re.IGNORECASE if ignore_case else 0):
        b = match.start()
        c = match.end()
        a = max(0, b - preview_length)
        d = min(len(text), c + preview_length)
        if len(preview) < preview_limit:
            preview.append(text[a:b] + f"<mark>{html_escape(match.group())}</mark>" + text[c:d])
        else:
            break
    return preview


def fulltext_search(queries: list[str], collections: list[str], ignore_case: bool = False):
    """
    全文搜索

    Args:
        query (str): 查询文本
        n_results (int): 返回的结果数量

    Returns:
        list: 搜索结果
    """
    logger.info(f"在{collections}中进行全文搜索{queries}")
    query = queries[0]
    logger.info("获取文档列表")
    keys = []
    for c in collections:
        res = zotero.get_items_in_collection(c)
        keys.extend([e["key"] for e in res]) # 取出附件文档的key
    logger.info(f"文档总数: {len(keys)}，开始在数据库中过滤")
    res = collection.get(
        where_document={"$regex": "(?i)" + query if ignore_case else query},
        where={"key": {"$in": keys}},
    )

    keys = set()
    for i in range(len(res["ids"])):
        key = res["metadatas"][i]["key"]
        keys.add(key)
    keys = list(keys)

    logger.info(f"在数据库中查询到{len(keys)}个符合条件的文档，开始进行全文搜索")
    res = []
    for key in tqdm(keys):
        full_text = get_fulltext(key)
        preview = []
        for query in queries:
            r = _fulltext_search(full_text, query, ignore_case)
            if r:
                preview.extend(r)
            else:  # 只要有一个query没有匹配，就跳过这个文档
                preview = []
                break
        if preview:
            info = zotero.get_item_info(key) # 获取文献的详细信息
            res.append(
                {
                    "title": info["title"],
                    "publication": info["publication"],
                    "key": key,
                    "pdf_key": info["pdf_key"],
                    "preview": preview,
                }
            )
    return res


if __name__ == "__main__":
    pass
