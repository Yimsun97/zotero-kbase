import os
import shutil
import pandas as pd
from typing import List, Optional
from pypdf import PdfReader
from config import (
    MINERU_CONFIG_DIR,
    MAGIC_PDF_CONFIG_FILENAME,
    IMAGES_DIR_NAME, 
    METADATA_CSV_FILENAME, 
    DEFAULT_BATCH_OUTPUT_DIR,
    DEFAULT_MAX_PAGES,
    DEFAULT_ENCODING,
)

# Script-specific configuration
# Temporary directory prefix
TEMP_DIR_PREFIX = "temp_"
# Image file extensions (as tuple for endswith() checks)
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp')

def get_mineru_config_path():
    """Get the full path to the MinerU magic-pdf.json configuration file."""
    return os.path.join(MINERU_CONFIG_DIR, MAGIC_PDF_CONFIG_FILENAME)

def create_images_dir(base_dir):
    """Create images directory within a base directory."""
    images_path = os.path.join(base_dir, IMAGES_DIR_NAME)
    os.makedirs(images_path, exist_ok=True)
    return images_path

def create_temp_dir(base_dir, index):
    """Create a temporary directory with index."""
    temp_path = os.path.join(base_dir, f"{TEMP_DIR_PREFIX}{index}")
    os.makedirs(temp_path, exist_ok=True)
    return temp_path

os.environ['MINERU_TOOLS_CONFIG_JSON'] = get_mineru_config_path()

from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod


