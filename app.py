from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(80), nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # 修正这里
    status = db.Column(db.String(80), nullable=False, default='Pending')

    def __repr__(self):
        return f'<Order {self.id}>'

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    search = request.args.get('search', '').strip()
    if search:
        orders = Order.query.filter(
            (Order.customer_name.contains(search)) |
            (Order.product_name.contains(search))
        ).all()
    else:
        orders = Order.query.all()
    return render_template('index.html', orders=orders, search=search)

@app.route('/add', methods=['GET', 'POST'])
def add_order():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        product_name = request.form['product_name']
        quantity = request.form['quantity']
        status = request.form['status']

        new_order = Order(customer_name=customer_name, product_name=product_name, quantity=quantity, status=status)
        db.session.add(new_order)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('add_order.html')

@app.route('/update/<int:order_id>', methods=['GET', 'POST'])
def update_order(order_id):
    order = Order.query.get_or_404(order_id)

    if request.method == 'POST':
        order.customer_name = request.form['customer_name']
        order.product_name = request.form['product_name']
        order.quantity = request.form['quantity']
        order.status = request.form['status']

        db.session.commit()
        return redirect(url_for('home'))

    return render_template('update_order.html', order=order)

@app.route('/delete/<int:order_id>')
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)