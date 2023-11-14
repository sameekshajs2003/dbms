from flask import Flask, json,redirect,render_template,flash,request
from flask.globals import request, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
import mysql.connector
from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user

# from flask_mail import Mail
import json


app = Flask(__name__)
app.secret_key = "dbmsnew"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/covid'
db = SQLAlchemy(app)

# Login Manager Configuration
login_manager = LoginManager(app)
login_manager.login_view = 'login'






@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) or Hospitaluser.query.get(int(user_id))


class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(20),unique=True)
    email=db.Column(db.String(50))
    dob_pass=db.Column(db.String(1000))


class Hospitaluser(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20))
    email=db.Column(db.String(50))
    password=db.Column(db.String(1000))


class Hospitaldata(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20),unique=True)
    hname=db.Column(db.String(200))
    normalbed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)

class Status(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20))
    normalbed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)
    querys=db.Column(db.String(50))
    date=db.Column(db.String(50))

class Bookingpatient(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(20),unique=True)
    bedtype=db.Column(db.String(100))
    hcode=db.Column(db.String(20))
    spo2=db.Column(db.Integer)
    pname=db.Column(db.String(100))
    pphone=db.Column(db.String(20))
    paddress=db.Column(db.String(100))
    dob=db.Column(db.String(1000))





@app.route("/")
def home():
   
    return render_template("index.html")

@app.route("/trigers")
def trigers():
    query=Status.query.all() 
    return render_template("trigers.html",query=query)



@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        srfid = request.form.get('srf')
        email = request.form.get('email')
        dob_pass = request.form.get('dob_pass')
        encpassword = generate_password_hash(dob_pass)
        user = User.query.filter_by(srfid=srfid).first()
        emailUser = User.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email or srfid is already taken", "warning")
            return render_template("usersignup.html")

        # Create a connection to the database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='covid'
        )

        cursor = connection.cursor()

     
        query = "INSERT INTO `user` (`srfid`, `email`, `dob_pass`) VALUES (%s, %s, %s)"
        values = (srfid, email, encpassword)

        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()

        flash("SignUp Success! Please Login", "success")
        return render_template("userlogin.html")

    return render_template("usersignup.html")


@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        srfid=request.form.get('srf')
        dob_pass=request.form.get('dob_pass')
        user=User.query.filter_by(srfid=srfid).first()
        if user and check_password_hash(user.dob_pass,dob_pass):
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("userlogin.html")


    return render_template("userlogin.html")

@app.route('/hospitallogin',methods=['POST','GET'])
def hospitallogin():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=Hospitaluser.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("hospitallogin.html")


    return render_template("hospitallogin.html")

@app.route('/admin',methods=['POST','GET'])
def admin():
 
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        if(username=="admin" and password=="admin"):
            session['user']=username
            flash("login success","info")
            return render_template("addHosUser.html")
        else:
            flash("Invalid Credentials","danger")

    return render_template("admin.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))

@app.route('/addHospitalUser', methods=['POST', 'GET'])
def hospitalUser():
    if 'user' in session and session['user'] == "admin":
        if request.method == "POST":
            hcode = request.form.get('hcode')
            email = request.form.get('email')
            password = request.form.get('password')
            encpassword = generate_password_hash(password)
            hcode = hcode.upper()

            # Call the stored procedure to check if 'hcode' exists
            connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='covid'
            )
            cursor = connection.cursor()

            try:
                result = cursor.callproc('CheckHCodeExistence', (hcode, 0))
                is_hcode_exists = result[1]

                if is_hcode_exists == 1:
                    flash("Hospital Code already exists.", "danger")
                else:
                    query = "INSERT INTO `hospitaluser` (`hcode`, `email`, `password`) VALUES (%s, %s, %s)"
                    values = (hcode, email, encpassword)
                    cursor.execute(query, values)
                    connection.commit()
                    flash("Data Sent and Inserted Successfully", "warning")
            except Exception as e:
                flash("An error occurred. This hospital code already exists.", "danger")

            cursor.close()
            connection.close()
        return render_template('addHosUser.html')
    else:
        flash("Login and try again", "warning")
        return render_template("addHosUser.html")

    


# testing wheather db is connected or not  
@app.route("/test")
def test():
    try:
        a=admin.query.all()
        print(a)
        return f'MY DATABASE IS CONNECTED'
    except Exception as e:
        print(e)
        return f'MY DATABASE IS NOT CONNECTED {e}'

@app.route("/logoutadmin")
def logoutadmin():
    session.pop('user')
    flash("You are logout admin", "primary")

    return redirect('/admin')
@app.route("/returns")
def returns():
    pass
    return render_template("addHosUser.html")
