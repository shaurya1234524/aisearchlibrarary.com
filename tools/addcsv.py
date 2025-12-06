
import pandas as pd
import sqlite3

df = pd.read_csv("aitoolsdirectory_tools.csv")
conn = sqlite3.connect("db.sqlite3")  # or your DB path
df.to_sql("tools_tool", conn, if_exists="append", index=False)
conn.close()
