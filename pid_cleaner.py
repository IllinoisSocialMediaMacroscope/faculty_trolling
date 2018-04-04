import sqlite3
from faculty_trolling.delete_pid import delete_pid
from faculty_trolling.email_alert import email_alert
import time
import psutil

def detect_pid_alive(pid):
    """
    Check For the existence of a unix pid.
    """
    proc = psutil.Process(pid)

    try:
        if proc.status() == psutil.STATUS_ZOMBIE:
            print('pid is zombie:',pid)
            return False
        elif proc.status() == psutil.STATUS_DEAD:
            print('pid is dead:', pid)
            return False
        else:
            print('pid is alive:', pid)
            return True
    except psutil.NoSuchProcess as e:
        print(e)
        print('pid does not exist:', pid)
        return False

def retrieve_pid():
    """
    :return: a key value pair of user_id: pid
    """
    conn = sqlite3.connect('db.sqlite3')
    sql = '''SELECT * FROM faculty_trolling_proccess'''
    cur = conn.cursor()
    all = cur.execute(sql).fetchall()

    pid_dict = {} # user_id: pid
    for row in all:
        pid_dict[row[2]] = row[1]

    return pid_dict

def retreive_user_info(user_id):
    conn = sqlite3.connect('db.sqlite3')
    sql = '''SELECT * FROM auth_user WHERE id=?'''
    cur = conn.cursor()
    user = cur.execute(sql,(user_id,)).fetchone()

    return (user[4], user[6])


if __name__ == '__main__':

    while True:
        pid_dict = retrieve_pid()

        for user_id, pid in pid_dict.items():

            if not detect_pid_alive(int(pid)):
                # delete that entry
                delete_pid(pid)

                # send out email
                user_info = retreive_user_info(user_id)
                username = user_info[0]
                email = user_info[1]
                message = 'We detect that your blocker has turned into Zombie state.'
                email_alert(email, username,message)

        time.sleep(10)
