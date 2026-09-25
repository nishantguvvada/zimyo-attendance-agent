# Zimyo Attendance Logger

Automated attendance logging for Zimyo portal using a LangGraph-based AI agent. Runs on a schedule via GitHub Actions (free) or manually via CLI.

## Features

- 🤖 **LangGraph Agent** - Intelligent decision-making for clock in/out based on time windows
- 🌍 **UAE Timezone Aware** - Automatically handles Asia/Dubai timezone
- 📅 **Smart Scheduling** - Only runs on weekdays, respects clock-in/out windows
- 💾 **Local Storage** - JSON file storage with full history
- ☁️ **Free Hosting** - Runs on GitHub Actions (no server costs)
- 🔐 **Secure Credentials** - Uses GitHub Secrets for sensitive data
- 📊 **Rich CLI** - Beautiful terminal output with history viewing

## Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo>
cd zimyo-attendance
```

### 2. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
# Edit .env with your Zimyo credentials
```

### 4. Test Locally

```bash
# Check current status
uv run python -m zimyo_attendance status

# Run auto attendance (decides based on time)
uv run python -m zimyo_attendance auto

# Force clock in
uv run python -m zimyo_attendance clock_in

# Force clock out
uv run python -m zimyo_attendance clock_out

# View history
uv run python -m zimyo_attendance history
```

## GitHub Actions Deployment (Free)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/zimyo-attendance.git
git push -u origin main
```

### 2. Add Repository Secrets

Go to your GitHub repo → Settings → Secrets and variables → Actions → New repository secret:

| Secret Name | Value |
|-------------|-------|
| `ZIMYO_USERNAME` | `nishant.guvvada@idctechnologies.com` |
| `ZIMYO_PASSWORD` | `okhxckfzr0` |
| `ZIMYO_BASE_URL` | `https://zimyo.work` |
| `ZIMYO_EMPLOYEE_ID` | `768646` |
| `CLOCK_IN_WINDOW_START` | `08:30` |
| `CLOCK_IN_WINDOW_END` | `09:30` |
| `CLOCK_OUT_WINDOW_START` | `17:30` |
| `CLOCK_OUT_WINDOW_END` | `18:30` |
| `TIMEZONE` | `Asia/Dubai` |

### 3. Enable Workflow

The workflow runs automatically on schedule. You can also trigger manually from Actions tab.

## Schedule Configuration

The GitHub Actions workflow runs on this schedule (UTC times for UAE UTC+4):

| Action | UAE Time | Cron (UTC) |
|--------|----------|------------|
| Clock-in attempts | 8:30-9:30 AM | `*/15 4-5 * * 1-5` |
| Clock-out attempts | 5:30-6:30 PM | `*/15 13-14 * * 1-5` |
| Ensure clock-in | 8:30 AM sharp | `30 4 * * 1-5` |
| Ensure clock-out | 6:00 PM sharp | `0 14 * * 1-5` |

## Project Structure

```
zimyo-attendance/
├── .github/
│   └── workflows/
│       └── attendance.yml      # GitHub Actions workflow
├── zimyo_attendance/
│   ├── __init__.py
│   ├── __main__.py             # CLI entry point
│   ├── agent/
│   │   └── graph.py            # LangGraph workflow
│   ├── config/
│   │   └── settings.py         # Configuration management
│   ├── storage/
│   │   └── json_file.py        # JSON file storage
│   └── tools/
│       └── zimyo_client.py     # Zimyo API client
├── data/
│   └── attendance.json         # Attendance records (auto-generated)
├── .env                        # Local environment (gitignored)
├── .env.example                # Template for environment variables
├── pyproject.toml              # Project configuration
└── README.md                   # This file
```

## How It Works

### LangGraph Agent Flow

```
get_uae_time → check_status → decide → [clock_in | clock_out | respond] → respond → END
```

1. **get_uae_time** - Gets current UAE time
2. **check_status** - Fetches attendance from Zimyo API
3. **decide** - LLM-free logic decides action based on:
   - Current UAE time
   - Clock-in/out windows
   - Current attendance status
   - Weekend check
4. **Execute** - Performs clock_in, clock_out, or just reports status
5. **respond** - Saves record to storage, formats output

### Decision Logic

| Current Status | Time Window | Action |
|----------------|-------------|--------|
| NOT_CLOCKED_IN | 8:30-9:30 AM | Clock In |
| NOT_CLOCKED_IN | Before 8:30 | Wait |
| NOT_CLOCKED_IN | After 9:30 | Manual needed |
| CLOCKED_IN | 5:30-6:30 PM | Clock Out |
| CLOCKED_IN | Before 5:30 | Wait |
| CLOCKED_IN | After 6:30 | Clock Out (late) |
| CLOCKED_OUT | Any | Already done |

## Customization

### Adjust Time Windows

Edit `.env` or GitHub Secrets:
```bash
CLOCK_IN_WINDOW_START=08:30
CLOCK_IN_WINDOW_END=09:30
CLOCK_OUT_WINDOW_START=17:30
CLOCK_OUT_WINDOW_END=18:30
```

### Add Holiday Support

Modify `decide_action` in `agent/graph.py` to check against a holiday calendar.

### Notifications

Add Slack/Telegram webhook in `format_response` function.

## Troubleshooting

### Login Fails
- Verify credentials in `.env` / GitHub Secrets
- Check if Zimyo portal is accessible
- Employee ID might be different - check network tab in browser

### Clock In/Out Fails
- The actual punch endpoints may differ - check browser dev tools Network tab
- Some endpoints require CSRF tokens or specific headers
- Selfie attendance may be required (`ENABLE_SELFIE_ATTENDANCE=1`)

### GitHub Actions Not Running
- Check Actions tab for workflow runs
- Verify secrets are set correctly
- Check workflow file syntax

## License

MIT License - Feel free to use and modify.

## Disclaimer

This tool automates attendance logging for personal use. Ensure compliance with your company's policies. Use responsibly.