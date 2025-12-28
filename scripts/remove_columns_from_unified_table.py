"""
Remove specified columns from all_valid_articles table:
- text_content
- validation_confidence
- validation_reason
- is_valid
- created_at
"""

import sys
from pathlib import Path

# Add project root to path
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Database connection
from database.db_config import get_db_cursor, test_connection

# Fix Windows encoding issue
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Columns to remove
COLUMNS_TO_REMOVE = [
    'source_type'
]


def check_column_exists(cur, table_name: str, column_name: str) -> bool:
    """Check if a column exists in the table."""
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = %s AND column_name = %s
    """, (table_name, column_name))
    return cur.fetchone() is not None


def remove_columns():
    """Remove specified columns from all_valid_articles table."""
    print("=" * 80)
    print("REMOVING COLUMNS FROM all_valid_articles TABLE")
    print("=" * 80)
    
    with get_db_cursor() as cur:
        # Check which columns exist
        print("\nChecking existing columns...")
        existing_columns = []
        for col in COLUMNS_TO_REMOVE:
            if check_column_exists(cur, 'all_valid_articles', col):
                existing_columns.append(col)
                print(f"  ✓ Found: {col}")
            else:
                print(f"  ✗ Not found: {col}")
        
        if not existing_columns:
            print("\n✓ None of the specified columns exist. Nothing to remove.")
            return
        
        # Remove columns
        print(f"\nRemoving {len(existing_columns)} column(s)...")
        for col in existing_columns:
            try:
                print(f"  Removing {col}...", end=" ")
                cur.execute(f"ALTER TABLE all_valid_articles DROP COLUMN IF EXISTS {col}")
                print("✓")
            except Exception as e:
                print(f"✗ Error: {e}")
        
        print(f"\n✓ Successfully removed {len(existing_columns)} column(s)")
        
        # Show remaining columns
        print("\nRemaining columns in all_valid_articles:")
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'all_valid_articles'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        for col in columns:
            print(f"  - {col['column_name']} ({col['data_type']})")


def main():
    # Test database connection
    if not test_connection():
        print("❌ Database connection failed. Please check your database configuration.")
        return
    
    remove_columns()
    
    print("\n" + "=" * 80)
    print("PROCESS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()

