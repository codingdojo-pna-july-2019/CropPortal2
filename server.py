import re
from flask_bcrypt import Bcrypt        
from flask import Flask, render_template, request, redirect, flash, session
from mysqlconnection import connectToMySQL   
 
app = Flask(__name__)
app.secret_key = "keep it secret"
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

@app.route("/")
def index():
    mysql = connectToMySQL("CropMap")	        
    mysql.query_db("SELECT * FROM `Crop_Portal`.Users;")  
    return render_template ("index.html")

@app.route("/signin", methods=["POST"])
def signin():
    is_valid = True
    if len(request.form['email']) < 1:
        is_valid = False
        flash("please enter your email")
    if len(request.form['password']) <8:
        is_valid = False
        flash("please enter your correct password")
    if not is_valid:
        return redirect("/")
    else:
       mysql = connectToMySQL("CropMap")
       query = "SELECT * from Users WHERE Users.email = %(email)s;"
       data = {
           'email': request.form['email']
       }
    user = mysql.query_db(query,data)
    if user:
        hashed_password = user[0]['password']
        if bcrypt.check_password_hash(hashed_password, request.form['password']):
            session['user_id'] = user[0]['User_id']
            return redirect("/CropPortal")
        else:
            flash("Password is invalid")
            return redirect("/")
    else:
        flash("Please use a valid email address")
        return redirect("/")
    return redirect("/")

@app.route("/createNew")
def route_to_register():
    mysql = connectToMySQL("CropMap")	        
    mysql.query_db("SELECT * FROM `Crop_Portal`.Users;") 
    return render_template ("createNew.html")

@app.route("/register", methods=['POST'])
def register():
    is_valid = True
    if len(request.form["fname"]) < 2:
        is_valid = False
        flash("Please enter a valid first name")
    if len(request.form["lname"]) < 2:
        is_valid = False
        flash("Please enter a valid last name")
    if not EMAIL_REGEX.match(request.form["email"]):    
        is_valid = False
        flash("Invalid email address!")
    if len(request.form["password"]) < 8:
        is_valid = False
        flash("Password should be at least 8 characters")
    if request.form['password'] != request.form['cpassword']:
        is_valid = False
        flash("Passwords need to match")
    if is_valid:
        mysql = connectToMySQL("CropMap")
        pw_hash = bcrypt.generate_password_hash(request.form['password'])  
        query = "INSERT INTO Users(first_name, last_name, email, password, created_at, updated_at) VALUES (%(fn)s, %(ln)s, %(e)s, %(password_hash)s, NOW(), NOW());"
        data = {
            "fn": request.form["fname"],
            "ln": request.form["lname"],
            "e": request.form["email"],
            "password_hash": pw_hash
        }
        user_id = mysql.query_db(query, data)
        session['User_id'] = user_id
        return redirect("/CropPortal")
    else: 
        return redirect("/createNew")

@app.route("/back1")
def back1():
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/CropPortal")
def CropPortal():
    return render_template ("cropMain.html")

@app.route("/YearMap", methods=["POST"])
def YearMap():
    mysql = connectToMySQL("CropMap")
    query =("SELECT * FROM Images WHERE year = %(yr)s")
    data = {
        'yr': request.form["year"]
    }
    image = mysql.query_db(query, data)
    mysql = connectToMySQL("CropMap")
    query =("SELECT * from Harvest JOIN Crops ON Harvest.Crops_Crop_ID = Crops.Crop_ID JOIN Fields ON Harvest.Fields_Field_id = Fields.Field_id WHERE year= %(yr)s")
    data = {
        'yr': request.form["year"]
    }
    year = mysql.query_db(query, data)
    return render_template("year.html", year= year[0], image = image[0])

@app.route("/CropMap", methods=["POST"])
def CropMap():
    print(request.form["crop"])
    mysql = connectToMySQL("CropMap")
    query =("SELECT * from  Crops WHERE crop_name= %(crop)s")
    data = {
        'crop': request.form["crop"]
    }
    crop = mysql.query_db(query, data)
    return render_template("crop.html", crop= crop[0])

@app.route("/addtoDB")
def addtoDB():
    return render_template ("edit.html")

@app.route("/back2")
def back2():
    return redirect("/CropPortal")

@app.route("/addCrop", methods=["POST","GET"])
def addCrop():
    is_valid = True
    if len(request.form['newcrop']) < 1:
        is_valid = False
        flash("please enter a crop")
    if not is_valid:
        return redirect("/addtoDB")
    if is_valid:
        mysql = connectToMySQL("CropMap")
        query = "INSERT INTO Crops(crop_name) VALUES (%(crop)s);"
        data = {
           'crop': request.form["newcrop"] 
        }
        mysql.query_db(query, data)
        return redirect("/addtoDB")

@app.route("/addField", methods=["POST","GET"])
def addField():
    is_valid = True
    if len(request.form['newfield']) < 1:
        is_valid = False
        flash("Please enter a field!")
    if not is_valid:
        return redirect("/addtoDB")
    if is_valid:
        mysql = connectToMySQL("CropMap")
        query = "INSERT INTO Fields(name) VALUES (%(field)s);"
        data = {
           'field': request.form["newfield"] 
        }
        mysql.query_db(query, data)
        return redirect("/addtoDB")

@app.route("/addHarvest", methods=["POST"])
def addHarvest():
    mysql = connectToMySQL("CropMap")
    query = "SELECT Field_id From Fields WHERE name = %(fname)s"
    data = {
        'fname': request.form["fieldname"]
    }
    field = mysql.query_db(query, data)
    
    
    mysql = connectToMySQL("CropMap")
    query = "SELECT Crop_id From Crops WHERE crop_name = %(cname)s"
    data = {
        'cname': request.form["crop"]
    }
    crop = mysql.query_db(query, data)
    
    is_valid = True
    if len(request.form['newYear']) < 1:
        is_valid = False
        flash("Please enter a Year!")
    if not is_valid:
        return redirect("/addtoDB")
    if len(request.form['newYield']) < 1:
        mysql = connectToMySQL("CropMap")
        query = "INSERT INTO Harvest(year, yield, Crops_Crop_id, Fields_Field_id) Values (%(year)s, NULL, %(crop)s, %(field)s)"
        data = {
          'year': request.form["newYear"],
          'crop': crop[0]['Crop_id'],
          'field': field[0]['Field_id']

        }
        mysql.query_db(query, data)
        return redirect("/addtoDB")

    elif len(request.form['newYield']) >= 1:
        mysql = connectToMySQL("CropMap")
        query = "INSERT INTO Harvest(year, yield, Crops_Crop_id, Fields_Field_id) Values (%(year)s, %(yield)s, %(crop)s, %(field)s)"
        data = {
          'year': request.form["newYear"],
          'yield': request.form["newYield"],
          'crop': crop[0]['Crop_id'],
          'field': field[0]['Field_id']
       }
        mysql.query_db(query, data)
        return redirect("/addtoDB")

@app.route("/field/<name>")
def lookatField(name):
    mysql = connectToMySQL("CropMap")
    query = "Select * from Harvest Left Join Fields ON Harvest.Fields_Field_id = Fields.Field_id Join Crops On Harvest.Crops_Crop_id = Crops.Crop_id WHERE name = %(name)s"
    data = {
        'name': name
    }
    fields = mysql.query_db(query, data)
    print(name)
    return render_template("field.html", fields = fields)

if __name__ == "__main__":
    app.run(debug=True)