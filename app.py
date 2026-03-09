"""
AIOps Control Panel v1.1 (Multi-Server & Multi-Webserver Edition)
-----------------------------------------------------------------
An AI-powered DevOps automation platform built with Streamlit and Ollama (Gemma 3:4b).
"""

import streamlit as st
import ollama
import server_ops
import os
import base64
import requests
import datetime
import json
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="AIOps Control Panel", page_icon="⚙️", layout="wide")

# ==========================================
# 0. SERVER CONFIGURATION
# ==========================================
try:
    with open('servers.json', 'r') as f:
        SERVERS = json.load(f)
except FileNotFoundError:
    st.error("⚠️ `servers.json` file not found!")
    st.stop()

@st.dialog("📄 Full Screen Log Viewer", width="large")
def show_fullscreen_logs():
    st.text_area("Raw Logs", st.session_state.current_logs, height=600, label_visibility="collapsed")

if "current_logs" not in st.session_state: st.session_state.current_logs = None
if "ai_diagnosis" not in st.session_state: st.session_state.ai_diagnosis = None
if "log_name" not in st.session_state: st.session_state.log_name = ""
if "messages" not in st.session_state: st.session_state.messages = []

st.sidebar.title("🛠️ DevOps Navigation")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Go To:", ["System Dashboard", "AI ChatOps", "Terraform / IaC Hub"])
st.sidebar.markdown("---")

st.sidebar.subheader("🌐 Target Server")
selected_server_name = st.sidebar.selectbox("Select Server:", list(SERVERS.keys()))

current_ip = SERVERS[selected_server_name]["ip"]
current_user = SERVERS[selected_server_name]["user"]
current_key = SERVERS[selected_server_name]["key_path"]
# Fetch the web server type from json (default to nginx if not mentioned)
current_web_server = SERVERS[selected_server_name].get("web_server", "nginx")

os.environ["SERVER_IP"] = current_ip
os.environ["SERVER_USER"] = current_user
os.environ["SSH_KEY_PATH"] = current_key

st.sidebar.success(f"Connected to: {selected_server_name}")
st.sidebar.code(current_ip)
st.sidebar.info(f"Web Engine: {current_web_server.capitalize()}")
st.sidebar.markdown("---")
st.sidebar.info("Status: Live Cloud Mode ☁️")
st.sidebar.success("AI Model: Gemma 3:4b\n(Streaming)")

