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
    conn = psycopg2.connect(database = "ddb5e18sfuevd6", user = "yshqknwdqhxmrw", password = "a74c3ed4c7d2f55df2425cc4dae95b35d16b46cdac0f978fd5141d7069823c87", host = "ec2-54-217-235-159.eu-west-1.compute.amazonaws.com", port = "5432")
    cur = conn.cursor()
    cur.execute(sql)
    info = cur.fetchone()
    conn.close()
    return info

def inserttodb(sql):    #function to write data to table
    conn = psycopg2.connect(database = "ddb5e18sfuevd6", user = "yshqknwdqhxmrw", password = "a74c3ed4c7d2f55df2425cc4dae95b35d16b46cdac0f978fd5141d7069823c87", host = "ec2-54-217-235-159.eu-west-1.compute.amazonaws.com", port = "5432")
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()
    return 1
