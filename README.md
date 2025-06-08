# Zotero Knowledge Base

A comprehensive Python toolkit for extracting, converting, and managing your Zotero research library. This system allows you to transform your Zotero database into a searchable knowledge base with full-text PDF conversion and annotation management.

## 🚀 Features

- **📊 Metadata Extraction**: Extract complete paper metadata, authors, collections, and attachment information from Zotero database
- **📝 Annotation Management**: Export all your Zotero annotations (highlights, notes, comments) to organized markdown files
- **📄 PDF to Markdown Conversion**: Convert PDF attachments to markdown format with image extraction using MinerU
- **🔍 Batch Processing**: Process multiple files efficiently with progress tracking and error handling
- **📁 Organized Output**: Structured output with images, metadata, and annotations in separate directories
- **🛠️ Configurable**: Easy configuration management for different Zotero installations

## 📋 Requirements

### Python Dependencies
```bash
pip install pandas pypdf pathlib
```

### External Tools
- **MinerU**: Required for PDF to markdown conversion
  - Install from: [MinerU GitHub](https://github.com/opendatalab/MinerU)
  - Configure `magic-pdf.json` configuration file

### System Requirements
- Python 3.7+
- Zotero database access (zotero.sqlite)
- Windows/Linux/macOS compatible

## ⚙️ Configuration

### 1. Update Configuration File

Edit `config.py` to match your system:

```python
# Zotero data directory
ZOTERO_DATA_DIR = <path_to_zotero_data_dir>

# Zotero database file
ZOTERO_DB_PATH = <path_to_zotero_db> (usually <path_to_zotero_data_dir>/zotero.sqlite)

# MinerU configuration directory
MINERU_CONFIG_DIR = <path_to_mineru_config_dir>
```

### 2. Test Configuration

```bash
python test_config.py
```

This will validate all paths and show configuration status.

## 🎯 Usage

### 1. Extract Metadata from Zotero

Extract all paper-attachment relationships with authors and collections:

```bash
python extract_zotero_metadata.py
```

**Output**: `zotero_metadata.csv` - Complete dataset with papers, authors, collections, and attachments

### 2. Extract Annotations

Export all your Zotero annotations to CSV format:

```bash
python extract_zotero_annotations.py
```

**Output**: `zotero_annotations.csv` - All annotations linked to papers and attachments

### 3. Convert Annotations to Markdown

#### Convert Single Attachment
```python
from convert_annotations import convert_single_annotation_by_id

# Convert annotations for attachment ID 94
result = convert_single_annotation_by_id(94, "output_directory")
```

#### Convert All Annotations
```python
from convert_annotations import convert_all_annotations

# Convert all attachments with annotations
results = convert_all_annotations("annotations_output")
```

### 4. Convert PDFs to Markdown

#### Single PDF Conversion
```python
from convert_pdf_files import convert_single_pdf_to_md

result = convert_single_pdf_to_md(
    pdf_path="path/to/paper.pdf",
    output_dir="output",
    output_name="paper_name"
)
```

#### Batch PDF Conversion
```python
from convert_pdf_files import convert_multiple_pdfs_to_md
import pandas as pd

# Load metadata
metadata = pd.read_csv("zotero_metadata.csv")
pdf_metadata = metadata[metadata['contentType'] == "application/pdf"]

results = convert_multiple_pdfs_to_md(
    fullpath_list=pdf_metadata["attachment_fullpath"].tolist(),
    id_list=pdf_metadata["attachment_id"].tolist(),
    out_dir="fulltexts",
    pages_max=100,  # Skip PDFs with more than 100 pages
    force_rebuild=False  # Skip already converted files
)
```

## 📊 Example Workflows

### Complete Knowledge Base Setup (Automated)

The easiest way to set up your complete knowledge base is to use the provided batch scripts:

**Windows:**
```bash
run_converter.bat
```

**Linux/macOS:**
```bash
chmod +x run_converter.sh
./run_converter.sh
```

These scripts will automatically:
1. Extract annotations from Zotero database
2. Convert all annotations to markdown files
3. Extract paper metadata from Zotero database  
4. Convert PDF files to markdown format

### Manual Step-by-Step Setup

If you prefer to run each step manually or need more control:

```bash
# 1. Extract all metadata
python extract_zotero_metadata.py

# 2. Extract all annotations  
python extract_zotero_annotations.py

# 3. Convert all annotations to markdown
python convert_annotations.py

# 4. Convert PDFs to markdown (with limits)
python convert_pdf_to_md.py
```

### Research Paper Analysis

```python
# Find papers with most annotations
import pandas as pd

annotations = pd.read_csv("zotero_annotations.csv")
top_papers = annotations.groupby(['paper_id', 'paper_title']).size().sort_values(ascending=False)
print(top_papers.head(10))
```

### Selective Processing

```python
# Convert only specific attachments
from convert_annotations import convert_single_annotation_by_id

# Convert annotations for specific attachment IDs
convert_single_annotation_by_id(94, "output_directory")
convert_single_annotation_by_id(95, "output_directory")
```

```python
# Convert only PDFs within page limits
from convert_pdf_to_md import convert_multiple_pdfs_to_md
import pandas as pd

metadata = pd.read_csv("zotero_metadata.csv")
# Filter for PDFs only
pdf_metadata = metadata[metadata['contentType'] == "application/pdf"]

# Convert with custom settings
results = convert_multiple_pdfs_to_md(
    fullpath_list=pdf_metadata["attachment_fullpath"].tolist(),
    id_list=pdf_metadata["attachment_id"].tolist(),
    out_dir="fulltexts",
    pages_max=50,  # Only convert PDFs with 50 pages or less
    force_rebuild=True  # Rebuild existing files
)
```

## 🚀 Quick Start

1. **Configure your paths** in `config.py`
2. **Test your configuration**: `python test_config.py`
3. **Run the complete conversion**: `run_converter.bat` (Windows) or `./run_converter.sh` (Linux/macOS)
4. **Check your output** in the generated directories

## 📁 Output Structure

```
your-project/
├── zotero_metadata.csv          # Paper and attachment metadata
├── zotero_annotations.csv       # All annotations
├── annotations/                 # Annotation markdown files
│   ├── 94.md                   # Annotations for attachment ID 94
│   ├── 95.md                   # Annotations for attachment ID 95
│   └── ...
├── fulltexts/                  # PDF converted to markdown
│   ├── images/                 # Extracted images from PDFs
│   │   ├── 94_image1.png
│   │   ├── 94_image2.png
│   │   └── ...
│   ├── 94_paper_title.md       # Converted PDF content
│   ├── 95_another_paper.md
│   └── ...
```

## 📄 File Formats

### Metadata CSV Columns
- `paper_id`, `paper_title`, `authors`, `collection_names`
- `attachment_id`, `attachment_path`, `attachment_fullpath`
- `contentType`, `link_mode`, date information

### Annotations CSV Columns
- `annotation_id`, `attachment_id`, `paper_id`
- `annotation_text`, `annotation_comment`, `annotation_color`
- `annotation_type_name`, `page_label`, `paper_title`

### Markdown Output
- **Annotations**: Organized by paper with page-by-page breakdown
- **PDF Content**: Full markdown conversion with linked images
- **Images**: Automatically extracted and properly referenced

## 🔧 Advanced Configuration

### PDF Conversion Settings

```python
# In config.py
DEFAULT_MAX_PAGES = 100           # Skip PDFs larger than this
DEFAULT_ENCODING = "utf-8"        # Text encoding for output files
IMAGES_DIR_NAME = "images"        # Image subdirectory name
```

### MinerU Configuration

Ensure your `magic-pdf.json` is properly configured for PDF processing. The system automatically sets the environment variable:

```python
os.environ['MINERU_TOOLS_CONFIG_JSON'] = get_mineru_config_path()
```

## 🚨 Troubleshooting

### Common Issues

1. **Database not found**
   - Verify Zotero is closed
   - Check `ZOTERO_DB_PATH` in config.py
   - Ensure you have read access to the database

2. **MinerU errors**
   - Verify MinerU installation
   - Check `magic-pdf.json` configuration
   - Ensure all MinerU dependencies are installed

3. **PDF conversion fails**
   - Check if PDF is corrupted
   - Verify file permissions
   - Consider reducing `pages_max` limit

4. **Memory issues with large PDFs**
   - Process files in smaller batches
   - Increase system memory
   - Use `pages_max` to skip large files

### Debug Mode

Enable detailed logging by modifying the scripts:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with your Zotero database
5. Submit a pull request

## 📝 License

This project is open source. Please check individual dependencies for their licenses.

## 🙏 Acknowledgments

- **MinerU Team**: For the excellent PDF processing capabilities
- **Zotero Project**: For the amazing reference management system
- **Python Community**: For the powerful libraries used in this project

---

**Note**: Always backup your Zotero database before running these scripts. The scripts only read from the database, but it's good practice to have backups.
