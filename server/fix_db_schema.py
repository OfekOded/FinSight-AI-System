from sqlalchemy import text
from database import engine

def upgrade_database():
    print("Connecting to database to fix schema...")
    with engine.connect() as conn:
        try:
            # הוספת user_id לטבלת מנויים
            print("Adding user_id to subscriptions...")
            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)"))
            
            # הוספת תאריך חידוש אם חסר
            print("Adding renewal_date to subscriptions...")
            conn.execute(text("ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS renewal_date INTEGER DEFAULT 1"))

            # הוספת user_id לטבלת תקציבים
            print("Adding user_id to budget_categories...")
            conn.execute(text("ALTER TABLE budget_categories ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)"))

            # הוספת user_id לטבלת חיסכון
            print("Adding user_id to savings_goals...")
            conn.execute(text("ALTER TABLE savings_goals ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)"))

            conn.commit()
            print("✅ Database schema updated successfully!")
            
        except Exception as e:
            print(f"⚠️ Error updating schema: {e}")
            print("Note: If the columns already exist, this error can be ignored.")

if __name__ == "__main__":
    upgrade_database()