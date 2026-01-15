import zipfile
from xml.sax.saxutils import escape

CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>
"""

RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""

DOCUMENT_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>
"""

TABLE_PR_XML = (
    "<w:tblPr>"
    "<w:tblW w:w=\"0\" w:type=\"auto\"/>"
    "<w:tblBorders>"
    "<w:top w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
    "<w:left w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
    "<w:bottom w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
    "<w:right w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
    "<w:insideH w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
    "<w:insideV w:val=\"single\" w:sz=\"4\" w:space=\"0\" w:color=\"auto\"/>"
    "</w:tblBorders>"
    "</w:tblPr>"
)


def _sanitize_text(value):
    if value is None:
        return ""
    text = str(value)
    text = text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    return escape(text)


def _text_run(text, bold=False):
    if bold:
        return f"<w:r><w:rPr><w:b/></w:rPr><w:t>{text}</w:t></w:r>"
    return f"<w:r><w:t>{text}</w:t></w:r>"


def _table_cell(text, bold=False):
    safe_text = _sanitize_text(text)
    run = _text_run(safe_text, bold=bold)
    return (
        "<w:tc>"
        "<w:tcPr><w:tcW w:w=\"0\" w:type=\"auto\"/></w:tcPr>"
        f"<w:p>{run}</w:p>"
        "</w:tc>"
    )


def _table_row(row, col_count, bold=False):
    row_list = list(row)
    if len(row_list) < col_count:
        row_list.extend([""] * (col_count - len(row_list)))
    elif len(row_list) > col_count:
        row_list = row_list[:col_count]
    cells = "".join(_table_cell(cell, bold=bold) for cell in row_list)
    return f"<w:tr>{cells}</w:tr>"


def _build_document_xml(title, headers, rows):
    safe_title = _sanitize_text(title)
    col_count = len(headers)
    header_row = _table_row(headers, col_count, bold=True)
    data_rows = "".join(_table_row(row, col_count) for row in rows)
    title_run = _text_run(safe_title, bold=True)
    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
        "<w:body>"
        f"<w:p>{title_run}</w:p>"
        "<w:p><w:r><w:t></w:t></w:r></w:p>"
        f"<w:tbl>{TABLE_PR_XML}{header_row}{data_rows}</w:tbl>"
        "<w:sectPr>"
        "<w:pgSz w:w=\"11906\" w:h=\"16838\"/>"
        "<w:pgMar w:top=\"1440\" w:right=\"1440\" w:bottom=\"1440\" w:left=\"1440\" "
        "w:header=\"720\" w:footer=\"720\" w:gutter=\"0\"/>"
        "</w:sectPr>"
        "</w:body>"
        "</w:document>"
    )


def create_docx_table(filepath, title, headers, rows):
    document_xml = _build_document_xml(title, headers, rows)
    with zipfile.ZipFile(filepath, "w", compression=zipfile.ZIP_DEFLATED) as docx_file:
        docx_file.writestr("[Content_Types].xml", CONTENT_TYPES_XML)
        docx_file.writestr("_rels/.rels", RELS_XML)
        docx_file.writestr("word/document.xml", document_xml)
        docx_file.writestr("word/_rels/document.xml.rels", DOCUMENT_RELS_XML)
