from fastapi import FastAPI, Form, HTTPException, Request
import os
import requests
import logging
import traceback
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://8939872d51c8.ngrok-free.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN","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")
headers1 = {
    "Authorization": "Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

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
        
        # Handle different PR actions
        if action == "edited":
            # Check what was edited
            changes = payload.get("changes", {})
            if "body" in changes or "title" in changes:
                logger.info(f"PR #{pr_number} title/description was edited")
                # You might want to re-analyze if description contains special commands
                # For now, we'll skip file processing since code didn't change
                return {"message": "PR metadata edited, no file processing needed"}
            else:
                logger.info(f"PR #{pr_number} edited but no relevant changes detected")
                return {"message": "PR edited but no action needed"}
        
        # Process code-related actions
        if action not in ["opened", "synchronize", "reopened"]:
            logger.info(f"Ignoring action: {action}")
            return {"message": f"Action {action} ignored"}
        
        # Get PR files
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}/files"
        logger.info(f"Fetching files from: {url}")
        
        response = requests.get(url, headers=headers1, timeout=30)
        
        if response.status_code == 401:
            logger.error("GitHub API authentication failed - check your GITHUB_TOKEN")
            raise HTTPException(status_code=500, detail="GitHub authentication failed")
        elif response.status_code == 403:
            logger.error("GitHub API rate limit or insufficient permissions")
            raise HTTPException(status_code=500, detail="GitHub API access denied")
        elif response.status_code != 200:
            logger.error(f"GitHub API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail="Failed to fetch PR files")
        
        files = response.json()
        
        logger.info(f"Found {len(files)} files in PR #{pr_number}")
        
        for file in files:
            filename = file.get("filename", "Unknown")
            status = file.get("status", "Unknown")
            additions = file.get("additions", 0)
            deletions = file.get("deletions", 0)
            patch = file.get("patch", "No patch available")
            
            print(f"📄 File: {filename}")
            print(f"📊 Status: {status} (+{additions}/-{deletions})")
            print(f"📝 Patch:\n{patch}")
            print("-" * 80)
        
        # Here you can add your custom logic to process the files
        # For example: code review, testing, deployment, etc.
        
        return {
            "message": "Webhook processed successfully",
            "pr_number": pr_number,
            "files_count": len(files),
            "repository": f"{owner}/{repo}"
        }
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


HF_API_KEY = os.getenv("HF_API_KEY", "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")

API_URL = "https://router.huggingface.co/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

def query_huggingface(text: str):
    try:
        system_prompt = """You are an expert code reviewer. Analyze the provided code and give feedback on:

Bugs & Logic Issues: Identify any errors or logical problems
Security: Check for vulnerabilities and security best practices
Performance: Suggest optimizations and efficiency improvements
Code Quality: Assess readability, naming, and structure
Best Practices: Review adherence to coding standards

RECOMMENDATIONS
Categorize findings as:

Fix Now: Bugs that break functionality, security vulnerabilities
Improve: Performance bottlenecks, code quality issues, maintainability
Enhance: Style consistency, documentation, minor optimizations

Be concise but thorough.

Example Code Review
Code Submitted:
pythonimport hashlib
import sqlite3

def login_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    result = cursor.execute(query).fetchone()
    
    if result:
        return True
    else:
        return False

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

class UserManager:
    def __init__(self):
        self.users = []
    
    def addUser(self, user):
        self.users.append(user)
        
    def findUser(self, username):
        for i in range(0, len(self.users)):
            if self.users[i].username == username:
                return self.users[i]
        return None
Code Review Analysis
🚨 Fix Now

SQL Injection Vulnerability (Line 7)

Issue: Direct string interpolation in SQL query allows injection attacks
Impact: Complete database compromise possible
Fix: Use parameterized queries

pythonquery = "SELECT * FROM users WHERE username = ? AND password = ?"
result = cursor.execute(query, (username, password)).fetchone()

Weak Cryptographic Hash (Line 15)

Issue: MD5 is cryptographically broken and unsuitable for passwords
Impact: Passwords easily crackable with rainbow tables
Fix: Use bcrypt, scrypt, or Argon2

pythonimport bcrypt
return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

Resource Leak (Line 5)

Issue: Database connection never closed
Impact: Connection pool exhaustion under load
Fix: Use context manager or explicit close()



⚡ Improve

Inefficient Linear Search (Line 26-29)

Issue: O(n) time complexity for user lookup
Impact: Poor performance with large user lists
Fix: Use dictionary for O(1) lookups

pythonself.users = {}  # username -> user mapping

Poor Error Handling

Issue: No exception handling for database operations
Impact: Application crashes on DB errors
Fix: Add try-catch blocks with proper error responses


Inconsistent Return Pattern (Line 9-12)

Issue: Explicit True/False return instead of direct boolean
Fix: return bool(result) or return result is not None
✨ Enhance
Naming Convention Inconsistency
Issue: Mixed camelCase (addUser) and snake_case (login_user)
Fix: Use consistent snake_case per PEP 8


Missing Type Hints

Enhancement: Add type annotations for better code clarity

pythondef login_user(username: str, password: str) -> bool:

No Docstrings

Enhancement: Add function documentation

pythondef login_user(username: str, password: str) -> bool:
    ""Authenticate user credentials against database.""

Magic Numbers/Strings

Issue: Hardcoded database filename
Fix: Use configuration constants



Summary

Critical Issues: 3 security vulnerabilities requiring immediate attention
Performance Issues: 1 scalability concern
Code Quality: 6 improvements for maintainability and standards compliance

Priority: Address SQL injection and weak hashing immediately before deployment.

Use this format and depth of analysis when reviewing code"""

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
            "max_tokens": 1900
        }
        
        logger.info(f"Sending request to HF API with payload size: {len(str(payload))}")
        
        response = requests.post(
            API_URL, 
            headers=headers, 
            json=payload,
            timeout=30  # Add timeout
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