@app.route("/returned")
def returned():
    pass
    return render_template("index.html")

def updatess(code):
    postsdata=Hospitaldata.query.filter_by(hcode=code).first()
    return render_template("hospitaldata.html",postsdata=postsdata)

@app.route("/addhospitalinfo",methods=['POST','GET'])
def addhospitalinfo():
    email=current_user.email
    posts=Hospitaluser.query.filter_by(email=email).first()
    code=posts.hcode
    postsdata=Hospitaldata.query.filter_by(hcode=code).first()
    if request.method=="POST":
        hcode=request.form.get('hcode')
        hname=request.form.get('hname')
        nbed=request.form.get('normalbed')
        ibed=request.form.get('icubeds')
        vbed=request.form.get('ventbeds')
        hcode=hcode.upper()
        huser=Hospitaluser.query.filter_by(hcode=hcode).first()
        hduser=Hospitaldata.query.filter_by(hcode=hcode).first()
        if hduser:
            flash("Data is already Present you can update it..","primary")
            return render_template(".html")
        if huser:            
           connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='covid'
            )
           cursor = connection.cursor()
           
           query = "INSERT INTO `hospitaldata` (`hcode`, `hname`, `normalbed`, `icubed`, `vbed`) VALUES (%s, %s, %s, %s, %s)"
           values = (hcode, hname, nbed, ibed, vbed)

           cursor.execute(query, values)
           
           connection.commit()

           cursor.close()
           connection.close()

           flash("Data is added", "primary")
           return redirect('/addhospitalinfo')           
            

        else:
            flash("Hospital Code not Exist","warning")
            return redirect('/addhospitalinfo')




    return render_template("hospitaldata.html",postsdata=postsdata)

from flask import render_template, flash, redirect

# Import any other necessary modules here
@app.route("/showhospitalusertable")
def showhospitalusertable():
        connection = mysql.connector.connect(
            host='localhost',
                user='root',
                password='',
                database='covid'
        )
        cursor = connection.cursor()
        # Call the stored procedure to get table data
        cursor.callproc("SelectHospitalUserData")
        # Fetch the result from the stored function
        result = cursor.stored_results()
        data = []
        
        for res in result:
            data.extend(res.fetchall())
        cursor.close()
        connection.close()
        return render_template("showhosuserdata.html", data=data)

@app.route("/showsevere")
def showsevere():
        connection = mysql.connector.connect(
            host='localhost',
                user='root',
                password='',
                database='covid'
        )
        cursor = connection.cursor()
        # Call the stored procedure to get table data
        cursor.callproc("GetSeverePatients")
        # Fetch the result from the stored function
        result = cursor.stored_results()
        data = []
        
        for res in result:
            data.extend(res.fetchall())
        cursor.close()
        connection.close()
        return render_template("showsevere.html", data=data)

@app.route("/showhospitaldatatable")
def showhospitaldatatable():
        connection = mysql.connector.connect(
            host='localhost',
                user='root',
                password='',
                database='covid'
        )
        cursor = connection.cursor()
        # Call the stored procedure to get table data
    
        cursor.callproc("DisplayHospitalDataWithTotalBeds")
        # Fetch the result from the stored function
        result = cursor.stored_results()
        data = []
        
        for res in result:
            data.extend(res.fetchall())
        cursor.close()
        connection.close()
        return render_template("showhosdata.html", data=data)

@app.route("/hosdata")
def hosdata():
        connection = mysql.connector.connect(
            host='localhost',
                user='root',
                password='',
                database='covid'
        )
        cursor = connection.cursor()
        # Call the stored procedure to get table data
        cursor.callproc("ViewHospitalData")
        # Fetch the result from the stored function
        result = cursor.stored_results()
        data = []
        for res in result:
            data.extend(res.fetchall())
        cursor.close()
        connection.close()
        return render_template("showhosdatahos.html", data=data)

@app.route("/showuserpatienttable")
def showuserpatienttable():
        connection = mysql.connector.connect(
            host='localhost',
                user='root',
                password='',
                database='covid'
        )
        cursor = connection.cursor()
        # Call the stored procedure to get table data
        cursor.callproc("DisplayUsersNotInBookingPatient")
        # Fetch the result from the stored function
        result = cursor.stored_results()
        data = []
        
        for res in result:
            data.extend(res.fetchall())
        cursor.close()
        connection.close()
        return render_template("showuserpatient.html", data=data)

