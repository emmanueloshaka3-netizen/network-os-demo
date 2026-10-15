from flask import Flask, request, render_template_string
import os
from datetime import datetime

app = Flask(__name__)

USERS = {
    "admin": {"pw": "admin123", "role": "Admin", "files": ["salary.xlsx", "exam.pdf", "public.txt"]},
    "student1": {"pw": "class2024", "role": "Student", "files": ["public.txt"]},
    "guest": {"pw": "guest", "role": "Guest", "files": []},
}

LOGS = []

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{font-family: Arial; padding:15px; background:#f4f4f4}
.box{background:white; padding:15px; border-radius:10px; margin-bottom:10px}
.success{color:green; font-weight:bold}
.fail{color:red; font-weight:bold}
pre{background:black; color:lime; padding:10px; border-radius:5px; height:200px; overflow:auto}
input,select{padding:8px; margin:5px}
</style>
</head>
<body>
<!-- dev note: remove /admin debug page before launch -->
<div class="box">
<h2>🏢 COMPANY SERVER - Network OS Live Demo</h2>
<p><b>Firewall:</b> BYPASSED (you are inside the network via public link)</p>
<p><b>Network OS:</b> Checking identity &amp; authorization...</p>
</div>
<div class="box">
<form method="GET">
Username: <input name="user" value="student1">
Password: <input name="pw" value="class2024">
File: <select name="file">
<option>salary.xlsx</option>
<option>exam.pdf</option>
<option>public.txt</option>
</select>
<input type="submit" value="Request File">
</form>
<hr>
<h3 class="{{cls}}">{{result}}</h3>
<p><b>Current User Role:</b> {{role}}</p>
</div>
<div class="box">
<h4>📜 Live Server Logs:</h4>
<pre>{{logs}}</pre>
<p><small>Class demo - fake files only. RBAC simulation.</small></p>
</div>
</body>
</html>
"""

@app.route('/')
def home():
    user = request.args.get('user')
    pw = request.args.get('pw')
    file = request.args.get('file')

    result = "Try to get salary.xlsx as student1 - can you bypass the Network OS?"
    cls = ""
    role = "Not logged in"

    if user:
        t = datetime.now().strftime("%H:%M:%S")
        LOGS.append(f"[{t}] {user} -> {file}")
        if len(LOGS) > 20:
            LOGS.pop(0)

        if user not in USERS or USERS[user]['pw'] != pw:
            result = "❌ BLOCKED by Network OS: invalid login"
            cls = "fail"
            LOGS[-1] += " ❌ INVALID LOGIN"
        else:
            role = USERS[user]['role']
            if file in USERS[user]['files']:
                result = f"✅ GRANTED: {user} ({role}) can read {file}"
                cls = "success"
                LOGS[-1] += " ✅ GRANTED"
            else:
                result = f"❌ BLOCKED: {user} ({role}) is NOT authorized for {file}. This is RBAC!"
                cls = "fail"
                LOGS[-1] += " ❌ DENIED"

    return render_template_string(HTML, result=result, cls=cls, role=role, logs="\n".join(reversed(LOGS)))


FLAG = "FLAG{rbac_bypassed_by_trusting_the_client}"

@app.route('/robots.txt')
def robots():
    return "User-agent: *\nDisallow: /admin\n", 200, {"Content-Type": "text/plain"}

@app.route('/admin')
def admin():
    # DELIBERATE WEAKNESS: trusts a role sent by the client
    if request.args.get('role') == 'admin':
        LOGS.append(f"[{datetime.now().strftime('%H:%M:%S')}] !!! /admin accessed")
        return f"<h2>Admin Panel</h2><p>You bypassed the Network OS. {FLAG}</p><p>Fix: never trust the client; check the role on the server.</p>"
    return "<h2>Admin Panel</h2><p>Access denied. Role required.</p>", 403

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
