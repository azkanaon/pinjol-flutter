# conda activate webservicep2plending webservicep2plending
# uvicorn main:app --reload


from typing import Union
from fastapi import FastAPI,Response,Request,HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

# @app.get("/mahasiswa/{nim}")
# def ambil_mhs(nim:str):
#     return {"nama": "Budi Martami"}

# @app.get("/mahasiswa2/")
# def ambil_mhs2(nim:str):
#     return {"nama": "Budi Martami 2"}   

# @app.get("/daftar_mhs/")
# def daftar_mhs(id_prov:str,angkatan:str):
#     return {"query":" idprov: {}  ; angkatan: {} ".format(id_prov,angkatan),"data":[{"nim":"1234"},{"nim":"1235"}]}

# panggil sekali saja
@app.get("/init/")
def init_db():
  try:
    DB_NAME = "user.db"
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    create_table = """ CREATE TABLE user(
            ID      	INTEGER PRIMARY KEY 	AUTOINCREMENT,
            nama            TEXT                NOT NULL,
            nama_umkm       TEXT                NOT NULL,
            email           TEXT                NOT NULL UNIQUE,
            password    	TEXT            	NOT NULL,
	        pin			    TEXT			    NOT NULL,
            no_telp         TEXT                NOT NULL,
            saldo           INT                 NULL
        );

        CREATE TABLE peminjaman(
            ID              INTEGER             NOT NULL,
            jumlah_pinjaman INTEGER             NOT NULL,
            jumlah_tagihan  INTEGER             NOT NULL,
            tagihan_bulanan INTEGER             NOT NULL,
	        tagihan_terbayarkan INTERTGER	    NOT NULL,
            jangka_waktu    TEXT                NOT NULL,
            tenggat_waktu   NUMERIC             NOT NULL,
            perpanjang      INTEGER             NULL,
            cashback        INTEGER             NULL,
            status          TEXT                NOT NULL 
        );
        
        CREATE TABLE promo(
            idpromo         INTEGER PRIMARY KEY     AUTOINCREMENT,
            judulpromo      TEXT                    NOT NULL,
            tenggatpromo    TEXT                    NOT NULL,
            desc            TEXT                    NOT NULL,
            cashback_per    INTEGER                 NULL,
            kodepromo       TEXT                    NOT NULL
        );

        CREATE TABLE artikel(
            idart           INTEGER PRIMARY KEY     AUTOINCREMENT,
            judulart        TEXT                    NOT NULL,
            desc            TEXT                    NOT NULL,
            gambar          TEXT                    NOT NULL
        );

        """
    cur.executescript(create_table)
    con.commit()
  except:
           return ({"status":"terjadi error"})  
  finally:
           con.close()
    
  return ({"status":"ok, db dan tabel berhasil dicreate"})

from typing import Optional

from pydantic import BaseModel

class User(BaseModel):
   nama: str
   nama_umkm: str
   password: str
   pin: str
   email: str
   no_telp: str

class Pnj(BaseModel):
   ID: int
   jumlah_pinjaman: int
   jumlah_tagihan: int
   tagihan_bulanan: int
   tagihan_terbayarkan: int
   jangka_waktu: str
   tenggat_waktu: str
   cashback: int
   
class Prm(BaseModel):
   judulpromo: str
   tenggat: str
   desc: str
   kode: str


#status code 201 standard return creation
#return objek yang baru dicreate (response_model tipenya Mhs)
@app.post("/tambah_user/", response_model=User,status_code=201)  
def tambah_user(m: User,response: Response, request: Request):
   try:
       DB_NAME = "user.db"
       con = sqlite3.connect(DB_NAME)
       cur = con.cursor()
       # hanya untuk test, rawal sql injecttion, gunakan spt SQLAlchemy
       cur.execute("""insert into user (nama,nama_umkm,email,password,pin,no_telp,saldo) values ( "{}","{}","{}","{}","{}","{}",0)""".format(m.nama,m.nama_umkm,m.email,m.password,m.pin,m.no_telp))
       con.commit() 
   except:
       print("oioi error")
       return ({"status":"terjadi error"})   
   finally:  	 
       con.close()
   response.headers["Location"] = "/user/{}".format(m.email) 
   print(m.nama)
   print(m.nama_umkm)
   print(m.email)
   print(m.password)
   print(m.pin)
   print(m.no_telp)
  
   return m

