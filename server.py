from flask import Flask, request, jsonify
from flask_cors import CORS
from main import process_query

app = Flask(__name__)
CORS(app)  # 로컬 테스트를 위해 CORS 활성화

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    input_text = data.get('text', '')
    department = data.get('department', 'all')  # 기본값: 전체
    result = process_query(input_text, department)  # main.py의 함수 호출
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)