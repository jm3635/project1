#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from operator import itemgetter
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, flash, g, redirect, Response, url_for
import time
from datetime import date

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = 'something'

# Swap out the URI below with the URI for the database created in part 2
DATABASEURI = "postgresql://jm3635:myz22@104.196.175.120/postgres"

# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  print request.args
  thisyear = date.year
#  print thisyear
  cursor = g.conn.execute("SELECT * FROM student")
  account_names = []
  for result in cursor:
    name = result['name']
    uni = result['uni']
    if name is None:
      name = 'not given'
    if uni is None:
      uni = 'does not have';
    year = result['class_year']
    if year < thisyear:
      year = 0
    account_name = {
      'Student Name':(result['name']), #result['name'],
      'UNI': uni, #result['uni']
      'Class Year': result['class_year']
    }
    account_names.append(account_name)
    
  #cursor.close()
  
  account_names = sorted(account_names, key=itemgetter('Student Name'))
  i=0;
  while i < len(account_names)-1:
    while i< len(account_names) -1 and account_names[i]['Student Name'] == account_names[i+1]['Student Name']:
      if account_names[i+1]['uni'][0] not in account_names[i]['uni']:
        account_names[i]['uni'].append(account_names[i+1]['uni'][0])
      if account_names[i+1]['class_year'][0] not in account_names[i]['class_year']:
        account_names[i]['class_year'].append(account_names[i+1]['class_year'][0])
      account_names.pop(i+1)
      i+=1 
  cursor.close()
  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = account_names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)
@app.route('/student/')
def another():
  cursor = g.conn.execute("SELECT * FROM student")
  account_names = []

  for result in cursor:
    name = result['name']
    uni = result['uni']
    if name is None:
      name = 'not given'
    if uni is None:
      uni = 'does not have';
    year = result['class_year']
    account_name = {
      'Student Name':(result['name']), #result['name'],
      'UNI': uni, 
      'Class Year': result['class_year']
    }
    account_names.append(account_name)
 
  cursor.close()

  account_names = sorted(account_names, key=itemgetter('Student Name'))
  i=0;
  while i < len(account_names)-1:
    while i< len(account_names) -1 and account_names[i]['Student Name'] == account_names[i+1]['Student Name']:
      if account_names[i+1]['uni'][0] not in account_names[i]['uni']:
       account_names[i]['uni'].append(account_names[i+1]['uni'][0])
      if account_names[i+1]['class_year'][0] not in account_names[i]['class_year']:
        account_names[i]['class_year'].append(account_names[i+1]['class_year'][0])
      account_names.pop(i+1)
    i+=1
  cursor.close()
  context = dict(data = account_names)

  return render_template("anotherfile.html", **context)

@app.route('/teacher')
def teacher():

  cursor = g.conn.execute("SELECT * FROM teacher")
  account_names = []

  for result in cursor:
    name = result['name']
    uni = result['uni']
    if name is None:
      name = 'not given'
    if uni is None:
      uni = 'does not have';
    dept = result['department']
    account_name = {
      'Teacher Name':(result['name']),
      'UNI': uni,
      'Department': result['department']
    }
    account_names.append(account_name)
  cursor.close()

  account_names = sorted(account_names, key=itemgetter('Teacher Name'))
  i=0;
  while i < len(account_names)-1:
    while i< len(account_names) -1 and account_names[i]['Teacher Name'] == account_names[i+1]['Teacher Name']:
      if account_names[i+1]['uni'][0] not in account_names[i]['uni']:
       account_names[i]['uni'].append(account_names[i+1]['uni'][0])
      if account_names[i+1]['department'][0] not in account_names[i]['department']:
        account_names[i]['department'].append(account_names[i+1]['department'][0])
      account_names.pop(i+1)
    i+=1
  cursor.close()
  context = dict(data = account_names)

  return render_template("teacher.html", **context)

@app.route('/courses')
def courses():
  cursor = g.conn.execute("SELECT * FROM course")
  courses = []

  for result in cursor:
    cid = result['cid']
    name = result['name']
    if name is None:
      name = 'not given'
    if cid is None:
      cid = '0';
    offered = result['semester_year']
    course = {
      'CID':result['cid'],
      'Course Name': result['name'], 
      'Offered': result['semester_year']
    }
    courses.append(course) 
  cursor.close()
