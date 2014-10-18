import time
from flask import redirect, request, url_for
from google.appengine.ext import db
from google.appengine.api import users
import pickle
from hashlib import md5
from bisect import bisect


class NonsensoUsers(db.Model):
    email = db.StringProperty(required=True)
    latest = db.IntegerProperty(required=True)
    questions = db.TextProperty(required=True)
    score = db.IntegerProperty(required=True)


# some global constants
epoch = 1413628978.194197
intervals = [15, 60, 180, 900, 3600, 10800, 86400, 259200, 1296000]
epoch_distances = [10800, 21600, 43200, 86400, 172800, 259200, 1296000]
arr = [7, 7, 4, 4, 7, 7, 15, 15, 13, 13, 13,
       13, 15, 15, 20, 20, 20, 20, 32, 32, 32,
       27, 27, 27, 27, 32, 31, 31, 31, 32, 33]
difficulty = [5, 2, 6, 4, 8, 6, 10, 4, 6, 5, 6,
              1, 3, 7, 10, 3, 8, 4, 6, 6, 7, 6,
              9, 10, 1, 6, 10, 5, 10, 9, 8, 3, 6]
answer = [
    '9c07d336cba4a19d4e68e558400fd53f',
    '9313c0e09555e8e97bf645d99b50195c',
    'd35e97ff9123df7142dd78815bb67671',
    '04fa5adc64681b6819ea3ea1efde79ea',
    'd92f52b08380ac4681b2a5fef9c73fce',
    '09a3163ed8ece972f794d88327618ebd',
    'a33d782764106cade800eee8eda7363a',
    'ae631d089b79901c5fdd796df7d29c94',
    '0635c792e8e27d2262239843b6c63755',
    'a6e514f9486b83cb53d8d932f9a04292',
    '896ffd737b8a03d6270f8f5896eb4106',
    'c1db8d3f43b73a2ae8f888daffbf5a78',
    '7f2d23b4cec6224e63d01ed254c7d35b',
    'f671a50d602479129d3129c9d2fc9080',
    'cfe819bed5b34b02ccb68ab69ab2055b',
    'a51e47f646375ab6bf5dd2c42d3e6181',
    '7edfa9865ac62fe492a614cd9ad022e7',
    'abf5f8c1886921486adf91c1d57318de',
    '87df2cd1570fd297de238aeee667fe0a',
    '07cc694b9b3fc636710fa08b6922c42b',
    '320381dbf7cd2f31c04baa6b36e1c682',
    'b3d97746dbb45e92dc083db205e1fd14',
    '25759290d52347979dbed53759aa76e6',
    '7e5c644641a3ff8fc4319d70bca92d44',
    'd293c98482fd37cff714ee96610174d6',
    'ec61ede4e515406997b902296f9bdbfb',
    'bda896bb247c0f87ebbd97bfc923938c',
    '0e9312087f58f367d001ec9bae8f325a',
    '64ea19295649877fd1944e7f8ecd0f7b',
    'ce922d89a6c244fb0c5aff66bc46e9be',
    '126ac4b07f93bc4f7bed426f5e978c16',
    'c48ba993d35c3abe0380f91738fe2a34',
    '154f020f4c00a706fdcbdfd49bee9a36']

array3232 = []
for x in xrange(33):
    for y in xrange(33):
        if x == y:
            array3232[x].append(1)
        else:
            array3232[x].append(0)
array3232[4][2] = 2
array3232[4][3] = 1
array3232[7][0] = 8
array3232[7][1] = 7
array3232[7][4] = 5
array3232[7][5] = 3
array3232[7][6] = 1
array3232[13][8] = 5
array3232[13][9] = 2
array3232[13][10] = 3
array3232[13][11] = 2
array3232[13][12] = 1
array3232[15][7] = 9
array3232[15][8] = 8
array3232[15][13] = 5
array3232[15][14] = 1
array3232[21][17] = 4
array3232[21][18] = 3
array3232[21][19] = 2
array3232[21][20] = 1
array3232[27][23] = 4
array3232[27][24] = 3
array3232[27][25] = 2
array3232[27][26] = 1
array3232[31][28] = 3
array3232[32][29] = 2
array3232[31][30] = 1
array3232[32][15] = 7
array3232[32][20] = 6
array3232[32][21] = 5
array3232[32][22] = 4
array3232[32][27] = 4
array3232[32][31] = 4


