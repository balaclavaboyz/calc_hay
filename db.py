from dataclasses import dataclass
import sqlite3


@dataclass
class Db:
    def init(self, con: sqlite3.Connection, cur: sqlite3.Cursor):
        cur.execute('drop table if exists estoque')
        cur.execute(
            'create table estoque(id text, price text, name text, date timestamp, qnt int, entrada int, nfe text, foreign key (nfe) references nfe (nfe))')

        cur.execute('drop table if exists pred')
        cur.execute('create table if not exists pred(id text, pred text)')

        # ID NFES
        cur.execute('drop table if exists nfe')
        cur.execute('create table if not exists nfe(nfe text primary key)')

        con.commit()

    def estoque_check(self, con: sqlite3.Connection, cur: sqlite3.Cursor, name: str, qnt: int):
        cur.execute('select distinct name from prod')
        res = cur.fetchall()

        if not res:
            return

        for i in res:
            cur.execute(
                'insert or ignore into estoque(name,q) values(?,?)', (int(i[0]), 0))
        cur.execute('''
                    update estoque
                    set q = ?
                    where name = ?
                    ''', (int(qnt)*-1, name))
        return

    def view_total(self, con: sqlite3.Connection, cur: sqlite3.Cursor):
        cur.execute('drop view temp')
        cur.execute('''
            create view temp
        ''')
        cur.execute('select * from temp')
        return cur.fetchall()
