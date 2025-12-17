from flask import Flask, render_template, request, jsonify, session
import uuid
import os
from flask_cors import CORS

# 初始化Flask应用
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dino-2025-1217')  # 随机密钥，可自定义
CORS(app, supports_credentials=True)  # 开启跨域

# 本地存储游戏实例（Vercel测试用，生产建议换Redis）
game_instances = {}

# 恐龙游戏核心类（纯手写，无外部依赖）
class DinoGame:
    def __init__(self, player_name):
        self.player_name = player_name
        self.score = 0
        self.is_jumping = False  # 是否跳跃
        self.is_ducking = False  # 是否蹲下
        self.game_over = False   # 游戏是否结束

    def start(self):
        """初始化游戏状态"""
        self.score = 0
        self.is_jumping = False
        self.is_ducking = False
        self.game_over = False

    def update_frame(self):
        """每帧更新（模拟游戏运行）"""
        if not self.game_over:
            self.score += 1  # 每帧加1分
            # 简单碰撞模拟：分数到500随机结束游戏（测试用）
            if self.score % 500 == 0 and self.score > 0:
                self.game_over = True

    def jump_action(self):
        """跳跃操作（防止连续跳）"""
        if not self.is_jumping and not self.game_over:
            self.is_jumping = True
            return True
        return False

    def duck_action(self, is_ducking):
        """蹲下/起身操作"""
        if not self.game_over:
            self.is_ducking = is_ducking

    def get_status(self):
        """返回当前游戏状态（给前端）"""
        return {
            "name": self.player_name,
            "score": self.score,
            "jumping": self.is_jumping,
            "ducking": self.is_ducking,
            "over": self.game_over
        }

# ------------------- 接口路由 -------------------
@app.route('/')
def home():
    """游戏主页（渲染前端）"""
    return render_template('index.html')

@app.route('/api/start-game', methods=['POST'])
def start_game():
    """开始新游戏"""
    try:
        player_name = request.json.get('name', '匿名玩家')
        game_id = str(uuid.uuid4())[:6]  # 生成短游戏ID
        game = DinoGame(player_name)
        game.start()
        game_instances[game_id] = game
        session['game_id'] = game_id  # 绑定到用户会话
        return jsonify({
            "success": True,
            "game_id": game_id,
            "status": game.get_status()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/update', methods=['POST'])
def update_game():
    """更新游戏帧状态"""
    try:
        game_id = session.get('game_id')
        if not game_id or game_id not in game_instances:
            return jsonify({"success": False, "error": "游戏未开始"}), 404
        game = game_instances[game_id]
        game.update_frame()
        # 模拟跳跃落地（每帧重置，实际由前端控制）
        if game.is_jumping:
            game.is_jumping = False
        return jsonify({"success": True, "status": game.get_status()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/jump', methods=['POST'])
def jump():
    """恐龙跳跃"""
    try:
        game_id = session.get('game_id')
        if not game_id or game_id not in game_instances:
            return jsonify({"success": False, "error": "游戏未开始"}), 404
        game = game_instances[game_id]
        jump_ok = game.jump_action()
        return jsonify({"success": True, "jump_ok": jump_ok, "status": game.get_status()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/duck', methods=['POST'])
def duck():
    """恐龙蹲下/起身"""
    try:
        game_id = session.get('game_id')
        if not game_id or game_id not in game_instances:
            return jsonify({"success": False, "error": "游戏未开始"}), 404
        is_ducking = request.json.get('duck', False)
        game = game_instances[game_id]
        game.duck_action(is_ducking)
        return jsonify({"success": True, "status": game.get_status()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/restart', methods=['POST'])
def restart_game():
    """重新开始游戏"""
    try:
        game_id = session.get('game_id')
        player_name = game_instances[game_id].player_name if game_id in game_instances else "匿名玩家"
        # 重建游戏实例
        new_game = DinoGame(player_name)
        new_game.start()
        if game_id:
            game_instances[game_id] = new_game
        else:
            game_id = str(uuid.uuid4())[:6]
            game_instances[game_id] = new_game
            session['game_id'] = game_id
        return jsonify({"success": True, "status": new_game.get_status()})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Vercel部署必须的WSGI入口
application = app

# 本地运行配置
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)