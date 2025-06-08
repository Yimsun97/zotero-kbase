"""
Zotero Database Extractor

This script extracts paper-attachment links from a Zotero SQLite database.
It creates a comprehensive CSV file with paper titles, authors, collections, and attachment information.

Usage:
    python extract_zotero_metadata.py

Output:
    - zotero_metadata.csv: Complete dataset with papers, authors, collections, and attachments
"""

import sqlite3
import pandas as pd
from pathlib import Path
from collections import Counter
from config import (
    ZOTERO_DATA_DIR,
    ZOTERO_DB_PATH,
    STORAGE_DIR_NAME,
    METADATA_CSV_FILENAME,
    DEFAULT_ENCODING,
    
)


def get_fullpath_from_zotero_path(path, key):
    """
    Convert Zotero storage path to full filesystem path.
    
    Args:
        path (str): The attachment path from Zotero
        key (str): The attachment key
    
    Returns:
        str: Full filesystem path to the attachment
    """
    if "storage:" in path:
        return f"{ZOTERO_DATA_DIR}\\{STORAGE_DIR_NAME}\\{key}\\{path.split('storage:')[1]}"
    else:
        return path

def get_fullpath(path, prefix, key):
    """
    Convert Zotero storage path to full filesystem path.
    
    Args:
        path (str): The attachment path from Zotero
        prefix (str): The Zotero data directory path
        key (str): The attachment key
    
    Returns:
        str: Full filesystem path to the attachment
    """
    return get_fullpath_from_zotero_path(path, key)

