from ftplib import FTP, error_perm
from os import path
import sqlite3
import client_config


def send_files():
    if path.isfile(client_config.database_path):
        conn = sqlite3.connect(client_config.database_path, detect_types=sqlite3.PARSE_COLNAMES)
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()
        cursor.execute("select * from file where transferred=? limit ?",
                       (client_config.TRANS_INCOMPLETE, client_config.TRANS_LIMIT))
        rows = cursor.fetchall()

        for row in rows:
            row_dict = dict(row)
            file = open(row_dict['file_path'], 'rb')
            ftp.storbinary('STOR %s|>%s|%s'
                           % (row_dict['file_name'], row_dict['file_type'], row_dict['hash_value']), file)
            resp = ftp.getresp()
            hash_index = resp.find('r=')
            if hash_index > -1:
                conn.execute("update file set transferred = ? where id = ?",
                             (int(resp[hash_index + 2:]), row_dict['id']))
                conn.commit()
            file.close()


if __name__ == "__main__":
    try:
        ftp = FTP(client_config.server_address)
        print(ftp.welcome[4:])
        username = client_config.username
        password = client_config.password
        logged_in = 0
        try:
            ftp.login(username, password)
            logged_in = 1
            print('login successful')
        except error_perm:
            print('login failed, attempting signing up')
            ftp.putcmd('SIGNIN -u ' + username + ' -p ' + password)
            ftp.quit()
            # re-instantiate ftp
            ftp = FTP(client_config.server_address)
            ftp.login(username, password)
            print('sign up and log in successful.')
            logged_in = 1
        if logged_in == 1:
            print('attempting sending files')
            send_files()
            print('Tasks finished, logging out')
        else:
            print('Access denied!')
        ftp.quit()
    except ConnectionRefusedError:
        print('Server down or can not be reached')