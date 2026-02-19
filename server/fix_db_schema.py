from sqlalchemy import text
from database import engine

def upgrade_database():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE events ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)"))
            
            conn.execute(text("UPDATE events SET user_id = CAST(payload->>'user_id' AS INTEGER) WHERE user_id IS NULL AND payload->>'user_id' IS NOT NULL"))

            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)"))
            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS renewal_date INTEGER DEFAULT 1"))
            conn.execute(text("ALTER TABLE budget_categories ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)"))
            conn.execute(text("ALTER TABLE savings_goals ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)"))

            conn.commit()
            print("Database schema updated successfully!")
            
        except Exception as e:
            print(f"Error updating schema: {e}")

if __name__ == "__main__":
    upgrade_database()