#  courses = sorted(course, key=itemgetter('Course Name'))
#  i=0;
#  while i < len(courses)-1:
#    while i< len(courses) -1 and courses[i]['Teacher Name'] == courses[i+1]['Teacher Name']:
#      if courses[i+1]['Teacher Name'][0] not in courses[i]['Teacher Name']:
#       courses[i]['Teacher Name'].append(courses[i+1]['Teacher Name'][0])
#      courses.pop(i+1)
#    i+=1
  context = dict(data = courses)
  return render_template("courses.html", **context)

@app.route('/assignments')
def assignments():
  cursor = g.conn.execute("SELECT * FROM assignments")
  assignments = []
  for result in cursor:
    name = result['name']
    uni = result['uni']
    if name is None:
      name = 'not given'
    if uni is None:
      uni = 'does not exist';

    assignment = {
      'Assignment Name':(result['name']),
      'UNI': (result['uni'])
    }

    assignments.append(assignment)
  cursor.close()
#  assignments = sorted(assignment, key=itemgetter('uni'))
  context = dict(data = assignments)
  return render_template("assignments.html", **context)

@app.route('/grades')
def grades():
  cursor = g.conn.execute("SELECT * FROM grades")
  grades = []
  for result in cursor:
    name = result['name']
    score = result['grade']
    if name is None:
      name = 'not given'
    if score is None:
      score = ['0'];
    submitted_by = result['submitted_by']
    grade = {
      'Assignment Name':(result['name']),
      'GRADE': score, 
      'Submitted By': result['submitted_by']
    }

    grades.append(grade)  
  cursor.close()
#  grades = sorted(grade, key=itemgetter('name'))

  context = dict(data = grades)
  return render_template("grades.html", **context)

@app.route('/department')
def departments():
  cursor = g.conn.execute("SELECT * FROM department")
  departments = []
  for result in cursor:
    name = result['dept_name']

    if name is None:
      name = 'not given'
    department = {
      'Department Name':(result['dept_name'])
    }

    departments.append(department)
  cursor.close()

#  departments = sorted(department, key=itemgetter('name'))

  context = dict(data = departments)
  return render_template("departments.html", **context)


# Add Student on Main Page
@app.route('/add', methods=['POST', 'GET'])
def add_main():
  print request.args
  thisyear = date.year
  if request.method == 'POST':
    sql = """
      SELECT COUNT(*) FROM student;
    """

    cursor = g.conn.execute(sql)
    
    name = request.form['name']
    uni = request.form['uni']
    class_year = request.form['class_year']

    sql = """
      SELECT * FROM student s
      WHERE s.uni = %s
    """
    cursor = g.conn.execute(sql, (uni))
    if cursor.fetchone() is not None:
      flash('UNI already taken!')
      return redirect(url_for('index'))
    
    sql = """
      SELECT * FROM student s
      WHERE s.class_year = %s
    """
    cursor = g.conn.execute(sql, (class_year))
    if cursor.fetchone() < thisyear:
      flash('Cannot be Class Year')
      return redirect(url_for('index'))

    sql = """
      INSERT INTO student VALUES
      (%s, %s, %s )
    """ 

    cursor = g.conn.execute(sql, (name, uni, class_year))
    cursor.close()
    return redirect('/student')

  else:
    cursor.close()
    return redirect('/')

@app.route('/add_student', methods=['POST', 'GET'])
def add_student():
  print request.args
  thisyear = date.year
  if request.method == 'POST':
    sql = """
      SELECT COUNT(*) FROM student;
    """

    cursor = g.conn.execute(sql)

    name = request.form['name']
    uni = request.form['uni']
    class_year = request.form['class_year']

    sql = """
      SELECT * FROM student s
      WHERE s.uni = %s
    """

    cursor = g.conn.execute(sql, (uni))
    if cursor.fetchone() is not None:
      flash('UNI already taken!')
      return redirect('/index')
  
    sql = """
      SELECT * FROM student s
      WHERE s.class_year = %s
    """
    cursor = g.conn.execute(sql, (class_year))
    if cursor.fetchone() < thisyear:
      flash('Cannot be Class Year')
      return redirect('/student')
 
    sql = """
      INSERT INTO student VALUES
      (%s, %s, %s )
    """

    cursor = g.conn.execute(sql, (name, uni, class_year))
    cursor.close()
    return redirect('/student')
  else:
    cursor.close()
    return redirect('/')

