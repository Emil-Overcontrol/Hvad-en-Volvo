from flask import Flask, jsonify, render_template

app = Flask(__name__, template_folder='Templates', static_folder='Static')


@app.route('/')
def index():
    return render_template('Index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello, World!"})

if __name__ == '__main__':
    app.run(debug=True)