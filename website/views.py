from flask import *
import psycopg2
from psycopg2.extras import Json

DB_HOST = "hotelserver.postgres.database.azure.com"
DB_NAME = "hoteldbms"
DB_USER = "Admin"
DB_PASS = "admin"
DB_PORT = "5432"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)


def get_cursor():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return cursor


def get_emp_position(data_id):
    try:
        cursor = get_cursor()
        cursor.execute('SELECT EP."PosName" FROM "EmpPosition"EP INNER JOIN "Employees"E ON E."EmpPosition" = EP."EmpPosition" INNER JOIN "PersonalData"PD on PD."DataID" = E."DataID" WHERE PD."DataID" = %s;', [data_id])
    except Exception as e:
        error = e
    emp_position = cursor.fetchone()
    return emp_position


def get_client_id(email):
    client_id = None
    try:
        cursor = get_cursor()
        cursor.execute(
            'SELECT C."ClientID" '
            'FROM "PersonalData"PD INNER JOIN "Clients"C ON PD."DataID" = C."DataID" '
            'WHERE PD."Email" = %s'
            , email)
        client_id = cursor.fetchone()
    except Exception as e:
        error = e
    client_id = cursor.fetchone()
    return client_id


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'Log-in' in request.form:
            cursor = get_cursor()
            email = request.form['Email']
            password = request.form['Password']
            try:
                cursor.execute(
                    'SELECT PD."DataID", PD."Email", PD."Password"'
                    ' FROM "PersonalData"PD'
                    ' WHERE PD."Email" = %s AND PD."Password" = %s'
                    , (email, password))
            except Exception as e:
                error = e
            account = cursor.fetchone()
            if account:
                session['DataID'] = account[0]
                session['Email'] = account[1]
                emp_position = get_emp_position(session['DataID'])
                if emp_position is not None:
                    session['Position'] = emp_position['PosName']
                else:
                    session['Position'] = 'Client'
                session['Logged'] = True
                return redirect(url_for('views.logged'))
        if 'Sign-up' in request.form:
            d = request.form
            try:
                cursor = get_cursor()
                cursor.execute(
                    'INSERT INTO "PersonalData" ("Email", "Password", "FirstName", "LastName", "Phone", "BirthDate")'
                    ' VALUES (%s, %s, %s, %s, %s, %s)',
                    (d['Email'], d['Password'], d['FirstName'], d['LastName'], d['Phone'], d['BirthDate']))
                conn.commit()
            except Exception as e:
                error = e
            return redirect(url_for('views.logged'))
    return render_template("home.html")


@views.route('/logged/', methods=['POST', 'GET'])
def logged():
    if session['Logged']:
        if request.method == 'POST':
            if 'Log-out' in request.form:
                session['Logged'] = False
                return redirect(url_for('views.home'))
            if 'Reserve' in request.form:
                r = request.form
                print(r)
                get_client_id(r['email'])
                try:
                    cursor = get_cursor()
                    cursor.execute()
                except Exception as e:
                    error = e
                pass
        return render_template("home-user.html")
    return redirect(url_for('views.home'))

