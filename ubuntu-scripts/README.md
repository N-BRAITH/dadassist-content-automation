# Ubuntu Server Scripts Backup

This directory contains backup copies of critical Python scripts that run on the Ubuntu web server (13.239.163.33).

## Scripts Overview

### Core Production Scripts

| Script | Ubuntu Location | Purpose | Size |
|--------|----------------|---------|------|
| `generate_article.py` | `/home/ubuntu/` | Main article generation using Q Developer AI | 19.4KB |
| `generate_instagram_image.py` | `/tmp/` | Creates Instagram images using Amazon Nova Canvas | 9.4KB |
| `deploy_article.py` | `/home/ubuntu/` | Deploys articles to web server with proper permissions | 4.3KB |
| `update_index_function.py` | `/home/ubuntu/` | Updates main articles index page | 2.5KB |

## Usage

These scripts are called by the GitHub Actions workflow during the automated content generation process:

1. **Article Generation Flow:**
   ```
   GitHub Actions → SSH → generate_article.py → deploy_article.py → update_index_function.py
   ```

2. **Image Generation Flow:**
   ```
   GitHub Actions → SSH → generate_instagram_image.py → Returns URL
   ```

## Deployment

To deploy updated scripts to the Ubuntu server:

```bash
# Upload to Ubuntu server
scp -i "LightsailDefaultKey.pem" script.py ubuntu@13.239.163.33:/home/ubuntu/

# Set executable permissions
ssh -i "LightsailDefaultKey.pem" ubuntu@13.239.163.33 "chmod +x /home/ubuntu/script.py"
```

## Backup Schedule

- **Last Backup:** October 26, 2025
- **Backup Frequency:** Before major changes
- **Version Control:** Stored in GitHub repository

## Dependencies

All scripts require:
- Python 3.x
- boto3 (AWS SDK)
- PIL/Pillow (Image processing)
- Various other Python libraries installed on Ubuntu server

## Notes

- Scripts contain AWS credentials and should be kept secure
- Ubuntu server has multiple backup versions of each script
- Always test scripts in development before deploying to production
