"""
Reorder columns in all_valid_articles table to put ID first.
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


def reorder_columns():
    """Reorder columns to put ID first."""
    print("=" * 80)
    print("REORDERING COLUMNS - ID FIRST")
    print("=" * 80)
    
    with get_db_cursor() as cur:
        # Get current column order
        print("\nStep 1: Getting current column information...")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'all_valid_articles'
            ORDER BY ordinal_position
        """)
        columns = cur.fetchall()
        
        # Separate ID column from others
        id_col = None
        other_cols = []
        
        for col in columns:
            if col['column_name'] == 'id':
                id_col = col
            else:
                other_cols.append(col)
        
        if not id_col:
            print("❌ ID column not found!")
            return
        
        print(f"  Found {len(columns)} columns")
        print(f"  ID column: {id_col['column_name']} ({id_col['data_type']})")
        
        # Get all column names in desired order (ID first)
        desired_order = ['id'] + [col['column_name'] for col in other_cols]
        
        print("\nStep 2: Creating new table with reordered columns...")
        
        # Build column definitions
        col_defs = []
        
        # ID column first
        id_def = f"id INTEGER"
        if id_col['is_nullable'] == 'NO':
            id_def += " NOT NULL"
        if id_col['column_default']:
            id_def += f" DEFAULT {id_col['column_default']}"
        col_defs.append(id_def)
        
        # Other columns
        for col in other_cols:
            col_name = col['column_name']
            data_type = col['data_type'].upper()
            
            # Handle array types
            if col['data_type'] == 'ARRAY':
                # Get array element type
                cur.execute("""
                    SELECT udt_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'all_valid_articles' 
                    AND column_name = %s
                """, (col_name,))
                udt_info = cur.fetchone()
                if udt_info and 'text' in udt_info['udt_name'].lower():
                    data_type = 'TEXT[]'
                else:
                    data_type = 'TEXT[]'  # Default to text array
            
            col_def = f"{col_name} {data_type}"
            if col['is_nullable'] == 'NO':
                col_def += " NOT NULL"
            if col['column_default']:
                col_def += f" DEFAULT {col['column_default']}"
            col_defs.append(col_def)
        
        # Create new table
        create_table_sql = f"""
            CREATE TABLE all_valid_articles_new (
                {', '.join(col_defs)},
                PRIMARY KEY (id)
            )
        """
        
        print("  Creating new table...")
        cur.execute("DROP TABLE IF EXISTS all_valid_articles_new")
        cur.execute(create_table_sql)
        
        print("Step 3: Copying data to new table...")
        # Build column list for INSERT
        col_list = ', '.join(desired_order)
        cur.execute(f"""
            INSERT INTO all_valid_articles_new ({col_list})
            SELECT {col_list}
            FROM all_valid_articles
        """)
        
        row_count = cur.rowcount
        print(f"  Copied {row_count} rows")
        
        print("Step 4: Replacing old table...")
        # Drop old table
        cur.execute("DROP TABLE all_valid_articles CASCADE")
        
        # Rename new table
        cur.execute("ALTER TABLE all_valid_articles_new RENAME TO all_valid_articles")
        
        print("\n✓ Successfully reordered columns - ID is now first")
        
        # Show new column order
        print("\nNew column order:")
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'all_valid_articles'
            ORDER BY ordinal_position
        """)
        new_columns = cur.fetchall()
        for i, col in enumerate(new_columns, 1):
            marker = " ← ID" if col['column_name'] == 'id' else ""
            print(f"  {i}. {col['column_name']}{marker}")


def main():
    # Test database connection
    if not test_connection():
        print("❌ Database connection failed. Please check your database configuration.")
        return
    
    reorder_columns()
    
    print("\n" + "=" * 80)
    print("PROCESS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()


