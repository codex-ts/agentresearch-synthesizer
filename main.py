import asyncio
import os
import json
from dotenv import load_dotenv

from openai import AsyncOpenAI
from agents import Agent, Runner, function_tool, set_default_openai_client
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

from retrieval import search_arxiv, search_web
from formatter import generate_html
from pdf_generator import save_pdf
from emailer import send_email
from validator import parse_and_validate_report

# After your imports, before SENDER_EMAIL = ...
try:
    from agents import disable_tracing
    disable_tracing()
except ImportError:
    pass

load_dotenv()

SENDER_EMAIL = os.getenv("EMAIL_USER")
APP_PASSWORD = os.getenv("EMAIL_PASS")
RECEIVER_EMAIL = os.getenv("EMAIL_USER")
PDF_PATH = "report.pdf"

# ── Local LLM setup ───────────────────────────────────────────────────────────

local_client = AsyncOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="local",
)

set_default_openai_client(local_client)

LOCAL_MODEL = OpenAIChatCompletionsModel(
    model="nvidia/nemotron-3-nano-4b",   
    openai_client=local_client,
)


# ── Tools ─────────────────────────────────────────────────────────────────────

@function_tool
def tool_search_arxiv(query: str) -> str:
    """Search arXiv for academic papers matching the query.
    Returns a JSON string of results with title, summary, authors, url."""
    results = search_arxiv(query, max_results=3)
    return json.dumps(results)


@function_tool
def tool_search_web(query: str) -> str:
    """Search the web for articles and resources matching the query.
    Returns a JSON string of results with title, summary, url."""
    results = search_web(query, max_results=3)
    return json.dumps(results)


@function_tool
def tool_deliver_report(report_json: str) -> str:
    """Takes a JSON research report, generates a PDF, and emails it."""
    try:
        print(f"[DEBUG] Received report JSON: {report_json[:200]}...")  # Log start
        
        report = parse_and_validate_report(report_json)
        print("[DEBUG] Report validated successfully")
        
        html = generate_html(report)
        save_pdf(html, PDF_PATH)
        print(f"[DEBUG] PDF saved to {PDF_PATH}")
        
        send_email(
            sender_email=SENDER_EMAIL,
            app_password=APP_PASSWORD,
            receiver_email=RECEIVER_EMAIL,
            file_path=PDF_PATH
        )
        print("[DEBUG] Email sent")
        return "Report delivered successfully via email."
        
    except Exception as e:
        print(f"[ERROR] Delivery failed: {str(e)}")  # <-- This is critical!
        import traceback
        traceback.print_exc()
        return f"Delivery failed: {str(e)}"


# ── Agents ────────────────────────────────────────────────────────────────────

writer_agent = Agent(
    name="Writer Agent",
    model=LOCAL_MODEL,
    instructions="""
You are a research report writer.

You are given already-collected research data.

Your job is ONLY to:
- write the final report
- output a valid JSON

STRICT RULES:
- DO NOT call any search tools (tool_search_arxiv, tool_search_web)
- DO NOT generate new queries
- DO NOT fetch new data
- DO NOT explain anything outside JSON
- ONLY output ONE valid JSON object

FORMAT:
{
 "title": "string",
 "summary": "string",
 "key_findings": [
   {"title": "string", "explanation": "string", "confidence": "HIGH/MEDIUM/LOW"}
 ],
 "why_it_matters": "string",
 "sources": [...]
}

After generating JSON, call tool_deliver_report.
""",
    tools=[tool_deliver_report],
)


research_agent = Agent(
    name="Research Agent",
    model=LOCAL_MODEL,
    instructions="""You are a research assistant who gathers information on topics.

CRITICAL:
- Always prioritize the most recent information (2025–2026 if available)
- Include terms like "latest", "2025", "2026", "recent trends" in your queries
- Prefer newer papers and articles over older ones

Given a topic, you will:
1. Generate ONE search query (focused on latest developments)
2. Call tool_search_arxiv with that query
3. Call tool_search_web with that query
4. Look at the results, then generate the NEXT query (again focusing on recency)
5. Repeat for 3 queries total
6. After 3 rounds of searching, hand off ALL findings to the Writer Agent

Important:
- Search ONE query at a time
- Wait for results before generating the next query
- Pass ALL collected results to the Writer Agent
- Do not summarize or filter
""",
    tools=[tool_search_arxiv, tool_search_web],
    handoffs=[writer_agent],
)


rewrite_agent = Agent(
    name="Rewrite Agent",
    model=LOCAL_MODEL,
    instructions="""
You are a writing assistant.

You will be given a report JSON.
Rewrite ONLY the requested section.

Return FULL valid JSON in same structure.
Do NOT change other fields.
""",
)


# ── Runner ────────────────────────────────────────────────────────────────────

async def main():
    topic = input("Enter a research topic: ").strip()
    if not topic:
        print("No topic entered.")
        return

    print(f"\nStarting research on: {topic}\n")
    print("=" * 50)

    result = await Runner.run(research_agent, topic)

    print("\n" + "=" * 50)
    print("Agent run complete.")
    
    # ── Check if tool was called ──────────────────────────────
    tool_called = any(
        hasattr(step, 'output') and 
        hasattr(step.output, 'tool_calls') and 
        step.output.tool_calls
        for step in result.steps
    )
    
    if tool_called:
        print("✅ tool_deliver_report was called by model.")
        return
    
    # ── Fallback: Model output JSON as plain text ─────────────
    print("⚠️  Model output JSON as text (no tool call). Processing manually...")
    
    try:
        from validator import parse_and_validate_report
        from formatter import generate_html
        from pdf_generator import save_pdf
        from emailer import send_email
        
        # Use validator to extract & parse JSON from messy output
        report = parse_and_validate_report(result.final_output)
        print(f"✓ Report parsed: {report['title']}")
        
        # Generate PDF
        html = generate_html(report)
        save_pdf(html, PDF_PATH)
        print(f"✓ PDF saved: {PDF_PATH}")
        
        # Send email
        if SENDER_EMAIL and APP_PASSWORD and RECEIVER_EMAIL:
            send_email(SENDER_EMAIL, APP_PASSWORD, RECEIVER_EMAIL, PDF_PATH)
            print("✅ Email sent! Check your inbox.")
        else:
            print("⚠️  Email credentials missing. PDF saved locally only.")
            print("   Add EMAIL_USER and EMAIL_PASS to your .env file")
            
    except Exception as e:
        print(f"❌ Delivery failed: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n💡 Debug: Raw output snippet:\n{result.final_output[:400]}...")





if __name__ == "__main__":
    asyncio.run(main())


