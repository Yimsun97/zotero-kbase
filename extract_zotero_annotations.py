"""
Zotero Annotations Extractor

This script extracts annotations (highlights, notes, comments) from a Zotero SQLite database.
It creates a comprehensive CSV file linking annotations to their papers and attachments.

Usage:
    python extract_zotero_annotations.py

Output:
    - zotero_annotations.csv: Complete dataset with annotations linked to papers
"""

import sqlite3
import pandas as pd
from pathlib import Path
import json
from config import (
    ZOTERO_DB_PATH,
    DEFAULT_ENCODING,
    ANNOTATIONS_CSV_FILENAME
)

# Zotero annotation type ID to name mapping
ANNOTATION_TYPE_MAPPING = {
    1: 'highlight',
    2: 'note', 
    3: 'image',
    4: 'ink'
}


def extract_zotero_annotations(db_path, output_csv):
    """
    Extract all annotations from Zotero database with paper and attachment context.
    
    Args:
        db_path (str): Path to the Zotero SQLite database
        output_csv (str): Output CSV filename
    """
    
    print(f"🔍 Extracting annotations from Zotero database: {db_path}", flush=True)
    
    # Check if database file exists
    if not Path(db_path).exists():
        print(f"❌ Database file not found: {db_path}", flush=True)
        return False
    
    try:
        # Connect to database in read-only mode
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        print("✅ Database connected successfully", flush=True)
          # First, let's get a simpler query working
        simple_query = f"""
        SELECT 
            ia.itemID as annotation_id,
            ia.parentItemID as attachment_id,
            ia.type as annotation_type,
            ia.text as annotation_text,
            ia.comment as annotation_comment,
            ia.color as annotation_color,
            ia.pageLabel as page_label,
            
            -- Attachment path
            attachments.path as attachment_path,
            attachments.contentType as attachment_content_type,
            
            -- Paper ID
            attachments.parentItemID as paper_id,
            
            -- Paper title
            COALESCE(title_values.value, 'No Title') as paper_title
            
        FROM itemAnnotations ia
        
        -- Join with attachments
        LEFT JOIN itemAttachments attachments ON ia.parentItemID = attachments.itemID
          -- Get paper title
        LEFT JOIN itemData title_data ON attachments.parentItemID = title_data.itemID AND title_data.fieldID = 1
        LEFT JOIN itemDataValues title_values ON title_data.valueID = title_values.valueID
        
        ORDER BY ia.itemID
        """
        
        print("📊 Executing simplified annotations query...", flush=True)
        cursor.execute(simple_query)
        results = cursor.fetchall()
        
        print(f"✅ Found {len(results)} annotations", flush=True)
        
        if results:
            # Create DataFrame
            columns = [
                'annotation_id', 'attachment_id', 'annotation_type', 'annotation_text',
                'annotation_comment', 'annotation_color', 'page_label', 'attachment_path',
                'attachment_content_type', 'paper_id', 'paper_title'
            ]
            df = pd.DataFrame(results, columns=columns)
              # Clean up the data - properly handle line breaks and special characters
            df['paper_title'] = df['paper_title'].astype(str).str.replace('\n', ' ').str.replace('\r', ' ').str.strip()
            
            # Clean annotation text and comments - remove line breaks and normalize whitespace
            df['annotation_text'] = df['annotation_text'].fillna('').astype(str)
            df['annotation_text'] = df['annotation_text'].str.replace('\n', ' ').str.replace('\r', ' ').str.replace('\t', ' ')
            df['annotation_text'] = df['annotation_text'].str.replace(r'\s+', ' ', regex=True).str.strip()
            
            df['annotation_comment'] = df['annotation_comment'].fillna('').astype(str)
            df['annotation_comment'] = df['annotation_comment'].str.replace('\n', ' ').str.replace('\r', ' ').str.replace('\t', ' ')
            df['annotation_comment'] = df['annotation_comment'].str.replace(r'\s+', ' ', regex=True).str.strip()
            
            df['attachment_path'] = df['attachment_path'].astype(str)
              # Add annotation type names
            df['annotation_type_name'] = df['annotation_type'].map(ANNOTATION_TYPE_MAPPING).fillna('unknown')              # Save to CSV with proper quoting to handle special characters
            output_path = Path(output_csv)
            df.to_csv(output_path, index=False, encoding=DEFAULT_ENCODING, quoting=1, escapechar='\\')  # quoting=1 means QUOTE_ALL
            print(f"✅ Results saved to: {output_path.absolute()}", flush=True)
            
            # Show summary statistics
            print(f"\n📋 Summary:", flush=True)
            print(f"   • Total annotations: {len(df)}", flush=True)
            print(f"   • Unique papers: {df['paper_id'].nunique()}", flush=True)
            print(f"   • Unique attachments: {df['attachment_id'].nunique()}", flush=True)
            
            # Annotation type distribution
            if 'annotation_type_name' in df.columns:
                annotation_types = df['annotation_type_name'].value_counts()
                print(f"\n📝 Annotation Types:", flush=True)
                for ann_type, count in annotation_types.items():
                    print(f"   • {ann_type}: {count}", flush=True)
            
            # Content type distribution for annotated attachments
            if 'attachment_content_type' in df.columns:
                content_types = df['attachment_content_type'].value_counts()
                print(f"\n📄 Annotated Content Types:")
                for content_type, count in content_types.head(5).items():
                    if pd.notna(content_type):
                        print(f"   • {content_type}: {count}")
            
            # Show papers with most annotations
            paper_annotation_counts = df.groupby(['paper_id', 'paper_title']).size().sort_values(ascending=False)
            print(f"\n🔥 Top 5 Most Annotated Papers:")
            for i, ((paper_id, title), count) in enumerate(paper_annotation_counts.head(5).items()):
                truncated_title = title[:60] + "..." if len(title) > 60 else title
                print(f"   {i+1}. {truncated_title} ({count} annotations)")
            
            print(f"\n✅ Annotation extraction completed successfully!")
            return True
            
        else:
            print("❌ No annotations found in the database")
            return False
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def analyze_annotations(csv_file):
    """
    Perform additional analysis on the extracted annotations.
    
    Args:
        csv_file (str): Path to the annotations CSV file
    """
    
    try:
        df = pd.read_csv(csv_file)
        
        print(f"\n🔍 Additional Analysis:")
        print(f"=" * 80)
        
        # Annotations by color
        if 'annotation_color' in df.columns:
            color_counts = df['annotation_color'].value_counts()
            print(f"\n🎨 Annotations by Color:")
            for color, count in color_counts.head(10).items():
                if pd.notna(color):
                    print(f"   • Color {color}: {count}")
        
        # Text vs non-text annotations
        text_annotations = df['annotation_text'].notna() & (df['annotation_text'] != '')
        comment_annotations = df['annotation_comment'].notna() & (df['annotation_comment'] != '')
        
        print(f"\n📝 Annotation Content:")
        print(f"   • With highlighted text: {text_annotations.sum()}")
        print(f"   • With comments: {comment_annotations.sum()}")
        print(f"   • With both: {(text_annotations & comment_annotations).sum()}")
        
        # Average annotations per paper
        avg_annotations = len(df) / df['paper_id'].nunique()
        print(f"\n📊 Statistics:")
        print(f"   • Average annotations per paper: {avg_annotations:.1f}")
        
        # Show sample annotation text
        text_samples = df[df['annotation_text'].notna() & (df['annotation_text'] != '')]['annotation_text'].head(3)
        if not text_samples.empty:
            print(f"\n📖 Sample Annotation Texts:")
            for i, text in enumerate(text_samples):
                truncated_text = text[:100] + "..." if len(text) > 100 else text
                print(f"   {i+1}. {truncated_text}")
        
    except Exception as e:
        print(f"❌ Error in analysis: {e}")

def main():
    """Main function to run the annotation extraction."""
    print("🚀 Zotero Annotations Extractor")
    print("=" * 80)
    
    success = extract_zotero_annotations(ZOTERO_DB_PATH, ANNOTATIONS_CSV_FILENAME)
    
    if success:
        print(f"\n🎉 Annotation extraction completed!")
        print(f"📁 Output file: {ANNOTATIONS_CSV_FILENAME}")
        
        # Perform additional analysis
        analyze_annotations(ANNOTATIONS_CSV_FILENAME)
        
        print(f"\n💡 You can now use this CSV file to:")
        print(f"   • Analyze your reading and annotation patterns")
        print(f"   • Export highlights and notes for review")
        print(f"   • Search across all your annotations")
        print(f"   • Generate reading summaries by paper")
    else:
        print(f"\n❌ Annotation extraction failed!")

if __name__ == "__main__":
    main()