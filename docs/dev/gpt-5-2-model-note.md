# GPT-5.2 Model Configuration Note

**Date:** 2025-12-17

## Current Configuration

The AI processing is configured to use `gpt-5.2` as the tagging model:

```yaml
# config/ai_settings.yaml
openai:
  tagging_model: gpt-5.2
```

## Important Notes

### Model Availability

**GPT-5.2** may not be available in all OpenAI accounts. Check your account's available models:

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY" | jq '.data[].id' | grep gpt
```

### Fallback Options

If GPT-5.2 is not available, update `config/ai_settings.yaml` to use:

#### Option 1: GPT-4o (Recommended)
```yaml
openai:
  tagging_model: gpt-4o
  max_tokens: 600
  temperature: 0.3
```

**Pricing:** $2.50 input / $10 output per 1M tokens
**Cost for 871 bookmarks:** ~$5.23 (assumes ~800 input / ~400 output tokens per bookmark)

#### Option 2: GPT-4o-mini (Budget)
```yaml
openai:
  tagging_model: gpt-4o-mini
  max_tokens: 600
  temperature: 0.3
```

**Pricing:** $0.15 input / $0.60 output per 1M tokens
**Cost for 871 bookmarks:** ~$0.31

#### Option 3: GPT-4-turbo
```yaml
openai:
  tagging_model: gpt-4-turbo
  max_tokens: 600
  temperature: 0.3
```

**Pricing:** $10 input / $30 output per 1M tokens
**Cost for 871 bookmarks:** ~$17.40

## Error Handling

If the configured model is not available, you'll see:

```
Error: The model `gpt-5.2` does not exist or you do not have access to it.
```

**Solution:** Update `config/ai_settings.yaml` with one of the fallback options above.

## Recommended Approach

1. **Try GPT-5.2 first** - If you have access, it likely offers best value
2. **Fall back to GPT-4o** - Excellent quality, reasonable cost
3. **Use GPT-4o-mini for testing** - Much cheaper, still good quality

## Quality vs Cost Trade-off

| Model | Quality | Cost (871 bookmarks) | Speed |
|-------|---------|---------------------|-------|
| GPT-5.2 | ??? (TBD) | TBD (assume similar to GPT-4o unless confirmed) | Fast |
| GPT-4o | Excellent | ~$5.23 | Fast |
| GPT-4o-mini | Good | ~$0.31 | Very Fast |
| GPT-4-turbo | Excellent | ~$17.40 | Slower |

**Recommendation:** Start with GPT-4o for production, GPT-4o-mini for testing.
