
# AWS CCTV Backup System

## Overview
This project is a cloud-based CCTV backup system that automatically transfers
video footage from a local FTP server to Amazon S3 for secure cloud storage.

## Business Problem
CCTV systems often store footage locally, which can be lost due to hardware
failure, theft, or accidental deletion.

## Solution
This system automatically backs up CCTV footage from an FTP server to an
Amazon S3 bucket and provides a web interface to browse and download files.

## Architecture
CCTV DVR → FTP Server → Python Backup Script → AWS S3 → Web Interface

## Technologies Used
- Python
- Flask
- AWS S3
- FTP
- HTML/CSS

## Key Features
- Automatic backup from FTP to S3
- Cloud-based storage
- Web interface for browsing footage
- Date-based file organization

## Deployment
- Cloud storage: Amazon S3
- Web access: semcloud.org
  <img width="960" height="504" alt="semcloud 1" src="https://github.com/user-attachments/assets/5ebc2c1a-400e-4194-be29-38a5f7c63715" />
<img width="960" height="504" alt="semcloud 2" src="https://github.com/user-attachments/assets/5f59356d-0b55-4abf-aa00-53e644839950" />


## Future Improvements
- Scheduled automatic backups
- Alert system for backup failures
- Video preview in web interface

