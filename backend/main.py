from fastapi import FastAPI, Form, HTTPException, Request
import os
import requests
import logging
import traceback
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()
# this is teat and my name is mohit
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://d9a538b0c699.ngrok-free.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get GitHub token from environment variable
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable is required")

GITHUB_TOKEN = GITHUB_TOKEN.strip()

# GitHub API headers
headers_github = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "GitHub-Webhook-Handler"
}

# Hugging Face API setup
HF_API_KEY = os.getenv("HF_API_KEY", "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")
API_URL = "https://router.huggingface.co/v1/chat/completions"
headers_hf = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

def post_comment_to_pr(owner: str, repo: str, pr_number: int, comment: str):
    """Post a comment to the GitHub PR"""
    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{pr_number}/comments"
        
        payload = {
            "body": comment
        }
        
        response = requests.post(url, headers=headers_github, json=payload, timeout=30)
        
        if response.status_code == 201:
            logger.info(f"Successfully posted comment to PR #{pr_number}")
            return True
        else:
            logger.error(f"Failed to post comment: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error posting comment to PR: {str(e)}")
        return False

def query_huggingface(text: str):
    """Query Hugging Face API for code review"""
    try:
        system_prompt = """You are an expert code reviewer. Analyze the provided code and give feedback on:

**Bugs & Logic Issues**: Identify any errors or logical problems
**Security**: Check for vulnerabilities and security best practices  
**Performance**: Suggest optimizations and efficiency improvements
**Code Quality**: Assess readability, naming, and structure
**Best Practices**: Review adherence to coding standards

**RECOMMENDATIONS**
Categorize findings as:
- 🚨 **Fix Now**: Bugs that break functionality, security vulnerabilities
- ⚡ **Improve**: Performance bottlenecks, code quality issues, maintainability  
- ✨ **Enhance**: Style consistency, documentation, minor optimizations

Be concise but thorough. Format your response in GitHub-compatible markdown."""

        payload = {
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": f"Please review this code:\n\n{text}"
                }
            ],
            "model": "Qwen/Qwen3-Coder-480B-A35B-Instruct:novita",
            "temperature": 0.3,
            "max_tokens": 900
        }
        
        logger.info(f"Sending request to HF API with payload size: {len(str(payload))}")
        
        response = requests.post(
            API_URL, 
            headers=headers_hf, 
            json=payload,
            timeout=60  # Increased timeout for code review
        )
        
        logger.info(f"HF API response status: {response.status_code}")
        
        if response.status_code != 200:
            logger.error(f"HF API error: {response.status_code} - {response.text}")
            response.raise_for_status()
        
        response_data = response.json()
        logger.info("Successfully received response from HF API")
        
        return response_data
        
    except requests.exceptions.Timeout:
        logger.error("Request to HF API timed out")
        raise HTTPException(status_code=504, detail="Request timed out")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception: {str(e)}")
        raise HTTPException(status_code=502, detail=f"External API error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in query_huggingface: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

@app.post("/")
async def github_webhook(request: Request):
    try:
        payload = await request.json()
        
        # Check if this is a pull request event
        if "pull_request" not in payload:
            logger.info("Not a pull request event, ignoring")
            return {"message": "Not a PR event"}
        
        # Extract basic info
        action = payload.get("action")
        pr_data = payload.get("pull_request")
        
        if not pr_data:
            logger.warning("No pull request data found")
            return {"message": "No PR data"}
        
        repo = payload["repository"]["name"]
        owner = payload["repository"]["owner"]["login"]
        pr_number = pr_data["number"]
        
        logger.info(f"Processing PR #{pr_number} in {owner}/{repo}, action: {action}")
        
        # Only process relevant actions
        if action in ["closed", "locked", "unlocked"]:
            logger.info(f"Ignoring action: {action}")
            return {"message": f"Action {action} ignored"}
        
        if action == "edited":
            changes = payload.get("changes", {})
            if "body" in changes or "title" in changes:
                logger.info(f"PR #{pr_number} title/description was edited")
                return {"message": "PR metadata edited, no file processing needed"}
        
        # Get PR files for code-related actions
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
        logger.info(f"Fetching files from: {url}")
        
        response = requests.get(url, headers=headers_github, timeout=30)
        
        if response.status_code == 401:
            logger.error("GitHub API authentication failed - check your GITHUB_TOKEN")
            logger.error("Make sure token has 'repo' scope and is not expired")
            raise HTTPException(status_code=500, detail="GitHub authentication failed")
        elif response.status_code == 403:
            logger.error("GitHub API rate limit or insufficient permissions")
            raise HTTPException(status_code=500, detail="GitHub API access denied")
        elif response.status_code == 404:
            logger.error("Repository or PR not found - check token permissions")
            raise HTTPException(status_code=500, detail="Repository not accessible")
        elif response.status_code != 200:
            logger.error(f"GitHub API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail="Failed to fetch PR files")
        
        files = response.json()
        logger.info(f"Found {len(files)} files in PR #{pr_number}")
        
        # Process files and generate code reviews
        all_reviews = []
        code_files_count = 0
        
        for file in files:
            filename = file.get("filename", "Unknown")
            status = file.get("status", "Unknown")
            additions = file.get("additions", 0)
            deletions = file.get("deletions", 0)
            patch = file.get("patch", "")
            
            # Skip non-code files or files without patches
            if not patch or patch == "No patch available":
                logger.info(f"Skipping {filename} - no patch data")
                continue
                
            # Filter for code files (you can customize these extensions)
            code_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb', '.cs', '.swift', '.kt']
            if not any(filename.lower().endswith(ext) for ext in code_extensions):
                logger.info(f"Skipping {filename} - not a code file")
                continue
            
            logger.info(f"Processing code file: {filename}")
            code_files_count += 1
            
            try:
                # Get AI review for this file
                review_response = query_huggingface(patch)
                
                if review_response and 'choices' in review_response:
                    review_content = review_response['choices'][0]['message']['content']
                    
                    file_review = f"""## 📄 Code Review: `{filename}`
**Status**: {status} (+{additions}/-{deletions} lines)

{review_content}

---"""
                    
                    all_reviews.append(file_review)
                    logger.info(f"Generated review for {filename}")
                else:
                    logger.warning(f"No valid review response for {filename}")
                    
            except Exception as e:
                logger.error(f"Error reviewing {filename}: {str(e)}")
                error_review = f"""## 📄 Code Review: `{filename}`
**Status**: {status} (+{additions}/-{deletions} lines)

❌ **Error**: Unable to generate review for this file due to processing error.

---"""
                all_reviews.append(error_review)
        
        # Post comprehensive comment if we have reviews
        if all_reviews:
            comment_header = f"""# 🤖 AI Code Review
**PR #{pr_number}**: Automated code review completed

**Summary**: Reviewed {code_files_count} code file(s) with AI assistance.

"""
            
            full_comment = comment_header + "\n".join(all_reviews)
            
            # GitHub has a comment size limit (~65KB), so truncate if needed
            if len(full_comment) > 60000:
                full_comment = full_comment[:60000] + "\n\n*Comment truncated due to length limit.*"
            
            success = post_comment_to_pr(owner, repo, pr_number, full_comment)
            
            if success:
                logger.info(f"Successfully posted AI code review to PR #{pr_number}")
            else:
                logger.error(f"Failed to post AI code review to PR #{pr_number}")
        else:
            logger.info(f"No code files to review in PR #{pr_number}")
        
        return {
            "message": "Webhook processed successfully",
            "pr_number": pr_number,
            "files_count": len(files),
            "code_files_reviewed": code_files_count,
            "repository": f"{owner}/{repo}",
            "action": action,
            "review_posted": len(all_reviews) > 0
        }
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


@app.post("/process/")
async def process_input(text: str = Form(None)):
    try:
        logger.info(f"Received request with text length: {len(text) if text else 0}")
        
        if not text:
            raise HTTPException(status_code=400, detail="No input provided. Submit either text or a file.")
        
        # Basic input validation and sanitization
        if len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Input text cannot be empty.")
        
        if len(text) > 10000:  # Reduced limit to avoid token issues
            raise HTTPException(status_code=400, detail="Input text too large. Please submit smaller code chunks (max 10,000 characters).")
        
        # Call Hugging Face API
        hf_response = query_huggingface(text)
        
        # Extract response safely
        if "choices" not in hf_response or not hf_response["choices"]:
            logger.error(f"Invalid HF response structure: {hf_response}")
            raise HTTPException(status_code=502, detail="Invalid response from AI model")
        
        assistant_reply = hf_response["choices"][0]["message"]["content"]
        
        logger.info("Successfully processed request")
        
        return {
            "input_type": "text",
            "input": text[:500] + "..." if len(text) > 500 else text,  # Truncate for response
            "model_response": assistant_reply,
            "status": "success"
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_input: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "api_key_configured": bool(HF_API_KEY)}

# Add a simple test endpoint
@app.get("/")
async def root():
    return {"message": "Code Review API is running"}
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