def extract_zotero_data(db_path, output_csv):
    """
    Extract complete paper-attachment data from Zotero database.
    
    Args:
        db_path (str): Path to the Zotero SQLite database
        output_csv (str): Output CSV filename
    """
    
    print(f"🔍 Extracting data from Zotero database: {db_path}")
    
    # Check if database file exists
    if not Path(db_path).exists():
        print(f"❌ Database file not found: {db_path}")
        return False
    
    try:
        # Connect to database in read-only mode
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        cursor = conn.cursor()
        print("✅ Database connected successfully")
          # Main query to get all paper-attachment relationships with authors and collections
        query = f"""
        SELECT 
            -- Paper information
            parent_items.itemID as paper_id,
            parent_items.key as paper_key,
            parent_items.dateAdded as paper_date_added,
            parent_items.dateModified as paper_date_modified,
            
            -- Paper title
            COALESCE(title_values.value, 'No Title') as paper_title,            -- Authors (concatenated)
            GROUP_CONCAT(
                CASE 
                    WHEN creators.firstName IS NOT NULL AND creators.lastName IS NOT NULL 
                    THEN creators.lastName || ', ' || creators.firstName
                    WHEN creators.lastName IS NOT NULL 
                    THEN creators.lastName
                    ELSE creators.firstName
                END, '; ') as authors,
              -- Collection names (using subquery to get unique collections per paper)
            (SELECT GROUP_CONCAT(c.collectionName, '; ')
             FROM (SELECT DISTINCT ci2.itemID, c.collectionName
                   FROM collectionItems ci2 
                   JOIN collections c ON ci2.collectionID = c.collectionID
                   WHERE ci2.itemID = parent_items.itemID) c) as collection_names,
            
            -- Attachment information
            attachments.itemID as attachment_id,
            attachment_items.key as attachment_key,
            attachment_items.dateAdded as attachment_date_added,
            attachments.contentType,
            attachments.path as attachment_path,
            
            -- Link mode description
            CASE attachments.linkMode
                WHEN 0 THEN 'imported_file'
                WHEN 1 THEN 'imported_url'
                WHEN 2 THEN 'linked_file'
                WHEN 3 THEN 'linked_url'
                ELSE 'unknown'
            END as link_mode
            
        FROM itemAttachments attachments
        
        -- Join with items table for attachment details
        JOIN items attachment_items ON attachments.itemID = attachment_items.itemID
        
        -- Join with parent items (papers)
        JOIN items parent_items ON attachments.parentItemID = parent_items.itemID
          -- Get paper title (fieldID=1 is typically title in Zotero)
        LEFT JOIN itemData title_data ON parent_items.itemID = title_data.itemID AND title_data.fieldID = 1
        LEFT JOIN itemDataValues title_values ON title_data.valueID = title_values.valueID
        
        -- Get paper authors
        LEFT JOIN itemCreators ic ON parent_items.itemID = ic.itemID
        LEFT JOIN creators ON ic.creatorID = creators.creatorID
        
        WHERE attachments.parentItemID IS NOT NULL
        
        GROUP BY 
            parent_items.itemID,
            attachments.itemID,
            parent_items.key,
            parent_items.dateAdded,
            parent_items.dateModified,
            title_values.value,
            attachments.contentType,
            attachments.path,
            attachment_items.key,
            attachment_items.dateAdded,
            attachments.linkMode
            
        ORDER BY parent_items.dateAdded DESC, attachments.itemID
        """
        print("📊 Executing query...")
        cursor.execute(query)
        results = cursor.fetchall()
        
        print(f"✅ Found {len(results)} paper-attachment records")
        
        if results:
            # Create DataFrame
            columns = [
                'paper_id', 'paper_key', 'paper_date_added', 'paper_date_modified',
                'paper_title', 'authors', 'collection_names', 'attachment_id', 'attachment_key',
                'attachment_date_added', 'contentType', 'attachment_path', 'link_mode'
            ]
            
            df = pd.DataFrame(results, columns=columns)
            
            # Clean up the data
            df['paper_title'] = df['paper_title'].astype(str).str.replace('\n', ' ').str.strip()
            df['authors'] = df['authors'].fillna('Unknown Author')
            df['collection_names'] = df['collection_names'].fillna('Uncategorized')
            df['attachment_path'] = df['attachment_path'].astype(str)
            
            # Add attachment full path
            df['attachment_fullpath'] = df.apply(
                lambda row: get_fullpath(
                    row['attachment_path'], 
                    ZOTERO_DATA_DIR, 
                    row['attachment_key']
                ),
                axis=1
            )              # Save to CSV
            output_path = Path(output_csv)
            df.to_csv(output_path, index=False, encoding=DEFAULT_ENCODING)
            
            print(f"✅ Results saved to: {output_path.absolute()}")
            
            # Show summary statistics
            print(f"\n📋 Summary:")
            print(f"   • Total records: {len(df)}")
            print(f"   • Unique papers: {df['paper_id'].nunique()}")
            print(f"   • Unique attachments: {df['attachment_id'].nunique()}")
            
            # Collection distribution
            if 'collection_names' in df.columns:
                # Count papers by collection (excluding those without collections)
                collections_data = df[df['collection_names'] != 'Uncategorized']['collection_names']
                if not collections_data.empty:
                    # Split multiple collections and count
                    all_collections = []
                    for collections_str in collections_data:
                        if pd.notna(collections_str):
                            all_collections.extend([c.strip() for c in collections_str.split(';')])
                    
                    collection_counts = Counter(all_collections)
                    print(f"\n📚 Top Collections:")
                    for collection, count in collection_counts.most_common(5):
                        print(f"   • {collection}: {count} papers")
            
            # Content type distribution
            if 'contentType' in df.columns:
                content_types = df['contentType'].value_counts()
                print(f"\n📄 Content Types:")
                for content_type, count in content_types.head(5).items():
                    if pd.notna(content_type):
                        print(f"   • {content_type}: {count}")
            
            # Link mode distribution
            if 'link_mode' in df.columns:
                link_modes = df['link_mode'].value_counts()
                print(f"\n🔗 Link Modes:")
                for mode, count in link_modes.items():
                    print(f"   • {mode}: {count}")
            
            print(f"\n✅ Extraction completed successfully!")
            return True
            
        else:
            print("❌ No paper-attachment links found in the database")
            return False
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    """Main function to run the extraction."""
    print("🚀 Zotero Data Extractor")
    print("=" * 80)
    
    success = extract_zotero_data(ZOTERO_DB_PATH, METADATA_CSV_FILENAME)
    
    if success:
        print(f"\n🎉 Data extraction completed!")
        print(f"📁 Output file: {METADATA_CSV_FILENAME}")
        print(f"💡 You can now use this CSV file for further analysis or processing.")
    else:
        print(f"\n❌ Data extraction failed!")

if __name__ == "__main__":
    main()