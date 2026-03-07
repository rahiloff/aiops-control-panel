# AIOps Control Panel 🤖☁️

An Enterprise-Grade, AI-powered DevOps automation and Server Management platform. Built to simplify cloud administration, automate database backups, analyze server logs using local LLMs, and generate Infrastructure as Code (IaC).

**Developed by:** [Mohammed Rahil T](https://github.com/rahiloff)

---

## 🏗️ Architecture & Tech Stack

This project integrates modern DevOps tools with Local AI to create an intelligent control plane for cloud infrastructure.

* **Frontend:** Python, Streamlit (for a clean, reactive UI)
* **AI Engine:** Ollama running **Gemma 3:4b** locally (Zero API costs, completely private)
* **Cloud Compute:** AWS EC2 (Ubuntu), Nginx Web Server
* **Storage & Security:** AWS S3, IAM Roles (Password-less, secure cloud access)
* **Automation & Alerting:** Linux Bash Scripts, Cronjobs, Discord Webhooks
* **IaC:** HashiCorp Terraform (HCL)

---

## ✨ Key Features

### 1. 🖥️ Secure Server Management
* Password-less remote execution on AWS EC2 using `.pem` SSH keys.
* Real-time monitoring of Nginx web server status directly from the dashboard.

### 2. 🕵️‍♂️ AI-Powered Log Analysis
* Fetches dynamic `access.log` and `error.log` directly from the production server.
* Filters logs by line count and error types (404, 500, etc.).
* Streams logs to the local **Gemma AI** model to instantly diagnose issues and recommend solutions.

### 3. 💾 Automated Database Backups & S3 Integration
* AI dynamically generates secure bash scripts for MariaDB/MySQL database dumps.
* Scripts are base64 encoded and executed remotely on the EC2 instance.
* Automatically uploads the `.sql` backup files to an **AWS S3 Bucket** using IAM Roles.
* Triggers a **Discord Webhook** notification upon successful backup and upload.

### 4. ⏰ Advanced Cronjob Scheduler
* User-friendly UI to schedule automated, recurring backups.
* Custom time-picker that translates UI inputs directly into backend Linux Crontab expressions.

### 5. 🏗️ AI Terraform (IaC) Hub
* **Generate:** Translates plain English infrastructure requirements into production-ready Terraform (HCL) code.
* **Validate:** Scans existing Terraform code for syntax errors, missing best practices, and security misconfigurations, providing automated fixes.

---

## ⚙️ Installation & Setup

**1. Clone the repository:**
```bash
git clone [https://github.com/rahiloff/aiops-control-panel.git](https://github.com/rahiloff/aiops-control-panel.git)
cd aiops-control-panel
Gemini said
Kuzhappamilla! Nammukku ippol thanne adipoli oru README.md undakkam. Ee file aanu ningalude project-nte "Mukham" (Face). GitHub-il aaru vannalum aadyam kanunna karyam ithaanu.

VS Code-il ithu cheyyan valare eluppamanu. Thazhe parayunna steps step-by-step aayi cheyyuka:

Step 1: File Undakkuka
VS Code-il ningalude project folder-nte (aiops-control-panel) left side-il ulla file list-il nokkuka.

Avide "New File" icon click cheyyuka (allengil right-click cheythu "New File" edukuka).

File-nte peru krithyamayi README.md ennu thanne type cheythu Enter adikkuka. (Capital letters aayirikkan shraddhikkuka).

Step 2: Content Paste Cheyyuka
Ippol open aayi vanna aa blank README.md file-il, thazhe ulla text muzhuvanayi copy cheythu paste cheyyuka:

Markdown
# AIOps Control Panel 🤖☁️

An Enterprise-Grade, AI-powered DevOps automation and Server Management platform. Built to simplify cloud administration, automate database backups, analyze server logs using local LLMs, and generate Infrastructure as Code (IaC).

**Developed by:** [Mohammed Rahil T](https://github.com/rahiloff)

---

## 🏗️ Architecture & Tech Stack

This project integrates modern DevOps tools with Local AI to create an intelligent control plane for cloud infrastructure.

* **Frontend:** Python, Streamlit (for a clean, reactive UI)
* **AI Engine:** Ollama running **Gemma 3:4b** locally (Zero API costs, completely private)
* **Cloud Compute:** AWS EC2 (Ubuntu), Nginx Web Server
* **Storage & Security:** AWS S3, IAM Roles (Password-less, secure cloud access)
* **Automation & Alerting:** Linux Bash Scripts, Cronjobs, Discord Webhooks
* **IaC:** HashiCorp Terraform (HCL)

---

## ✨ Key Features

### 1. 🖥️ Secure Server Management
* Password-less remote execution on AWS EC2 using `.pem` SSH keys.
* Real-time monitoring of Nginx web server status directly from the dashboard.

### 2. 🕵️‍♂️ AI-Powered Log Analysis
* Fetches dynamic `access.log` and `error.log` directly from the production server.
* Filters logs by line count and error types (404, 500, etc.).
* Streams logs to the local **Gemma AI** model to instantly diagnose issues and recommend solutions.

### 3. 💾 Automated Database Backups & S3 Integration
* AI dynamically generates secure bash scripts for MariaDB/MySQL database dumps.
* Scripts are base64 encoded and executed remotely on the EC2 instance.
* Automatically uploads the `.sql` backup files to an **AWS S3 Bucket** using IAM Roles.
* Triggers a **Discord Webhook** notification upon successful backup and upload.

### 4. ⏰ Advanced Cronjob Scheduler
* User-friendly UI to schedule automated, recurring backups.
* Custom time-picker that translates UI inputs directly into backend Linux Crontab expressions.

### 5. 🏗️ AI Terraform (IaC) Hub
* **Generate:** Translates plain English infrastructure requirements into production-ready Terraform (HCL) code.
* **Validate:** Scans existing Terraform code for syntax errors, missing best practices, and security misconfigurations, providing automated fixes.

---

## ⚙️ Installation & Setup

**1. Clone the repository:**
```bash
git clone [https://github.com/rahiloff/aiops-control-panel.git](https://github.com/rahiloff/aiops-control-panel.git)
cd aiops-control-panel

2. Install dependencies:

Bash
pip install streamlit ollama paramiko python-dotenv requests


3. Setup Environment Variables (.env):
Create a .env file in the root directory:

Code snippet
SERVER_IP=your_ec2_public_ip
SERVER_USER=ubuntu
SSH_KEY_PATH=./your-secure-key.pem
TARGET_DIR=/var/www/html
DISCORD_WEBHOOK_URL=your_discord_webhook_url
S3_BUCKET_NAME=your_aws_s3_bucket_name


4. Run the Application:

Bash
streamlit run app.py
