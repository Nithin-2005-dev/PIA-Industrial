import sqlite3
import json
import sys
from pathlib import Path

# Adjust path to import backend modules if needed, or just work directly with sqlite
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.adapters.database.sqlite_provider import _DEFAULT_DB_PATH, _table_name
from app.adapters.database.models import RepositorySessionRecord

def main():
    print(f"Connecting to DB: {_DEFAULT_DB_PATH}")
    if not _DEFAULT_DB_PATH.exists():
        print("Database not found!")
        return

    conn = sqlite3.connect(str(_DEFAULT_DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    table = _table_name(RepositorySessionRecord)
    
    # Fetch all sessions
    cursor.execute(f"SELECT object_id, data FROM {table}")
    rows = cursor.fetchall()
    
    sessions = []
    for r in rows:
        obj_id = r["object_id"]
        data = json.loads(r["data"])
        sessions.append((obj_id, data))

    # Group by repo:branch
    grouped = {}
    for obj_id, data in sessions:
        repo = str(data.get("repository", "")).strip().strip("/").lower()
        branch = str(data.get("branch") or "main")
        if not repo:
            continue
        key = f"{repo}:{branch}"
        if key not in grouped:
            grouped[key] = []
        grouped[key].append((obj_id, data))

    # Find duplicates and delete
    deleted_count = 0
    for key, group in grouped.items():
        if len(group) > 1:
            print(f"Found {len(group)} sessions for {key}")
            # Sort by last_synced_at or identity.created_at
            def get_sort_key(item):
                data = item[1]
                identity = data.get("identity", {})
                last_synced = data.get("last_synced_at")
                updated = identity.get("updated_at")
                created = identity.get("created_at")
                return last_synced or updated or created or ""
                
            group.sort(key=get_sort_key, reverse=True)
            
            canonical = group[0]
            duplicates = group[1:]
            
            print(f"  Keeping canonical: {canonical[0]}")
            for dup in duplicates:
                print(f"  Deleting duplicate: {dup[0]}")
                cursor.execute(f"DELETE FROM {table} WHERE object_id = ?", (dup[0],))
                # Optionally delete from fts table
                cursor.execute(f"DELETE FROM {table}_fts WHERE object_id = ?", (dup[0],))
                deleted_count += 1
                
    if deleted_count > 0:
        conn.commit()
        print(f"Successfully deleted {deleted_count} duplicate sessions.")
    else:
        print("No duplicate sessions found.")
        
    conn.close()

if __name__ == "__main__":
    main()
