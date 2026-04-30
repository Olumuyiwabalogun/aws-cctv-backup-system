# SemCloud NVR – AWS CCTV Backup System

A production-grade hybrid cloud backup bridge that automatically migrates CCTV footage from a local FTP/NVR server to Amazon S3, with a secure web interface for remote footage browsing and download.

**Live demo:** [semcloud.org](https://semcloud.org)

---

## The Problem

CCTV systems store footage locally on DVR/NVR hardware. This creates critical risks:
- Footage lost permanently if hardware fails, is stolen, or suffers power damage
- No remote access to footage during incidents
- Manual backup processes are unreliable and inconsistent

This is a real-world problem faced by small businesses, homes, and surveillance operators — especially in environments where hardware theft is a concern.

---

## The Solution

An automated Python bridge that runs on the same network as the NVR, polls the FTP share for new footage, and pushes files to S3 with date-based folder organisation. A Flask web interface provides secure remote access without exposing the NVR directly to the internet.

---

## Architecture

```
CCTV Camera(s)
      │
      ▼
 NVR / DVR (local)
      │  FTP share
      ▼
Python Backup Agent  ──────────►  AWS S3 Bucket
  (Flask + Boto3)                 (semcloudnvr)
      │                               │
      ▼                               │
 Web Interface  ◄───────────────────── 
  (semcloud.org)
      │
      ▼
 Authorised User (remote browser/download)
```

**Flow:**
1. NVR writes footage to a local FTP directory
2. Python agent traverses the FTP share and identifies new files
3. Files are uploaded to S3 with `YYYY/MM/DD/camera-name/` prefix structure
4. Credentials are managed via environment variables — never hardcoded
5. The Flask web app authenticates users and streams file listings directly from S3
6. Users can browse by date/folder and download footage on demand

---

## Architectural Decision: FTP vs API Gateway

During design, I evaluated two ingestion approaches:

| Approach | Cost | Complexity | Verdict |
|---|---|---|---|
| **FTP server (chosen)** | ~$0/month (LAN only) | Low — standard Python ftplib | ✅ Optimal for this use case |
| AWS API Gateway + Lambda | ~$3.50/1M requests + Lambda costs | High — requires internet exposure of NVR | ❌ Over-engineered and more expensive |

**Why FTP won:** The backup agent runs on the same local network as the NVR. There is no need to route footage over the internet twice (NVR → Lambda → S3). FTP keeps the ingestion path local and zero-cost, while S3 handles the durable cloud storage. API Gateway adds cost and attack surface without adding value at this scale.

This is a deliberate cost-optimisation decision, not a limitation.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Cloud storage | AWS S3 |
| AWS SDK | Boto3 |
| Web framework | Python / Flask |
| Authentication | Flask session (login-gated routes) |
| Infrastructure | Terraform (see `/terraform`) |
| Environment config | python-dotenv |

---

## Security Considerations

- AWS credentials loaded from environment variables via `.env` — never committed to source
- S3 bucket is private; all access goes through the Flask app with session authentication
- IAM role follows least-privilege principle (see Terraform config) — only `s3:GetObject`, `s3:PutObject`, `s3:ListBucket` on the specific bucket
- Session-protected download routes prevent unauthenticated direct access

---

## Project Structure

```
aws-cctv-backup-system/
├── application.py          # Flask app — auth, file browser, download handler
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── templates/              # Jinja2 HTML templates
│   ├── index.html          # Login page
│   ├── dashboard.html      # Main dashboard
│   └── files.html          # S3 file browser
├── static/images/          # UI assets
├── downloads/              # Temporary local download cache
└── terraform/              # Infrastructure as Code
    ├── main.tf             # S3 bucket + IAM policy
    ├── variables.tf        # Input variables
    └── outputs.tf          # Output values
```

---

## Local Setup

### Prerequisites
- Python 3.9+
- AWS account with S3 access
- An NVR/DVR with FTP share enabled (or test with a local folder)

### 1. Clone and install

```bash
git clone https://github.com/Olumuyiwabalogun/aws-cctv-backup-system.git
cd aws-cctv-backup-system
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your values
```

### 3. Run

```bash
python application.py
# App runs at http://localhost:5000
```

---

## Infrastructure Deployment (Terraform)

Provision the S3 bucket and IAM policy in one command:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

See `/terraform/README.md` for full details.

---

## Cost Analysis

This system is designed to be extremely cost-efficient. Estimated monthly AWS costs for a 4-camera system recording 24/7 at standard NVR compression:

| Component | Monthly cost |
|---|---|
| S3 storage (500GB footage, 30-day retention) | ~$11.50 |
| S3 PUT requests (uploads) | ~$0.25 |
| S3 GET requests (web browsing/downloads) | ~$0.05 |
| Data transfer out (occasional downloads) | ~$0.90 |
| **Total estimate** | **~$12.70/month** |

Compare this to commercial cloud NVR services which charge $30–$80/month per camera. This architecture delivers the same durability at a fraction of the cost.

---

## Future Improvements

- [ ] Scheduled automatic backup with cron/Task Scheduler integration
- [ ] SNS email/SMS alert on backup failure
- [ ] S3 Lifecycle Policy for automatic footage expiry after configurable retention period
- [ ] Video thumbnail preview in web interface using Lambda + FFmpeg
- [ ] Multi-site support (multiple NVRs → separate S3 prefixes)
- [ ] CloudWatch dashboard for backup metrics

## Author
**Olumuyiwa Balogun**   
Portfolio: [semcloud.org](https://semcloud.org)
