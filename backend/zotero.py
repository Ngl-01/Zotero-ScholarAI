import os
import logging
import httpx
import pymupdf
import shutil
from config import config

logger = logging.getLogger("backend")
client = httpx.Client(base_url="http://127.0.0.1:23119/api/users/0/")


def get_collections():
    """
    获取所有文献集
    """
    res = client.get("collections")
    return [{"key": e["key"], "name": e["data"]["name"], "numItems": e["meta"]["numItems"]} for e in res.json()]


def get_items_in_collection(collection_key: str):
    """
    获取指定文献集中的所有文献

    Args:
        collection_key (str): 文献集的唯一标识符

    Returns:
        list: 文献集中的所有文献
    """
    res = client.get(f"collections/{collection_key}/items")
    return [{"key": e["key"], "title": e["data"].get("title", "Untitled")} for e in res.json()]


def find_pdf_file_in_path(path: str) -> str:
    """
    在指定路径中查找PDF文件

    理论上应该用Zotero api，但是这个方法更高效

    Args:
        path (str): 要查找的路径

    Returns:
        str: 找到的PDF文件的路径，如果未找到则返回None
    """
    for e in os.listdir(path):
        if os.path.splitext(e)[1] == ".pdf":
            return f"{path}/{e}"
    return None


def get_pdf_path_in_collection(collection_key: str):
    """
    获取文献集中文献的PDF文件路径

    Args:
        collection_key (str): 文献集的唯一标识符

    Returns:
        list: 文献集中文献的PDF文件路径
    """
    zotero_path = config["zotero_path"]
    res = client.get(f"collections/{collection_key}/items")
    ret = []
    for e in res.json():
        if "attachment" not in e["links"]:
            continue
        pdf_key = e["links"]["attachment"]["href"][-8:]
        pdf_path = find_pdf_file_in_path(f"{zotero_path}/storage/{pdf_key}")
        title = e["data"]["title"]
        if not pdf_path:
            logger.warning(f"PDF file of {title} not found. Skipping.")
            continue
        ret.append(
            {
                "key": e["key"],
                "title": title,
                "path": pdf_path,
                "publication": e["data"].get("publicationTitle", ""),
            }
        )
    return ret


def get_item_info(item_key: str):
    """
    获取文献的详细信息

    Args:
        item_key (str): 文献的唯一标识符

    Returns:
        dict: 文献的详细信息
    """
    res = client.get(f"items/{item_key}")
    if res.status_code != 200:
        return None
    data = res.json()
    pdf_key = None
    if "attachment" in data["links"]:
        pdf_key = data["links"]["attachment"]["href"][-8:]
    info = {
        "title": data["data"].get("title", ""),
        "pdf_key": pdf_key,
        "publication": data["data"].get("publicationTitle", ""),
    }
    return info


def open_pdf(pdf_key: str):
    """
    使用用户默认的PDF阅读器打开PDF文件

    Args:
        pdf_key (str): PDF文件的唯一标识符
    """
    zotero_path = config["zotero_path"]
    pdf_path = find_pdf_file_in_path(f"{zotero_path}/storage/{pdf_key}")
    if not pdf_path:
        logger.warning(f"PDF file of {pdf_key} not found. Skipping.")
        return
    os.startfile(pdf_path)


def export_pdf(pdf_key: str) -> str:
    """
    导出PDF文件到指定路径

    Args:
        pdf_key (str): PDF文件的唯一标识符

    Returns:
        str: 导出的PDF文件路径
    """
    zotero_path = config["zotero_path"]
    export_path = "data/export"
    if not os.path.exists(export_path):
        os.makedirs(export_path)
    pdf_path = find_pdf_file_in_path(f"{zotero_path}/storage/{pdf_key}")
    if not pdf_path:
        logger.warning(f"PDF file of {pdf_key} not found. Skipping.")
        return None
    shutil.copy(pdf_path, export_path)


def open_export_path():
    """打开导出PDF文件的文件夹"""
    export_path = "data/export"
    if not os.path.exists(export_path):
        os.makedirs(export_path)
    os.startfile(os.path.abspath(export_path))


def get_pdf_text(pdf_path: str):
    """
    获取PDF文件的文本内容

    Args:
        pdf_path (str): PDF文件的路径

    Returns:
        str: PDF文件的文本内容
    """
    text = ""
    anno = ""
    doc = pymupdf.open(pdf_path)
    for page in doc:
        textpage = page.get_textpage()
        text += textpage.extractText()
        for a in page.annots():
            content = a.info["content"]
            if content:
                anno += content + "\n"
    return text + "\n---\n用户笔记：" + anno
