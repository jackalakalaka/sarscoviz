#SarsCoViz - Backend
#See Backend documentation (^ indicates notes) at: https://bit.ly/SarsCoViz_Docn
#* - indicates an issue

from datetime import datetime
from flask import Flask, render_template, url_for, flash, request, redirect #^1
from flask_sqlalchemy import SQLAlchemy # Database ORM ^2
from forms import RegistrationForm, LoginForm
import requests
import csv

#Constructor sends app var to instance of Flask class & tells where to look
#for template/html and static/CSS-Js files
application = Flask(__name__, template_folder='./', static_folder="/")
application.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 #Ensures pages reload
#Secret key: protects against modifying cookies, cross-site requests, forgery
#attacks, etc ****not public - hardcoded
application.config['SECRET_KEY'] = 'dcf825233586379d01d31beb7d7b5306'
#This will create a site.db file, w/ /// indicating relative path
application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #Disables default nofos


#Creates instance of database. Db structure will be of classes/models
db = SQLAlchemy(application) #^3

#Define classes that inherit from db.Model aka have their own db's ^4
'''
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #20 is max username char limit; cannot be NULL—needs a username
    username = db.Column(db.String(20), unique=True, nullable=False)
    #120 is max email char limit; can't be null either
    email = db.Column(db.String(120), unique=True, nullable=False)
    #propic doesn't need to be unique—users will have same default.jpg propic
    #Can add default propic \
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False) # Pw's will be hashed

    #One (User) to many (Post)s backref relationship
    # lazy gets all related posts rather than selected ones
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self): # Defs how User obj is printed
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    #Datetime column type; utcnow fn is passed into default as arg
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    #Integer is related user's primary key; posts need author, so not nullable
    """Referencing User db's table/column name w/ user.id, so lowercase as is
    default name for User. Same default name rule for Post class ("post")"""
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self): # Defs how Post obj is printed
        return f"Post('{self.title}', '{self.date_posted}')"
'''

#Define posts dict
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


#Routes to particular pages
@application.route("/")
@application.route("/home") #another web addr option to same route
def home():
    return render_template("index.html", title='SARSCoViz - Plots')

@application.route("/about")
def about():
    return render_template("about.html", title='SARSCoViz - About')

@application.route("/register", methods=['GET', 'POST']) #methods for user
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        #Shows flash msg w/ success alert  category
        flash(f'Account created for {form.username.data}', 'success')
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


#Fetch data from web
COVID19DeathsByWeek_AgeSex = requests.get('https://data.cdc.gov/resource/vsak-wrfu.csv?$limit=200000')
COVID19CasesAndDeathsByDay = requests.get('https://data.cdc.gov/resource/9mfq-cb36.csv?$limit=200000')

'''* - this may be optimazable by parsing thru response obj's directly, rather
than reading from and parsing thru a temporary csv file'''
#Write response obj's to temporary csv files
with open('temp_DBW_AS.csv', mode='w') as write1: #Deaths by wk: age, sex
    write1.write(COVID19DeathsByWeek_AgeSex.text)
with open('temp_CADBD.csv', mode='w') as write2: #Cases & deaths by day
    write2.write(COVID19CasesAndDeathsByDay.text)


#* - WIP; turning what's below into functions, and the cases and deaths by day/week data is wrong

#Context manager reads from temp csv files, parses out relevant info
with open('temp_DBW_AS.csv', 'r') as read1: #Deaths by wk: age, sex
    #DBW_AS_reader is an iterable of a list of dicts
    DBW_AS_reader = csv.DictReader(read1, delimiter=',')

    DBW_A = [] #list of dicts: deaths by wk over age, plus general cause deaths
    DBW = [] #list of dicts: deaths by wk, plus general cause deaths

    # Look at data for all sexes
    for line in DBW_AS_reader:
        if line['sex'] == 'All Sex':
            DBW_A.append(line) #Turn iterable into regular list
    
    # Look at data for all ages
    for line in DBW_A:
        if line['age_group']=='All Ages':
            DBW.append(line) #Turn iterable into regular list
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

with open('temp_CADBD.csv', 'r') as read2: #Cases & deaths by day
    #CADBD_reader is an iterable of a list of dicts
    CADBD_reader = csv.DictReader(read2, delimiter=',')

    CADBD = [] #list of dicts: cases & deaths by day
    for line in CADBD_reader:
        CADBD.append(line) #Turn iterable into regular list line-by-line
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
    
    #List of 60 lists of dicts, w/ index for each state's daily case info
    #60 states/regions total
    #Paired w/ CADBD_byState_labels for construction
    CADBD_byState = [[], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], []]
    #State labels list that corresponds to by-day and by-wk lists
    CADBD_byState_labels = ['CO'] #Will grow as CADBD_byState is filled

    #For each line in CADBD indicates state # (as each state appears
    #in top-bottom order in CADBD/temp_CADBD.csv)
    stateCount = 1
    #Related to stateCount, indicates label of each state. Starts w/ Colorado
    state = 'CO'
    #Iterate thru each line and fills in CADBD_byState & CADBD_byState_labels
    for line in CADBD:
        #When read state changes, alter state & statecount & append new info
        if state != line['state']:
            state = line['state'] #Set state equal to new state label
            stateCount=stateCount+1 #Increment stateCount
            CADBD_byState_labels.append(state) #Add new state to labels list
        del line['state'] #Remove line's 'state' key-value pair
        #Append altered line to corresponding nested state list in CADBD_byState
        CADBD_byState[stateCount-1].append(line)
    #end for

    print('THIS IS WRONG. Currently working on fixing it -Jack')
    for i in range(0,60):
        print(CADBD_byState_labels[i],'last day cases (>= last week cases):',CADBD_byState[i][-1]['tot_cases'],'and deaths (>= last week deaths)\
        in nested list:',CADBD_byState[i][-1]['tot_death'])
    
    print('last day cases (>= last week cases):',CADBD[297]['tot_cases'],'and deaths (>= last week deaths) in og list:',\
        CADBD[297]['tot_death'])

    #Convert CADBD_byState to CADBW_byState
    #List (of 60 lists of dics) w/ an index for each of 60 states's weekly case info
    CADBW_byState = [[], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], [],\
        [], [], [], [], [], [], [], [], [], []]
    #For each state in daily data, change data to weekly
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
    for i in range(0,60):
        print(CADBD_byState_labels[i],'last week cases:',CADBW_byState[i][-1]['tot_cases'],'and deaths:',CADBW_byState[i][-1]['tot_death'])
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


def totalToNew_byState():
    pass