# Security Guidelines for Omnius

## Handling Tokens and API Keys

### Discord Token Security

**IMPORTANT**: If you've accidentally committed your Discord token or API keys to Git or shared them in any way, you should immediately regenerate them. **A token that has been exposed should be considered compromised.**

### ⚠️ IMMEDIATE ACTION REQUIRED ⚠️

Your Discord token has been exposed during this session. You must immediately:

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application
3. Go to the "Bot" section
4. Click "Reset Token" under the token section
5. Confirm the action and copy your new token
6. Update your `.env` file with the new token

### Best Practices for API Keys and Tokens

1. **Never commit tokens to Git**
   - Always use `.env` files for local development
   - Ensure `.env` is in your `.gitignore` file
   - Use `.env.example` as a template with placeholder values

2. **Rotate tokens regularly**
   - Change your tokens periodically, especially for production systems
   - Immediately rotate tokens if you suspect they've been compromised

3. **Use environment variables in production**
   - For deployed applications, use environment variables provided by your hosting platform
   - Don't store tokens in files in production environments

4. **Implement token scoping**
   - Discord bot tokens should have only the permissions they need
   - Use the minimal set of scopes and permissions required

5. **Audit and monitoring**
   - Regularly check your application's API usage
   - Monitor for unusual activity that could indicate a compromised token

## Log File Security

Your log files may contain sensitive information, such as your bot's client ID. The client ID is a component used to generate the bot token, so while it's not a secret on its own, it's best to keep it private when possible.

To properly secure your logs:

1. **Keep logs out of version control**
   - Ensure log files are in `.gitignore`
   - Only store logs in designated locations

2. **Implement log rotation**
   - Set up log rotation to avoid excessive log buildup
   - Remove old logs that are no longer needed

3. **Sanitize logs**
   - Consider implementing a log filter to sanitize sensitive information
   - Remove or mask IDs, tokens, and other potentially sensitive data

4. **Secure log access**
   - Restrict access to log files in production environments
   - Use appropriate file permissions (e.g., 0640 or 0600)

## Environment File (.env)

Your `.env` file should follow this template:

```
# Discord Bot Configuration
DISCORD_TOKEN=your_discord_token_here

# LLM Configuration
LLM_MODEL_PATH=models/mistral-7b-v0.1.gguf
LLM_CONTEXT_SIZE=4096
LLM_THREADS=4

# Vector Store Configuration
VECTOR_STORE_PATH=data/vector_store
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/omnius.log
```

Remember: **Never share your `.env` file with others or commit it to version control.** 