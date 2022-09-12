from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))
    price = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    is_active = db.Column(db.Boolean, default=True)

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html', title='Главная')

@app.route('/about')
def about():
    return render_template('about.html', title='О нас')

@app.route('/create', methods=['POST','GET'])
def create():
    if request.method == "POST":

            title = request.form['title']
            description = request.form['description']
            price = int(request.form['price'])

            item = Item(title=title, description=description, price=price)
            try:
                db.session.add(item)
                db.session.commit()
                return redirect('/goods')
            except:
                return 'При добавлении товара произошла ошибка'

    else:
        return render_template('create.html', title='Добавить товар')

@app.route('/goods')
def goods():
    goods = Item.query.order_by(desc(Item.date)).all()
    return render_template('goods.html', title='Товары на складе', goods=goods)

#________________________________________________________________________________________________________
if __name__ == '__main__':
    app.run(debug=True)