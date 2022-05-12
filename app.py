#!/usr/bin/python3
# -*- coding: utf-8 -*-
from flask import *
from flaskext.mysql import *
from werkzeug.security import *
import os
import uuid
import logging

app = Flask(__name__)
mysql = MySQL()

handler = logging.FileHandler("./app.log", encoding="UTF-8")
logging.getLogger().setLevel(logging.INFO)
app.logger.addHandler(handler)


app.config["MYSQL_DATABASE_USER"] = "root"
app.config["MYSQL_DATABASE_PASSWORD"] = "link start"
app.config["MYSQL_DATABASE_DB"] = "MyBlog_db"
app.config["MYSQL_DATABASE_LOCALHOST"] = "localhost"

mysql.init_app(app)

app.config["SECRET_KEY"] = "Why would I tell you my secret key?"
app.config["UPLOAD_FOLDER"] = "static/Uploads"


@app.route("/")
def main():
    app.logger.info("ok")
    return render_template("index.html")

@app.route("/showSignUp")
def showSignUp():
    return render_template("signup.html")

@app.route("/signUp", methods = ["POST"])
def signUp():
    try:
        _name = request.form["inputName"]
        _email = request.form["inputEmail"]
        _password = request.form["inputPassword"]
        if _name and _email and _password:
            conn = mysql.connect()
            cursor = conn.cursor()
            _hashed_password = generate_password_hash(_password)
            cursor.callproc("sp_createUser",(_name, _email, _hashed_password))
            data = cursor.fetchall()

            if len(data) == 0:
                conn.commit()
                return render_template("error.html", error = "用户创建成功！")
            else:
                return render_template("error.html", error = str(data[0]))
        else:
            return render_template("error.html", error = "输入必需的信息")
    except Exception as e:
        return render_template("error.html", error = str(e))
    finally:
        cursor.close()
        conn.close()

@app.route("/showSignIn")
def showSignIn():
    if (session.get("user")): return redirect("/")
    else: return render_template("signin.html")

@app.route("/validateLogin", methods=["post"])
def validateLogin():
    try:
        _username = request.form["inputEmail"]
        _password = request.form["inputPassword"]
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc("sp_validateLogin", (_username,))
        data = cursor.fetchall()
        if len(data) > 0:
            if check_password_hash(str(data[0][3]), _password):
                session["user"] = data[0][0]
                session["username"] = data[0][1]
                return redirect("/userHome")
            else:
                return render_template("error.html", error = "错误的邮箱或密码")
        else:
            return render_template("error.html", error = "错误的邮箱或密码")
    except Exception as e:
        return render_template("error.html", error = str(e))
    finally:
        cursor.close()
        con.close()

@app.route("/userHome")
def userHome():
    if (session.get("user")): return render_template("userHome.html")
    else: return render_template("/showSignIn")

@app.route("/logout")
def logout():
    session.pop('user', None)
    session.pop("user_name", None)
    return redirect('/')

@app.route("/showAddBlog")
def showAddBlog():
    return render_template("addBlog.html")

@app.route("/addBlog", methods=["POST"])
def addBlog():
    if session.get("user"):
        _title = request.form["inputTitle"]
        _description = request.form["inputDescription"]
        _user = session.get("user")
        if request.form.get("filePath") is None:
            _filePath = ""
        else:
            _filePath = request.form.get("filePath")
        if request.form.get("private") is None:
            _private = 0
        else:
            _private = 1

        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc("sp_addBlog", (_title, _description, _user, _filePath, _private))
        data = cursor.fetchall()
        if len(data) == 0:
            con.commit()
            return redirect("/userHome")
        else:
            return render_template("error.html", error = "发生错误!")
        cursor.close()
        con.close()
    else:
        return redirect("/showSignIn")
    

@app.route("/getBlog")
def getBlog():
    try:
        if session.get("user"):
            _user = session.get("user")

            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc("sp_GetBlogByUser", (_user,))

            blogs = cursor.fetchall()

            blogs_dict = []
            for blog in blogs:
                blog_dict = {
                    "Id": blog[0],
                    "Title": blog[1],
                    "Description": blog[2],
                    "Date": blog[4],
                    "filePath": blog[5],
                    "IdPath": "/passage/" + str(blog[0]) + "/"
                }
                blogs_dict.append(blog_dict)
            cursor.close()
            con.close()
            return json.dumps(blogs_dict)
        else:
            return redirect("/showSignIn")
    except Exception as e:
        return render_template("error.html", error = str(e))

@app.route("/getHomeBlog")
def getHomeBlog():
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc("sp_GetHomeBlog", ())
        blogs = cursor.fetchall()
        blogs_dict = []
        for blog in blogs:
            blog_dict = {
                "Id": blog[0],
                "Title": blog[1],
                "Description": blog[2],
                "Date": blog[4],
                "filePath": blog[5],
                "IdPath": "/passage/" + str(blog[0]) +"/"
            }
            blogs_dict.append(blog_dict)
        cursor.close()
        con.close()
        return json.dumps(blogs_dict)
    except Exception as e:
        return render_template("error.html", error = str(e))
    
@app.route("/getBlogById", methods=["POST"])
def get_BlogById():
    try:
        if session.get("user"):
            _id = request.form["id"]
            _user = session.get("user")
            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc("sp_GetBlogById", (_id,))

            result = cursor.fetchall()

            blog = []
            blog.append({"Id":result[0][0], "Title":result[0][1], "Description":result[0][2], "FilePath":result[0][3],"Private":result[0][4]})
            return json.dumps(blog)
        else:
            return render_template("error.html", error = "Unauthorized Access")
    except Exception as e:
        return render_template("error.html", error = str(e))    
        
@app.route("/updateBlog", methods=["POST"])
def updateBlog():
    try:
        if session.get("user"):
            _user = session.get("user")
            _title = request.form["title"]
            _description = request.form["description"]
            _blog_id = request.form["id"]
            _file_path = request.form["filepath"]
            if request.form["private_"] == "true":
                _private = 1
            else:
                _private = 0

            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc("sp_updateBlog", (_title, _description, _blog_id, _user,  _file_path, _private))
            data = cursor.fetchall()
            if len(data) == 0:
                con.commit()
                return json.dumps("ok")
            else:
                return render_template("error.html", error = "Unauthorized Access")
    except Exception as e:
        return render_template("error.html", error = str(e))    

@app.route("/deleteBlog", methods=["POST"])
def deleteBlog():
    try:
        if session.get("user"):
            _id = request.form["id"]
            _user = session.get("user")

            con = mysql.connect()
            cursor = con.cursor()
            cursor.callproc("sp_deleteBlog", (_id, _user))
            result = cursor.fetchall()
            if len(result) == 0:
                con.commit()
                return json.dumps({"status":"OK"})
            else:
                return json.dumps({"status":"An Error occured"})
    except Exception as e:
        return json.dumps(str(e))
    finally:
        cursor.close()
        con.close()

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    extension = os.path.splitext(file.filename)[1]
    f_name = str(uuid.uuid4()) + extension

    file.save(os.path.join(app.config["UPLOAD_FOLDER"], f_name))
    return json.dumps({"filename": f_name})

@app.route("/passage/<int:_id>/", methods=["GET"])
def passage(_id):
    try:
        con = mysql.connect()
        cursor = con.cursor()
        cursor.callproc("sp_GetBlogById", (_id,))
        result = cursor.fetchall()
        return render_template("passage.html", Title=result[0][1], Description=result[0][2])
    except Exception as e:
        return render_template("error.html", error = str(e))
    
if  __name__ == "__main__":
    app.run(debug = True)
