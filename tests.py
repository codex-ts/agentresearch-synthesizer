  #!/usr/bin/env python3
"""
Quick test script to verify Research Agent components.
Run with: python test.py
"""
import os
import json
import tempfile
from dotenv import load_dotenv
import smtplib

# Load environment variables
load_dotenv()

print("🔍 Running Component Tests\n" + "="*50)

# ── Test 1: Validator ─────────────────────────────────────
print("\n✅ Test 1: validator.py")
try:
    from validator import parse_and_validate_report
    
    sample_json = '''
    {
        "title": "Test Report",
        "summary": "This is a test summary.",
        "key_findings": [
            {
                "title": "Finding 1",
                "explanation": "Test explanation",
                "confidence": "Empirical Evidence"
            }
        ],
        "why_it_matters": "Testing matters.",
        "sources": [
            {
                "title": "Test Source",
                "url": "https://example.com",
                "source_type": "web",
                "authors": [],
                "published_date": "2026-01-01",
                "summary": "Test summary"
            }
        ]
    }
    '''
    result = parse_and_validate_report(sample_json)
    print(f"   ✓ Validator passed. Title: {result['title']}")
except Exception as e:
    print(f"   ✗ Validator failed: {e}")

# ── Test 2: PDF Generator ─────────────────────────────────
print("\n✅ Test 2: pdf_generator.py + formatter.py")
try:
    from formatter import generate_html
    from pdf_generator import save_pdf
    
    sample_report = {
        "title": "Test Report",
        "summary": "This is a test summary.",
        "key_findings": [
            {"title": "Finding 1", "explanation": "Test", "confidence": "Empirical Evidence"}
        ],
        "why_it_matters": "Testing matters.",
        "sources": []
    }
    
    html = generate_html(sample_report)
    test_pdf = "test_report.pdf"
    save_pdf(html, test_pdf)
    
    if os.path.exists(test_pdf):
        size = os.path.getsize(test_pdf)
        print(f"   ✓ PDF generated: {test_pdf} ({size} bytes)")
    else:
        print("   ✗ PDF file not created")
except Exception as e:
    print(f"   ✗ PDF generation failed: {e}")

# ── Test 3: Email Sender ──────────────────────────────────
print("\n✅ Test 3: emailer.py")
try:
    from emailer import send_email
    
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")
    receiver = os.getenv("EMAIL_USER")  # Send to self for testing
    
    if not all([sender, password]):
        print("   ⚠ Skipping email test: EMAIL_USER or EMAIL_PASS not set in .env")
    else:
        # Use the PDF from Test 2, or create a dummy one
        test_file = "test_report.pdf" if os.path.exists("test_report.pdf") else "validator.py"
        
        print(f"   → Sending test email to {receiver}...")
        send_email(
            sender_email=sender,
            app_password=password,
            receiver_email=receiver,
            file_path=test_file
        )
        print("   ✓ Email sent! Check inbox (and spam folder).")
        
except smtplib.SMTPAuthenticationError:  # type: ignore
    print("   ✗ Email auth failed: Use a Gmail App Password, not your regular password")
except Exception as e:
    print(f"   ✗ Email failed: {type(e).__name__}: {e}")

# ── Test 4: Retrieval (Optional, needs internet) ──────────
print("\n✅ Test 4: retrieval.py (optional)")
try:
    from retrieval import search_web, search_arxiv
    
    print("   → Testing web search...")
    web_results = search_web("python programming", max_results=1)
    if web_results:
        print(f"   ✓ Web search returned {len(web_results)} result(s)")
    else:
        print("   ⚠ Web search returned no results (may be rate-limited)")
    
    print("   → Testing arXiv search...")
    arxiv_results = search_arxiv("machine learning", max_results=1)
    if arxiv_results:
        print(f"   ✓ arXiv search returned {len(arxiv_results)} result(s)")
    else:
        print("   ⚠ arXiv search returned no results")
        
except Exception as e:
    print(f"   ⚠ Retrieval test skipped/failed: {e}")

# ── Cleanup ───────────────────────────────────────────────
print("\n" + "="*50)
for f in ["test_report.pdf"]:
    if os.path.exists(f):
        os.remove(f)
        print(f"🗑 Cleaned up: {f}")

print("\n💡 Tips if email didn't work:")
print("   1. Use Gmail App Password: https://myaccount.google.com/apppasswords")
print("   2. Check Spam/Junk folder")
print("   3. Ensure 2FA is enabled on your Google account")
print("   4. Try sending to a different email provider (Outlook, etc.)")