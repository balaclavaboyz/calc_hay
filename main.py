from pprint import pp
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
                item = i.getElementsByTagName('cProd')[0].firstChild.data
                vProd = i.getElementsByTagName(
                    'vProd')[0].firstChild.data
                indTot = i.getElementsByTagName(
                    'indTot')[0].firstChild.data

                # saida
                cur.execute('''
                    insert into estoque(
                    id,
                    price,
                    date,
                    qnt,
                    entrada)
                    values(?,?,?,?,?)
                ''', (id, vProd, data_hora_emissao, int(indTot), 1)
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
                item = i.getElementsByTagName('cProd')[0].firstChild.data
                vProd = i.getElementsByTagName(
                    'vProd')[0].firstChild.data
                indTot = i.getElementsByTagName(
                    'indTot')[0].firstChild.data

                # saida
                cur.execute('''
                    insert into estoque(
                    id,
                    price,
                    date,
                    qnt,
                    entrada)
                    values(?,?,?,?,?)
                ''', (id, vProd, data_hora_emissao, int(indTot), 0)
                )


def pred(con: sqlite3.Connection, cur: sqlite3.Cursor):
    cur.execute('select * from estoque group by id')
    unique_id = cur.fetchall()
    pp(unique_id)


if __name__ == '__main__':
    con = sqlite3.Connection('db.db')
    cur = con.cursor()
    bomdia = Db()

    # bomdia.recreate_db(con, cur)
    # xml_process(con, cur)
    pred(con, cur)

    cur.close()
    con.commit()
    con.close()
