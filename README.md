# CV Tailoring Dashboard

AI-powered CV tailoring system that adapts your CV to match job descriptions, analyzes skill gaps, and maintains application history.

## Features

- **AI-Powered CV Tailoring**: Automatically adapts CV content to match job descriptions
- **Skill Gap Analysis**: Identifies missing skills and suggests how to acquire them
- **Application History**: Track all your job applications with organized records
- **PDF Generation**: Automatically generates PDF versions of tailored CVs
- **Historical Learning**: Uses previous tailored CVs to improve future adaptations

## Setup

### Prerequisites

- Python 3.14+
- `uv` package manager
- Playwright (for PDF generation)

### Installation

1. Install dependencies:
```bash
uv sync
```

2. Install Playwright browsers:
```bash
uv run playwright install chromium
```

3. Configure AI API:
   - Copy `.env.example` to `.env`
   - Add your Vercel AI Gateway URL and API key, or configure OpenAI directly
   - Alternatively, edit `config.json` directly

### Configuration

Edit `config.json` or set environment variables:

```json
{
  "ai": {
    "gateway_url": "https://ai-gateway.vercel.sh/v1",
    "api_key": "your-api-key",
    "model": "gpt-4"
  },
  "cv_template_path": "cv.html"
}
```

**Important**: The official Vercel AI Gateway URL is `https://ai-gateway.vercel.sh/v1`. If you're using a custom gateway, ensure it's accessible and ends with `/v1`.

Or use environment variables:
- `VERCEL_AI_GATEWAY_URL`: Vercel AI Gateway endpoint (default: `https://ai-gateway.vercel.sh/v1`)
- `VERCEL_AI_API_KEY`: API key for the gateway

**Note**: You can also use OpenAI directly by leaving `gateway_url` empty and setting `OPENAI_API_KEY` instead.

## Usage

### Verify Installation

Before starting, verify everything is set up correctly:

```bash
uv run python test_app.py
```

### Start the Dashboard

```bash
uv run python run.py
```

The dashboard will be available at `http://localhost:5000`

### Generate a Tailored CV

1. Click "Generate New CV" in the dashboard
2. Paste the job description
3. Optionally add company name and job title
4. Review skill gaps if any are detected
5. Add missing skills if you have them
6. Generate the tailored CV

### View Application History

- All applications are saved in the `applications/` directory
- View details, download PDFs, and add skills to existing applications

## Project Structure

```
open-cv-gen/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes.py            # Web routes
│   ├── ai_client.py         # AI API client
│   ├── cv_engine.py         # CV tailoring engine
│   ├── skill_analyzer.py    # Skill gap analysis
│   └── storage.py           # JSON storage operations
├── templates/               # HTML templates
├── applications/            # Application history (JSON)
├── cv_history/             # Generated CV HTML/PDF files
├── config.json             # Configuration
├── cv.html                 # Base CV template
├── html_to_pdf.py          # PDF generation
└── run.py                  # Application entry point
```

## How It Works

1. **Job Description Analysis**: Extracts required skills and requirements
2. **Skill Gap Detection**: Compares job requirements with CV skills
3. **Interactive Prompting**: Asks user about missing skills
4. **CV Tailoring**: Uses AI to adapt CV content while maintaining accuracy
5. **Historical Learning**: Uses previous tailored CVs to improve adaptations
6. **PDF Generation**: Creates print-ready PDF versions
7. **Application tracking**: Saves all applications for follow-up

## Notes

- The base CV template (`cv.html`) is preserved and used as a starting point
- All generated CVs are saved for future reference
- Skill gaps are tracked and can be addressed later
- Historical CVs inform future tailoring for better results

