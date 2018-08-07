import psycopg2
#+++++++++++++++++++++++ MYSQL Syntax FOR CONNECTION +++++++++++++++++
#db = MySQLdb.connect(host="127.0.0.1",user="root",passwd="0000",db="MINDHACKS")
#cur =db.cursor()
#cur.execute("SELECT * FROM USERS")
#rows = cur.fetchall()
#for row in rows:
#	for col in row:
#		print "%s  " % col
#db.close()

def fetchall(sql):   #function that executes a query and returns its output/ read data from table
    sql = str(sql)
    db = MySQLdb.connect(host="127.0.0.1",user="root",passwd="0000",db="TOILO")
    cur =db.cursor()
    cur.execute(sql)
    info = cur.fetchall()
    db.close()
    return info

def fetchone(sql):   #function that executes a query and returns its output/ read data from table
    sql = str(sql)
    conn = psycopg2.connect(database = "d3s7cs38jotj0a", user = "wzlgzdgpdtrmcq", password = "9bb2c0c2e168a8debd55955330e691bac669e332d2c0fb403162c066b2b5a986", host = "ec2-54-217-217-194.eu-west-1.compute.amazonaws.com", port = "5432")
    cur = conn.cursor()
    cur.execute(sql)
    info = cur.fetchone()
    conn.close()
    return info

def inserttodb(sql):    #function to write data to table
    conn = psycopg2.connect(database = "d3s7cs38jotj0a", user = "wzlgzdgpdtrmcq", password = "9bb2c0c2e168a8debd55955330e691bac669e332d2c0fb403162c066b2b5a986", host = "ec2-54-217-217-194.eu-west-1.compute.amazonaws.com", port = "5432")
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()
    return 1
