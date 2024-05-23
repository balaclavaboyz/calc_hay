from pprint import pp
import datetime
import numpy
import sqlite3
from xml.dom.minidom import parse
from glob import glob

from db import Db


def xml_process(con: sqlite3.Connection, cur: sqlite3.Cursor):
    xmls_entrada = [i for i in glob('./entrada/*.xml')]

    if xmls_entrada:
        for i in xmls_entrada:
            with open(i, encoding='utf-8') as f:
                domtree = parse(f)

            data_hora_emissao = domtree.getElementsByTagName('dhEmi')[
                0].firstChild.data

            all_prods = domtree.getElementsByTagName('det')

            nfe = domtree.getElementsByTagName(
                'infNFe')[0].getAttribute('Id')

            # insert new nfe id
            cur.execute('insert into nfe(nfe)values(?)', (nfe,))

            for i in all_prods:
                id = domtree.getElementsByTagName('cEAN')[0].firstChild.data
                # item = i.getElementsByTagName('cProd')[0].firstChild.data
                vProd = i.getElementsByTagName(
                    'vProd')[0].firstChild.data
                indTot = i.getElementsByTagName(
                    'indTot')[0].firstChild.data
                name = i.getElementsByTagName(
                    'xProd')[0].firstChild.data

                # entrada
                cur.execute('''
                    insert into estoque(
                    id,
                    price,
                    date,
                    qnt,
                    entrada,
                    name,
                    nfe)
                    values(?,?,datetime(?) ,?,?,?,?)
                ''', (id, vProd, data_hora_emissao, int(indTot), 1, name, nfe)
                )

    # ===

    xml_saida = [i for i in glob('./saida/*.xml')]
    bomdia = []
    for i in xml_saida:
        if 'Evento' not in i:
            bomdia.append(i)
    xml_saida = bomdia

    if xml_saida:
        for file in xml_saida:
            with open(file, encoding='utf-8') as f:
                domtree = parse(f)

            data_hora_emissao = domtree.getElementsByTagName('dhEmi')[
                0].firstChild.data

            all_prods = domtree.getElementsByTagName('det')
            nfe = domtree.getElementsByTagName(
                'infNFe')[0].getAttribute('Id')

            # insert new nfe id
            cur.execute('insert into nfe(nfe)values(?)', (nfe,))

            for i in all_prods:
                id = domtree.getElementsByTagName('cEAN')[0].firstChild.data
                # item = i.getElementsByTagName('cProd')[0].firstChild.data
                vProd = i.getElementsByTagName(
                    'vProd')[0].firstChild.data
                indTot = i.getElementsByTagName(
                    'indTot')[0].firstChild.data
                name = i.getElementsByTagName(
                    'xProd')[0].firstChild.data

                # saida
                cur.execute('''
                    insert into estoque(
                    id,
                    price,
                    date,
                    qnt,
                    entrada,
                    name,
                    nfe)
                    values(?,?,datetime(?) ,?,?,?,?)
                ''', (id, vProd, data_hora_emissao, int(indTot), 0, name, nfe)
                )


def pred(con: sqlite3.Connection, cur: sqlite3.Cursor):
    cur.execute('select * from estoque where entrada = 0 order by id')

    temp = {}

    for x in cur.fetchall():
        if x[0] not in temp.keys():
            item_date = datetime.datetime.strptime(x[3], '%Y-%m-%d %H:%M:%S')
            item_id = x[0]
            temp[item_id] = [item_date]
        else:
            item_date = datetime.datetime.strptime(x[3], '%Y-%m-%d %H:%M:%S')
            item_id = x[0]
            old = temp.get(item_id)
            old.append(item_date)
            temp[item_id] = old

    for k, v in temp.items():
        new_values = [v[i]-v[i-1]
                      for i in range(1, len(v))]

        avg_values = sum(new_values, datetime.timedelta(0))/len(new_values)

        # 3600 minuto e hora e 24 horas
        pred_per_day = avg_values.total_seconds()/3600/24

        cur.execute('select * from pred where id = ?', (k,))
        res = cur.fetchone()
        if not res:
            cur.execute('insert into pred(id)values(?)', (k,))

        cur.execute('''
            update pred
            set pred = ?
            where id = ?
        ''', (round(pred_per_day, 2), k))


if __name__ == '__main__':
    con = sqlite3.connect('db.db')
    cur = con.cursor()
    bomdia = Db()

    bomdia.init(con, cur)
    xml_process(con, cur)
    pred(con, cur)

    cur.close()
    con.commit()
    con.close()
