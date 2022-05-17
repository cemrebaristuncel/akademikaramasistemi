from lib2to3.pgen2 import driver
from neo4j import GraphDatabase
from flask import (
    Flask,
    Response,
    render_template,
    request,
    session,
)
from sqlalchemy import true
import csv
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
app = Flask(__name__)



with open("sifre.txt")as file:
 data=csv.reader(file,delimiter=",")
 for row in data:
    id=row[0]
    password=row[1]
 file.close()

driver=GraphDatabase.driver(uri="<YOUR NEO4J URL>",auth=(id,password))
session=driver.session()

yazaridleri = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28]

app.config.update(
    DEBUG = True,
    SECRET_KEY = 'gizli'
)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):

    def __init__(self, id):
        self.id = id
        
    def __repr__(self):
        return "%d" % (self.id)



@app.route('/')
@login_required
def home():
    return render_template("login.html")

 
@app.route("/giris", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
     if request.form["submit"]=="girisyap":
        username = request.form['username']
        password = request.form['password']        
        if password == "tuncel" and username == "baris":
          return render_template("profile.html")
        else:
            return render_template("login.html")
     elif request.form["submit"]=="misafir":
          return render_template("arama.html")                       
    else:
        return render_template("login.html")

      


@app.route("/cikis")
@login_required
def logout():
    logout_user()
    return Response('<p>Başarıyla çıkış yapıldı.</p>')
          
@login_manager.user_loader
def load_user(userid):
    return User(userid)

@app.route("/ekle",methods=["GET","POST"])
def ekle():
    if request.method=="POST":
     yazaridleri = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28]
     flag = 0
     if request.form["submit"]=="submit":
        yazarid = int(request.form["yazarid"])
        yazaradi = request.form["yazaradi"]
        for i in yazaridleri:
            if i == yazarid:
             flag = 1   
             return Response('<p>Bu araştırmacı ID si daha önceden kullanılmış. Lütfen farklı bir ID giriniz.</p>')
            
        if flag == 0: 
         yazaridleri.append(yazarid)
         query = """CREATE (a:Arastirmacilar {yazarid:$yazarid, yazaradi: $yazaradi})
        """
         parameter={"yazarid":yazarid, "yazaradi":yazaradi} 
         session.run(query,parameter)
         return render_template("profile.html")

     elif request.form["submit"]=="submit1":
        yazaradi = request.form["yazaradi"]
        yayinid = request.form["yayinid"]
        yayinadi = request.form["yayinadi"]
        yayinyili = (int)(request.form["yayinyili"])
        query = """CREATE (b:Yayinlar {yazaradi:$yazaradi, yayinid:$yayinid, yayinadi: $yayinadi, yayinyili:$yayinyili})
         WITH b
 	     MATCH (a:Arastirmacilar {yazaradi:$yazaradi}), (b:Yayinlar {yazaradi:$yazaradi})
         MERGE (b)-[:YayınYazarı]->(a)
         WITH a,b
         MATCH (c:Yayinlar {yayinadi:$yayinadi})-[:YayınYazarı]->(d:Arastirmacilar)
         SET d.yayinadi = $yayinadi
         SET d.yayinyili = $yayinyili
         WITH c,d 
         MATCH (c:Arastirmacilar {yayinadi:$yayinadi}),(d:Arastirmacilar {yayinadi:$yayinadi})
         MERGE (c)<-[:OrtakCalisir]->(d)
        """
        parameter={"yazaradi":yazaradi, "yayinid":yayinid, "yayinadi":yayinadi, "yayinyili":yayinyili} 
        session.run(query,parameter)
        return render_template("profile.html")

     elif request.form["submit"]=="submit2":
        yayinid = request.form["yayinid"]
        yayinturu = request.form["yayinturu"]
        yayinyeri = request.form["yayinyeri"]
        query = """MERGE (c:Turler {yayinid:$yayinid,yayinturu: $yayinturu, yayinyeri: $yayinyeri })
        WITH c
        MATCH (a:Arastirmacilar), (b:Yayinlar), (c:Turler)
        WITH a,b,c 
        WHERE b.yayinid = c.yayinid
        SET a.yayinturu = c.yayinturu
        SET a.yayinyeri = c.yayinyeri
        SET b.yayinturu = c.yayinturu
        SET b.yayinyeri = c.yayinyeri
        MERGE (b)-[:Yayınlanır]->(c) 
        """
        parameter={"yayinid":yayinid,"yayinturu":yayinturu, "yayinyeri":yayinyeri}
        session.run(query,parameter)   
        return render_template("profile.html")

       


