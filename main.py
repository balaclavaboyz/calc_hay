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
                    name)
                    values(?,?,?,?,?,?)
                ''', (id, vProd, data_hora_emissao, int(indTot), 1, name)
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
                    name)
                    values(?,?,?,?,?,?)
                ''', (id, vProd, datetime.datetime.strptime(data_hora_emissao[:-6], '%Y-%m-%dT%H:%M:%S'), int(indTot), 0, name)
                )


def pred(con: sqlite3.Connection, cur: sqlite3.Cursor):
    cur.execute('select * from estoque where entrada = 0 order by id')

    temp = {}

    for x in cur.fetchall():
        if x[0] not in temp.keys():
            item_date = x[3]
            item_id = x[0]
            temp[item_id] = [item_date]
        else:
            item_date = x[3]
            item_id = x[0]
            old = temp.get(item_id)
            old.append(item_date)
            temp[item_id] = old

    for k, v in temp.items():
        new_values = [v[i]-v[i-1]
                      for i in range(1, len(v))]

        avg_values = sum(new_values, datetime.timedelta(0))/len(new_values)

        pred_per_day = avg_values.total_seconds()/30/3600

        cur.execute('select * from pred where id = ?', (k,))
        res = cur.fetchone()
        if not res:
            cur.execute('insert into pred(id)values(?)', (k,))

        cur.execute('''
            update pred
            set pred = ?
            where id = ?
        ''', (pred_per_day, k))
        # TODO no db nao existe o row com o nome para k

        # for index in range(len(v)):
        #     date1 = v[index]
        #     date2 = v[index - 1]
        #     pp(date1.timestamp())
        #     pp(date2.timestamp())
        #     diff = date2.timestamp() - date1.timestamp()
        #     delta_time += diff
        #     pp(delta_time)
        # pp('===')
        # fazendo diff entre os els da list de datetime e dps fazer mean a lista resultante e dps usaro res na func abaixo
        # pp(delta_time/len(v))
    # pp(temp['7898446731243'])
        ''', (round(pred_per_day, 2), k))


if __name__ == '__main__':
    con = sqlite3.connect(
        'db.db', detect_types=sqlite3.PARSE_COLNAMES | sqlite3.PARSE_DECLTYPES)
    cur = con.cursor()
    bomdia = Db()

    bomdia.recreate_db(con, cur)
    xml_process(con, cur)
    pred(con, cur)

    cur.close()
    con.commit()
    con.close()
