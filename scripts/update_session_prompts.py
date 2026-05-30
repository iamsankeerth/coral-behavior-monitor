import sqlite3
import os

db_path = r"C:\Users\lenovo\AppData\Local\hermes\state.db"
soul_path = r"C:\Users\lenovo\AppData\Local\hermes\SOUL.md"

def main():
    if not os.path.exists(db_path):
        print(f"Error: state.db not found at {db_path}")
        return
    if not os.path.exists(soul_path):
        print(f"Error: SOUL.md not found at {soul_path}")
        return

    with open(soul_path, "r", encoding="utf-8") as f:
        soul_content = f.read()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all active sessions
    cursor.execute("SELECT id FROM sessions")
    sessions = cursor.fetchall()
    
    print(f"Found {len(sessions)} sessions in database.")
    for (sid,) in sessions:
        print(f"Updating system_prompt for session: {sid}")
        cursor.execute(
            "UPDATE sessions SET system_prompt = ? WHERE id = ?",
            (soul_content, sid)
        )
        
    conn.commit()
    conn.close()
    print("Successfully updated system prompts in state.db!")

if __name__ == "__main__":
    main()
