import os
import tempfile
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SUPPORTED_EXTS = {".pdf", ".docx", ".txt", ".htm", ".html"}


def parse_bytes(filename: str, data: bytes) -> str:
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTS:
        raise ValueError(f"不支持的文件格式: {ext}，支持: {', '.join(sorted(SUPPORTED_EXTS))}")

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(data)
        tmp_path = tmp.name

    try:
        logger.info(f"解析: {filename} ({len(data)} bytes)")

        # 延迟导入，按需加载
        if ext == ".pdf":
            from unstructured.partition.pdf import partition_pdf
            elements = partition_pdf(filename=tmp_path, strategy="fast")
        elif ext == ".docx":
            from unstructured.partition.docx import partition_docx
            elements = partition_docx(filename=tmp_path)
        elif ext == ".txt":
            from unstructured.partition.text import partition_text
            elements = partition_text(filename=tmp_path)
        elif ext in (".htm", ".html"):
            from unstructured.partition.html import partition_html
            elements = partition_html(filename=tmp_path)
        else:
            from unstructured.partition.text import partition_text
            elements = partition_text(filename=tmp_path)

        text = "\n".join(str(el) for el in elements)
        return clean_text(text)

    except Exception as e:
        logger.error(f"解析失败: {filename} - {e}")
        raise RuntimeError(f"文档解析失败 ({filename}): {e}") from e
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def parse_filepath(filepath: str) -> str:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {filepath}")
    return parse_bytes(path.name, path.read_bytes())


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace("\u0000", "")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)


def is_supported(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED_EXTS