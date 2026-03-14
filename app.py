from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------------
# Database Model
# ------------------------
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Float, nullable=False)

# Create DB
with app.app_context():
    db.create_all()

# ------------------------
# Dashboard
# ------------------------
@app.route('/')
def dashboard():
    search = request.args.get('search')
    department_filter = request.args.get('department')

    query = Employee.query

    if search:
        query = query.filter(Employee.name.contains(search))

    if department_filter:
        query = query.filter(Employee.department == department_filter)

    employees = query.all()

    # Chart Data
    dept_data = db.session.query(
        Employee.department,
        func.count(Employee.id)
    ).group_by(Employee.department).all()

    departments = [d[0] for d in dept_data]
    counts = [d[1] for d in dept_data]

    return render_template(
        'dashboard.html',
        employees=employees,
        departments=departments,
        counts=counts
    )

# ------------------------
# Add Employee
# ------------------------
@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        
        new_employee = Employee(
            name=request.form['name'],
            email=request.form['email'],
            department=request.form['department'],
            salary=request.form['salary']
        )
        db.session.add(new_employee)
        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('add_employee.html')

# ------------------------
# Edit Employee
# ------------------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    employee = Employee.query.get_or_404(id)

    if request.method == 'POST':
        employee.name = request.form['name']
        employee.email = request.form['email']
        employee.department = request.form['department']
        employee.salary = request.form['salary']

        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('edit_employee.html', employee=employee)

# ------------------------
# Delete Employee
# ------------------------
@app.route('/delete/<int:id>')
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)