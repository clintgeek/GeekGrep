# OpenAI API Configuration

## Overview

geekGrep supports two LLM backends:
- **OpenAI** (default) - Cloud-based, requires API key
- **Ollama** (local) - Self-hosted, no API key needed

## Getting an OpenAI API Key

### Step 1: Create OpenAI Account
1. Go to https://platform.openai.com/signup
2. Sign up or log in with your account
3. Verify your email

### Step 2: Create API Key
1. Navigate to https://platform.openai.com/api/keys
2. Click "Create new secret key"
3. Copy the key (you won't see it again)

### Step 3: Add to .env File

Edit `.env` in the project root:

```bash
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_API_URL=https://api.openai.com/v1
GEEKGREP_LLM_BACKEND=openai
GEEKGREP_MODEL=gpt-4o-mini
```

Replace `sk-your-actual-key-here` with your actual API key.

**Note:** `OPENAI_API_URL` defaults to OpenAI's official endpoint. Use this if:
- Using a proxy or reverse proxy
- Using Azure OpenAI (different URL)
- Using a compatible API provider (e.g., vLLM, LocalAI)

### Step 4: Restart Docker

```bash
docker compose restart geekgrep
```

## Available Models

- `gpt-4o-mini` (recommended) - Fast, cost-effective
- `gpt-4o` - Most capable
- `gpt-3.5-turbo` - Legacy, cheaper

## Pricing

Check current pricing at https://openai.com/pricing

## Troubleshooting

**"Invalid API key" error:**
- Verify the key is correct
- Check it hasn't been revoked
- Ensure no extra spaces in `.env`

**"Rate limit exceeded":**
- You've hit usage limits
- Wait a moment and retry
- Check your usage at https://platform.openai.com/account/usage/overview

**"Model not found":**
- Verify model name is correct
- Check you have access to the model
- Some models may require specific account tiers

## Using Ollama Instead

To use local Ollama instead:

```bash
GEEKGREP_LLM_BACKEND=ollama
GEEKGREP_MODEL=llama2
```

Then start Ollama:
```bash
docker compose --profile local up
```

## Security Notes

- Never commit `.env` to version control (already in `.gitignore`)
- Keep your API key private
- Monitor usage to avoid unexpected charges
- Consider setting spending limits in OpenAI dashboard

## TODO: Web UI Configuration

Future enhancement: Add API key configuration directly in the Streamlit web UI sidebar for easier setup without editing `.env` files.
