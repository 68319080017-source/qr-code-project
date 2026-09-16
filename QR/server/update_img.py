import sqlite3
conn = sqlite3.connect('sql_app.db')
c = conn.cursor()
c.execute("UPDATE assets SET image_path = '/uploads/' || asset_code || '.jpg'")
conn.commit()
print('DONE')
conn.close()
