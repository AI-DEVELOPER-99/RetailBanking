from application import app
from flask import render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from passlib.hash import sha256_crypt
from functools import wraps
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Database.db'
db = SQLAlchemy(app)

# Table for customer executive account
class ExecutiveAccount(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100),nullable=False)
    password = db.Column(db.String(20),nullable=False)
    timestamp = db.Column(db.DateTime,nullable=False,default = datetime.utcnow)

    def __repr__(self): 
        return 'Executive : ' + str(self.id)

class ExecutiveLoggedIn(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100),nullable=False)
    login_timestamp = db.Column(db.DateTime,nullable=False,default = datetime.utcnow)

    def __repr__(self):
        return 'Username :' + str(self.username) 


class CustomerAccount(db.Model):
    custid = db.Column(db.Integer, primary_key = True) 
    ssnid = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100),nullable=False)
    age = db.Column(db.Integer,nullable=False)
    address = db.Column(db.Text,nullable=False)
    state = db.Column(db.String(30),nullable=False)
    city = db.Column(db.String(30),nullable=False)

    def __repr__(self):
        return 'SSNID : ' + str(self.ssnid)


# password = sha256_crypt.encrypt(passwd)
# if(sha256_crypt.verify(password_candidate,password))
#db.create_all()



@app.route('/home')
def home():
    return render_template('home.html', home = True)

@app.route('/')
@app.route('/login',methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form['username']
        password_candidate = request.form['password']
        login_type = request.form['login_type']
        
        result = db.session.query(ExecutiveAccount).filter(ExecutiveAccount.username==user_name)
        
        if(len(result.all())>0):
            for row in result:
                if(user_name == row.username and password_candidate == row.password):
                    session['logged_in'] = True
                    session['username'] = user_name
                    db.session.add(ExecutiveLoggedIn(username=user_name))
                    db.session.commit()
                    flash("Successfully Logged In","success")
                    return render_template('create_customer.html')
                else:
                    flash("Wrong password!! Try Again !!",category= "warning")
                    return render_template('login.html', login_page = True)
        else:
            flash("Invalid Username","warning")
            return render_template('login.html', login_page = True)

    return render_template('login.html', login_page = True)

# Declaring a decorator to check if user is logged in (Authorization)
def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,*kwargs)
        else:
            flash('Must be logged in to process','warning')
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out !','success')
    return redirect(url_for('login'))

@app.route('/create_customer', methods = ['GET', 'POST'])
@is_logged_in
def createCustomer():
    if request.method == 'POST':
        #create customer and return accordingly
        ssid = request.form['cust_ssid']
        name = request.form['cust_name']
        age = request.form['cust_age']
        address = request.form['cust_address']
        state = request.form['cust_state']
        city = request.form['cust_city']

        prev_custid = db.session.query(CustomerAccount).order_by(CustomerAccount.custid.desc()).first().custid
        custid = prev_custid + 1

        customer_obj = CustomerAccount(custid=custid,ssnid=ssid,name=name,age=age,address=address,state=state,city=city)
        db.session.add(customer_obj)
        db.session.commit()

        flash('Customer created successfully', 'success')
        return render_template('create_customer.html', activate_customer_mgmt = True)
    return render_template('create_customer.html', activate_customer_mgmt = True)
    
@app.route('/update_customer', methods = ['GET', 'POST'])
@is_logged_in
def updateCustomer():
    if request.method == "POST":
        if( 'input_type' in request.form and 'id' in request.form):
            input_type = request.form['input_type']
            cust_id = int(request.form['id'])
            #search for customer data with id and input_type...write a funtion to pull data from db using input_Type and id
            if(input_type=='cust_id'):
                result = db.session.query(CustomerAccount).filter(CustomerAccount.custid==cust_id)
                if(len(result.all())>0):
                    for row in result:
                        if(cust_id == row.custid):
                            flash(f"Customer found!",category="success")
                            return render_template('update_customer.html',search = False, data = row, activate_customer_mgmt = True)
                        else:
                            flash(f"Customer with {input_type} = {cust_id} not found!", category='warning')
                            return render_template('update_customer.html', search = True,  activate_customer_mgmt = True)
        
            elif(input_type=='ssn_id'):
                result = db.session.query(CustomerAccount).filter(CustomerAccount.ssnid==cust_id)
                if(len(result.all())>0):
                    for row in result:
                        if(cust_id == row.ssnid):
                            flash(f"Customer found!",category="success")
                            return render_template('update_customer.html',search = False, data = row, activate_customer_mgmt = True)
                        else:
                            flash(f"Customer with {input_type} = {cust_id} not found!", category='warning')
                            return render_template('update_customer.html', search = True,  activate_customer_mgmt = True)
    # else:
    #     flash(f"Invalid Request", category='warning')
    #     return render_template('update_customer.html', search = True,  activate_customer_mgmt = True)

    return render_template('update_customer.html', search = True,  activate_customer_mgmt = True)


@app.route('/update_into_database', methods = ['GET', 'POST'])
@is_logged_in
def updateIntoDatabase():
    if request.method == 'POST':
        cust_ssid = request.form['cust_ssid']
        cust_id = request.form['cust_id']
        cust_old_name = request.form['cust_old_name']
        cust_new_name = request.form['cust_new_name']
        cust_old_age = request.form['cust_old_age']
        cust_new_age = request.form['cust_new_age']
        cust_new_address = request.form['cust_new_address']
        cust_state = request.form['cust_state']
        cust_city = request.form['cust_city']
        #udpate into database
        try:
            obj = CustomerAccount.query.get((cust_id,cust_ssid))
            obj.name = cust_new_name
            obj.age = cust_new_age
            obj.address = cust_new_address
            obj.state =  cust_state
            obj.city = cust_city
            db.session.commit()
            flash("Updated Successfully", category= 'success')
            return redirect(url_for('updateCustomer'))
        except:
            flash("An unknown error occured", category= 'warning')
            return redirect(url_for('updateCustomer'))



