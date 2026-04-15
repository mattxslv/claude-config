#!/bin/bash

# post-commit hook — updates active session ticket or creates a new one, then marks Done.

CONFIG="$HOME/.claude/.jira-config"
SESSION_FILE="$HOME/.claude/.jira-session"
if [ ! -f "$CONFIG" ]; then exit 0; fi
source "$CONFIG"

# Get last commit message and hash
COMMIT_MSG=$(git log -1 --pretty=%s)
COMMIT_HASH=$(git log -1 --pretty=%h)
COMMIT_BODY=$(git log -1 --pretty=%b)
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Parse prefix — only act on feat/fix/refactor/chore/docs commits
PREFIX=$(echo "$COMMIT_MSG" | grep -oP '^(feat|fix|refactor|chore|docs)(?:\([^)]+\))?(?=:)')
if [ -z "$PREFIX" ]; then exit 0; fi

# Build description from commit info
DESCRIPTION="Commit: $COMMIT_HASH\nBranch: $BRANCH\nMessage: $COMMIT_MSG"
if [ -n "$COMMIT_BODY" ]; then
  DESCRIPTION="$DESCRIPTION\n\n$COMMIT_BODY"
fi

DESC_JSON=$(printf '%s' "$DESCRIPTION" | node -e "let d=''; process.stdin.on('data',c=>d+=c); process.stdin.on('end',()=>process.stdout.write(JSON.stringify(d.trim())))")

# --- Path A: session ticket exists — add commit as comment, mark Done, clear session ---
if [ -f "$SESSION_FILE" ]; then
  TICKET_KEY=$(cat "$SESSION_FILE" | tr -d '[:space:]')

  curl -s -u "$JIRA_EMAIL:$JIRA_TOKEN" \
    -X POST \
    -H "Content-Type: application/json" \
    "$JIRA_BASE_URL/rest/api/3/issue/$TICKET_KEY/comment" \
    -d "{
      \"body\": {
        \"type\": \"doc\",
        \"version\": 1,
        \"content\": [{
          \"type\": \"paragraph\",
          \"content\": [{ \"type\": \"text\", \"text\": $DESC_JSON }]
        }]
      }
    }" > /dev/null

  curl -s -u "$JIRA_EMAIL:$JIRA_TOKEN" \
    -X POST \
    -H "Content-Type: application/json" \
    "$JIRA_BASE_URL/rest/api/3/issue/$TICKET_KEY/transitions" \
    -d '{"transition":{"id":"41"}}' > /dev/null

  rm -f "$SESSION_FILE"
  echo "  → Jira $TICKET_KEY updated & marked Done: $JIRA_BASE_URL/browse/$TICKET_KEY"
  exit 0
fi

# --- Path B: no session ticket — create one per commit and mark Done ---
case "${PREFIX%%(*}" in
  feat)     ISSUE_TYPE_ID="10003" ;;
  fix)      ISSUE_TYPE_ID="10005" ;;
  *)        ISSUE_TYPE_ID="10004" ;;
esac

SUMMARY=$(echo "$COMMIT_MSG" | sed 's/^[a-z]*([^)]*): //' | sed 's/^[a-z]*: //')
SUMMARY="[$BRANCH] $SUMMARY"
SUM_JSON=$(echo "$SUMMARY" | node -e "let d=''; process.stdin.on('data',c=>d+=c); process.stdin.on('end',()=>process.stdout.write(JSON.stringify(d.trim())))")

RESPONSE=$(curl -s -u "$JIRA_EMAIL:$JIRA_TOKEN" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  "$JIRA_BASE_URL/rest/api/3/issue" \
  -d "{
    \"fields\": {
      \"project\": { \"key\": \"$JIRA_PROJECT_KEY\" },
      \"summary\": $SUM_JSON,
      \"description\": {
        \"type\": \"doc\",
        \"version\": 1,
        \"content\": [{
          \"type\": \"paragraph\",
          \"content\": [{ \"type\": \"text\", \"text\": $DESC_JSON }]
        }]
      },
      \"issuetype\": { \"id\": \"$ISSUE_TYPE_ID\" },
      \"assignee\": { \"accountId\": \"$JIRA_ACCOUNT_ID\" },
      \"customfield_10020\": $JIRA_SPRINT_ID
    }
  }")

TICKET_KEY=$(echo "$RESPONSE" | node -e "let d=''; process.stdin.on('data',c=>d+=c); process.stdin.on('end',()=>{try{process.stdout.write(JSON.parse(d).key||'ERROR')}catch{process.stdout.write('ERROR')}})" 2>/dev/null)

if [ "$TICKET_KEY" != "ERROR" ] && [ -n "$TICKET_KEY" ]; then
  curl -s -u "$JIRA_EMAIL:$JIRA_TOKEN" \
    -X POST \
    -H "Content-Type: application/json" \
    "$JIRA_BASE_URL/rest/api/3/issue/$TICKET_KEY/transitions" \
    -d '{"transition":{"id":"41"}}' > /dev/null
  echo "  → Jira $TICKET_KEY created & marked Done: $JIRA_BASE_URL/browse/$TICKET_KEY"
else
  echo "  → Jira ticket creation failed: $RESPONSE"
fi