@app.get("/tampilkan_semua_user/")
def tampil_semua_user():
   try:
    DB_NAME = "user.db"
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    recs = []
    for row in cur.execute("select * from user"):
        recs.append(row)
   except:
    return ({"status":"terjadi error"})   
   finally:    
    con.close()
   return {"data":recs}

@app.delete("/delete_user/{ID}")
def delete_user(id: str):
    try:
       DB_NAME = "user.db"
       con = sqlite3.connect(DB_NAME)
       cur = con.cursor()
       sqlstr = "delete from user  where id='{}'".format(id)                 
       print(sqlstr) # debug 
       cur.execute(sqlstr)
       con.commit()
    except:
       return ({"status":"terjadi error"})   
    finally:  	 
       con.close()
    
    return {"status":"ok"}

class UsrPatch(BaseModel):
   umkm: str | None = "kosong"
   email: str | None = "kosong"
   no_telp: str | None = "kosong"

@app.patch("/update_usr_patch/{id}",response_model = UsrPatch)
def update_mhs_patch(response: Response, id: str, m: UsrPatch):
    try:
      print(str(m))
      DB_NAME = "user.db"
      con = sqlite3.connect(DB_NAME)
      cur = con.cursor() 
      cur.execute("SELECT * FROM user WHERE ID = ?", (id,) )  #tambah koma untuk menandakan tupple
      existing_item = cur.fetchone()
    except Exception as e:
      raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e))) # misal database down  
    
    if existing_item:  #data ada, lakukan update
        sqlstr = "UPDATE user SET " #asumsi minimal ada satu field update
        # todo: bisa direfaktor dan dirapikan
        if m.umkm!="kosong":
            if m.umkm!=None:
                sqlstr = sqlstr + " nama_umkm = '{}' ,".format(m.umkm)
            else:     
                sqlstr = sqlstr + " nama_umkm = null ,"
        
        if m.email!="kosong":
            if m.email!=None:
                sqlstr = sqlstr + " email = '{}' ,".format(m.email)
            else:
                sqlstr = sqlstr + " email = null ,"
        
        if m.no_telp!="kosong":
            if m.no_telp!=None:
                sqlstr = sqlstr + " no_telp = '{}' ,".format(m.no_telp) 
            else:
                sqlstr = sqlstr + " no_telp = null, "     

        sqlstr = sqlstr[:-1] + " where ID='{}' ".format(id)  #buang koma yang trakhir  
        print(sqlstr)      
        try:
            cur.execute(sqlstr)
            con.commit()         
            response.headers["location"] = "/user/{}".format(id)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))   
        

    else:  # data tidak ada 404, item not found
         raise HTTPException(status_code=404, detail="Item Not Found")
   
    con.close()
    return m

@app.get("/login_user/")
def login_user(email: str):
   try:
    DB_NAME = "user.db"
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    recs = []
    for row in cur.execute("select * from user where email='{}'".format(email)):
        # maps = {"ID":row[0], "nama":row[1], "nama_umkm":row[3], "email":row[4], "password":row[5], "pin":row[6], "no_Telp":row[7], "saldo":row[8]}
        recs.append(row)
    return recs[0]
   except:
    return ['Salah']   
   finally:    
    con.close()

#---------------------------------------------
# Untuk Update Saldo
class UsrSaldo(BaseModel):
   saldo: Optional[int] | None = -9999

@app.patch("/update_usr_saldo/{id}",response_model = UsrSaldo)
def update_usr_saldo(response: Response, id: str, m: UsrSaldo):
    try:
      #print(str(m))
      DB_NAME = "user.db"
      con = sqlite3.connect(DB_NAME)
      cur = con.cursor() 
      cur.execute("SELECT * FROM user WHERE ID = ?", (id,) )  #tambah koma untuk menandakan tupple
      existing_item = cur.fetchone()
    except Exception as e:
      raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e))) # misal database down  
    
    if existing_item:  #data ada, lakukan update
        sqlstr = "UPDATE user SET " #asumsi minimal ada satu field update
        # todo: bisa direfaktor dan dirapikan
        if m.saldo!= -9999:
            if m.saldo!=None:
                sqlstr = sqlstr + " saldo = saldo + {} ,".format(m.saldo)
            else:     
                sqlstr = sqlstr + " saldo = null ,"


        sqlstr = sqlstr[:-1] + " where ID='{}' ".format(id)  #buang koma yang trakhir  
        print(sqlstr)      
        try:
            cur.execute(sqlstr)
            con.commit()         
            response.headers["location"] = "/user/{}".format(id)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))   
        

    else:  # data tidak ada 404, item not found
         raise HTTPException(status_code=404, detail="Item Not Found")
   
    con.close()
    return m

