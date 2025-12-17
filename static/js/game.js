// 全局变量
let gameRunning = false;
let gameInterval = null;
let isDucking = false;

// DOM元素
const startBtn = document.getElementById('startBtn');
const restartBtn = document.getElementById('restartBtn');
const jumpBtn = document.getElementById('jumpBtn');
const duckBtn = document.getElementById('duckBtn');
const playerNameInput = document.getElementById('playerName');
const scoreSpan = document.getElementById('score');
const gameStatus = document.getElementById('gameStatus');
const dino = document.getElementById('dino');
const obstacle = document.getElementById('obstacle');

// 开始游戏
startBtn.addEventListener('click', async () => {
    const playerName = playerNameInput.value.trim() || '匿名玩家';
    // 调用后端开始游戏接口
    const res = await fetch('/api/start-game', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: playerName })
    });
    const data = await res.json();
    if (data.success) {
        gameRunning = true;
        startBtn.style.display = 'none';
        restartBtn.style.display = 'inline-block';
        gameStatus.textContent = '游戏中...';
        obstacle.style.display = 'block';
        // 每100ms更新一次游戏状态
        gameInterval = setInterval(updateGame, 100);
    } else {
        alert('开始游戏失败：' + data.error);
    }
});

// 重新开始游戏
restartBtn.addEventListener('click', async () => {
    const res = await fetch('/api/restart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    if (data.success) {
        scoreSpan.textContent = '0';
        gameStatus.textContent = '游戏中...';
        dino.classList.remove('duck');
        isDucking = false;
        obstacle.style.display = 'block';
        gameRunning = true;
        clearInterval(gameInterval);
        gameInterval = setInterval(updateGame, 100);
    } else {
        alert('重启游戏失败：' + data.error);
    }
});

// 跳跃操作
jumpBtn.addEventListener('click', jump);
document.addEventListener('keydown', (e) => {
    if (e.code === 'Space' && gameRunning) jump();
    if (e.code === 'ArrowDown' && gameRunning) toggleDuck(true);
});
document.addEventListener('keyup', (e) => {
    if (e.code === 'ArrowDown' && gameRunning) toggleDuck(false);
});

// 跳跃逻辑
async function jump() {
    if (!gameRunning) return;
    const res = await fetch('/api/jump', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    if (data.success && data.jump_ok) {
        // 前端视觉效果：跳跃
        dino.style.bottom = '80px';
        setTimeout(() => {
            dino.style.bottom = '0';
        }, 500);
    }
}

// 蹲下/起身逻辑
async function toggleDuck(duck = null) {
    if (!gameRunning) return;
    isDucking = duck !== null ? duck : !isDucking;
    const res = await fetch('/api/duck', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ duck: isDucking })
    });
    const data = await res.json();
    if (data.success) {
        if (isDucking) {
            dino.classList.add('duck');
        } else {
            dino.classList.remove('duck');
        }
    }
}

// 更新游戏状态
async function updateGame() {
    const res = await fetch('/api/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    });
    const data = await res.json();
    if (data.success) {
        scoreSpan.textContent = data.status.score;
        // 游戏结束处理
        if (data.status.over) {
            gameRunning = false;
            clearInterval(gameInterval);
            gameStatus.textContent = `游戏结束！最终分数：${data.status.score}`;
            obstacle.style.display = 'none';
        }
    } else {
        alert('更新游戏失败：' + data.error);
        clearInterval(gameInterval);
    }
}