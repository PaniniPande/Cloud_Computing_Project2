from math import radians,sin,cos,asin,sqrt
from datetime import date, datetime, timedelta
from flask import Flask, render_template, request
import pyodbc
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Panini'

Panini_driver = '{ODBC Driver 18 for SQL Server}'
Panini_database = 'ADB'
Panini_server = 'tcp:adbassignments15.database.windows.net,1433'
Panini_username = "pxp4144"
Panini_password = "Paridhi@15"
Panini_conn= pyodbc.connect('DRIVER='+Panini_driver+';SERVER='+Panini_server+';DATABASE='+Panini_database+';UID='+Panini_username+';PWD='+ Panini_password)
Panini_cursor = Panini_conn.cursor() 

# with pyodbc.connect(
#         'DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password) as conn:
#     with conn.cursor() as cursor:
#         temp = []
#         cursor.execute("SELECT TOP 3 time, id FROM data")
#         while True:
#             r = cursor.fetchone()
#             if not r:
#                 break
#             print(str(r[0]) + " " + str(r[1]))
#             temp.append(r)


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template('index.html')


class MyForm1(FlaskForm):
    mag = StringField(label='Enter Magnitude: ', validators=[DataRequired()])
    submit = SubmitField(label='Submit')


@app.route('/mag', methods=['GET', 'POST']) 
def mag():
    form = MyForm1()
    cnt = 0
    if form.validate_on_submit():
        try:
            mag = float(form.mag.data)
            if mag <= 5.0:
                return render_template('ShowMag.html', form=form, error="value must be > 5.0", temp=1)
            Panini_cursor.execute("SELECT * FROM data where mag > ?", mag)
            output = []
            while True:
                row = Panini_cursor.fetchone()
                if not row:
                    break
                output.append(row)
                cnt += 1
            return render_template('ShowMag.html', output=output, cnt=cnt, temp=0)
        except ValueError:
            return render_template('ShowMag.html', form=form, error="value must be numeric.", temp=1)
    return render_template('ShowMag.html', form=form, temp=1)

def distance(lat1, lat2, lon1, lon2):
    	# The math module contains a function named
	# radians which converts from degrees to radians.
	lon1 = radians(lon1)
	lon2 = radians(lon2)
	lat1 = radians(lat1)
	lat2 = radians(lat2)
	# Haversine formula
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
	c = 2 * asin(sqrt(a))
	# Radius of earth in kilometers. Use 3956 for miles
	r = 6371
	# calculate the result
	return(c * r)

@app.route('/Task3',methods=['POST','GET'])
def lsearch():
    if request.method =='POST':
        lat1=request.form['lat1']
        lon1=request.form['lon1']
        km=request.form['kms']
        querry="Select id,time,latitude,longitude,mag,place from data"
        Panini_cursor.execute(querry)
        lat1=float(lat1)
        lon1=float(lon1)
        km=float(km)
        rows = Panini_cursor.fetchall()
        bkm=[]
        for i in rows:
            x=distance(lat1,float(i[2]),lon1,float(i[3]))
            if x<=km:
                bkm.append(i)
        return render_template("Task3.html",rows = bkm)
    else:
        return render_template('Task3.html')    

@app.route('/Task2', methods = ['GET','POST'])
def Task2():
    if request.method =='POST':
        Range1 = str(request.form['Range1'])
        Range2 = str(request.form['Range2'])
        Fromdate = request.form['Fromdate']
        Todate = request.form['Todate']
        query = "SELECT * FROM data where (mag BETWEEN '"+Range1+"' and '"+Range2+"') and (CAST(time as date) BETWEEN CAST('"+Fromdate+"' as date) and CAST('"+Todate+"' as date)) "
        Panini_cursor.execute(query)
        results = Panini_cursor.fetchall()
        return render_template("Task2.html", length = len(results), rows = results)
    else:
        return render_template("Task2.html")


@app.route("/Task4", methods=['GET', 'POST'])
def Task4():
    count =0
    query=("SELECT mag,COUNT(*) FROM data  group by mag")
    Panini_cursor.execute(query)
    result=Panini_cursor.fetchall()
    return render_template("Task4.html",msg="completed", rows=result)

