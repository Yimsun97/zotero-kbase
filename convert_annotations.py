"""
User-friendly script to convert Zotero annotations to markdown files.
This script can convert single attachments or all attachments at once.
"""

import pandas as pd
from pathlib import Path
from config import (
    ANNOTATIONS_CSV_FILENAME,
    DEFAULT_ANNOTATIONS_OUTPUT_DIR,
    DEFAULT_ENCODING
)


def annotations_to_markdown(attachment_id, output_path=DEFAULT_ANNOTATIONS_OUTPUT_DIR, csv_file=ANNOTATIONS_CSV_FILENAME):
    """
    Convert annotations for a specific attachment_id to a markdown file.
    
    Args:
        attachment_id (int): The attachment ID to filter annotations
        output_path (str): Directory path where the markdown file will be saved
        csv_file (str): Path to the CSV file containing annotations
    
    Returns:
        str: Path to the created markdown file
    """
    # Read the CSV file
    try:
        annot = pd.read_csv(csv_file, header=0)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file '{csv_file}' not found.")
    
    # Filter annotations for the specific attachment_id
    annot_sel = annot.query(f"attachment_id == {attachment_id}")
    
    if annot_sel.empty:
        print(f"No annotations found for attachment_id: {attachment_id}")
        return None
    
    # Get paper information (use the first row since all rows should have the same paper info)
    paper_info = annot_sel.iloc[0]
    paper_title = paper_info['paper_title']
    
    # Sort annotations by page_label (assuming it represents page numbers)
    annot_sel = annot_sel.sort_values('page_label', na_position='last')
    
    # Create markdown content
    markdown_content = []
    markdown_content.append(f"# {paper_title}\n\n")
    markdown_content.append(f"**Attachment ID:** {attachment_id}  \n")
    markdown_content.append(f"**Paper ID:** {paper_info['paper_id']}  \n")
    markdown_content.append(f"**File Path:** {paper_info['attachment_path']}  \n\n")
    markdown_content.append("---\n\n")
    
    # Group annotations by page
    current_page = None
    for _, row in annot_sel.iterrows():
        page = row['page_label']
        annotation_text = row['annotation_text']
        annotation_comment = row['annotation_comment']
        annotation_type = row['annotation_type_name']
        annotation_color = row['annotation_color']
        
        # Add page header if we're on a new page
        if page != current_page:
            if current_page is not None:  # Add spacing between pages
                markdown_content.append("\n")
            markdown_content.append(f"## Page {page}\n\n")
            current_page = page
        
        # Add annotation
        markdown_content.append(f"### {annotation_type.title()}")
        if annotation_color:
            markdown_content.append(f" `{annotation_color}`")
        markdown_content.append("\n\n")
        
        if annotation_text and pd.notna(annotation_text):
            markdown_content.append(f"**Text:** {annotation_text}\n\n")
        
        if annotation_comment and pd.notna(annotation_comment):
            markdown_content.append(f"**Comment:** {annotation_comment}\n\n")
        
        markdown_content.append("---\n\n")
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
      # Write to markdown file
    output_file = output_dir / f"{attachment_id}.md"
    
    with open(output_file, 'w', encoding=DEFAULT_ENCODING) as f:
        f.write(''.join(markdown_content))
    
    print(f"✅ Markdown file created: {output_file}")
    print(f"📊 Total annotations: {len(annot_sel)}")
    
    return str(output_file)


