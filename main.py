from fastapi import FastAPI, Depends, HTTPException, status, Form
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
import hashlib
import secrets
import uvicorn

app = FastAPI(title="LMS Cloud Key Generator")

# ==========================================
# 🛑 1. ตั้งค่ารหัสผ่านเข้าเว็บ Gen Key ของทีมงาน
# ==========================================
TEAM_USERNAME = "admin"
TEAM_PASSWORD = "password123"  # แนะนำให้เปลี่ยนรหัสผ่านตรงนี้ครับ!

# 🛑 2. รหัสลับที่ใช้ผสมคีย์ (ต้องตรงกับโปรแกรมฝั่งลูกค้าเป๊ะๆ!)
SECRET_SALT = "MySchoolLMS_SuperSecret_2026"
# ==========================================

security = HTTPBasic()

def verify_team_member(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, TEAM_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, TEAM_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

def generate_license_key(machine_code: str) -> str:
    clean_code = machine_code.strip().upper()
    raw_key = hashlib.sha256((clean_code + SECRET_SALT).encode()).hexdigest()[:16].upper()
    return f"{raw_key[:4]}-{raw_key[4:8]}-{raw_key[8:12]}-{raw_key[12:]}"

@app.get("/", response_class=HTMLResponse)
def get_home(username: str = Depends(verify_team_member)):
    return f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NTY Cloud Keygen</title>
        <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body {{ font-family: 'Prompt', sans-serif; background-color: #0f172a; display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 100vh; margin: 0; color: white; padding: 20px; box-sizing: border-box; }}
            .card {{ background: #1e293b; padding: 40px; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.4); width: 100%; max-width: 400px; text-align: center; border: 1px solid #334155; }}
            h2 {{ margin-top: 0; color: #f8fafc; font-weight: 800; font-size: 24px; }}
            p {{ color: #94a3b8; font-size: 13px; margin-bottom: 25px; line-height: 1.5; }}
            input {{ width: 100%; padding: 15px; margin: 10px 0 20px 0; background: #0f172a; border: 2px solid #334155; border-radius: 12px; font-size: 18px; text-align: center; text-transform: uppercase; font-family: monospace; font-weight: bold; color: #38bdf8; outline: none; transition: border-color 0.3s; box-sizing: border-box; }}
            input:focus {{ border-color: #3b82f6; }}
            button {{ background-color: #3b82f6; color: white; border: none; padding: 15px 20px; font-size: 16px; font-weight: 600; border-radius: 12px; cursor: pointer; width: 100%; font-family: 'Prompt', sans-serif; transition: background-color 0.3s; box-sizing: border-box; }}
            button:hover {{ background-color: #2563eb; }}
            .btn-logout {{ background-color: #ef4444; margin-top: 15px; font-size: 14px; padding: 12px 20px; }}
            .btn-logout:hover {{ background-color: #dc2626; }}
            .result-box {{ margin-top: 25px; padding: 20px; background-color: #064e3b; border: 2px dashed #22c55e; border-radius: 12px; display: none; }}
            .result-title {{ font-size: 12px; color: #86efac; font-weight: 600; margin-bottom: 5px; }}
            #resultKey {{ font-size: 22px; font-weight: 800; color: #4ade80; letter-spacing: 2px; font-family: monospace; user-select: all; word-break: break-all; }}
            .welcome-box {{ margin-top: 25px; padding-top: 20px; border-top: 1px solid #334155; text-align: left; }}
            .welcome-text {{ font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; display: block; }}
            .copyright {{ font-size: 10px; color: #475569; margin-top: 30px; letter-spacing: 0.5px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>☁️ NTY Cloud Keygen</h2>
            <p>ระบบออก License Key<br>(สำหรับทีมงานติดตั้งเท่านั้น)</p>
            
            <input type="text" id="machineCode" placeholder="กรอกรหัสเครื่องลูกค้า" autocomplete="off" />
            <button onclick="generateKey()">ออกคีย์ปลดล็อกระบบ</button>
            
            <div id="resultBox" class="result-box">
                <div class="result-title">นำคีย์ด้านล่างกรอกที่เครื่องลูกค้า:</div>
                <div id="resultKey"></div>
            </div>
            
            <div class="welcome-box">
                <span class="welcome-text">Logged in as: <b style="color:#e2e8f0;">{username}</b></span>
                <button onclick="logout()" class="btn-logout">
                    <svg style="width: 16px; height: 16px; display: inline-block; vertical-align: text-bottom; margin-right: 5px;" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                    ออกจากระบบ (Logout)
                </button>
            </div>
        </div>

        <div class="copyright">Copyright © NTY Cloud Keygen MULTIMEDIA CO.,LTD</div>

        <script>
            async function generateKey() {{
                const codeInput = document.getElementById('machineCode');
                const code = codeInput.value.trim();
                if (!code) {{ alert('กรุณากรอกรหัสเครื่องลูกค้าก่อนครับ'); codeInput.focus(); return; }}
                
                try {{
                    const response = await fetch('/generate', {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
                        body: new URLSearchParams({{ 'machine_code': code }})
                    }});
                    
                    if (!response.ok) throw new Error('Network response was not ok');
                    
                    const data = await response.json();
                    document.getElementById('resultKey').innerText = data.key;
                    document.getElementById('resultBox').style.display = 'block';
                }} catch (error) {{
                    alert('เกิดข้อผิดพลาดในการสร้างคีย์ กรุณาลองใหม่');
                    console.error(error);
                }}
            }}

            function logout() {{
                if (confirm("คุณต้องการออกจากระบบใช่หรือไม่?")) {{
                    // 🌟 ทริค JavaScript: แอบส่ง Request ด้วย Username/Password ปลอมๆ ไปทับของเก่า
                    var xhr = new XMLHttpRequest();
                    xhr.open("GET", "/", true, "logout_user", "wrong_password");
                    xhr.send();
                    
                    xhr.onreadystatechange = function() {{
                        if (xhr.readyState == 4) {{
                            // เมื่อทับรหัสสำเร็จ ให้เปลี่ยนหน้าจอเป็นข้อความแจ้งเตือน
                            document.body.innerHTML = `
                                <div class="card" style="text-align: center;">
                                    <h2 style="margin-bottom: 10px;">👋 ออกจากระบบสำเร็จ</h2>
                                    <p style="color: #94a3b8; font-size: 14px; margin-bottom: 30px;">
                                        เซสชันของคุณถูกยกเลิกแล้ว<br>เพื่อความปลอดภัยสูงสุด กรุณาปิดแท็บหรือปิดเบราว์เซอร์นี้
                                    </p>
                                    <button onclick="window.location.href='/'" style="background-color: #3b82f6;">เข้าสู่ระบบใหม่</button>
                                </div>
                            `;
                        }}
                    }};
                }}
            }}
        </script>
    </body>
    </html>
    """

@app.post("/generate")
def generate_api(machine_code: str = Form(...), username: str = Depends(verify_team_member)):
    key = generate_license_key(machine_code)
    return {"key": key}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9999)