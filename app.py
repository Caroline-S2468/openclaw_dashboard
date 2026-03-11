from flask import Flask, jsonify, send_from_directory
import os
from datetime import datetime

app = Flask(__name__, static_folder='static')

# 自动创建前端 HTML
def create_html():
    os.makedirs('static', exist_ok=True)
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OpenClaw Monitor Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body { font-family: system-ui, -apple-system, sans-serif; background: #f3f4f6; }
.card { background: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 16px; }
.stat-value { font-size: 2rem; font-weight: bold; color: #3b82f6; }
.task-todo { border-left: 4px solid #9ca3af; }
.task-progress { border-left: 4px solid #3b82f6; }
.task-done { border-left: 4px solid #10b981; }
.task-stuck { border-left: 4px solid #ef4444; }
.agent-idle { background: #d1fae5; border: 2px solid #10b981; }
.agent-busy { background: #dbeafe; border: 2px solid #3b82f6; }
.agent-stuck { background: #fee2e2; border: 2px solid #ef4444; }
</style>
</head>
<body class="bg-gray-50 min-h-screen">
<div class="max-w-7xl mx-auto px-4 py-8">
  <header class="mb-8">
    <h1 class="text-3xl font-bold text-gray-900">🤖 OpenClaw Monitor Dashboard</h1>
    <p class="text-gray-600 mt-2">Real-time Task & Agent Monitoring</p>
  </header>

  <div id="loading" class="text-center py-12">
    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
    <p class="text-gray-600">Loading dashboard...</p>
  </div>

  <div id="dashboard" style="display:none;">
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="card text-center">
        <div class="stat-value" id="stat-tasks">-</div>
        <div class="text-gray-600 text-sm">Total Tasks</div>
      </div>
      <div class="card text-center">
        <div class="stat-value text-green-600" id="stat-agents">-</div>
        <div class="text-gray-600 text-sm">Agents</div>
      </div>
      <div class="card text-center">
        <div class="stat-value text-purple-600" id="stat-skills">-</div>
        <div class="text-gray-600 text-sm">Skills</div>
      </div>
      <div class="card text-center">
        <div class="stat-value text-indigo-600" id="stat-completion">-%</div>
        <div class="text-gray-600 text-sm">Completion</div>
      </div>
    </div>

    <div class="card">
      <h2 class="text-xl font-bold mb-4">📋 Tasks by Status</h2>
      <div id="tasks-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4"></div>
    </div>

    <div class="card">
      <h2 class="text-xl font-bold mb-4">👥 Agents Status</h2>
      <div id="agents-container" class="grid grid-cols-1 md:grid-cols-3 gap-4"></div>
    </div>

    <div class="card">
      <h2 class="text-xl font-bold mb-4">🧩 Skills</h2>
      <div id="skills-container"></div>
    </div>
  </div>
</div>

<script>
function renderDashboard(data) {
  if (!data.success) {
    document.getElementById('loading').innerHTML = '<p class="text-red-600">Error loading data</p>';
    return;
  }

  document.getElementById('loading').style.display = 'none';
  document.getElementById('dashboard').style.display = 'block';

  const s = data.stats;
  document.getElementById('stat-tasks').textContent = s.total_tasks;
  document.getElementById('stat-agents').textContent = s.total_agents;
  document.getElementById('stat-skills').textContent = s.total_skills;
  document.getElementById('stat-completion').textContent = s.completion_rate + '%';

  const tbs = data.tasks_by_status;
  const columns = [
    {key: 'todo', title: 'To Do', class: 'task-todo'},
    {key: 'in_progress', title: 'In Progress', class: 'task-progress'},
    {key: 'done', title: 'Done', class: 'task-done'},
    {key: 'stuck', title: 'Stuck', class: 'task-stuck'}
  ];

  let tasksHtml = '';
  columns.forEach(col => {
    const tasks = tbs[col.key] || [];
    tasksHtml += '<div><h3 class="font-bold mb-2 text-gray-700">' + col.title + ' (' + tasks.length + ')</h3>';
    tasks.forEach(t => {
      const priorityColor = t.priority === 'high' ? 'text-red-600' : t.priority === 'medium' ? 'text-yellow-600' : 'text-green-600';
      tasksHtml += '<div class="card ' + col.class + ' mb-2 p-3">';
      tasksHtml += '<div class="font-medium">' + t.title + '</div>';
      tasksHtml += '<div class="w-full bg-gray-200 rounded-full h-2 mt-2"><div class="bg-blue-500 h-2 rounded-full" style="width:' + t.progress + '%"></div></div>';
      tasksHtml += '<div class="text-xs mt-1 ' + priorityColor + '">' + t.progress + '% | ' + t.priority + ' | ' + (t.agent_name || 'Unassigned') + '</div>';
      tasksHtml += '</div>';
    });
    tasksHtml += '</div>';
  });
  document.getElementById('tasks-container').innerHTML = tasksHtml;

  let agentsHtml = '';
  data.agents.forEach(a => {
    const statusClass = a.status === 'idle' ? 'agent-idle' : a.status === 'busy' ? 'agent-busy' : 'agent-stuck';
    const icon = a.status === 'idle' ? '🟢' : a.status === 'busy' ? '🔵' : '🔴';
    agentsHtml += '<div class="' + statusClass + ' rounded-lg p-4">';
    agentsHtml += '<div class="flex items-center mb-2"><span class="text-2xl mr-2">' + icon + '</span><span class="font-bold">' + a.name + '</span></div>';
    agentsHtml += '<div class="text-sm text-gray-600">Status: ' + a.status + '</div>';
    if (a.current_task) agentsHtml += '<div class="text-sm text-gray-600">Task: ' + a.current_task_title + '</div>';
    agentsHtml += '<div class="text-xs text-gray-500 mt-1">Skills: ' + a.skills.slice(0, 3).join(', ') + '</div>';
    agentsHtml += '</div>';
  });
  document.getElementById('agents-container').innerHTML = agentsHtml;

  let skillsHtml = '<div class="overflow-x-auto"><table class="w-full text-left"><thead><tr class="border-b"><th class="pb-2">Skill</th><th class="pb-2">Category</th><th class="pb-2">Agents</th></tr></thead><tbody>';
  data.skills.forEach(s => {
    skillsHtml += '<tr class="border-b border-gray-100"><td class="py-3 font-medium">' + s.name + '</td><td class="py-3"><span class="inline-block bg-gray-200 px-3 py-1 rounded-full text-sm">' + s.category + '</span></td><td class="py-3">' + s.agents_having.join(', ') + '</td></tr>';
  });
  skillsHtml += '</tbody></table></div>';
  document.getElementById('skills-container').innerHTML = skillsHtml;
}

fetch('/api/dashboard').then(r => r.json()).then(renderDashboard).catch(err => {
  document.getElementById('loading').innerHTML = '<p class="text-red-600">Error: ' + err.message + '</p>';
});
</script>
</body>
</html>'''
    with open('static/index.html', 'w') as f:
        f.write(html)

# 数据
def get_data():
    return {
        "tasks": [
            {"id": "1", "title": "Research competitors", "status": "in_progress", "progress": 45, "priority": "high", "agent_name": "Claw-Master", "agent_id": "a1"},
            {"id": "2", "title": "Draft email campaign", "status": "todo", "progress": 0, "priority": "medium"},
            {"id": "3", "title": "Code review PR #234", "status": "done", "progress": 100, "priority": "high", "agent_name": "Code-Helper", "agent_id": "a2"},
            {"id": "4", "title": "Fix database connection bug", "status": "stuck", "progress": 20, "priority": "critical", "agent_name": "Claw-Master", "agent_id": "a1"}
        ],
        "agents": [
            {"id": "a1", "name": "Claw-Master", "status": "busy", "current_task": "Research competitors", "current_task_title": "Research competitors", "skills": ["web_search", "coding", "analysis"], "total_tasks_completed": 42, "uptime_minutes": 360},
            {"id": "a2", "name": "Code-Helper", "status": "idle", "current_task": None, "skills": ["coding", "debugging", "git"], "total_tasks_completed": 28, "uptime_minutes": 240},
            {"id": "a3", "name": "Writer-Bot", "status": "stuck", "current_task": "Fix database connection bug", "current_task_title": "Fix database connection bug", "skills": ["writing", "translation"], "total_tasks_completed": 15, "uptime_minutes": 120}
        ],
        "skills": [
            {"name": "web_search", "description": "Search the web for information", "category": "research", "enabled": True, "used_count": 156, "agents_having": ["Claw-Master"]},
            {"name": "coding", "description": "Write and review code", "category": "development", "enabled": True, "used_count": 89, "agents_having": ["Claw-Master", "Code-Helper"]},
            {"name": "analysis", "description": "Analyze data and reports", "category": "research", "enabled": True, "used_count": 67, "agents_having": ["Claw-Master"]},
            {"name": "writing", "description": "Write and edit content", "category": "content", "enabled": True, "used_count": 134, "agents_having": ["Writer-Bot"]},
            {"name": "debugging", "description": "Debug code issues", "category": "development", "enabled": True, "used_count": 52, "agents_having": ["Code-Helper"]}
        ],
        "stats": {
            "total_tasks": 4,
            "total_agents": 3,
            "total_skills": 5,
            "completion_rate": 25.0,
            "task_status": {"todo": 1, "in_progress": 1, "done": 1, "stuck": 1},
            "agent_status": {"idle": 1, "busy": 1, "stuck": 1},
            "system_status": "connected",
            "last_updated": datetime.now().isoformat()
        }
    }

@app.route('/api/dashboard')
def dashboard():
    data = get_data()
    tasks_by_status = {"todo": [], "in_progress": [], "done": [], "stuck": []}
    for t in data["tasks"]:
        if t["status"] in tasks_by_status:
            tasks_by_status[t["status"]].append(t)
    return jsonify({
        "success": True,
        "tasks_by_status": tasks_by_status,
        "agents": data["agents"],
        "skills": data["skills"],
        "stats": data["stats"]
    })

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "openclaw_connected": True})

@app.route('/')
def index():
    create_html()  # 确保 HTML 文件存在
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    create_html()  # 启动时创建前端文件
    print("Starting OpenClaw Dashboard on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)