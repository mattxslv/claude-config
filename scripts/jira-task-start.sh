#!/bin/bash

# UserPromptSubmit hook — creates a Jira ticket as "In Progress" when a dev task starts.
# Skips if a session ticket already exists (avoids duplicates mid-task).

CONFIG="$HOME/.claude/.jira-config"
SESSION_FILE="$HOME/.claude/.jira-session"

if [ ! -f "$CONFIG" ]; then exit 0; fi
source "$CONFIG"

# Skip if a session ticket is already active
if [ -f "$SESSION_FILE" ]; then exit 0; fi

# Read prompt from stdin JSON
INPUT=$(cat)
PROMPT=$(echo "$INPUT" | node -e "
  let d='';
  process.stdin.on('data',c=>d+=c);
  process.stdin.on('end',()=>{
    try { process.stdout.write(JSON.parse(d).prompt||'') }
    catch { process.stdout.write('') }
  })
" 2>/dev/null)

if [ -z "$PROMPT" ]; then exit 0; fi

# Detect dev task vs question — only create ticket for actionable tasks
IS_TASK=$(echo "$PROMPT" | node -e "
  let d='';
  process.stdin.on('data',c=>d+=c);
  process.stdin.on('end',()=>{
    const p = d.trim().toLowerCase();
    const questions = ['what ','how ','why ','explain','show me','describe','tell me','can you explain','should i','is there','does ','will ','would ','could you explain'];
    const tasks = ['fix','add','implement','create','build','update','refactor','optimize','remove','delete','migrate','setup','configure','integrate','deploy','write','make','change','move','rename','convert','replace'];
    const isQuestion = questions.some(w => p.startsWith(w));
    const hasTask = tasks.some(v => {
      const re = new RegExp('\\\\b' + v + '\\\\b');
      return re.test(p);
    });
    process.stdout.write((hasTask && !isQuestion) ? 'yes' : 'no');
  })
" 2>/dev/null)

if [ "$IS_TASK" != "yes" ]; then exit 0; fi

# Determine issue type from prompt keywords
ISSUE_TYPE_ID="10004" # Task (default)
if echo "$PROMPT" | grep -qiE '\bfix\b|\bbug\b|\bbroken\b|\berror\b|\bcrash\b'; then
  ISSUE_TYPE_ID="10005" # Bug
elif echo "$PROMPT" | grep -qiE '\badd\b|\bimplement\b|\bcreate\b|\bbuild\b|\bfeature\b|\bnew\b'; then
  ISSUE_TYPE_ID="10003" # Story
fi

# Build summary: clean up prompt into a proper ticket title
BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
SUMMARY=$(echo "$PROMPT" | node -e "
  let d=''; process.stdin.on('data',c=>d+=c); process.stdin.on('end',()=>{
    let s = d.trim()
      .replace(/https?:\/\/[^\s]+/g, '')  // strip URLs
      .replace(/\[Image[^\]]*\]/g, '')     // strip [Image #N]
      .replace(/\s+/g, ' ')               // collapse whitespace
      .trim()
    if (s) s = s[0].toUpperCase() + s.slice(1)
    if (s.length > 80) s = s.slice(0, 77) + '...'
    process.stdout.write('[${BRANCH}] ' + (s || 'Task'))
  })
" 2>/dev/null)
if [ -z "$SUMMARY" ]; then SUMMARY="[$BRANCH] Task"; fi

RESPONSE=$(curl -s -u "$JIRA_EMAIL:$JIRA_TOKEN" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  "$JIRA_BASE_URL/rest/api/3/issue" \
  -d "{
    \"fields\": {
      \"project\": { \"key\": \"$JIRA_PROJECT_KEY\" },
      \"summary\": $(echo "$SUMMARY" | node -e "let d=''; process.stdin.on('data',c=>d+=c); process.stdin.on('end',()=>process.stdout.write(JSON.stringify(d.trim())))"),
      \"issuetype\": { \"id\": \"$ISSUE_TYPE_ID\" },
      \"assignee\": { \"accountId\": \"$JIRA_ACCOUNT_ID\" },
      \"customfield_10020\": $JIRA_SPRINT_ID
    }
  }")

TICKET_KEY=$(echo "$RESPONSE" | node -e "
  let d='';
  process.stdin.on('data',c=>d+=c);
  process.stdin.on('end',()=>{
    try { process.stdout.write(JSON.parse(d).key||'ERROR') }
    catch { process.stdout.write('ERROR') }
  })
" 2>/dev/null)

if [ "$TICKET_KEY" != "ERROR" ] && [ -n "$TICKET_KEY" ]; then
  # Transition to In Progress (ID: 21)
  curl -s -u "$JIRA_EMAIL:$JIRA_TOKEN" \
    -X POST \
    -H "Content-Type: application/json" \
    "$JIRA_BASE_URL/rest/api/3/issue/$TICKET_KEY/transitions" \
    -d '{"transition":{"id":"21"}}' > /dev/null

  echo "$TICKET_KEY" > "$SESSION_FILE"
  echo "  → Jira $TICKET_KEY created (In Progress): $JIRA_BASE_URL/browse/$TICKET_KEY"
fi

exit 0
