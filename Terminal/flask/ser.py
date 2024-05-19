import subprocess
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
processes = {}

@app.route('/')
def index():
    return "Hello, World!"

@app.route('/start_<service>', methods=['GET'])
def start_service(service):
    scripts = {
        'ryu': './start_ryu.sh',
        'mininet': './start_mininet.sh',
        'flask': './start_flask.sh',
        'react': './start_react.sh'
    }
    script = scripts.get(service)
    if script:
        proc = subprocess.Popen(script, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        processes[service] = proc
        return jsonify({'message': f'{service} started', 'pid': proc.pid}), 200
    else:
        return jsonify({'error': 'Invalid service name'}), 400

@app.route('/kill_<service>', methods=['GET'])
def kill_service(service):
    scripts = {
        'ryu': './kill_ryu.sh',
        'mininet': './kill_mininet.sh',
        'flask': './kill_flask.sh',
        'react': './kill_react.sh'
    }
    script = scripts.get(service)
    if script:
        result = subprocess.run(script, shell=True, capture_output=True, text=True)
        return jsonify({'output': result.stdout, 'error': result.stderr, 'status': result.returncode}), 200
    else:
        return jsonify({'error': 'Invalid service name'}), 400


@app.route('/run_command', methods=['POST'])
def run_command():
    command = request.json.get('command')
    if not command:
        return jsonify({'error': 'No command provided'}), 400

    result = subprocess.run(['./run_mininet_command.sh', command], shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        return jsonify({'output': result.stdout}), 200
    else:
        return jsonify({'error': result.stderr.strip() or "Unknown error", 'status': result.returncode}), 500




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5100)
