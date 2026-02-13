#!/bin/bash
# Render Keep-Alive Script
# Run this as a cron job or background service to ping your Render app

# Configuration
RENDER_URL="${RENDER_URL:-https://your-app.onrender.com}"
INTERVAL="${KEEP_ALIVE_INTERVAL:-600}"  # 10 minutes default

# Log file (optional)
LOG_FILE="${LOG_FILE:-/tmp/render_keep_alive.log}"

echo "$(date): Starting keep-alive for $RENDER_URL (interval: ${INTERVAL}s)"

while true; do
    # Ping health endpoint
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time 30 "$RENDER_URL/health")
    
    if [ "$response" = "200" ]; then
        echo "$(date): ✅ Ping successful (HTTP $response)"
    else
        echo "$(date): ⚠️  Ping failed (HTTP $response)"
    fi
    
    # Sleep for interval
    sleep "$INTERVAL"
done