@app.route('/add_teacher', methods=['POST', 'GET'])
def add_teacher():
  print request.args
  if request.method == 'POST':
    sql = """
      SELECT COUNT(*) FROM teacher;
    """

    cursor = g.conn.execute(sql)

    name = request.form['name']
    uni = request.form['uni']
    department = request.form['department']

    sql = """
      SELECT * FROM teacher t
      WHERE t.uni = %s
    """

    cursor = g.conn.execute(sql, (uni))
    if cursor.fetchone() is not None:
      flash('UNI already taken!')
      return redirect('/teacher')
 
    sql = """
      SELECT * FROM teacher t
      WHERE t.department = %s
    """

    cursor = g.conn.execute(sql, (department))
    if cursor.fetchone() is  None:
      flash('Department does not exist!')
      return redirect('/teacher')

    sql = """
      INSERT INTO teacher VALUES
      (%s, %s, %s )
    """

    cursor = g.conn.execute(sql, (name, uni, department))
    cursor.close()
    return redirect('/teacher')
  else:
    cursor.close()
    return redirect('/')

@app.route('/add_course', methods=['POST', 'GET'])
def add_course():
  print request.args
  if request.method == 'POST':
    sql = """
      SELECT COUNT(*) FROM course;
    """
    cursor = g.conn.execute(sql)
    cid = request.form['cid']
    name = request.form['name']
    semester_year = request.form['semester_year']

    sql = """
      SELECT * FROM course c
      WHERE c.cid = %s
    """
    cursor = g.conn.execute(sql, (cid))
    if cursor.fetchone() is not None:
      flash('Class already exists!')
      return redirect('/')

    sql = """
      INSERT INTO course VALUES
      (%s, %s, %s )
    """
    cursor = g.conn.execute(sql, (cid, name, semester_year))
    cursor.close()
    return redirect('/courses')
  else:
    cursor.close()
    return redirect('/')

@app.route('/add_grade', methods=['POST', 'GET'])
def add_grade():
  print request.args
  if request.method == 'POST':
    sql = """
      SELECT COUNT(*) FROM grades;
    """
    cursor = g.conn.execute(sql)
    grade = request.form['grade']
#  print name
    name = request.form['name']
#  print uni
    submitted_by = request.form['submitted_by']

    sql = """
      SELECT * FROM grades g
      WHERE g.submitted_by = %s AND g.name = %s
    """
    cursor = g.conn.execute(sql, (name, submitted_by))
    if cursor.fetchone() is not None:
      flash('Already submitted!')
      return redirect('/assignments')

    sql = """
      SELECT * FROM grades g
      WHERE g.grade = %s
    """
    cursor = g.conn.execute(sql, (grade))
    if cursor.fetchone() < 0 or cursor.fetchone() > 100:
      flash('Grades between 0 and 100')
      return redirect('/grades')

    sql = """
      INSERT INTO grades VALUES
      (%s, %s, %s )
    """
    cursor = g.conn.execute(sql, (grade, name, submitted_by))
    cursor.close()
    return redirect('/grades')
  else:
    cursor.close()
    return redirect('/')

@app.route('/add_department', methods=['POST', 'GET'])
def add_department():
  print request.args
  if request.method == 'POST':
    sql = """
      SELECT COUNT(*) FROM department;
    """
    cursor = g.conn.execute(sql)
    name = request.form['dept_name']

    sql = """
      SELECT * FROM  department d
      WHERE d.dept_name = %s
    """
    cursor = g.conn.execute(sql, (name))
    if cursor.fetchone() is not None:
      flash('Department Already Exists!')
      return redirect('/department')

    sql = """
      INSERT INTO department VALUES
      (%s )
    """
    cursor = g.conn.execute(sql, (name))
    cursor.close()
    return redirect('/department')
  else:
    cursor.close()
    return redirect('/')


@app.route('/stud_avg')
def stud_avg():

  print request.args

  sql = """SELECT AVG(G.grade) 
    FROM grades as G, student as S
    WHERE G.submitted_by = S.uni
  """
  cursor = g.conn.execute(sql)

  averages = []
  for result in cursor:
    grade = result[0]
    average = {
      'Average': grade
    }
    averages.append(average)
    cursor.close() 
  context = dict( data = averages ) 
  return render_template("grades.html", **context)

@app.route('/stud_range')
def stud_range():

  print request.args

  sql = """Select S.uni, G.grade
FROM student as S, grades as g
Where S.uni = A.submitted_by IN ( SELECT * FROM Grade G WHERE G.grade >= <90> AND G.grade <= <85>)
  """
  cursor = g.conn.execute(sql)

  averages = []
  for result in cursor:
    grade = result[0]
    average = {
      'Average': grade
    }
    averages.append(average)
    cursor.close()
  context = dict( data = averages )
  return render_template("grades.html", **context)
@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
