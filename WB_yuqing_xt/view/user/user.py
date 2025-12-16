from flask import Blueprint, render_template, request, jsonify

# 创建用户蓝图
ub = Blueprint('user', __name__)

@ub.route('/user/profile')
def user_profile():
    """用户资料页面"""
    return render_template('user_profile.html')

@ub.route('/user/settings')
def user_settings():
    """用户设置页面"""
    return render_template('user_settings.html')

@ub.route('/api/user/profile')
def get_user_profile():
    """获取用户资料API"""
    # 模拟用户数据
    return jsonify({
        'username': 'admin',
        'email': 'admin@example.com',
        'role': 'administrator',
        'created_at': '2024-01-01T00:00:00'
    })

@ub.route('/api/user/update', methods=['POST'])
def update_user_profile():
    """更新用户资料API"""
    data = request.get_json()
    # 这里应该有实际的更新逻辑
    return jsonify({'success': True, 'message': '更新成功'})