@app.patch("/update_tarik_saldo/{id}",response_model = UsrSaldo)
def update_tarik_saldo(response: Response, id: str, m: UsrSaldo):
    try:
      #print(str(m))
      DB_NAME = "user.db"
      con = sqlite3.connect(DB_NAME)
      cur = con.cursor() 
      cur.execute("SELECT * FROM user WHERE ID = ?", (id,) )  #tambah koma untuk menandakan tupple
      existing_item = cur.fetchone()
    except Exception as e:
      raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e))) # misal database down  
    
    if existing_item:  #data ada, lakukan update
        sqlstr = "UPDATE user SET " #asumsi minimal ada satu field update
        # todo: bisa direfaktor dan dirapikan
        if m.saldo!= -9999:
            if m.saldo!=None:
                sqlstr = sqlstr + " saldo = saldo - {} ,".format(m.saldo)
            else:     
                sqlstr = sqlstr + " saldo = null ,"


        sqlstr = sqlstr[:-1] + " where ID='{}' ".format(id)  #buang koma yang trakhir  
        print(sqlstr)      
        try:
            cur.execute(sqlstr)
            con.commit()         
            response.headers["location"] = "/user/{}".format(id)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))   
        

    else:  # data tidak ada 404, item not found
         raise HTTPException(status_code=404, detail="Item Not Found")
   
    con.close()
    return m


class updateTagihan(BaseModel):
   tagihan: int

@app.patch("/update_bayar_tagihan/{id}",response_model = UsrSaldo)
def update_tarik_saldo(response: Response, id: int, m: updateTagihan):
    try:
      #print(str(m))
      DB_NAME = "user.db"
      con = sqlite3.connect(DB_NAME)
      cur = con.cursor() 
      cur.execute("SELECT * FROM peminjaman WHERE ID ={} AND status='Diterima'".format(id))  #tambah koma untuk menandakan tupple
      existing_item = cur.fetchone()
    except Exception as e:
      raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e))) # misal database down  
    
    if existing_item:  #data ada, lakukan update
        sqlstr = "UPDATE peminjaman SET " #asumsi minimal ada satu field update
        # todo: bisa direfaktor dan dirapikan
        if m.tagihan!= -9999:
            if m.tagihan!=None:
                sqlstr = sqlstr + " tagihan_terbayarkan = tagihan_terbayarkan + {} ,".format(m.tagihan)
            else:     
                sqlstr = sqlstr + " saldo = null ,"


        sqlstr = sqlstr[:-1] + " WHERE ID ={} AND status='Diterima'".format(id)  #buang koma yang trakhir  
        print(sqlstr)      
        try:
            cur.execute(sqlstr)
            con.commit()         
            response.headers["location"] = "/pinjaman/{}".format(id)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))   
        

    else:  # data tidak ada 404, item not found
         raise HTTPException(status_code=404, detail="Item Not Found")
   
    con.close()
    return m

@app.patch("/lunaskan_peminjaman/{id}",response_model = UsrSaldo)
def update_lunaskan(response: Response, id: int):
    try:
      #print(str(m))
      DB_NAME = "user.db"
      con = sqlite3.connect(DB_NAME)
      cur = con.cursor() 
      cur.execute("SELECT * FROM peminjaman WHERE ID ={} AND status='Diterima'".format(id))  #tambah koma untuk menandakan tupple
      existing_item = cur.fetchone()
    except Exception as e:
      raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e))) # misal database down  
    
    if existing_item:  #data ada, lakukan update
        sqlstr = "UPDATE peminjaman SET status='Lunas' WHERE ID ={} AND status='Diterima'".format(id) #asumsi minimal ada satu field update
        # todo: bisa direfaktor dan dirapikan  
        print(sqlstr)      
        try:
            cur.execute(sqlstr)
            con.commit()         
            response.headers["location"] = "/pinjaman/{}".format(id)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))   
        

    else:  # data tidak ada 404, item not found
         raise HTTPException(status_code=404, detail="Item Not Found")
   
    con.close()
    return m