def convert_single_pdf_to_md(pdf_path: str, output_dir: str, output_name: str = None) -> str:
    """
    Convert a single PDF file to markdown format.
    
    Args:
        pdf_path (str): Full path to the PDF file
        output_dir (str): Directory where the markdown file and images will be saved
        output_name (str, optional): Name for the output markdown file (without extension).
                                   If None, uses the PDF filename without extension.
    
    Returns:
        str: Path to the generated markdown file
    """
    # Get output filename
    if output_name is None:
        output_name = os.path.splitext(os.path.basename(pdf_path))[0]
      # Prepare directories
    local_image_dir = os.path.join(output_dir, IMAGES_DIR_NAME)
    image_dir = IMAGES_DIR_NAME  # relative path for markdown references
    
    os.makedirs(local_image_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize writers
    image_writer = FileBasedDataWriter(local_image_dir)
    md_writer = FileBasedDataWriter(output_dir)
    
    # Read PDF bytes
    reader = FileBasedDataReader("")
    pdf_bytes = reader.read(pdf_path)
    
    # Create dataset instance
    ds = PymuDocDataset(pdf_bytes)
    
    # Perform inference based on PDF type
    if ds.classify() == SupportedPdfParseMethod.OCR:
        infer_result = ds.apply(doc_analyze, ocr=True)
        pipe_result = infer_result.pipe_ocr_mode(image_writer)
    else:
        infer_result = ds.apply(doc_analyze, ocr=False)
        pipe_result = infer_result.pipe_txt_mode(image_writer)
      # Get markdown content and save
    md_content = pipe_result.get_markdown(image_dir)
    md_filename = f"{output_name}.md"
    pipe_result.dump_md(md_writer, md_filename, image_dir)
    
    return os.path.join(output_dir, md_filename)


def convert_multiple_pdfs_to_md(fullpath_list: List[str], id_list: List[int], out_dir: str, pages_max: Optional[int] = None, force_rebuild: bool = False) -> List[str]:
    """
    Convert multiple PDF files to markdown format with ID-based naming.
    
    Args:
        fullpath_list (List[str]): List of full paths to PDF files
        id_list (List[int]): List of IDs corresponding to each PDF file
        out_dir (str): Directory where all markdown files and images will be saved
        pages_max (int, optional): Maximum number of pages for PDFs to be converted.
                                 If None, all PDFs will be converted regardless of page count.
        force_rebuild (bool): If True, delete existing output directory and rebuild from scratch.
                            If False, skip files that are already converted.
    
    Returns:
        List[str]: List of paths to the generated markdown files
    """
    if len(id_list) != len(fullpath_list):
        raise ValueError("Number of IDs must match number of PDF paths")
    
    # Handle force_rebuild: delete and recreate output directory
    if force_rebuild and os.path.exists(out_dir):
        print(f"Force rebuild enabled. Deleting existing directory: {out_dir}")
        shutil.rmtree(out_dir)
      # Prepare main output directory and images subdirectory
    images_dir = os.path.join(out_dir, IMAGES_DIR_NAME)
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    
    generated_files = []
    skipped_files = []
    already_converted_files = []
    
    def get_pdf_page_count(pdf_path: str) -> int:
        """Get the number of pages in a PDF file."""
        try:
            reader = PdfReader(pdf_path)
            return len(reader.pages)
        except Exception as e:
            print(f"Warning: Could not read page count for {pdf_path}: {str(e)}")
            return 0
    
    for i, (pdf_path, pdf_id) in enumerate(zip(fullpath_list, id_list)):
        # Generate names based on ID and filename
        filename_without_ext = os.path.splitext(os.path.basename(pdf_path))[0]
        output_name = f"{pdf_id}_{filename_without_ext}"
        image_prefix = str(pdf_id)
          
        # Check if file already exists and skip if force_rebuild is False
        final_md_path = os.path.join(out_dir, f"{output_name}.md")
        if not force_rebuild and os.path.exists(final_md_path):
            print(f"[{i+1}/{len(fullpath_list)}] Already converted: {output_name}.md (skipping)")
            already_converted_files.append(final_md_path)
            generated_files.append(final_md_path)
            continue
        
        # Check page count if pages_max is specified
        if pages_max is not None:
            page_count = get_pdf_page_count(pdf_path)
            if page_count > pages_max:
                print(f"[{i+1}/{len(fullpath_list)}] Skipping {pdf_path} ({page_count} pages > {pages_max} pages limit)")
                skipped_files.append(pdf_path)
                continue
            elif page_count == 0:
                print(f"[{i+1}/{len(fullpath_list)}] Skipping {pdf_path} (could not determine page count)")
                skipped_files.append(pdf_path)
                continue
            else:
                print("=" * 80)
                print(f"[{i+1}/{len(fullpath_list)}] Converting {pdf_path} ({page_count} pages) to {output_name}.md...")
        else:
            print("=" * 80)
            print(f"[{i+1}/{len(fullpath_list)}] Converting {pdf_path} to {output_name}.md...")
        
        # Create a temporary directory for this PDF's processing
        temp_dir = os.path.join(out_dir, f"{TEMP_DIR_PREFIX}{i}")
        
        try:
            # Convert the PDF
            md_file = convert_single_pdf_to_md(pdf_path, temp_dir, output_name)
              # Move the markdown file to the main output directory
            final_md_path = os.path.join(out_dir, f"{output_name}.md")
            shutil.move(md_file, final_md_path)
            
            # Move and rename images with prefix
            temp_images_dir = os.path.join(temp_dir, IMAGES_DIR_NAME)
            if os.path.exists(temp_images_dir):
                for image_file in os.listdir(temp_images_dir):
                    if image_file.lower().endswith(IMAGE_EXTENSIONS):
                        # Add prefix to image name (using only ID as prefix)
                        new_image_name = f"{image_prefix}_{image_file}"
                        src_path = os.path.join(temp_images_dir, image_file)
                        dst_path = os.path.join(images_dir, new_image_name)
                        shutil.move(src_path, dst_path)
                        
                        # Update image references in the markdown file
                        with open(final_md_path, 'r', encoding=DEFAULT_ENCODING) as f:
                            content = f.read()
                        content = content.replace(f"{IMAGES_DIR_NAME}/{image_file}", f"{IMAGES_DIR_NAME}/{new_image_name}")
                        with open(final_md_path, 'w', encoding=DEFAULT_ENCODING) as f:
                            f.write(content)
            
            generated_files.append(final_md_path)
            print(f"Successfully converted to {final_md_path}")
            
        except Exception as e:
            print(f"Error converting {pdf_path}: {str(e)}")
            
        finally:
            # Clean up temporary directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
      # Print summary
    print(f"\nConversion complete:")
    print(f"  Successfully converted: {len(generated_files) - len(already_converted_files)} files")
    if already_converted_files:
        print(f"  Already converted (skipped): {len(already_converted_files)} files")
    if pages_max is not None and skipped_files:
        print(f"  Skipped (too many pages): {len(skipped_files)} files")
    print(f"  Total output files: {len(generated_files)} files")
    
    return generated_files


if __name__ == "__main__":
    # # Demo of single PDF conversion
    # pdf_file_name = "D:\\AppData\\ZoteroData\\Cheng_Basu_2017_Biogeochemical hotspots.pdf"
    # output_directory = "output"
    # result = convert_single_pdf_to_md(pdf_file_name, output_directory)
    # print(f"Generated: {result}")

    # Multiple PDFs conversion
    metadata = pd.read_csv(METADATA_CSV_FILENAME, header=0)
    metadata_pdf = metadata.loc[metadata['contentType'] == "application/pdf"].copy()    
    fullpath_list = metadata_pdf["attachment_fullpath"].tolist()
    id_list = metadata_pdf["attachment_id"].tolist()

    results = convert_multiple_pdfs_to_md(fullpath_list, id_list, DEFAULT_BATCH_OUTPUT_DIR, pages_max=DEFAULT_MAX_PAGES, force_rebuild=False)
    print("All of the pdfs are converted to md files! Enjoy chatting with your documents!")
