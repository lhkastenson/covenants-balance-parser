from flask import Flask, render_template, flash, request, redirect, url_for, session
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
import json

# App config.
DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

class TokenPrice:
    def __init__(self, id, currentPrice, liquidity, fees):
        self.id = id
        self.currentPrice = currentPrice
        self.liquidity = liquidity
        self.fees = fees

    def __repr__(self):
        return self.id

class TokenPriceForm(Form):
    tokenId = TextField('tokenId', validators=[validators.required()])
    currentPrice = TextField('currentPrice', validators=[validators.required()])
    liquidity = TextField('liquidity', validators=[validators.required()])
    fees = TextField('fees', validators=[validators.required()])
    @app.route('/add_token', methods=['POST'])
    def add_token():
        import TokenPrice
        tokenPrice = TokenPrice(text=request.form['tokenPrice'], complete=False)
        session[f'{tokenPrice}-token'] = tokenPrice
        return redirect(url_for('main'))

class BalanceForm2(Form):
    prices = TextAreaField('Prices:', validators=[validators.required()])
    balances = TextAreaField('Balances:', validators=[validators.required()])
    @app.route("/form2", methods=['GET', 'POST'])
    def main2():
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
            for i in tokenKeys:
                data[i]['dailyUSD']=data[i]['daily']*float(price[i][0])
                data[i]['availableUSD']=data[i]['available']*float(price[i][0])
                data[i]['uniFarmUSD']=data[i]['uniPool']*float(price[i][0])*2*float(price[i][2])/float(price[i][1])
                totalAvailableUSD+=data[i]['availableUSD']
                totalDailyRewardUSD+=data[i]['dailyUSD']
                totalUniFarmUSD+=data[i]['uniFarmUSD']
                totalStakedUSD+=data[i]['totalPool']*float(price[i][0])*2
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
        print("hello")
        print(form.errors)
        if request.method == 'POST':
            prices = request.form['prices']
            balances = request.form['balances']

            if form.validate():
                result = parseBalances(json.loads(prices), balances)
                flash(f'{result[0]} {result[1]}')
            else:
                flash('Error! All the form fields are required. ')

        return render_template('form2.html', form=form)


class BalanceForm(Form):
    prices = TextAreaField('Prices:', validators=[validators.required()])
    balances = TextAreaField('Balances:', validators=[validators.required()])
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
            for i in tokenKeys:
                data[i]['dailyUSD']=data[i]['daily']*float(price[i][0])
                data[i]['availableUSD']=data[i]['available']*float(price[i][0])
                data[i]['uniFarmUSD']=data[i]['uniPool']*float(price[i][0])*2*float(price[i][2])/float(price[i][1])
                totalAvailableUSD+=data[i]['availableUSD']
                totalDailyRewardUSD+=data[i]['dailyUSD']
                totalUniFarmUSD+=data[i]['uniFarmUSD']
                totalStakedUSD+=data[i]['totalPool']*float(price[i][0])*2
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
        print("hello")
        print(form.errors)
        if request.method == 'POST':
            prices = request.form['prices']
            balances = request.form['balances']

            if form.validate():
                result = parseBalances(json.loads(prices), balances)
                flash(f'{result[0]} {result[1]}')
            else:
                flash('Error! All the form fields are required. ')

        return render_template('form.html', form=form)