# ==========================================
# 1. SYSTEM DASHBOARD
# ==========================================
if menu == "System Dashboard":
    st.title("🖥️ EC2 Server Control")
    st.markdown(f"**Target:** `{selected_server_name}` (`{current_ip}`)")
    
    col1, col2, col3 = st.columns(3)
    
    # --- MODULE: Dynamic Web Server Status ---
    with col1:
        st.info(f"Web Server ({current_web_server.capitalize()})")
        if st.button("Check Service Status"):
            with st.spinner(f"Checking {current_web_server} on {current_ip}..."):
                # DYNAMIC COMMAND: Uses apache2 or nginx based on JSON
                success, result = server_ops.run_remote_command(f"sudo systemctl status {current_web_server} | grep Active")
                if success:
                    st.success("Success!")
                    st.code(result.strip(), language="bash")
                else:
                    st.error(f"Failed to get {current_web_server} status.")
                    
    # --- MODULE: AI Log Fetcher ---
    with col2:
        st.error("AI Log Management")
        log_type = st.selectbox("Select Log to Fetch:", ["Access Log (Traffic & 404s)", "Error Log (Server Crashes)"])
        col_f1, col_f2 = st.columns(2)
        with col_f1: log_lines = st.selectbox("Recent lines?", [15, 50, 100, 500])
        with col_f2: only_errors = st.checkbox("Only Errors")
            
        if st.button("Fetch & Analyze Logs"):
            with st.spinner(f"Fetching logs from {selected_server_name}..."):
                # DYNAMIC LOG PATH: /var/log/nginx/.. OR /var/log/apache2/..
                if "Access" in log_type:
                    log_path = f"/var/log/{current_web_server}/access.log"
                    grep_filter = " | grep -E ' 404 | 500 | 502 | 503 | 504 '" if only_errors else ""
                else:
                    log_path = f"/var/log/{current_web_server}/error.log"
                    grep_filter = " | grep -i 'error\\|crit\\|warn'" if only_errors else ""
                    
                command = f"sudo tail -n {log_lines} {log_path}{grep_filter}"
                success, logs = server_ops.run_remote_command(command)
                
                if success:
                    if not logs.strip():
                        st.success("No logs found. Looks clean! ✅")
                        st.session_state.current_logs = None
                    else:
                        st.session_state.current_logs = logs
                        st.session_state.log_name = log_type
                        st.markdown("---")
                        st.markdown("### 🤖 AI Diagnosis...")
                        message_placeholder = st.empty()
                        full_response = ""
                        ai_prompt = f"You are a DevOps expert. Read this {current_web_server} {log_type}. Explain the issue briefly and give a solution. Log:\n\n{logs}"
                        try:
                            for chunk in ollama.chat(model='gemma3:4b', messages=[{'role': 'user', 'content': ai_prompt}], stream=True):
                                full_response += chunk['message']['content']
                                message_placeholder.markdown(full_response + "▌")
                            message_placeholder.markdown(full_response)
                            st.session_state.ai_diagnosis = full_response
                        except Exception as e:
                            st.error(f"AI Error: {e}")
                else:
                    st.error(f"Failed to fetch {current_web_server} logs. Path might not exist: {log_path}")
                    
    # --- MODULE: DB Backup & Cronjob ---
    with col3:
        st.success("Database Automation")
        if st.button("AI Generate & Run DB Backup"):
            with st.spinner("Processing..."):
                s3_bucket = os.getenv("S3_BUCKET_NAME")
                ai_prompt = f"Write a bash script to backup MariaDB database 'aiops_test_db' using username 'aiops_user' and password 'admin123'. Save the output to '/home/ubuntu/aiops_backup.sql'. Then, add a command to upload this file to AWS S3 using 'aws s3 cp /home/ubuntu/aiops_backup.sql s3://{s3_bucket}/aiops_backup.sql'. Output EXACTLY the raw bash code. No markdown, no backticks, no comments."
                try:
                    response = ollama.chat(model='gemma3:4b', messages=[{'role': 'user', 'content': ai_prompt}])
                    ai_script = response['message']['content'].replace('```bash', '').replace('```', '').strip()
                    st.markdown("**Generated Bash Script:**")
                    st.code(ai_script, language="bash")
                    b64_script = base64.b64encode(ai_script.encode()).decode()
                    remote_cmd = f"echo '{b64_script}' | base64 -d > /home/ubuntu/db_backup.sh && chmod +x /home/ubuntu/db_backup.sh && bash /home/ubuntu/db_backup.sh"
                    success, result = server_ops.run_remote_command(remote_cmd)
                    if success:
                        st.success("Success! ✅")
                        st.code(result, language="bash")
                        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
                        if webhook_url: requests.post(webhook_url, json={"content": f"🚀 **Backup Success**\n**Server:** `{selected_server_name}`\n**Storage:** `s3://{s3_bucket}`"})
                    else: st.error(result)
                except Exception as e: st.error(str(e))
                    
        st.markdown("---")
        st.markdown("**Cronjob Scheduler**")
        cron_time = st.selectbox("Backup Frequency:", ["Everyday at 2:00 AM", "Every Hour", "Custom Time"])
        final_cron_expr = "0 2 * * *" if cron_time == "Everyday at 2:00 AM" else "0 * * * *"
        if cron_time == "Custom Time":
            custom_time = st.time_input("Pick Time:", datetime.time(10, 10))
            final_cron_expr = f"{custom_time.minute} {custom_time.hour} * * *"
            
        if st.button("Schedule Cronjob"):
            with st.spinner("Configuring crontab..."):
                cron_cmd = f'(crontab -l 2>/dev/null | grep -v "db_backup.sh"; echo "{final_cron_expr} /bin/bash /home/ubuntu/db_backup.sh") | crontab - && crontab -l'
                success, result = server_ops.run_remote_command(cron_cmd)
                if success: st.success("Scheduled! ⏰")
                else: st.error(result)

    if st.session_state.current_logs:
        st.markdown("---")
        col_res1, col_res2 = st.columns([3, 1])
        with col_res1:
            st.markdown(f"### 🤖 AI Diagnosis ({current_web_server}):")
            st.write(st.session_state.ai_diagnosis)
            st.code(st.session_state.current_logs[:500] + "\n...", language="bash")
        with col_res2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("🔍 Full Screen Logs", use_container_width=True): show_fullscreen_logs()

# ==========================================
# 2. AI CHATOPS & 3. TERRAFORM HUB (Unchanged logic, kept clean)
# ==========================================
elif menu == "AI ChatOps":
    st.title("🤖 ChatOps Assistant")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])
    if prompt := st.chat_input("Ask something..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            resp = ""
            try:
                ai_msgs = [{'role': 'system', 'content': f'You are managing {current_web_server} on {selected_server_name}.'}] + st.session_state.messages
                for chunk in ollama.chat(model='gemma3:4b', messages=ai_msgs, stream=True):
                    resp += chunk['message']['content']
                    placeholder.markdown(resp + "▌")
                placeholder.markdown(resp)
                st.session_state.messages.append({"role": "assistant", "content": resp})
            except Exception as e: placeholder.error(str(e))

elif menu == "Terraform / IaC Hub":
    st.title("🏗️ Terraform AI Hub")
    t1, t2 = st.tabs(["✨ Generate", "✅ Validate"])
    with t1:
        req = st.text_area("Infrastructure Request:")
        if st.button("Generate Code", type="primary") and req:
            placeholder = st.empty()
            resp = ""
            for chunk in ollama.chat(model='gemma3:4b', messages=[{'role': 'user', 'content': f"Write Terraform for: {req}. Code only."}], stream=True):
                resp += chunk['message']['content']
                placeholder.markdown(resp + "▌")
            placeholder.markdown(resp)
    with t2:
        code = st.text_area("Paste HCL Code:")
        if st.button("Analyze Code", type="primary") and code:
            placeholder = st.empty()
            resp = ""
            for chunk in ollama.chat(model='gemma3:4b', messages=[{'role': 'user', 'content': f"Review this Terraform for security and errors: \n{code}"}], stream=True):
                resp += chunk['message']['content']
                placeholder.markdown(resp + "▌")
            placeholder.markdown(resp)
# Testing CI/CD Webhook