@app.route('/nightdata',methods=['POST','GET'])
def nightdata():
    count=0
    time1 = "06:00:00.0000000 +00:00"
    time2 = "18:00:00.0000000 +00:00"
    query = "SELECT place, CAST(time as time) FROM data where mag > 4.0 and (CAST(time as time) not BETWEEN CAST('"+time1+"' as time) and CAST('"+time2+"' as time)) "
    Panini_cursor.execute(query)
    result = Panini_cursor.fetchall()
    count1 = len(result)
    query1 = "SELECT place, CAST(time as time) FROM data where mag > 4.0"
    Panini_cursor.execute(query1)
    result1 = Panini_cursor.fetchall()
    count2 = len(result1)

    if(count1>(count2-count1)):
        display="Earthqakes occur more at night(6pm to 6am) than in the day,out of "+str(count2)+" earth quakes "+str(count1)+" occured in the night"
    else:
        display="Earthqakes occur more at day(6am to 6pm) than in the night,out of "+str(count2)+" earth quakes "+str(count2-count1)+" occured in the day time"
    return render_template("newrecord.html",display = display)      


@app.route('/add_record')
def addrecord():
    return render_template('add_record.html')

@app.route('/add_record', methods=['POST','GET'])
def add_new():
    if (request.method=='POST'):

        city = str(request.form['city'])
        state = str(request.form['state'])
        population = str(request.form['population'])
        lat = str(request.form['lat'])
        lon = str(request.form['lon'])
        # Place = str(request.form['Place'])
        #pic= str(request.form['pic'])
        #notes= str(request.form['notes'])
        query = "Insert INTO data Values('" +city+ "','" +state+ "','" +population+ "','" +lat+ "','" +lon+ "')"
        Panini_cursor.execute(query)
        Panini_conn.commit()
        query2 ="SELECT * FROM data"
        Panini_cursor.execute(query2)
        
        rows = Panini_cursor.fetchall()
                
    return render_template("list.html",rows = rows)


@app.route('/delete_record')
def delete_record():
   return render_template('delete_record.html')

@app.route('/delete_record', methods=['GET', 'POST'])
def deleterecord():
    if (request.method=='POST'):
        
        city= str(request.form['city'])
        state = str(request.form['state'])
        query="DELETE FROM data WHERE city ='"+city+"' and state ='"+state+"'"
        Panini_cursor.execute(query)
        Panini_conn.commit()
        query2="Select * from data "
        Panini_cursor.execute(query2)
        rows = Panini_cursor.fetchall()
        
    return render_template("list.html",rows = rows)

@app.route('/update_record')
def updaterecord():
    return render_template('update_record.html')

@app.route('/update_record', methods=['POST','GET'])
def update_new():
    if (request.method=='POST'):

        city = str(request.form['city'])
        state = str(request.form['state'])
        population = str(request.form['population'])
        lat = str(request.form['lat'])
        lon = str(request.form['lon'])
        querry="UPDATE data SET state = '"+state+"', population = '"+population+"',  lat = '"+lat+"', lon = '"+lon+"'   WHERE city ='"+city+"' "
        
        Panini_cursor.execute(querry)
        Panini_conn.commit()
        query2 ="SELECT * FROM data"
        Panini_cursor.execute(query2)
        
        rows = Panini_cursor.fetchall()
                
    return render_template("list.html",rows = rows)

@app.route('/all', methods=['POST','GET'])
def full_list():
    
    querry="Select * from data"
    Panini_cursor.execute(querry)
    rows = Panini_cursor.fetchall()
    
    return render_template("list.html",rows = rows)


@app.route('/FindPerson')
def FindPerson():
   return render_template('FindPerson.html') 

@app.route('/FindPerson_deets', methods=['POST','GET'])
def Details():
    if(request.method=='POST'):
     Panini_field=str(request.form['place'])
     Panini_query="Select * from data WHERE place like'%"+Panini_field+"%' "
     Panini_cursor.execute(Panini_query)
     rows = Panini_cursor.fetchall()
    return render_template("list.html",rows = rows)








if __name__ == '__main__':
    app.run(debug=True)
