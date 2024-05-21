import sqlite3
from xml.dom.minidom import parse
from glob import glob

from db import Db

if __name__ == '__main__':
    con = sqlite3.Connection('db.db')
    cur = con.cursor()
    bomdia = Db()

    bomdia.recreate_db(con, cur)

    xmls_entrada = [i for i in glob('./entrada/*.xml')]

    if xmls_entrada:
        for i in xmls_entrada:
            with open(i) as f:
                domtree = parse(f)

            name = domtree.getElementsByTagName('nNF')[0].firstChild.data
            item = domtree.getElementsByTagName('cProd')[0].firstChild.data
            vProd = domtree.getElementsByTagName('vProd')[0].firstChild.data
            indTot = domtree.getElementsByTagName('indTot')[0].firstChild.data
            data_hora_emissao = domtree.getElementsByTagName('dhEmi')[0].firstChild.data

            cur.execute('''
                insert into estoque(
                id,
                price,
                date,
                qnt,
                entrada)
                values(?,?,?,?,?)
            ''', (name, vProd, data_hora_emissao(), int(indTot), 1)
            )

    xml_saida = [i for i in glob('./saida/*.xml')]
    if xml_saida:
        for file in xml_saida:
            with open(file) as f:
                domtree = parse(f)

            name = domtree.getElementsByTagName('nNF')[0].firstChild.data
            item = domtree.getElementsByTagName('cProd')[0].firstChild.data
            vProd = domtree.getElementsByTagName('vProd')[0].firstChild.data
            indTot = domtree.getElementsByTagName('indTot')[0].firstChild.data
            data_hora_emissao = domtree.getElementsByTagName('dhEmi')[0].firstChild.data

            # saida
            cur.execute('''
                insert into estoque(
                id,
                price,
                date,
                qnt,
                entrada)
                values(?,?,?,?,?)
            ''', (name, vProd, data_hora_emissao, int(indTot), 0)
            )

    cur.close()
    con.commit()
    con.close()
