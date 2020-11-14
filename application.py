#Import classes
#url_for makes it easier to call certain url's that may be dynamic
from datetime import datetime
from flask import Flask, render_template, url_for, flash, request, redirect
from flask_sqlalchemy import SQLAlchemy # Database ORM
from forms import RegistrationForm, LoginForm
import requests
import csv

"""object relational mapper (ORM) allows access of db in a simple, object-oriented way
and can use diff db's w/o changing python code—just need to pass in diff url"""

#Cosntructor sends app var to instance of Flask class & tells where to look for html's
application = Flask(__name__, template_folder='./', static_folder="/")
#app.config['TEMPLATES_AUTO_RELOAD'] = True
application.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

#Secret key: protects against modifying cookies, cross-site requests, forgery attacks, etc ****not public - hardcoded
application.config['SECRET_KEY'] = 'dcf825233586379d01d31beb7d7b5306'

#This will create a site.db file
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # /// indicates relative path, for db file
#Creates instance of database. Db structure will be of classes/models
db = SQLAlchemy(application)
""" This SQLAlchemy instance was called to create db structure in same diry as app w/: from application import
    db; db.create_all(). Then models were imported: from application import User, Post. Could then add users &
    posts: userObj = User(username='jack', email='jack@gmail.com', password='pass');
    postObj = Post(title='Title', content='Content', user_id='user.id'); db.session.add(userObj);
    db.session.commit() . Can clear db using db.drop_all()"""
# User.query.all() shows all User objs; User.query.first()
# User.query.filter_by(username='jackalakalaka') - .first() too
# User.query.get(id)    # userObj.posts


# User class inheriting from db.Model
'''class User(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)

    #20 is max username char limit; cannot be NULL—needs a username
    username = db.Column(db.String(20), unique=True, nullable=False)

    #120 is max email char limit; can't be null either
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    #propic doesn't need to be unique—users will have same default.jpg propic
    #* - can add default propic \
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')

    # Passwords will be hashed
    password = db.Column(db.String(60), nullable=False)

    """One to many relnship b/w (one) User & (many) Post classes. Backref adds
    another column to Post model with all of above-defnd user info. posts attr,
    in the background, queries a User's posts and other attributes; it is not a
    column in the db"""
    # For a Post obj, can use backref to get corresponding User obj: postObj.author
    # lazy gets all related posts rather than selected ones
    posts = db.relationship('Post', backref='author', lazy=True)

    #Double underscore ("dunder" or "magic") method w/ self - OO printing method
    #Def's how User obj is printed when printed out
    #repr?
    def __repr__(self):

        # Defs how a User obj is printed
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


# Post class inheriting from db.Model
class Post(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)

    #Datetime column type; utcnow fn is passed into default as arg
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    content = db.Column(db.Text, nullable=False)

    #Integer is related user's primary key; each post requires an author so not nullable
    """Referencing User db's table/column name w/ user.id, so lowercase as is default name
    for User. Same default name rule for Post class ("post")"""
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        # Defs how a Post obj is printed
        return f"Post('{self.title}', '{self.date_posted}')"'''

"""If want more info about user/author from a particular post, can call 'author'
backref thing from User's posts attribute as if it were an attribute of Post to
receive the info"""

posts = [
    {
        'author': 'Jack Carson',
        'title': 'Update 1',
        'content': "As of today, the web app has launched. If there's anything\
         I've learned during the process of setting this up—from getting into\
         WebDev, learning Python Flask as well as D3.js, and setting up\
        hosting—it's that tasks take 5 times longer than expected. My next\
         goal is to continue expressing analyzed COVID data with several more\
         API-sourced charts!",
        'date_posted': '21 September 2020 at 17:35EST'
    }
]

"""Routes are what are typed into browser to go to diff pages"""



#2 routes handled by same fn
@application.route("/")
@application.route("/home")
def home():
    return render_template("index.html", title='SARSCoViz - Plots')


@application.route("/about")
def about():
    return render_template("about.html", title='SARSCoViz - About')


#Allows the following methods for user
@application.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        #Shows flash msg w/ success alert  category
        #f signifies passing in a var
        flash(f'Account created for {form.username.data}!', 'success')
        #Redirect function goes back to home page
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@application.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@application.route("/updates", methods=['GET','POST'])
def updates():
    return render_template("updates.html", title='SARSCoViz - Updates', posts=posts)



#Printing .text gives # of chars in str
COVID19DeathsByWeek_AgeSex = requests.get('https://data.cdc.gov/resource/vsak-wrfu.csv?$limit=200000')
#Printing gives <Response [200]> which indicates GET success
"""Can also use:
if COVID19DeathsByWeek_AgeSex:
    print('Response OK')
else:
    print('Response Failed')
to see if GET success"""
#Printing .text gives # of chars in str
"""print(COVID19DeathsByWeek_AgeSex.headers) shows headers, w/ 'X-SODA2-Fields'
preceding the data's headers"""

