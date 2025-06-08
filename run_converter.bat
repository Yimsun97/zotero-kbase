REM 1. convert annotations to markdown files
python extract_zotero_annotations.py
python convert_annotations.py

REM 2. convert pdf files to markdown files
python extract_zotero_metadata.py
python convert_pdf_files.py
