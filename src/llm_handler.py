from openai import OpenAI
from typing import List, Dict
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class LLMHandler:
    """Handles OpenAI LLM interactions with conversation classification"""

    def __init__(self, api_key: str, model: str):
        """Initialize OpenAI client"""
        try:
            self.client = OpenAI(api_key=api_key)
            self.model = model
            logger.info("✅ OpenAI client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    # =========================
    # CLASSIFICATION
    # =========================
    def classify_conversation(self, query: str) -> str:
        """
        Classify user message into exactly one category:
        CASUAL | ACTIONABLE
        """

        classification_prompt = f"""
DNEXT Intelligence SA is a dynamic and privately-owned Swiss-based company specializing in agriculture commodity expertise.
Classify the following user message into exactly ONE category.

CATEGORIES:

CASUAL:
- Greetings, thanks, small talk
- Jokes, chitchat
- "hello", "thanks", "how are you?"

ACTIONABLE:
- Platform usage or troubleshooting
- Market data, analysis, forecasts
- API, code, technical questions
- Subscription, access, account questions
- Any query where the word "Dnext" exists 

User message:
"{query}"

Respond with ONLY ONE WORD:
CASUAL or ACTIONABLE
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": classification_prompt}],
                temperature=0.1,
                max_tokens=10
            )

            classification = response.choices[0].message.content.strip().upper()
            logger.info(f"Conversation classified as: {classification}")

            return classification if classification in ["CASUAL", "ACTIONABLE"] else "ACTIONABLE"

        except Exception as e:
            logger.error(f"Classification error: {e}")
            return "ACTIONABLE"  # Safe default

    # =========================
    # RESPONSE GENERATION
    # =========================
    def generate_response(self, context: str, query: str) -> str:
        """Generate response using LLM with website-aware context"""
        
        conversation_type = self.classify_conversation(query)

        if conversation_type == "CASUAL":
            prompt = self._create_casual_prompt(query)
        else:  # ACTIONABLE
            # Fetch dnext.io content
            website_context = self.fetch_website_content("https://www.dnext.io/")
            
            # Combine with previous context (e.g., docs)
            combined_context = f"{context}\n\n--- WEBSITE CONTENT ---\n{website_context}"
            
            prompt = self._create_technical_prompt(combined_context, query)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3 if conversation_type == "CASUAL" else 0.2,
                max_tokens=800 if conversation_type == "CASUAL" else 1500
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return f"❌ Error generating response: {str(e)}"

    # =========================
    # PROMPTS
    # =========================
    def _create_casual_prompt(self, query: str) -> str:
        """Prompt for casual conversation"""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are Dnext Assistant, a friendly and helpful AI assistant for the Dnext platform.

<|start_header_id|>user<|end_header_id|>
{query}

<|start_header_id|>assistant<|end_header_id|>
**Instructions:**
- Respond naturally and warmly like a human support agent
- Be friendly, short, and engaging
- Use emojis when appropriate 😊👋
- If asked what you can help with, mention:
• Market data and analysis
• Forecasts
• API usage
• Dataset access
• Platform troubleshooting

Now respond naturally:"""

    def _create_technical_prompt(self, context: str, query: str) -> str:
        """Prompt for actionable (technical or procedural) questions"""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are Dnext Assistant, a technical and product support expert providing precise, reliable answers.

<|start_header_id|>user<|end_header_id|>
**Customer Question:**
{query}

**Technical Documentation (reference only):**
{context}

<|start_header_id|>assistant<|end_header_id|>
**Response Guidelines:**

1. **CORE RULES**
- Answer confidently as an expert
- NEVER mention documentation or sources
- Use ONLY information present above
- If information is missing, say:
    "For this request, please contact support@dnext.io"

2. **ACCOUNT / SUBSCRIPTION SAFETY**
- If the question concerns accounts, billing, subscriptions, or access
    and is NOT clearly covered above,
    respond with:
    "For account or subscription-related issues, please contact support@dnext.io"

3. **CODE RESPONSES**
- Provide COMPLETE, WORKING examples
- Use ```python``` blocks
- Include all imports
- Add brief inline comments
- Ensure copy-paste readiness

4. **STEP-BY-STEP GUIDES**
- Use numbered steps
- Mention prerequisites
- Highlight common pitfalls

5. **FORMATTING**
- Use **bold** for key concepts
- Bullet points for lists
- Clear sections
- Concise paragraphs

6. **TONE**
- Professional, direct, and technical
- Minimal emojis (✅ ❌ only if helpful)

Now provide the best possible answer:"""

    def fetch_website_content(self, url: str) -> str:
        """Fetch and clean text content from a website."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            for script in soup(["script", "style"]):
                script.decompose()

            text = " ".join(soup.stripped_strings)
            logger.info(f"Website content fetched from {url}")
            return text[:4000]  # truncate to avoid token overflow
        except Exception as e:
            logger.error(f"Error fetching website content: {e}")
            return ""