@app.route("/showpatienttable")
def showpatienttable():
        connection = mysql.connector.connect(
            host='localhost',
                user='root',
                password='',
                database='covid'
        )
        cursor = connection.cursor()
        # Call the stored procedure to get table data
        cursor.callproc("GetAllBookingPatients")
        # Fetch the result from the stored function
        result = cursor.stored_results()
        data = []
        
        for res in result:
            data.extend(res.fetchall())
        cursor.close()
        connection.close()
        return render_template("showpatient.html", data=data)

@app.route("/hedit/<string:id>",methods=['POST','GET'])
@login_required
def hedit(id):
    posts=Hospitaldata.query.filter_by(id=id).first()
  
    if request.method=="POST":
        hcode=request.form.get('hcode')
        hname=request.form.get('hname')
        nbed=request.form.get('normalbed')
        ibed=request.form.get('icubeds')
        vbed=request.form.get('ventbeds')
        hcode=hcode.upper()
        connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='covid'
            )
        cursor = connection.cursor()

        query = "UPDATE `hospitaldata` SET `hcode` = %s, `hname` = %s, `normalbed` = %s, `icubed` = %s, `vbed` = %s WHERE `id` = %s"
        values = (hcode, hname, nbed, ibed, vbed, id)

        cursor.execute(query, values)
        connection.commit()

        cursor.close()
        connection.close()
        flash("Slot Updated","info")
        return redirect("/addhospitalinfo")

    # posts=Hospitaldata.query.filter_by(id=id).first()
    return render_template("hedit.html",posts=posts)


@app.route("/hdelete/<string:id>",methods=['POST','GET'])
@login_required
def hdelete(id):
    connection = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='covid'
            )
    cursor = connection.cursor()

    query = "DELETE FROM `hospitaldata` WHERE `id` = %s"
    values = (id,)

    cursor.execute(query, values)
    connection.commit()

    cursor.close()
    connection.close()
    flash("Data Deleted","danger")
    return redirect("/addhospitalinfo")


@app.route("/pdetails",methods=['GET'])
@login_required
def pdetails():
    code=current_user.srfid
    print(code)
    data=Bookingpatient.query.filter_by(srfid=code).first()
    return render_template("detials.html",data=data)

@app.route("/slotbooking",methods=['POST','GET'])
@login_required
def slotbooking():
    query1=Hospitaldata.query.all()
    query=Hospitaldata.query.all()
    if request.method=="POST":
        
        srfid=request.form.get('srfid')
        bedtype=request.form.get('bedtype')
        hcode=request.form.get('hcode')
        spo2=request.form.get('spo2')
        pname=request.form.get('pname')
        pphone=request.form.get('pphone')
        paddress=request.form.get('paddress') 
        dob= request.form.get('dob') 
        check2=Hospitaldata.query.filter_by(hcode=hcode).first()
        checkpatient=Bookingpatient.query.filter_by(srfid=srfid).first()
        if checkpatient:
            flash("already srd id is registered ","warning")
            return render_template("booking.html",query=query,query1=query1)
        
        if not check2:
            flash("Hospital Code not exist","warning")
            return render_template("booking.html",query=query,query1=query1)

        code=hcode
        # dbb=db.engine.execute(f"SELECT * FROM `hospitaldata` WHERE `hospitaldata`.`hcode`='{code}' ")  
        dbb=Hospitaldata.query.filter_by(hcode=hcode).first()      
        bedtype=bedtype
        if bedtype == "NormalBed":
         seat = dbb.normalbed
         ar = Hospitaldata.query.filter_by(hcode=code).first()
         ar.normalbed = seat - 1
         db.session.commit()
                
            

        elif bedtype == "ICUBed":
          seat = dbb.icubed
          ar = Hospitaldata.query.filter_by(hcode=code).first()
          ar.icubed = seat - 1
          db.session.commit()

        elif bedtype=="VENTILATORBed":
            seat=dbb.vbed
            ar=Hospitaldata.query.filter_by(hcode=code).first()
            ar.vbed=seat-1
            db.session.commit()
        else:
            pass

        check=Hospitaldata.query.filter_by(hcode=hcode).first()
        if check!=None:
            if(seat>0 and check):
                res=Bookingpatient(srfid=srfid,bedtype=bedtype,hcode=hcode,spo2=spo2,pname=pname,pphone=pphone,paddress=paddress,dob=dob)
                db.session.add(res)
                db.session.commit()
                flash("Slot is Booked kindly Visit Hospital for Further Procedure","success")
                return render_template("booking.html",query=query,query1=query1)
            else:
                flash("Something Went Wrong","danger")
                return render_template("booking.html",query=query,query1=query1)
        else:
            flash("Give the proper hospital Code","info")
            return render_template("booking.html",query=query,query1=query1)
            
    
    return render_template("booking.html",query=query,query1=query1)




app.run(debug=True)