if __name__ == '__main__':
    import datetime
    import sqlite3
    from xml.dom.minidom import parse
    from glob import glob

    con = sqlite3.Connection('db.db')
    cur = con.cursor()

    # cur.execute('drop table if exists prod')
    # cur.execute(
    #     '''create table if not exists prod(
    #     name text,
    #     price text,
    #     date text,
    #     pred text)''')

    cur.execute('drop table if exists estoque')
    cur.execute('create table')

    xmls = [i for i in glob('./xmls/*.xml')]

    for file in xmls:
        with open(file) as f:
            domtree = parse(f)

        name = domtree.getElementsByTagName('nNF')[0].firstChild.data
        # print(name[0].firstChild.data)

        item = domtree.getElementsByTagName('cProd')[0].firstChild.data
        # print(item[0].firstChild.data)

        vProd = domtree.getElementsByTagName('vProd')[0].firstChild.data
        indTot = domtree.getElementsByTagName('indTot')[0].firstChild.data
        date = datetime.datetime.today()
        print(name)
        print(vProd)
        print(date)

        cur.execute('''
            insert into prod(
            name,
            price,
            date)
            values(?,?,?)
        ''', (name, vProd, str(date))
        )

        cur.close()
        con.commit()
        con.close()
