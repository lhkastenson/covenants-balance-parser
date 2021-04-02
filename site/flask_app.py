from flask import Flask, render_template, flash, request, redirect, url_for, session
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField, FloatField, Field
import json

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class TokenForm(Form):
    symbol = Field('symbol', validators=[validators.required(message = "Symbol is required")])
    price = FloatField('price', validators=[validators.Required(message = "Price is required (number)"), validators.NumberRange(min = 0, message = "Price must be a number greater than zero")])
    liquidity = FloatField('liquidity', validators=[validators.Required(message = "Liquidity is required (number)"), validators.NumberRange(min = 0, message = "Liquidity must be a number greater than zero")])
    fees = FloatField('fees', validators=[validators.Required(message = "Fees is required (number)"), validators.NumberRange(min = 0, message = "Fees must be a number greater than zero")])
    @app.route('/add_token', methods=['POST'])
    def add_token():
        form = TokenForm(request.form)
        if form.validate():
            symbol = request.form['symbol']
            price = request.form['price']
            liquidity = request.form['liquidity']
            fees = request.form['fees']
            if 'tokens' in session:
                tokens = session['tokens']
            else:
                tokens = {}
            tokens.update({symbol: {'price': price, 'liquidity': liquidity, 'fees': fees}})
            session['tokens'] = tokens
        else:
            flash(f'Error! {form.errors}')

        return redirect(url_for('main'))

class BalanceForm(Form):
    balances = TextAreaField('Balances:', validators=[validators.required(message = "Balance input required.")])
    @app.route("/form", methods=['GET', 'POST'])
    def main():
        def parseBalances(price, balances):
            tokenKeys = list(price.keys())

            data = {}
            for i in tokenKeys:
                data.update({i:{'daily':0,'available':0,'uniPool':0,'totalPool':0,'dailyUSD':0,'availableUSD':0,'uniFarmUSD':0}})

            lines=balances.split('\n')

            for nl,l in enumerate(lines):
                if 'Locked Farming' in l:
                    farm='Locked'
                    exchange=lines[nl][len('Locked Farming '):]
                    amountx=lines[nl+10].split(')Metamask')[0].split('(')[-1].split(' - ')[0].split(' ')
                    amounty=lines[nl+10].split(')Metamask')[0].split('(')[-1].split(' - ')[1].split(' ')
                    amounts={a[1]:float(a[0].replace(',','')) for a in (amountx,amounty)}
                    for a in (amountx[1],amounty[1]):
                        if a!='ETH': token=a
                    available=[lines[nl+11].split('Available')[1].split(' ')[1],token]
                    data[token]['totalPool']+=amounts[token]
                    if 'UniswapV2' in exchange:data[token]['uniPool']+=amounts[token]
                    data[token]['available']+=float(available[0].replace(',',''))

                if 'Free Farming' in l:
                    farm='Free'
                    exchange=lines[nl][len('Free Farming '):]
                    amountx=lines[nl+4].split('Deposit: ')[1].split('Farm')[0].split('- ')[1].split(' ')[:2]
                    amounty=lines[nl+4].split('Deposit: ')[1].split('Farm')[0].split('- ')[1].split(' ')[2:]
                    amounts={a[1]:float(a[0].replace(',','')) for a in (amountx,amounty)}
                    for a in (amountx[1],amounty[1]):
                        if a!='ETH': token=a
                    z=lines[nl+4].split('Earnings')[1].split('Available')
                    daily=z[0].split(' ')[1:]
                    available=z[1].split('TransferClaim')[0].split(' ')[1:]
                    data[token]['totalPool']+=amounts[token]
                    if 'UniswapV2' in exchange:data[token]['uniPool']+=amounts[token]
                    data[available[1]]['available']+=float(available[0].replace(',',''))
                    data[daily[1]]['daily']+=float(daily[0].replace(',',''))

            totalAvailableUSD=0
            totalDailyRewardUSD=0
            totalUniFarmUSD=0
            totalStakedUSD=0
            daily = ''

            print(f"#$$$ tokenKeys {tokenKeys}")
            for i in tokenKeys:
                data[i]['dailyUSD']=data[i]['daily']*float(price[i]['price'])
                data[i]['availableUSD']=data[i]['available']*float(price[i]['price'])
                data[i]['uniFarmUSD']=data[i]['uniPool']*float(price[i]['price'])*2*float(price[i]['fees'])/float(price[i]['liquidity'])
                totalAvailableUSD+=data[i]['availableUSD']
                totalDailyRewardUSD+=data[i]['dailyUSD']
                totalUniFarmUSD+=data[i]['uniFarmUSD']
                totalStakedUSD+=data[i]['totalPool']*float(price[i]['price'])*2
                daily += f'{i} \n'
                daily += f'{"daily":15}{data[i]["daily"]}\n'
                for x in ['available','uniPool','totalPool','dailyUSD','availableUSD','uniFarmUSD']:
                    daily += f'{x:15}{data[i][x]}\n'
                daily += '\n*********************\n'

            totals = f'*******TOTALS********\n'
            totals += f'{"staked":15}${totalStakedUSD}\n'
            totals += f'{"daily reward":15}${totalDailyRewardUSD}\n'
            totals += f'{"daily farm":15}${totalUniFarmUSD}\n'
            totals += f'{"daily total":15}${totalDailyRewardUSD+totalUniFarmUSD}\n'
            totals += f'{"available":15}${totalAvailableUSD}\n'
            return (daily, totals)

        form = BalanceForm(request.form)
        if 'tokens' in session:
            tokens = session['tokens']
        else:
            tokens = {}

        if request.method == 'POST':
            if len(tokens) > 0:
                tokenPrices = tokens
                balances = request.form['balances']

                if form.validate():
                    result = parseBalances(tokenPrices, balances)
                    flash(f'{result[0]} {result[1]}')
                else:
                    flash('Error! {form.errors}')
            else:
                flash('Error! Add some tokens first')

        return render_template('form.html', form=form)