#Get CADBD data
COVID19CasesAndDeathsByDay = requests.get('https://data.cdc.gov/resource/9mfq-cb36.csv?$limit=200000')


"""#Shows attr's & methods accessible in this resp obj
print(dir(COVID19DeathsByWeek_AgeSex))
#More detailed v of dir
print(help(COVID19DeathsByWeek_AgeSex))
#Gives content of resp in unicode
print(COVID19DeathsByWeek_AgeSex.text)"""

"""#Gets data and creates CSV file
#new_csvReader printed would just show an obj in mem
new_csvReader = csv.reader(COVID19DeathsByWeek_AgeSex.text)
#Skips over first element
next(new_csvReader)
for element in new_csvReader:
    print(element)"""



#w indicates writing new file; a could be used to just append to file
with open('temp_DBW_AS.csv', mode='w') as write1:
    # lenCount=0
    # for line in write1:
    #     lenCount = lenCount + 1
    # print(lenCount)
    #Does nothing but create file pass
    write1.write(COVID19DeathsByWeek_AgeSex.text)

#Write CADBD data to temp csv file
with open('temp_CADBD.csv', mode='w') as write2:
    #Does nothing but create file pass
    write2.write(COVID19CasesAndDeathsByDay.text)



#Read temp DBW_AS file, Process for relevant info
with open('temp_DBW_AS.csv', 'r') as read1:
    #csvReader is list of dics
    #\t for tab delimiter if desired
    csvReader = csv.DictReader(read1, delimiter=',')
    #print(csvReader) prints addr of data

    week_ending_date = []
    sex = []
    #Create new dic that doesn't diff by age, sex, data upload date, state, or week
    DBW = []

    DBW_A = []
    # Look at data for all sexes
    for line in csvReader:
        if line['sex'] == 'All Sex':
            DBW_A.append(line)
    
    # Look at data for all ages in bottom-most rows of csv file.
    # There are 12 age groups including 'All ages'.
    '''DBW_len = len(DBW_A)/12
    firstAllagesIndex = int(len(DBW_A) - DBW_len)
    lastAllagesIndex = int(len(DBW_A)-1)
    for i in range(firstAllagesIndex, lastAllagesIndex+1):
        DBW.append(DBW_A[i])'''
    for line in DBW_A:
        if line['age_group']=='All Ages':
            DBW.append(line)
    
    for line in DBW:
        # Remove irrelevant columns
        del line['sex']
        del line['data_as_of']
        del line['state']
        del line['mmwr_week']
        del line['age_group']
        # Add weekNum key-value pair to each row
        index = DBW.index(line)
        line['weekNum'] = index+1


