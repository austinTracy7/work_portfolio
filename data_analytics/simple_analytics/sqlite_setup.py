import pandas as pd
import sqlite3

db_path = "data/burgers_and_shakeland.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the table
cursor.execute("""
CREATE TABLE IF NOT EXISTS burgers_and_shakeland (
    DateTime TEXT,
    Location TEXT,
    ItemID INTEGER,
    Transaction_EmployeeID INTEGER,
    Employee_Name TEXT,
    Item TEXT,
    Price REAL
);
""")

# Get and insert data
df = pd.read_csv(r"data/burgers_and_shakeland.csv")
cursor.executemany("""
    INSERT INTO BURGERS_AND_SHAKELAND VALUES (?,?,?,?,?,?,?)
""",df.applymap(lambda x: str(x)).to_records(index=False))

# Ensure data got inserted alright
cursor.execute("SELECT * FROM BURGERS_AND_SHAKELAND")
cursor.fetchall()


# End
conn.commit()
conn.close()