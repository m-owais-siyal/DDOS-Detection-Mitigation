from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import sys

sys.path.append('../../controller')
from controller import SimpleMonitor13

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
ryu_controller = SimpleMonitor13()

basedir = os.path.abspath(os.path.dirname(__file__))
csv_file_path = os.path.join(basedir, '../../controller/AllFlowStatsfile.csv')
alert_status = {'alert': False, 'message': ''}

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/api/flow_stats', methods=['GET'])
def get_flow_stats():
    flow_stats = ryu_controller.get_flow_stats()
    return jsonify(flow_stats)

@app.route('/api/ddos_alert', methods=['GET'])
def get_ddos_alert():
    return jsonify(alert_status)

@app.route('/api/update_alert', methods=['POST'])
def update_alert():
    global alert_status
    data = request.json
    alert_status = {'alert': data['alert'], 'message': data['message']}
    return jsonify({'status': 'success'})

@app.route('/api/update_alert1', methods=['POST'])
def update_alert1():
    global alert_status
    data = request.json
    alert_status['alert'] = data['alert']
    alert_status['message'] = data['message']
    return jsonify({'status': 'success'})

@app.route('/api/get_headers', methods=['GET'])
def get_headers():
    try:
        data = pd.read_csv(csv_file_path)
        headers = list(data.columns)
        return jsonify(headers)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/data_visualization', methods=['GET'])
def data_visualization():
    header = request.args.get('header')
    if not header:
        return jsonify({"error": "No header specified"}), 400
    
    try:
        data = pd.read_csv(csv_file_path)
        if header not in data.columns:
            return jsonify({"error": "Column not found"}), 404
        
        # Count occurrences of each value in the column
        value_counts = data[header].value_counts().to_dict()
        return jsonify(value_counts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/historical_data', methods=['GET'])
def get_historical_data():
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 30))
        sort_by = request.args.get('sort_by', 'timestamp')
        sort_order = request.args.get('sort_order', 'asc')

        data = pd.read_csv(csv_file_path, index_col=False)

        search_term = request.args.get('search', '')
        if search_term:
            import re
            pattern = re.compile(r'\s(AND|OR)\s')
            parts = pattern.split(search_term)
            conditions = [parts[0].strip()]
            operators = []

            for part in parts[1:]:
                if part.upper() in ['AND', 'OR']:
                    operators.append(part.upper())
                else:
                    conditions.append(part.strip())

            results = None
            for index, condition in enumerate(conditions):
                column, value = condition.split('=')
                column, value = column.strip(), value.strip()
                if column in data.columns:
                    current_result = data[column].astype(str).str.contains(value, case=False)
                else:
                    return jsonify({"error": f"Column '{column}' not found in CSV"}), 404

                if results is None:
                    results = current_result
                elif operators[index - 1] == 'AND':
                    results &= current_result
                elif operators[index - 1] == 'OR':
                    results |= current_result

            data = data[results]

        data.sort_values(by=sort_by, ascending=sort_order == 'asc', inplace=True)
        start = (page - 1) * per_page
        end = start + per_page
        paginated_data = data.iloc[start:end]

        return jsonify(paginated_data.to_dict(orient='records')), 200
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
