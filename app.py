"""
AIOps Control Panel v1.0
------------------------
An AI-powered DevOps automation platform built with Streamlit and Ollama (Gemma 3:4b).
Features include:
- Remote EC2 Server Management via secure SSH keys
- Automated AI Log Analysis (Nginx)
- Database Backup Automation with AWS S3 integration & Cronjob scheduling
- Discord Webhook Alerts for job success/failure
- Infrastructure as Code (Terraform) Generation and Validation
"""

import streamlit as st
import ollama
import server_ops
import os
import base64
import requests 
import datetime 
from dotenv import load_dotenv

# Load environment variables (Security best practice)
load_dotenv()

# --- STREAMLIT UI CONFIGURATION ---
st.set_page_config(page_title="AIOps Control Panel", page_icon="R", layout="wide")

# --- UI COMPONENTS ---
@st.dialog("📄 Full Screen Log Viewer", width="large")
def show_fullscreen_logs():
    """Displays a modal popup for easy reading of large log files."""
    st.markdown("Here you can read and copy the full logs clearly.")
    st.text_area("Raw Logs", st.session_state.current_logs, height=600, label_visibility="collapsed")

# --- SESSION STATE MANAGEMENT ---
# Keep track of fetched logs and AI responses so they don't disappear on button clicks
if "current_logs" not in st.session_state:
    st.session_state.current_logs = None
if "ai_diagnosis" not in st.session_state:
    st.session_state.ai_diagnosis = None
if "log_name" not in st.session_state:
    st.session_state.log_name = ""

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🛠️ DevOps Navigation")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Go To:", ["System Dashboard", "AI ChatOps", "Terraform / IaC Hub"])

st.sidebar.markdown("---")
st.sidebar.info("Status: Live Cloud Mode ☁️")
st.sidebar.success("AI Model: Gemma 3:4b (Streaming)")

