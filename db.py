from dataclasses import dataclass
import sqlite3
from pprint import pp


@dataclass
class Db:
    def init(self, con: sqlite3.Connection, cur: sqlite3.Cursor):
        cur.execute('drop table if exists estoque')
        cur.execute(
            'create table estoque(id text, natop text, price real, name text, date timestamp, qnt int, entrada int, nfe text, foreign key (nfe) references nfe (nfe))')

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

    def view_imposto(self, con: sqlite3.Connection, cur: sqlite3.Cursor):
        cur.execute('''select sum(price)
        from estoque
        where entrada = 0 and natop = 'Venda de mercadorias' ''')
        res = cur.fetchall()

        total = res[0][0]
        simples = total * 0.04
        ml_tax = total * .25

        pp(total)
        pp(simples)
        pp(ml_tax)