@app.route('/delete_customer', methods = ['GET', 'POST'])
# @is_logged_in
def deleteCustomer():
    if request.method == "POST":
        flag = 0
        input_type = request.form['input_type']
        cid = request.form['id']
        if(input_type=='cust_id'):
            result = db.session.query(CustomerAccount).filter(CustomerAccount.custid==cid)
            if(len(result.all())>0):
                flag = 1
                for row in result:
                    flash("Customer Found",category="success")
                    return render_template('delete_customer.html',search = False, data = row, activate_account_mgmt = True)
            
        elif(input_type=='ssn_id'):
            result = db.session.query(CustomerAccount).filter(CustomerAccount.ssnid==cid)
            if(len(result.all())>0):
                flag = 1
                for row in result:
                    flash("Customer Found",category="success")
                    return render_template('delete_customer.html',search = False, data = row, activate_account_mgmt = True)
        if(flag==0):
            flash(f'Account not found for {input_type} = {cid} ', 'warning')
            return render_template('delete_customer.html', search = True,  activate_customer_mgmt = True)

    return render_template('delete_customer.html', search = True,  activate_customer_mgmt = True)
    #     if( 'input_type' in request.form and 'id' in request.form):
    #         input_type = request.form['input_type']
    #         id = request.form['id']
    #         #search for customer data with id and input_type...write a funtion to pull data from db using input_Type and id
    #         if 1==1: #if customer found
    #             return render_template('delete_customer.html',search = False, data = 'sainath', activate_customer_mgmt = True)
    #         else:
    #             flash(f"Customer with {input_type} = {id} not found!", category='warning')
    
    # return render_template('delete_customer.html', search = True,  activate_customer_mgmt = True)



@app.route('/delete_customer_from_database', methods = ['GET', 'POST'])
@is_logged_in
def deleteCustomerFromDatabase():
    if request.method == 'POST':
        # same like updateIntoDatabase
        custid = request.form['cust_id']
        ssid = request.form['cust_ssid'] 
        obj = CustomerAccount.query.get((custid,ssid))
        db.session.delete(obj)
        db.session.commit()
        flash("Successfully Deleted !!","success")
        return render_template('delete_customer.html', search = True,  activate_customer_mgmt = True)


@app.route('/view_customer', methods = ['GET', 'POST'])
# @is_logged_in
def viewCustomer():
    return render_template('view_customer.html', datatable = True,  activate_customer_mgmt = True)

@app.route('/customer_status')
# @is_logged_in
def customerStatus():
    return render_template('customer_status.html', datatable = True)

@app.route('/customer_management')
# @is_logged_in
def customerManagement():
    customers = CustomerAccount.query.all()
    return render_template('customer_mgmt.html', datatable = True,  activate_customer_mgmt = True, data=customers)

@app.route('/create_account', methods = ['GET', 'POST'])
def createAccount():
    if request.method == 'POST':
        if( 'cust_id' in request.form and 'account_type' in request.form and 'deposit_amt' in request.form ):
            cust_id = request.form['cust_id']
            account_type = request.form['account_type']
            deposit_amt = request.form['deposit_amt']

            if 1==1: #if customer found
                if 1==1: # if deposit success
                    flash('Deposit Success', 'success')
                    return redirect(url_for('createAccount'), activate_account_mgmt = True)
                else:
                    flash('An unknown error occured', 'warning')
                    return redirect(url_for('createAccount'), activate_account_mgmt = True)
            else:
                flash(f'Customer with id = {cust_id} not found! ', 'warning')
                return redirect(url_for('createAccount'), activate_account_mgmt = True)
                
    return render_template('create_account.html', activate_account_mgmt = True)


@app.route('/delete_account', methods = ['GET', 'POST'])
# @is_logged_in
def deleteAccount():
    if request.method == "POST":
        if('input_type' in request.form and 'id' in request.form):
            input_type = request.form['input_type']
            cid = request.form['id']
            if(input_type=='cust_id'):
                result = db.session.query(CustomerAccount).filter(CustomerAccount.custid==cid)
                if(len(result.all())>0):
                    for row in result:
                        if(cid==row.custid):
                            flash("Customer Found",category="success")
                            return render_template('delete_account.html',search = False, data = row, activate_account_mgmt = True)
            else:
                if(input_type=='ssn_id'):
                    result = db.session.query(CustomerAccount).filter(CustomerAccount.ssnid==cid)
                    if(len(result.all())>0):
                        for row in result:
                            if(cid==row.ssnid):
                                flash("Customer Found",category="success")
                                return render_template('delete_account.html',search = False, data = row, activate_account_mgmt = True)
        else:
            flash(f'Account not found for {input_type} = {cid} ', 'warning')
            return redirect(url_for('deleteAccount'), search = True, activate_account_mgmt = True)
            
                               

@app.route('/delete_account_from_database', methods = ['GET', 'POST'])
def deleteAccountFromDatabase():
    if request.method == 'POST':
        # same like updateIntoDatabase
        return redirect(url_for('deleteAccount'))



"""
cd ~
source webflask/bin/activate
cd Documents/Flask\ Apps/RetailBanking_latest

"""