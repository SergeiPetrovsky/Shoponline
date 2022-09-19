from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import desc

from cloudipsp import Api, Checkout

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
    url = db.Column(db.String(300))
    is_active = db.Column(db.Boolean, default=True)
    num_in_stock = db.Column(db.Integer, nullable=False)  # количество на складе
    num_of_purch = db.Column(db.Integer)   #  число продаж
    discount = db.Column(db.Integer)    # Скидка

    # def __repr__(self):
    #     return 'Запись'

@app.route('/')
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
            url = request.form['url']
            discount = request.form['discount']

            num_in_stock = request.form['num_in_stock']

            item = Item(title=title, description=description, price=price, url=url,
                        num_in_stock=num_in_stock, discount=discount)
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


@app.route('/stock')
def stock():
    goods = Item.query.all()
    return render_template('stock.html', title='Акции', goods=goods)

@app.route('/popular')
def popular():
    return render_template('popular.html', title='Выбор покупателей')

@app.route('/new')
def new():
    today = date.today()
    goods = Item.query.all()
    return render_template('new.html', title='Новинки', today=today, goods=goods)

# @app.route('/buy/<int:id>')
# def buy(id):
#     item = Item.query.get(id)
#
#     api = Api(merchant_id=1396424,
#               secret_key='test')
#     checkout = Checkout(api=api)
#     data = {
#         "currency": "BYN",
#         "amount": item.price * 100
#     }
#     url = checkout.url(data).get('checkout_url')
#     return redirect(url)

def payment_imitation(e_mail, card_num, cvv2, sum):   # ИМИТАЦИЯ ОПЛАТЫ ТОВАРА
    if e_mail and card_num and cvv2 and sum:
        return True
    else:
        return False

@app.route('/buy/<int:id>',methods=['POST','GET'] )
def buy(id):
    item = Item.query.get(id)
    if request.method == "POST":
            Email = request.form['Email']
            card_num = request.form['card_num']
            price = int(request.form['price'])
            cvv2 = request.form['cvv2']

            if payment_imitation(Email, card_num, cvv2, price):
                item.num_in_stock = item.num_in_stock - 1
                db.session.commit()

                return render_template('message.html', item=item)
            else:
                return 'Оплата не прошла'

    else:
        return render_template('my_payment.html', title='Оплата товара', item=item)



@app.route('/buy-discount/<int:id>')
def buy_discount(id):
    item = Item.query.get(id)

    api = Api(merchant_id=1396424,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "BYN",
        "amount": item.price * (100 - item.discount)
    }
    url = checkout.url(data).get('checkout_url')
    return redirect(url)
#________________________________________________________________________________________________________
if __name__ == '__main__':
    app.run(debug=True)