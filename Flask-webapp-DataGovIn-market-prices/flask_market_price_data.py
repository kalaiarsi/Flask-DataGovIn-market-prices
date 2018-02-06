from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import xml.etree.ElementTree as et
import datetime
import os
import download_market_price_catalog
import logging		

logging.basicConfig(filename="catalog_download.log", level=logging.INFO, filemode="a")
URL_PREFIX="https://data.gov.in/catalog/variety-wise-daily-market-prices-data-"
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crops.sqlite3'
app.config['SECRET_KEY'] = "secretLol"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class crops(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    cropname=db.Column(db.String(100))
    state = db.Column(db.String(200)) 
    district = db.Column(db.String(10))
    market = db.Column(db.String(200)) 
    commodity = db.Column(db.String(10))
    variety = db.Column(db.String(200))
    arrivaldate = db.Column(db.Date)
    minprice = db.Column(db.Integer) 
    maxprice = db.Column(db.Integer)
    modalprice = db.Column(db.Integer) 
"""
def __init__(self, variety):
    self.variety = variety
"""

#db.session.add(model object) − inserts a record into mapped table
#db.session.delete(model object) − deletes record from table
#model.query.all() − retrieves all records from table (corresponding to SELECT query).	ex:Students.query.filter_by(city = ’Hyderabad’).all()
#http://localhost:5000

@app.route('/')
def show_all():
    return render_template('show_all_crops.html', crops = crops.query.limit(10) )#crops.query.all() 

#https://data.gov.in/catalog/variety-wise-daily-market-prices-data-cowpeaveg

def push_to_db(tables,cropname,filename):
	for table in tables:
		st,dist,mkt,com,var,arr,minp,maxp,modp=table.getchildren()
		#  for subtag in table.getchildren():
		#     print(subtag.text,end="\t")
		crop = crops(cropname=cropname,state=st.text,district=dist.text,market=mkt.text,commodity=com.text,
					variety=var.text,arrivaldate=datetime.datetime.strptime(arr.text,"%d/%m/%Y"), minprice=minp.text,maxprice=maxp.text,modalprice=modp.text)
		db.session.add(crop)
	print("file read:",filename,"\tcommitting DB",len(tables))
	db.session.commit()
	flash("file read: and committing DB\n")

#https://data.gov.in/catalog/variety-wise-daily-market-prices-data-cowpea-lobiaasparagus
def read_xml(catalogname):
	cropname=catalogname.split("data-")[-1]
	download_folder=os.path.join(os.getcwd(),catalogname.split('/')[-1])
	logging.info("in read_xml func")
	if os.path.exists(download_folder):
		logging.info("Found download folder")
	else:
		logging.error("Download folder missing")
		print("Cannot find download folder")
		return
	for files in os.walk(download_folder):
		for filename in files[2]:
			logging.info("reading file :%s"%filename)
			tree=et.parse(os.path.join(download_folder,filename))
			root=tree.getroot()
			try:
				tables=root.getchildren()[0].getchildren()[0].getchildren()[0].getchildren()[1].getchildren()[0].getchildren()
				logging.info("push to db")
				push_to_db(tables,cropname,filename)
			except Exception as err:
				logging.error("FILE has no DATA%s"%err)
	logging.info("finished loading data from files onto DB")
	return

@app.route('/new', methods = ['GET', 'POST'])
def new():
    if request.method == 'POST':
       if not request.form['cropname']:
           flash('Please enter all the fields', 'error')
       else:
           logging.info("cropname:%s"%request.form['cropname'])
           catalogname=URL_PREFIX+request.form['cropname']
           print("catalogname:",catalogname)
           download_market_price_catalog.download_catalog(catalogname,"xml")
           read_xml(catalogname)
           return redirect(url_for('show_all'))
    return render_template('newcrop.html')



if __name__ == '__main__':
    db.create_all()
    logging.info("Tables created in DB")
#    extract_data_from_xml()
    app.run(debug = True)




