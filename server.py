from flask import Flask, request, jsonify
from flask_cors import CORS
from main import process_query

app = Flask(__name__)
CORS(app)  # 로컬 테스트를 위해 CORS 활성화

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    input_text = data.get('text', '')
    department_id = data.get('department', 'all')  # 기본값: 전체
    if department_id == 'all':
        department = '전체'
    elif department_id == 'computer_science':
        department = '컴퓨터공학과'
    elif department_id == 'ai_convergence':
        department = 'AI융합학과'
    else:
        return jsonify({'error': '잘못된 부서 선택입니다.'}), 400
    result = process_query(input_text, department)  # main.py의 함수 호출
    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True)