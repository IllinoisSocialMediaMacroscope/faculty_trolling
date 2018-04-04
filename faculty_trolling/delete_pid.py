import sqlite3

def delete_pid(pid):
    conn = sqlite3.connect('/home/ubuntu/faculty_trolling/db.sqlite3')
    sql = '''DELETE FROM faculty_trolling_proccess WHERE pid=?'''
    cur = conn.cursor()
    cur.execute(sql, (pid, ))
    conn.commit()
    print('delete pid from database: ', pid)