from flask import Flask
app = Flask(__name__)
app.config['DEBUG'] = True

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


@app.route('/')
def index():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'


@app.route('/login')
def login():
    user = users.get_current_user()
    if user:
        return app.send_static_file('successfully_logged_in.html')
    return app.send_static_file('login.html')


@app.route('/quiz')
def quiz():
    user = users.get_current_user()
    if not user:
        return redirect(users.create_login_url(request.base_url))
    q = NonsensoUsers.all()
    q.filter('email =', user.email())
    if not q.get():
        newuser = NonsensoUsers(email=user.email(),
                                latest=int(time.time()),
                                x=0,
                                predicate=False,
                                score=0)
        # print str(db.Text(questions_template))
        newuser.put()
    return 'entered into quiz'


@app.route('/quizzz/<question>')
def quizzz(question):
    user = users.get_current_user()
    if not user:
        return redirect(users.create_login_url(request.base_url))
    q = NonsensoUsers.all()
    q.filter('email =', user.email())
    punk = q.get()
    if not punk:
        newuser = NonsensoUsers(email=user.email(),
                                lasttime=int(time.time()),
                                x=0,
                                predicate=False,
                                score=0)
        newuser.put()
    if request.method == 'POST':
        if answer[int(question)] == request.form['answer']:
            if question == arr[punk.x]:
                punk.score += ((11 - bisect(intervals, time.time() -
                                punk.lasttime)) *
                               array3232[question][punk.x] *
                               difficulty[question])
                punk.predicate = True
            elif question == punk.x:
                if arr[punk.x] == punk.x + 1:
                    if punk.predicate is True:
                        punk.x += 2
                    else:
                        punk.x += 1
                else:
                    punk.x += 1
        punk.put()
    if not punk.predicate:
        if punk.x == question or arr[punk.x] == question:
            return app.send_static_file(punk.x + '.html')
        else:
            return redirect(url_for('quiz'))
    else:
        if question == punk.x:
            return app.send_static_file(punk.x + '.html')
        else:
            return redirect(url_for('quiz'))


@app.route('/quiz/<question>')
def questions(question):
    print question
    user = users.get_current_user()
    if not user:
        return redirect(users.create_login_url(request.base_url))
    q = NonsensoUsers.all()
    q.filter('email =', user.email())
    punk = q.get()
    if not punk:
        questions_template = open('questions.template', 'r').read()
        newuser = NonsensoUsers(email=user.email(),
                                latest=int(time.time()),
                                questions=db.Text(questions_template),
                                score=0)
        newuser.put()
    question = question.split('.')
    try:
        qdata = pickle.loads(punk.questions)
        print punk.questions
        print qdata
        q_data = qdata
        print question
        for x in question:
            print x
            q_data = q_data[x]
    except:
        return '<h1>you there! how dare you play in my dimension.</h1>'

    print q_data

    if not q_data['access']:
        # TODO: write some info about where he is..
        print 'redirecting here'
        return redirect(url_for('quiz'))
    if request.method == 'POST':
        if q_data['answer'] == md5(request.form['answer']):
            q_data['parent']['access'] = True
            q_data['status'] = True
            punk.questions = pickle.dumps(qdata)
            # TODO: update score
            punk.score += ((11 - bisect(intervals, time.time() - punk.latest)) *
                           q_data['difficulty'] *
                           (11 - bisect(epoch_distances, time.time() - epoch)))
            punk.put()
            return redirect(url_for('quiz'))
    return app.send_static_file(q_data['filename'])


# 4xx error handlers
@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return '<h1>Sorry, nothing at this URL.<h1>', 404


@app.errorhandler(401)
def unauthorized(e):
    """ custom 401 """
    return '<h1>hey, you there, no wandering around here</h1>', 401
