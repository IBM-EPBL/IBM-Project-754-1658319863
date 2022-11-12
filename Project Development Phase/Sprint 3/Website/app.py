from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('homepage.html', title='Home', active_page='home')

@app.route('/intro')
def intro():
    return render_template('intro.html', title='Home', active_page='intro')

@app.route('/launch')
def launch():
    return render_template('homepage.html', title='Home', active_page='launch')

@app.route('/weather')
def weather():
    return render_template('weather.html', title='Weather Forecast', active_page='weather')

if __name__ == '__main__':
    app.run(debug=True)