#----------------------------------------------------------------------
# Untuk Perpanjangan pinjaman

class Perpanjangan(BaseModel):
   perpanjang: Optional[int] | None = -9999

@app.patch("/update_perpanjangan/{id}",response_model = Perpanjangan)
def update_perpanjangan(response: Response, id: str, m: Perpanjangan):
    try:
      #print(str(m))
      DB_NAME = "user.db"
      con = sqlite3.connect(DB_NAME)
      cur = con.cursor() 
      cur.execute("SELECT * FROM peminjaman WHERE ID = ?", (id,) )  #tambah koma untuk menandakan tupple
      existing_item = cur.fetchone()
    except Exception as e:
      raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e))) # misal database down  
    
    if existing_item:  #data ada, lakukan update
        sqlstr = "UPDATE peminjaman SET status='Diperpanjang', " #asumsi minimal ada satu field update
        # todo: bisa direfaktor dan dirapikan
        if m.perpanjang!= -9999:
            if m.perpanjang!=None:
                sqlstr = sqlstr + " perpanjangan = {} ,".format(m.perpanjang)
            else:     
                sqlstr = sqlstr + " perpanjangan = null ,"


        sqlstr = sqlstr[:-1] + " where ID='{}' ".format(id)  #buang koma yang trakhir  
        print(sqlstr)      
        try:
            cur.execute(sqlstr)
            con.commit()         
            response.headers["location"] = "/user/{}".format(id)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))   
        

    else:  # data tidak ada 404, item not found
         raise HTTPException(status_code=404, detail="Item Not Found")
   
    con.close()
    return m

class SetStatus(BaseModel):
    status : str | None = "kosong"

@app.patch("/update_status/{id}",response_model = SetStatus)
def update_status(response: Response, id: str, m: SetStatus):
    try:
      #print(str(m))
      DB_NAME = "user.db"
      con = sqlite3.connect(DB_NAME)
      cur = con.cursor() 
      cur.execute("SELECT * FROM peminjaman WHERE ID = ?", (id,) )  #tambah koma untuk menandakan tupple
      existing_item = cur.fetchone()
    except Exception as e:
      raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e))) # misal database down  
    
    if existing_item:  #data ada, lakukan update
        sqlstr = "UPDATE peminjaman SET " #asumsi minimal ada satu field update
        # todo: bisa direfaktor dan dirapikan
        if m.status!= "kosong":
            if m.status!=None:
                sqlstr = sqlstr + " status = '{}' ,".format(m.status)
            else:     
                sqlstr = sqlstr + " status = null ,"


        sqlstr = sqlstr[:-1] + " where ID='{}' ".format(id)  #buang koma yang trakhir  
        print(sqlstr)      
        try:
            cur.execute(sqlstr)
            con.commit()         
            response.headers["location"] = "/user/{}".format(id)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))   
        

    else:  # data tidak ada 404, item not found
         raise HTTPException(status_code=404, detail="Item Not Found")
   
    con.close()
    return m

@app.get("/history_perpanjangan/{id}")
def history_perpanjangan(id: str):
    try:
        DB_NAME = "user.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT * FROM peminjaman WHERE ID = {} AND perpanjangan NOT NULL".format(id))
        rows = cur.fetchall()

        recs = []
        for row in rows:
            artikel = {
                "id": row[0],
                "jumlah_pinjaman": row[1],
                "jumlah_tagihan": row[2],
                "tagihan_bulanan": row[3],
                "tagihan_terbayarkan": row[4],
                "jangka_waktu": row[5],
                "tenggat_waktu": row[6],
                "cashback": row[7],
                "perpanjangan": row[8],
                "status": row[9]
            }
            recs.append(artikel)
        return {"data": recs}
    except:
        return {"status": "terjadi error"}   
    finally:
        con.close()