@app.route("/yazarara",methods=['GET',"POST"])
def yazarara():
    if request.method=="POST":
     if request.form["submit"]=="submit":
         aratilanyazaradi = request.form["aratilanyazaradi"]
         
         query="""MATCH (b:Yayinlar {yazaradi:$aratilanyazaradi})-[:YayınYazarı]->(a:Arastirmacilar {yazaradi:$aratilanyazaradi})
        return b.yayinadi, b.yayinyili
        """

         parameter = {"aratilanyazaradi":aratilanyazaradi}
         results=session.run(query,parameter)
         sonuclar=[]
         
         for result in results:
            dc = {}
            yayinadi=result["b.yayinadi"]
            yayinyili=result["b.yayinyili"]
            dc.update({"Yayın adı":yayinadi,"Yayın Yılı":yayinyili})
            sonuclar.append(dc)     
         return render_template("yazarsonuc.html",sonuclar=sonuclar)

    if request.method=="GET":
         gelen = request.args.get('type')
         query="""MATCH (b:Yayinlar {yazaradi:$gelen})-[:YayınYazarı]->(a:Arastirmacilar {yazaradi:$gelen})
        return b.yayinadi, b.yayinyili
        """

         parameter = {"gelen":gelen}
         results=session.run(query,parameter)
         sonuclar=[]
         
         for result in results:
            dc = {}
            yayinadi=result["b.yayinadi"]
            yayinyili=result["b.yayinyili"]
            dc.update({"Yayın adı":yayinadi,"Yayın Yılı":yayinyili})
            sonuclar.append(dc)     
         return render_template("yazarsonuc.html",sonuclar=sonuclar)     

        
    

@app.route("/yayinara",methods=["GET","POST"])
def yayinara():
    if request.method=="POST":
       
      if request.form["submit"]=="submit":
         aratilanyayinadi = request.form["aratilanyayinadi"]
         
         query="""MATCH (b:Yayinlar {yayinadi:$aratilanyayinadi})-[:YayınYazarı]->(a:Arastirmacilar), (b:Yayinlar {yayinadi:$aratilanyayinadi})-[:Yayınlanır]->(c:Turler)
        return a.yazaradi, c.yayinturu, c.yayinyeri
        """
         parameter = {"aratilanyayinadi":aratilanyayinadi}
         results=session.run(query,parameter)
         sonuclar=[]
         b = ""
         c = ""
         for result in results:
            b = result["c.yayinturu"]
            c = result["c.yayinyeri"]
            dc={}
            yazaradi=result["a.yazaradi"]
            yayinturu = result["c.yayinturu"]
            yayinyeri = result["c.yayinyeri"]
            dc.update({"Yazar adı":yazaradi,"Yayın Türü":yayinturu,"Yayın Yeri":yayinyeri})
            sonuclar.append(dc)

         return render_template("yayinsonuc.html",sonuclar=sonuclar,b=b,c=c)

    if request.method=="GET":
         secilen = request.args.get('type')
         query="""MATCH (b:Yayinlar {yayinadi:$secilen})-[:YayınYazarı]->(a:Arastirmacilar), (b:Yayinlar {yayinadi:$secilen})-[:Yayınlanır]->(c:Turler)
        return a.yazaradi, c.yayinturu, c.yayinyeri
        """
         parameter = {"secilen":secilen}
         results=session.run(query,parameter)
         sonuclar=[]
         b = ""
         c = ""
         for result in results:
            b = result["c.yayinturu"]
            c = result["c.yayinyeri"]
            dc={}
            yazaradi=result["a.yazaradi"]
            yayinturu = result["c.yayinturu"]
            yayinyeri = result["c.yayinyeri"]
            dc.update({"Yazar adı":yazaradi,"Yayın Türü":yayinturu,"Yayın Yeri":yayinyeri})
            sonuclar.append(dc)
            
         return render_template("yayinsonuc.html",sonuclar=sonuclar,b=b,c=c)

            
        


if __name__=='__main__':
    app.run(debug=true)