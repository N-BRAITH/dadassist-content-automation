# DadAssist Automated Video Generation

Automated weekly video generation and YouTube publishing for DadAssist articles.

## Architecture

```
GitHub Actions (Monday 9am)
    ↓
Select next unprocessed article
    ↓
Call AWS API Gateway
    ↓
AWS Step Functions Pipeline (3-5 min)
    ↓
Return S3 URL
    ↓
Upload to YouTube
    ↓
Update processed_urls.json
```

## Setup Instructions

### 1. GitHub Repository Setup

1. Create new GitHub repository (or use existing)
2. Push this code to the repository
3. Enable GitHub Actions in repository settings

### 2. YouTube API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project (or use existing)
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials:
   - Application type: Desktop app
   - Download credentials JSON
5. Run OAuth flow to get refresh token:
   ```bash
   python scripts/get_youtube_token.py
   ```

### 3. GitHub Secrets Setup

Add these secrets in GitHub repository settings (Settings → Secrets → Actions):

- `YOUTUBE_CLIENT_ID` - From OAuth credentials
- `YOUTUBE_CLIENT_SECRET` - From OAuth credentials
- `YOUTUBE_REFRESH_TOKEN` - From OAuth flow

### 4. Test the Workflow

Manually trigger the workflow:
1. Go to Actions tab in GitHub
2. Select "Weekly Video Generation"
3. Click "Run workflow"

## Files

- `.github/workflows/weekly-video.yml` - GitHub Actions workflow
- `scripts/select_article.py` - Selects next unprocessed article
- `scripts/call_api.py` - Calls AWS API to generate video
- `scripts/upload_youtube.py` - Uploads video to YouTube
- `processed_urls.json` - Tracks processed articles

## API Endpoint

**POST** `https://l5a6iab630.execute-api.ap-southeast-2.amazonaws.com/prod/start-video`

Request:
```json
{
  "article_url": "https://www.dadassist.com.au/posts/articles/..."
}
```

Response (after 3-5 minutes):
```json
{
  "status": "success",
  "s3_url": "https://dadassist-video-work.s3.ap-southeast-2.amazonaws.com/.../final_video_captioned.mp4",
  "title": "Understanding Child Support in Australia",
  "category": "child_support",
  "execution_id": "abc-123",
  "article_url": "https://www.dadassist.com.au/..."
}
```

## Schedule

- Runs every Monday at 9:00 AM UTC
- Can be manually triggered anytime via GitHub Actions UI

## Monitoring

- View workflow runs in GitHub Actions tab
- Each run shows detailed logs with emoji indicators
- Summary shows video title, category, and YouTube URL
- Email notifications on failure (configurable in GitHub settings)

## AWS Components

- **API Gateway**: Public HTTPS endpoint
- **Lambda**: API handler (waits for Step Functions)
- **Step Functions**: Existing video pipeline (6 Lambdas)
- **S3**: Public read access on final videos

## Cost

- **GitHub Actions**: Free (2,000 minutes/month)
- **AWS API Gateway**: ~$0.01 per video
- **AWS Lambda**: ~$0.10 per video
- **AWS S3**: ~$0.01 per video
- **Total**: ~$0.50/month for 4 videos

## Troubleshooting

### Workflow fails at "Select next article"
- Check if all articles have been processed
- Verify dadassist.com.au is accessible

### Workflow fails at "Generate video"
- Check API Gateway logs in AWS CloudWatch
- Verify Lambda has correct permissions
- Check Step Functions execution in AWS console

### Workflow fails at "Upload to YouTube"
- Verify YouTube API credentials are correct
- Check YouTube API quota (10,000 units/day)
- Ensure refresh token hasn't expired

## Manual Testing

Test individual components:

```bash
# Test article selection
python scripts/select_article.py

# Test API call
python scripts/call_api.py

# Test YouTube upload (requires env vars)
export YOUTUBE_CLIENT_ID="..."
export YOUTUBE_CLIENT_SECRET="..."
export YOUTUBE_REFRESH_TOKEN="..."
python scripts/upload_youtube.py
```