# "SELECT * FROM peminjaman WHERE ID = {}".format(id)

@app.get("/history_peminjaman/{id}")
def history_peminjaman(id: str):
    try:
        DB_NAME = "user.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT * FROM peminjaman WHERE ID = {}".format(id))
        rows = cur.fetchall()

        recs = []
        for row in rows:
            artikel = {
                "id": row[0],
                "jumlah_pinjaman": row[1],
                "jumlah_tagihan": row[2],
                "tagihan_bulanan": row[3],
                "tagihan_terbayarkan": row[4],
                "jangka_waktu": row[5],
                "tenggat_waktu": row[6],
                "cashback": row[7],
                "perpanjangan": row[8],
                "status": row[9]
            }
            recs.append(artikel)
        return {"data": recs}
    except:
        return {"status": "terjadi error"}   
    finally:
        con.close()

@app.get("/tampilkan_semua_user/")
def tampil_semua_user():
   try:
    DB_NAME = "user.db"
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    recs = []
    for row in cur.execute("select * from user"):
        recs.append(row)
   except:
    return ({"status":"terjadi error"})   
   finally:    
    con.close()
   return {"data":recs}


#-------------------------------------------------------------------
#/*
#   Promo 
# */
@app.post("/tambah_promo/", response_model=Prm,status_code=201)  
def tambah_promo(m: Prm,response: Response, request: Request):
   try:
       DB_NAME = "user.db"
       con = sqlite3.connect(DB_NAME)
       cur = con.cursor()
       # hanya untuk test, rawal sql injecttion, gunakan spt SQLAlchemy
       cur.execute("""INSERT INTO promo (judulpromo,tenggatpromo,desc,kodepromo) values ( "{}","{}","{}","{}")""".format(m.judulpromo,m.tenggat,m.desc,m.kode))
       con.commit() 
   except:
       print("oioi error")
       return ({"status":"terjadi error"})   
   finally:  	 
       con.close()
   response.headers["Location"] = "/promo/{}".format(m.judulpromo) 
   print(m.judulpromo)
   print(m.tenggat)
   print(m.desc)
   print(m.kode)
  
   return m

@app.get("/potongan_promo/")
def potongan_promo(kode: str):
    try:
        DB_NAME = "user.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT * FROM promo WHERE kodepromo='{}'".format(kode))
        rows = cur.fetchone()

        return {"cashback": rows[4]}
    except:
        return {"cashback": 0}   
    finally:
        con.close()

@app.get("/tampilkan_semua_promo/")
def tampil_semua_promo():
    try:
        DB_NAME = "user.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT * FROM promo")
        rows = cur.fetchall()

        recs = []
        for row in rows:
            promo = {
                "id": str(row[0]),
                "judul": row[1],
                "desc": row[3],
                "kode": row[5]
            }
            recs.append(promo)
        return {"data": recs}
    except:
        return {"status": "terjadi error"}   
    finally:
        con.close()
    

@app.get("/tampilkan_promo_detail/{idpromo}")
def tampil_promo_detail(idpromo: str):
    try:
        DB_NAME = "user.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        
        # Update the SQL query to select a specific promo by ID
        cur.execute("SELECT * FROM promo WHERE idpromo = ?", (idpromo,))
        
        row = cur.fetchone()  # Fetch a single row
        
        if row is None:
            return {"status": "Promo not found"}

        promo = {
            "id": str(row[0]),
            "judul": row[1],
            "tenggat": row[2],
            "desc": row[3],
            "kode": row[5]
        }
        
        return promo
        
    except:
        return {"status": "Terjadi error"}   
    finally:
        con.close()
    

@app.delete("/delete_promo/{ID}")
def delete_promo(id: str):
    try:
       DB_NAME = "user.db"
       con = sqlite3.connect(DB_NAME)
       cur = con.cursor()
       sqlstr = "delete from promo  where idpromo='{}'".format(id)                 
       print(sqlstr) # debug 
       cur.execute(sqlstr)
       con.commit()
    except:
       return ({"status":"terjadi error"})   
    finally:  	 
       con.close()
    
    return {"status":"ok"}


