import uuid
import hashlib
import sqlite3
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# 数据库配置
DATABASE = 'activation_keys.db'

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """初始化数据库，创建激活码表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activation_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_key TEXT NOT NULL UNIQUE,
            product_name TEXT NOT NULL,
            created_at TIMESTAMP,
            is_used BOOLEAN DEFAULT 0,
            used_at TIMESTAMP,
            response_key TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("数据库初始化完成")

def generate_response_key(machine_code, product_name):
    """生成返回给前端使用的密钥"""
    input_code = machine_code + product_name
    response_key = hashlib.md5(input_code.encode()).hexdigest()
    return response_key



@app.route('/add_product', methods=['POST'])
def add_product():
    """添加激活码到数据库"""
    try:
        data = request.get_json()
        product_key = data.get('product_key')
        product_name = data.get('product_name')
        
        if not product_key or not product_name:
            return jsonify({
                'success': False,
                'message': '缺少必要参数：product_key 或 product_name'
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO activation_keys (product_key, product_name, created_at) VALUES (?, ?, ?)',
                (product_key, product_name, datetime.now())
            )
            conn.commit()
            conn.close()
            
            return jsonify({
                'success': True,
                'message': '激活码添加成功',
                'product_key': product_key,
                'product_name': product_name
            }), 200
            
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({
                'success': False,
                'message': '激活码已存在'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

@app.route('/verify_product_key', methods=['POST'])
def verify_product_key():
    """验证激活码并生成响应密钥"""
    try:
        data = request.get_json()
        product_key = data.get('product_key')
        product_name = data.get('product_name')
        machine_code = data.get("machine_code")
        
        if not product_key or not product_name:
            return jsonify({
                'success': False,
                'message': '异常请求',
                'response_key': None
            }), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询激活码是否存在
        cursor.execute(
            'SELECT * FROM activation_keys WHERE product_key = ? AND product_name = ?',
            (product_key, product_name)
        )
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return jsonify({
                'success': False,
                'message': '无效激活码',
                'response_key': None
            }), 404
        
        # 检查是否已使用
        if result['is_used']:
            conn.close()
            return jsonify({
                'success': False,
                'message': '激活码已被使用',
                'response_key': result['response_key']
            }), 400
        
        # 生成响应密钥
        print(product_key)
        print(product_name)
        response_key = generate_response_key(machine_code, product_name)
        
        # 标记为已使用并更新使用时间
        cursor.execute(
            'UPDATE activation_keys SET is_used = 1, used_at = ?, response_key = ? WHERE product_key = ?',
            (datetime.now(), response_key, product_key)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '激活码验证成功',
            'response_key': response_key
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}',
            'response_key': None
        }), 500



@app.route('/list_products', methods=['GET'])
def list_products():
    """列出所有激活码"""
    try:
        product_name = request.args.get('product_name')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if product_name:
            cursor.execute(
                'SELECT * FROM activation_keys WHERE product_name = ? ORDER BY created_at DESC',
                (product_name,)
            )
        else:
            cursor.execute('SELECT * FROM activation_keys ORDER BY created_at DESC')
        
        results = cursor.fetchall()
        conn.close()
        
        codes = []
        for row in results:
            codes.append({
                'id': row['id'],
                'product_key': row['product_key'],
                'product_name': row['product_name'],
                'created_at': row['created_at'],
                'is_used': bool(row['is_used']),
                'used_at': row['used_at'],
                'response_key': row['response_key']
            })
        
        return jsonify({
            'success': True,
            'count': len(codes),
            'codes': codes
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'服务器错误: {str(e)}'
        }), 500

if __name__ == '__main__':
    # 初始化数据库
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