def process_all_attachments(output_path=DEFAULT_ANNOTATIONS_OUTPUT_DIR, csv_file=ANNOTATIONS_CSV_FILENAME):
    """
    Convert annotations for ALL attachment IDs to markdown files.
    
    Args:
        output_path (str): Directory path where the markdown files will be saved
        csv_file (str): Path to the CSV file containing annotations
    
    Returns:
        dict: Dictionary with attachment_id as key and result info as value
    """
    # Read the CSV file
    try:
        annot = pd.read_csv(csv_file, header=0)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file '{csv_file}' not found.")
    
    # Get all unique attachment IDs
    attachment_ids = annot['attachment_id'].unique()
    total_attachments = len(attachment_ids)
    
    print(f"🚀 Starting batch processing of {total_attachments} attachments...")
    print(f"📁 Output directory: {output_path}")
    print("=" * 80)
    
    # Create output directory if it doesn't exist
    output_dir = Path(output_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = {}
    successful = 0
    failed = 0
    
    for i, attachment_id in enumerate(sorted(attachment_ids), 1):
        try:
            print(f"Processing {i}/{total_attachments}: Attachment ID {attachment_id}...", end=" ")
            
            # Filter annotations for this attachment_id
            annot_sel = annot.query(f"attachment_id == {attachment_id}")
            
            if annot_sel.empty:
                print("❌ No annotations found")
                results[attachment_id] = {"status": "failed", "reason": "No annotations found"}
                failed += 1
                continue
            
            # Get paper information
            paper_info = annot_sel.iloc[0]
            paper_title = paper_info['paper_title']
            
            # Sort annotations by page_label
            annot_sel = annot_sel.sort_values('page_label', na_position='last')
            
            # Create markdown content (same logic as single function)
            markdown_content = []
            markdown_content.append(f"# {paper_title}\n\n")
            markdown_content.append(f"**Attachment ID:** {attachment_id}  \n")
            markdown_content.append(f"**Paper ID:** {paper_info['paper_id']}  \n")
            markdown_content.append(f"**File Path:** {paper_info['attachment_path']}  \n\n")
            markdown_content.append("---\n\n")
            
            # Group annotations by page
            current_page = None
            for _, row in annot_sel.iterrows():
                page = row['page_label']
                annotation_text = row['annotation_text']
                annotation_comment = row['annotation_comment']
                annotation_type = row['annotation_type_name']
                annotation_color = row['annotation_color']
                
                # Add page header if we're on a new page
                if page != current_page:
                    if current_page is not None:
                        markdown_content.append("\n")
                    markdown_content.append(f"## Page {page}\n\n")
                    current_page = page
                
                # Add annotation
                markdown_content.append(f"### {annotation_type.title()}")
                if annotation_color:
                    markdown_content.append(f" `{annotation_color}`")
                markdown_content.append("\n\n")
                
                if annotation_text and pd.notna(annotation_text):
                    markdown_content.append(f"**Text:** {annotation_text}\n\n")
                
                if annotation_comment and pd.notna(annotation_comment):
                    markdown_content.append(f"**Comment:** {annotation_comment}\n\n")
                
                markdown_content.append("---\n\n")
              # Write to markdown file
            output_file = output_dir / f"{attachment_id}.md"
            
            with open(output_file, 'w', encoding=DEFAULT_ENCODING) as f:
                f.write(''.join(markdown_content))
            
            print(f"✅ ({len(annot_sel)} annotations)")
            results[attachment_id] = {
                "status": "success", 
                "file_path": str(output_file),
                "annotation_count": len(annot_sel),
                "paper_title": paper_title
            }
            successful += 1
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results[attachment_id] = {"status": "failed", "reason": str(e)}
            failed += 1
    
    # Print summary
    print("=" * 80)
    print(f"🎉 Batch processing completed!")
    print(f"✅ Successful: {successful}/{total_attachments}")
    print(f"❌ Failed: {failed}/{total_attachments}")
    
    if failed > 0:
        print("\n❌ Failed attachments:")
        for att_id, result in results.items():
            if result["status"] == "failed":
                print(f"  - ID {att_id}: {result['reason']}")
    
    return results


def list_available_attachments(csv_file=ANNOTATIONS_CSV_FILENAME):
    """List all available attachment IDs with their paper titles."""
    try:
        annot = pd.read_csv(csv_file, header=0)
        attachments = annot.groupby('attachment_id').agg({
            'paper_title': 'first',
            'annotation_id': 'count'
        }).rename(columns={'annotation_id': 'annotation_count'})
        
        print("📚 Available attachments:")
        print("=" * 120)
        for att_id, info in attachments.iterrows():
            print(f"ID: {att_id:4d} | Annotations: {info['annotation_count']:3d} | Title: {info['paper_title']}")
        print("=" * 120)
        
    except FileNotFoundError:
        print(f"❌ CSV file '{csv_file}' not found.")
        print("💡 Run extract_zotero_annotations.py first to generate the annotations CSV.")


def convert_single_annotation_by_id(attachment_id: int, output_path: str = DEFAULT_ANNOTATIONS_OUTPUT_DIR, csv_file: str = ANNOTATIONS_CSV_FILENAME) -> str:
    """
    Convert annotations for a specific attachment_id to a markdown file.
    
    Args:
        attachment_id (int): The attachment ID to filter annotations
        output_path (str): Directory path where the markdown file will be saved
        csv_file (str): Path to the CSV file containing annotations
    
    Returns:
        str: Path to the created markdown file
    """
    try:
        # Read the CSV file
        annot = pd.read_csv(csv_file, header=0)
        
        # Filter annotations for the specific attachment_id
        annot_sel = annot.query(f"attachment_id == {attachment_id}")
        
        if annot_sel.empty:
            print(f"❌ No annotations found for attachment_id: {attachment_id}")
            return None
        
        # Get paper information (use the first row since all rows should have the same paper info)
        paper_info = annot_sel.iloc[0]
        paper_title = paper_info['paper_title']
        
        print(f"🔄 Converting annotations for: {paper_title}")
        print(f"📊 Found {len(annot_sel)} annotations")
        
        result = annotations_to_markdown(attachment_id, output_path, csv_file)
        
        if result:
            print(f"✅ Successfully created: {result}")
        
        return result
        
    except FileNotFoundError:
        print(f"❌ Annotations CSV file not found: {csv_file}")
        print("💡 Run extract_zotero_annotations.py first to generate the annotations CSV.")
        return None
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        return None


def convert_all_annotations(output_path: str = DEFAULT_ANNOTATIONS_OUTPUT_DIR, csv_file: str = ANNOTATIONS_CSV_FILENAME) -> dict:
    """
    Convert annotations for ALL attachment IDs to markdown files.
    
    Args:
        output_path (str): Directory path where the markdown files will be saved
        csv_file (str): Path to the CSV file containing annotations
    
    Returns:
        dict: Dictionary with attachment_id as key and result info as value
    """
    try:
        # Read the CSV file
        annot = pd.read_csv(csv_file, header=0)
        
        # Get all unique attachment IDs
        attachment_ids = annot['attachment_id'].unique()
        total_attachments = len(attachment_ids)
        
        if total_attachments == 0:
            print("❌ No attachments found in annotations CSV")
            return {}
        
        print(f"🚀 Found {total_attachments} attachments with annotations to convert")
        print(f"📁 Output directory: {output_path}")
        
        return process_all_attachments(output_path, csv_file)
        
    except FileNotFoundError:
        print(f"❌ Annotations CSV file not found: {csv_file}")
        print("💡 Run extract_zotero_annotations.py first to generate the annotations CSV.")
        return {}
    except Exception as e:
        print(f"❌ Error during batch conversion: {e}")
        return {}


if __name__ == "__main__":
    """Main function for direct execution without command line arguments."""
    print("🚀 Zotero Annotations to Markdown Converter")
    print("=" * 80)
    
    # Example 1: List available attachments
    # print("📋 Available attachments with annotations:")
    # list_available_attachments()
    
    # Example 2: Convert a single attachment by ID
    # Uncomment and modify the attachment_id to convert a specific attachment
    # attachment_id = 94  # Replace with your desired attachment ID
    # result = convert_single_annotation_by_id(attachment_id, "single_output")
    
    # Example 3: Convert all attachments
    # Uncomment to convert all attachments with annotations
    results = convert_all_annotations(DEFAULT_ANNOTATIONS_OUTPUT_DIR)
    
    if results:
        successful_count = sum(1 for r in results.values() if r["status"] == "success")
        total_annotations = sum(r.get("annotation_count", 0) for r in results.values() if r["status"] == "success")
        
        print(f"\n🎉 Batch conversion completed!")
        print(f"📊 {successful_count} markdown files created with {total_annotations} total annotations")
        print(f"📁 Files saved to: all_annotations_output")