@app.post("/tambah_pinjaman/", response_model=Pnj,status_code=201)  
def tambah_injaman(m: Pnj,response: Response, request: Request):
   try:
       DB_NAME = "user.db"
       con = sqlite3.connect(DB_NAME)
       cur = con.cursor()
       # hanya untuk test, rawal sql injecttion, gunakan spt SQLAlchemy
       cur.execute("""INSERT INTO peminjaman (ID, jumlah_pinjaman, jumlah_tagihan, tagihan_bulanan, tagihan_terbayarkan, jangka_waktu, tenggat_waktu, cashback, status) values ( {},{},{},{},{},"{}","{}",{},"Diajukan")""".format(m.ID, m.jumlah_pinjaman, m.jumlah_tagihan, m.tagihan_bulanan, m.tagihan_terbayarkan, m.jangka_waktu, m.tenggat_waktu, m.cashback))
       con.commit() 
   except:
       print("oioi error")
       return ({"status":"terjadi error"})   
   finally:  	 
       con.close()
   response.headers["Location"] = "/promo/{}".format(m.ID) 
  
   return m

@app.get("/pinjaman_berjalan/")
def pinjaman_berjalan(id: int):
   try:
    DB_NAME = "user.db"
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT * FROM peminjaman WHERE ID={} AND status='Diterima'".format(id))
    
    row = cur.fetchone()
    
        
    pinjaman = {
            "ID": row[0],
            "jumlah_pinjaman": row[1],
            "jumlah_tagihan": row[2],
            "tagihan_bulanan": row[3],
            "tagihan_terbayarkan": row[4],
            "jangka_waktu": str (row[5]),
            "tenggat_waktu": str (row[6]),
            "cashback": row[7],
            "perpanjangan": row[8],
            "status": str (row[9])
        }
    
    return pinjaman
   except:
    pinjaman = {
            "ID": 0,
            "jumlah_pinjaman": 0,
            "jumlah_tagihan": 0,
            "tagihan_bulanan": 0,
            "tagihan_terbayarkan": 0,
            "jangka_waktu": "",
            "tenggat_waktu": "0000-00-00 00:00:00.000",
            "cashback": 0,
            "perpanjangan": 0,
            "status": "Belum Meminjam"
        }
    return pinjaman   
   finally:    
    con.close()
#------------------------------------------------
#Ini Artikel

class Art(BaseModel):
    judulart: str
    desc: str
    gambar: str

@app.post("/tambah_artikel/", response_model=Art,status_code=201)
def tambah_artikel(m: Art,response: Response, request: Request):
    try:
       DB_NAME = "user.db"
       con = sqlite3.connect(DB_NAME)
       cur = con.cursor()
       # hanya untuk test, rawal sql injecttion, gunakan spt SQLAlchemy
       cur.execute("""INSERT INTO artikel (judulart,desc,gambar) values ( "{}","{}","{}")""".format(m.judulart,m.desc,m.gambar))
       con.commit() 
    except:
       print("oioi error")
       return ({"status":"terjadi error"})   
    finally:  	 
       con.close()
    response.headers["Location"] = "/artikel/{}".format(m.judulart) 
    print(m.judulart)
    print(m.desc)
    print(m.gambar)
    return m
  

@app.get("/tampilkan_semua_artikel/")
def tampil_semua_artikel():
    try:
        DB_NAME = "user.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT * FROM artikel")
        rows = cur.fetchall()

        recs = []
        for row in rows:
            artikel = {
                "id": str(row[0]),
                "judul": row[1],
                "desc": row[2],
                "gambar": row[3]
            }
            recs.append(artikel)
        return {"data": recs}
    except:
        return {"status": "terjadi error"}   
    finally:
        con.close()
    


@app.get("/tampilkan_artikel_detail/{idart}")
def tampil_artikel_detail(idart: str):
    try:
        DB_NAME = "user.db"
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        
        # Update the SQL query to select a specific promo by ID
        cur.execute("SELECT * FROM artikel WHERE idart = ?", (idart,))
        
        row = cur.fetchone()  # Fetch a single row
        
        if row is None:
            return {"status": "Promo not found"}

        artikel = {
            "id": str(row[0]),
            "judul": row[1],
            "desc": row[2],
            "gambar": row[3]
        }
        return artikel
        
    except:
        return {"status": "Terjadi error"}   
    finally:
        con.close()
    

