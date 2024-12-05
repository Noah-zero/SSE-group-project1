from flask import Flask, render_template, request, session
import pandas as pd
import akshare as ak
import yfinance as yf
from datetime import datetime, timedelta

def get_stock_data_with_name(file_path, symbol, start_date, end_date):
    stock_name_data = pd.read_csv(file_path, encoding="latin1")
    company_name = stock_name_data.loc[stock_name_data['symbol'] == symbol, 'name'].values
    if len(company_name) == 0:
        return 1 ## no company
    company_name = company_name[0]

    try:
        stock_data = ak.stock_us_daily(symbol=symbol, adjust="qfq")
        stock_data['date'] = pd.to_datetime(stock_data['date'])
        filtered_data = stock_data[(stock_data['date'] >= start_date) & (stock_data['date'] <= end_date)]
        filtered_data = filtered_data[['date', 'close']]
    except:
        try:
            stock_data = yf.download(symbol, start=start_date, end=end_date)
            stock_data.reset_index(inplace=True)
            filtered_data = stock_data[['Date', 'Close']]
            filtered_data.rename(columns={'Date': 'date', 'Close': 'close'}, inplace=True)
        except:
            return 2 ## no data 

    filtered_data['code'] = symbol
    filtered_data['name'] = company_name
    filtered_data = filtered_data[['name', 'code', 'date', 'close']]
    return filtered_data


app = Flask(__name__,
            static_url_path='/assets',
            static_folder='static/assets')

app.secret_key = 'aslkghioahgoahkvh'

@app.before_request
def before_request():
    session['cash'] = 50000
    session['stock_name'] = []
    session['stock_code'] = []
    session['stock_quantity'] = []
    session['average_initial_cost'] = []

@app.route("/")
def lets_play_a_game():
    return render_template("index.html")

@app.route("/first_day")
def first_day():
    cash = session.get('cash')
    stock_name = session.get('stock_name')
    stock_code = session.get('stock_code')
    stock_quantity = session.get('stock_quantity')
    average_initial_cost = session.get('average_initial_cost')
    return render_template("first_day.html",)

@app.route("/middle_day")
def middle_day():
    return render_template("middle_day.html")

@app.route("/search", methods=["POST"])
def search():
    labels = []
    values = []
    symbol = ""
    company_name = ""
    
    file_path = './blueprints/us_stock_name1.csv'
    symbol = request.form.get("symbol")
    date = request.form.get("date")  # Get stock symbol from form input
    current_date = datetime.strptime(date, "%Y-%m-%d")
    one_year_ago = current_date - timedelta(days=365)
    end_date = current_date.strftime("%Y-%m-%d")
    start_date = one_year_ago.strftime("%Y-%m-%d")

    if date == "2022-01-02":
        session['previous_page'] = "/first_day"

    previous_page = session.get('previous_page')

    stock_data = get_stock_data_with_name(file_path, symbol, start_date, end_date)

    if isinstance(stock_data, int):
        if stock_data == 1:
            return render_template('error.html',
                                error_code = 400,
                                error_message = "There is no such code in the US stock market.",
                                # return_url = previous_page
                                )
        elif stock_data == 2:
            return render_template('error.html',
                                error_code = 404,
                                error_message = "Sorry, we don't find price of this stock.",
                                # return_url = previous_page
                                )
    else: 
        labels = stock_data['date'].dt.strftime('%Y-%m-%d').tolist()
        values = stock_data['close'].tolist()
        company_name = stock_data['name'].iloc[0]  # Get company name

    return render_template(
        'chartjs-example.html',
        labels=labels,
        values=values,
        symbol=symbol,
        company_name=company_name,
        return_url = previous_page,
    )

@app.route("/buy_or_sell", methods=['GET'])
def buy_or_sell():
    number = request.args.get("number")
    action = request.args.get("action")
    previous_page = session.get('previous_page')

    try:
        if not number:
            return render_template("error.html", 
                error_code="400", 
                error_message="Number is required",)
            
        if action == "buy":
            # if True: ##check_buy()
            #     # update_info()
            #     print(previous_page)
            #     return render_template("result.html", 
            #         message = f"Bought {number} shares",
            #         return_url = previous_page,)
            # else:
            #     return render_template("error.html", 
            #     error_code="400", 
            #     error_message="You don't have enough money",)
            return render_template("error.html", 
            error_code="400", 
            error_message="You don't have enough money",)
            
        elif action == "sell":
            if True: ## check_sell()
                # update_info()
                return render_template("result.html", 
                    message = f"Sold {number} shares",
                    return_url = previous_page,)
            else:
                return render_template("error.html", 
                error_code="400", 
                error_message="You don't have enough stocks",)
                
    except Exception as e:
        return render_template("error.html", 
            error_code="500", 
            error_message=str(e))



# if __name__ == '__main__':
#     app.run(debug=True)