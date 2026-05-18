# GitLab Daily — Commands Reference

## Rebuild and redeploy
```bash
source ~/.claude/.gitlab-config
gcloud builds submit --tag gcr.io/ai-innov-474401/gitlab-daily-job:latest --project ai-innov-474401 ~/.claude/gitlab-daily/
gcloud run jobs update gitlab-daily-job \
  --image gcr.io/ai-innov-474401/gitlab-daily-job:latest \
  --region asia-southeast1 --project ai-innov-474401
```

## Manual trigger
```bash
gcloud run jobs execute gitlab-daily-job --region asia-southeast1 --project ai-innov-474401
```

## Check logs
```bash
gcloud run jobs executions list --job gitlab-daily-job --region asia-southeast1 --project ai-innov-474401
```

## First-time setup (already done — reference only)
```bash
source ~/.claude/.gitlab-config

gcloud run jobs create gitlab-daily-job \
  --image gcr.io/ai-innov-474401/gitlab-daily-job:latest \
  --region asia-southeast1 --project ai-innov-474401 \
  --set-env-vars "GITLAB_TOKEN=${GITLAB_TOKEN},GITHUB_TOKEN=${GITHUB_TOKEN},GEMINI_API_KEY=${GEMINI_API_KEY}" \
  --max-retries 1 --task-timeout 300

gcloud scheduler jobs create http gitlab-daily-update \
  --location asia-southeast1 --project ai-innov-474401 \
  --schedule "0 15 * * *" --time-zone "UTC" \
  --uri "https://asia-southeast1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/ai-innov-474401/jobs/gitlab-daily-job:run" \
  --http-method POST \
  --oauth-service-account-email $(gcloud projects describe ai-innov-474401 --format="value(projectNumber)")-compute@developer.gserviceaccount.com
```