#Read temp CADBD file, Process for relevant info
with open('temp_CADBD.csv', 'r') as read2:
    #csvReader is list of dics
    #\t for tab delimiter if desired
    csvReader = csv.DictReader(read2, delimiter=',')
    #Transfer each row (from csvReader addr obj?) to CADBD list (printable)
    CADBD = []
    for line in csvReader:
        CADBD.append(line)
    #Remove irrelevant rows from CADBD
    for line in CADBD:
        del line['new_case']
        del line['pnew_case']
        del line['new_death']
        del line['pnew_death']
        del line['created_at']
        del line['consent_cases']
        del line['consent_deaths']
        del line['conf_cases']
        del line['prob_cases']
        del line['conf_death']
        del line['prob_death']
    

    #List (of 60 lists of dics) w/ an index for each of 60 states's daily case info, paired w/ CADBD_byState_labels
    CADBD_byState = [[], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], []]
    #List of labels for each state corresponding to CADBD_byState, starting w/ CO
    CADBD_byState_labels = ['CO']

    # For each line in CADBD indicates # of state {1 to 50+10}, as each state appears
    # in top-bottom order in CADBD/temp_CADBD.csv
    stateCount = 1
    # Paired w/ stateCount, indicates label of each state. Starts w/ Colorado
    state = 'CO'
    # Iterate thru each line and fills in CADBD_byState & CADBD_byState_labels
    for line in CADBD:
        # When the state of interest changes, edits some vars
        if state != line['state']:
            # Set state equal to new state label,
            state = line['state']
            # increment stateCount,
            stateCount=stateCount+1
            # and add new state to correct labels list index.
            CADBD_byState_labels.append(state)
        # Remove line's 'state' key-value pair,
        del line['state']
        # and append remaining line to corresponding state's list in
        # CADBD_byState
        CADBD_byState[stateCount-1].append(line)#* - out of rnge
    # end for

    print('CO last day cases (>= last week cases):',CADBD_byState[0][-1]['tot_cases'])

    #Convert CADBD_byState to CADBW_byState
    #List (of 60 lists of dics) w/ an index for each of 60 states's weekly case info
    CADBW_byState = [[], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], []]
    #For each state in daily data, compile data to weekly
    for state, stateInfo in enumerate(CADBD_byState): #stateInfo is a list
        dayCnt = -1 #Rst day of wk counter for this state, including day 1Feb2020 as 1st wk
        weekCnt = 0 #Rst week counter {0 to n-1} for next state

        for dayInfo in stateInfo: #For each of state's days in CADBD_byState:
            if dayCnt==1: #If iterating on new wk,
                wkDict = {} #append empty dict to state list for this wk
                CADBW_byState[state].append(wkDict)
                #Insert partial data from CADBD_byState
                CADBW_byState[state][weekCnt]['tot_cases'] = int(dayInfo['tot_cases'])
                CADBW_byState[state][weekCnt]['tot_death'] = int(dayInfo['tot_death'])
            elif dayCnt == -1: #Special case to include 1Feb2020 as 1st wk
                wkDict = {} #append empty dict to state list
                CADBW_byState[state].append(wkDict)
                CADBW_byState[state][0]['tot_cases'] = int(dayInfo['tot_cases'])
                CADBW_byState[state][0]['tot_death'] = int(dayInfo['tot_death'])
                dayCnt = 7 #Indicate "week" is fully accounted for
            else:
                #Add partial data from CADBD_byState
                CADBW_byState[state][weekCnt]['tot_cases'] += int(dayInfo['tot_cases'])
                CADBW_byState[state][weekCnt]['tot_death'] += int(dayInfo['tot_death'])

            #Increment counters, and insert weekCntNum col entry into each wk's data row
            if dayCnt!=7:
                dayCnt += 1
            else:
                CADBW_byState[state][weekCnt]['weekNum'] = weekCnt + 1
                dayCnt = 1
                weekCnt +=1
            #end for dayInfo in CADBD_byState:

        #Chk that final row is a full week. If not, discard
        if dayCnt!=1: #If dayCnt was not just-previously 7:
            CADBW_byState[state].pop(weekCnt)

    """for stateData, stateLabel in zip(CADBW_byState, CADBD_byState_labels):
        print(stateLabel)
        for wkData in stateData:
            print(wkData)
        print('\n')"""
    
    print('CO last week cases:',CADBW_byState[0][-1]['tot_cases'])
    '''#Convert CADBW_byState to CADBW
    CADBW = []
    numWeeks = CADBW_byState[0][-1]['weekNum']
    for weekNum in range(0,numWeeks): #For each week, sum states' data
        print('\n\n')
        for stateIndex in range(0,60): #Iterate thru each state and add its data to total
            if stateIndex==0: #If iterating at new week, append fields & 1st state's data to CADBW
                CADBW.append(CADBW_byState[0][weekNum])
                #Cast str's as int
                CADBW[weekNum]['tot_cases'] = int(CADBW[weekNum]['tot_cases'])
                CADBW[weekNum]['tot_death'] = int(CADBW[weekNum]['tot_death'])
                print(int(CADBW[weekNum]['tot_cases']))
            else: #Add particular state's data to totally for weekNum'th week
                CADBW[weekNum]['tot_cases'] += int(CADBW_byState[stateIndex][weekNum]['tot_cases'])
                CADBW[weekNum]['tot_death'] += int(CADBW_byState[stateIndex][weekNum]['tot_death'])
                print(int(CADBW_byState[stateIndex][weekNum]['tot_cases']))
    for elem in CADBW:
        print(elem)'''
# end with open('temp_CADBD.csv', 'r')


#Create deaths by week .csv to be called by js
with open('DBW.csv', 'w', newline='') as write3: # newline='' removes spacing b/w commas
    writer = csv.writer(write3)

    #Write keys of csv header line - .writerow convention
    writer.writerow(DBW[0])

    #Writes 1 row at a time thru whole list
    for row in DBW:
        csvRow = [row['week_ending_date'], row['total_deaths'],\
            row['covid_19_deaths'], row['weekNum']]
        writer.writerow(csvRow)
# end with open('DBW_A.csv', 'w', newline='')

'''
#Create cases and deaths by day .csv to be called by js
with open('CADBD.csv', 'w', newline='') as write4: # newline='' removes spacing b/w commas
    writer = csv.writer(write4)

    #Write keys of csv header line - .writerow convention
    writer.writerow(CADBW_byState[0])

    #Writes 1 row at a time thru whole list
    for row in CADBW_byState:
        csvRow = [row['submission_date'], row['tot_cases'],\
            row['tot_death'], row['weekNum']]
        writer.writerow(csvRow)
# end with open('DBW_A.csv', 'w', newline='')'''



#Run app in debug mode: removes need to restart server for every change
"""__name__ is __main__ if script is run w/ Python directly. So if we are debugging
and running it directly then debug mode engages"""
if __name__ == '__main__':
    application.run(debug=True)