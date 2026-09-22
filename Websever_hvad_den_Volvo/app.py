from flask import Flask, jsonify, render_template

if __package__:
    from .database import get_car_models, initialize_database
else:
    from database import get_car_models, initialize_database


app = Flask(__name__, static_folder="Static")
initialize_database()

@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"cars": get_car_models()})


@app.route('/api/cars', methods=['GET'])
def get_cars():
    return jsonify({"cars": get_car_models()})


@app.route('/api/cars/<model_name>', methods=['GET'])
def get_car(model_name):
    cars = get_car_models(model_name)
    if not cars:
        return jsonify({"error": "Car model not found"}), 404
    return jsonify(cars[0])

if __name__ == '__main__':
    app.run(debug=True)