# ==========================================
# 1. SYSTEM DASHBOARD 
# ==========================================
if menu == "System Dashboard":
    st.title("🖥️ EC2 Server Control")
    st.markdown(f"**Target Server IP:** `{os.getenv('SERVER_IP')}`")
    
    st.subheader("Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    # ------------------------------------------
    # MODULE: Web Server Status
    # ------------------------------------------
    with col1:
        st.info("Web Server (Nginx)")
        if st.button("Check Nginx Status"):
            with st.spinner("Connecting to EC2 via SSH..."):
                success, result = server_ops.run_remote_command("sudo systemctl status nginx | grep Active")
                if success:
                    st.success("Success!")
                    st.code(result.strip(), language="bash")
                else:
                    st.error("Failed to connect.")
            
    # ------------------------------------------
    # MODULE: AI Log Fetcher & Analyzer
    # ------------------------------------------
    with col2:
        st.error("AI Log Management")
        log_type = st.selectbox("Select Log to Fetch:", ["Access Log (Traffic & 404s)", "Error Log (Server Crashes)"])
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            log_lines = st.selectbox("How many recent lines?", [15, 50, 100, 500])
        with col_f2:
            only_errors = st.checkbox("Show Only Errors")
        
        if st.button("Fetch & Analyze Logs"):
            with st.spinner(f"Fetching logs from EC2..."):
                
                # Determine log path and grep filters based on user selection
                if "Access" in log_type:
                    log_path = "/var/log/nginx/access.log"
                    grep_filter = " | grep -E ' 404 | 500 | 502 | 503 | 504 '" if only_errors else ""
                else:
                    log_path = "/var/log/nginx/error.log"
                    grep_filter = " | grep -i 'error\\|crit\\|warn'" if only_errors else ""
                    
                command = f"sudo tail -n {log_lines} {log_path}{grep_filter}"
                success, logs = server_ops.run_remote_command(command)
                
                if success:
                    if not logs.strip():
                        st.success("No logs found matching your criteria. Looks clean! ✅")
                        st.session_state.current_logs = None 
                    else:
                        # Store logs in memory
                        st.session_state.current_logs = logs
                        st.session_state.log_name = log_type
                        
                        st.markdown("---")
                        st.markdown("### 🤖 AI Diagnosis in Progress...")
                        
                        message_placeholder = st.empty()
                        full_response = ""
                        
                        # AI Prompt for Log Analysis
                        ai_prompt = f"You are a DevOps expert. Read this Nginx {log_type}. Explain the issue briefly and give a solution. Here is the log:\n\n{logs}"
                        
                        try:
                            # Stream the response for better UX
                            for chunk in ollama.chat(model='gemma3:4b', messages=[{'role': 'user', 'content': ai_prompt}], stream=True):
                                full_response += chunk['message']['content']
                                message_placeholder.markdown(full_response + "▌")
                            message_placeholder.markdown(full_response)
                            
                            # Save AI response to memory
                            st.session_state.ai_diagnosis = full_response
                        except Exception as e:
                            st.error(f"Error connecting to local AI: {e}")
                else:
                    st.error(f"Failed to fetch logs. Error: {logs}")
                    
    # ------------------------------------------
    # MODULE: DB Automation, S3 Backup & Discord
    # ------------------------------------------
    with col3:
        st.success("Database Automation")
        
        if st.button("AI Generate & Run DB Backup"):
            with st.spinner("AI is generating the backup & S3 upload script..."):
                s3_bucket = os.getenv("S3_BUCKET_NAME")
                
                # AI Prompt for script generation
                ai_prompt = f"Write a bash script to backup MariaDB database 'aiops_test_db' using username 'aiops_user' and password 'admin123'. Save the output to '/home/ubuntu/aiops_backup.sql'. Then, add a command to upload this file to AWS S3 using 'aws s3 cp /home/ubuntu/aiops_backup.sql s3://{s3_bucket}/aiops_backup.sql'. Output EXACTLY the raw bash code. No markdown, no backticks, no comments."
                
                try:
                    # Request script from AI
                    response = ollama.chat(model='gemma3:4b', messages=[{'role': 'user', 'content': ai_prompt}])
                    ai_script = response['message']['content'].replace('```bash', '').replace('```', '').strip()
                    
                    st.markdown("**Generated Bash Script:**")
                    st.code(ai_script, language="bash")
                    
                    # Safely encode the script to Base64 to prevent SSH execution breaks
                    b64_script = base64.b64encode(ai_script.encode()).decode()
                    remote_cmd = f"echo '{b64_script}' | base64 -d > /home/ubuntu/db_backup.sh && chmod +x /home/ubuntu/db_backup.sh && bash /home/ubuntu/db_backup.sh"
                    
                    success, result = server_ops.run_remote_command(remote_cmd)
                    
                    if success:
                        st.success("Backup & S3 Upload Successful! ✅")
                        st.code(result, language="bash")
                        
                        # Trigger Discord Webhook Alert
                        webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
                        domain_name = os.getenv("SERVER_IP")
                        discord_message = {
                            "content": f"🚀 **Enterprise Backup Success**\n**Domain/IP:** `{domain_name}`\n**Storage:** `s3://{s3_bucket}`\nDatabase securely backed up to AWS S3 via AIOps Platform!"
                        }
                        requests.post(webhook_url, json=discord_message)
                    else:
                        st.error(f"Backup Execution Failed: {result}")
                except Exception as e:
                    st.error(f"Process Error: {e}")
                    
        # --- Cronjob Scheduler UI ---
        st.markdown("---")
        st.markdown("**Cronjob Scheduler**")
        cron_time = st.selectbox("Select Backup Frequency:", ["Everyday at 2:00 AM", "Everyday at Midnight", "Every Hour", "Custom Daily Time"])
        
        final_cron_expr = ""
        if cron_time == "Everyday at 2:00 AM":
            final_cron_expr = "0 2 * * *"
        elif cron_time == "Everyday at Midnight":
            final_cron_expr = "0 0 * * *"
        elif cron_time == "Every Hour":
            final_cron_expr = "0 * * * *"
        else:
            custom_time = st.time_input("Pick a Daily Backup Time:", datetime.time(10, 10))
            final_cron_expr = f"{custom_time.minute} {custom_time.hour} * * *"
            st.info(f"Generated Cron Expression: `{final_cron_expr}`")
        
        if st.button("Schedule Backup (Cronjob)"):
            with st.spinner("Configuring crontab on target EC2..."):
                # Append to crontab without deleting existing jobs
                cron_cmd = f'(crontab -l 2>/dev/null | grep -v "db_backup.sh"; echo "{final_cron_expr} /bin/bash /home/ubuntu/db_backup.sh") | crontab - && crontab -l'
                success, result = server_ops.run_remote_command(cron_cmd)
                
                if success:
                    st.success("Cronjob Scheduled Successfully! ⏰")
                    st.code(result, language="bash")
                else:
                    st.error(f"Failed to set cronjob: {result}")

    # ------------------------------------------
    # DISPLAY RESULTS (Log Viewer)
    # ------------------------------------------
    if st.session_state.current_logs:
        st.markdown("---")
        st.header(f"📊 Results: {st.session_state.log_name}")
        col_res1, col_res2 = st.columns([3, 1])
        
        with col_res1:
            st.markdown("### 🤖 AI Diagnosis:")
            st.write(st.session_state.ai_diagnosis)
            st.markdown("### 📄 Log Preview:")
            preview_logs = st.session_state.current_logs[:500] + "\n\n... [Log is longer. Click Full Screen to view all] ..."
            st.code(preview_logs, language="bash")
            
        with col_res2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("🔍 Open Full Screen Logs", use_container_width=True):
                show_fullscreen_logs()

# ==========================================
# 2. AI CHATOPS (Conversational Assistant)
# ==========================================
elif menu == "AI ChatOps":
    st.title("🤖 R DevOps Assistant")
    st.markdown("Ask anything about Linux commands, log analysis, or automation scripts.")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle user input
    if prompt := st.chat_input("Enter your command or question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                # System prompt to set AI persona
                ai_messages = [{'role': 'system', 'content': 'You are a Senior DevOps automation assistant.'}]
                ai_messages.extend(st.session_state.messages)
                
                for chunk in ollama.chat(model='gemma3:4b', messages=ai_messages, stream=True):
                    full_response += chunk['message']['content']
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                message_placeholder.error(f"Local AI Connection Error: {e}")

# ==========================================
# 3. TERRAFORM / IaC HUB (Generator & Validator)
# ==========================================
elif menu == "Terraform / IaC Hub":
    st.title("🏗️ AI Infrastructure as Code (IaC) Hub")
    st.markdown("Generate and Validate Terraform (HCL) scripts automatically using AI.")
    
    tab1, tab2 = st.tabs(["✨ Generate IaC", "✅ Validate IaC"])
    
    # ------------------------------------------
    # GENERATOR TAB
    # ------------------------------------------
    with tab1:
        st.subheader("Generate Terraform Code")
        infra_request = st.text_area("Describe the infrastructure you want to build:", 
                                     placeholder="e.g., Create an AWS EC2 t2.micro instance with a security group allowing port 80 and 22.")
        
        if st.button("Generate Terraform Code", type="primary"):
            if infra_request:
                st.markdown("---")
                st.markdown("### 🤖 Generated Code:")
                message_placeholder = st.empty()
                full_response = ""
                
                ai_prompt = f"You are an expert Cloud Architect. Write standard, production-ready Terraform (HCL) code for the following request: '{infra_request}'. Include basic comments. Use best practices. Output the code inside a Markdown code block."
                
                try:
                    for chunk in ollama.chat(model='gemma3:4b', messages=[{'role': 'user', 'content': ai_prompt}], stream=True):
                        full_response += chunk['message']['content']
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                except Exception as e:
                    st.error(f"Generation Error: {e}")
            else:
                st.warning("Please describe what you want to build first.")

    # ------------------------------------------
    # VALIDATOR TAB
    # ------------------------------------------
    with tab2:
        st.subheader("Validate & Fix Terraform Code")
        existing_hcl = st.text_area("Paste your Terraform (HCL) code here:", height=250, 
                                    placeholder='''resource "aws_instance" "web" {\n  ami = "ami-12345"\n  # missing instance_type\n}''')
        
        if st.button("Analyze & Fix Code", type="primary"):
            if existing_hcl:
                st.markdown("---")
                st.markdown("### 🤖 AI Analysis & Fix:")
                message_placeholder = st.empty()
                full_response = ""
                
                ai_prompt = f"You are an expert Cloud Security Architect. Review the following Terraform (HCL) code. Identify any syntax errors, missing best practices, or security flaws. Explain the issues briefly, and then provide the corrected code in a Markdown code block.\n\nCode to review:\n{existing_hcl}"
                
                try:
                    for chunk in ollama.chat(model='gemma3:4b', messages=[{'role': 'user', 'content': ai_prompt}], stream=True):
                        full_response += chunk['message']['content']
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                except Exception as e:
                    st.error(f"Analysis Error: {e}")
            else:
                st.warning("Please paste some code to analyze.")
