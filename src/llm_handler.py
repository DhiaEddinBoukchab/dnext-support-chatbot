from openai import OpenAI
from typing import List, Dict, Generator, Optional
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class LLMHandler:
    """Handles OpenAI LLM interactions with conversation classification and streaming"""
    
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
    # HISTORY HELPER  ← NEW
    # =========================
    def _build_history_messages(self, conversation_history: Optional[List[Dict]], max_turns: int = 10) -> List[Dict]:
        """
        Convert session history into OpenAI messages format.
        Keeps only the last `max_turns` messages to avoid hitting token limits.
        Only includes clean role/content pairs — skips anything malformed.
        """
        if not conversation_history:
            return []

        # Keep only last max_turns messages
        recent = conversation_history[-max_turns:] if len(conversation_history) > max_turns else conversation_history

        history_messages = []
        for msg in recent:
            role = msg.get("role")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                history_messages.append({"role": role, "content": content})

        return history_messages

    # =========================
    # RESPONSE GENERATION (NON-STREAMING)
    # =========================
    def generate_response(self, context: str, query: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """Generate response using LLM with website-aware context (non-streaming)"""
        
        conversation_type = self.classify_conversation(query)

        if conversation_type == "CASUAL":
            prompt = self._create_casual_prompt(query)
        else:  # ACTIONABLE
            # Fetch dnext.io content
            website_context = self.fetch_website_content("https://www.dnext.io/")
            
            # Combine with previous context (e.g., docs)
            combined_context = f"{context}\n\n--- WEBSITE CONTENT ---\n{website_context}"
            
            prompt = self._create_technical_prompt(combined_context, query)

        # ── Build messages: system instruction extracted from prompt + history + current ──
        # We keep the original prompt as the user message for full backward compatibility,
        # and prepend conversation history so the LLM has memory.
        messages = []
        messages += self._build_history_messages(conversation_history)  # ← inject history
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3 if conversation_type == "CASUAL" else 0.2,
                max_tokens=800 if conversation_type == "CASUAL" else 1500
            )
            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return f"❌ Error generating response: {str(e)}"

    # =========================
    # RESPONSE GENERATION (STREAMING)
    # =========================
    def generate_response_stream(self, context: str, query: str, conversation_history: Optional[List[Dict]] = None) -> Generator[str, None, None]:
        """Generate streaming response using LLM with website-aware context and conversation memory"""
        
        conversation_type = self.classify_conversation(query)

        if conversation_type == "CASUAL":
            prompt = self._create_casual_prompt(query)
        else:  # ACTIONABLE
            # Fetch dnext.io content
            website_context = self.fetch_website_content("https://www.dnext.io/")
            
            # Combine with previous context (e.g., docs)
            combined_context = f"{context}\n\n--- WEBSITE CONTENT ---\n{website_context}"
            
            prompt = self._create_technical_prompt(combined_context, query)

        # ── Build messages: history + current prompt (original prompt templates fully preserved) ──
        messages = []
        messages += self._build_history_messages(conversation_history)  # ← inject history
        messages.append({"role": "user", "content": prompt})

        logger.info(f"Sending {len(messages)} messages to LLM ({len(messages)-1} history + 1 current)")

        try:
            # Create streaming response
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3 if conversation_type == "CASUAL" else 0.2,
                max_tokens=800 if conversation_type == "CASUAL" else 1500,
                stream=True  # Enable streaming
            )
            
            # Yield chunks as they arrive
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"LLM streaming error: {e}")
            yield f"❌ Error generating response: {str(e)}"

    # =========================
    # PROMPTS  (100% unchanged)
    # =========================
    def _create_casual_prompt(self, query: str) -> str:
        """Prompt for casual conversation"""
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are Dnext Assistant, a professional and helpful AI assistant for the Dnext platform.

<|start_header_id|>user<|end_header_id|>
{query}

<|start_header_id|>assistant<|end_header_id|>
**Instructions:**
- Respond naturally and warmly like a human support agent
- Be formal, short, and engaging
- If asked what you can help with, mention else dont mention:
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

    # =========================
    # WEBSITE CONTENT FETCHING  (unchanged)
    # =========================
    def fetch_website_content(self, url: str) -> str:
        """Fetch and clean text content from a website."""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()

            text = " ".join(soup.stripped_strings)
            logger.info(f"Website content fetched from {url}")
            return text[:4000]  # truncate to avoid token overflow
        except Exception as e:
            logger.error(f"Error fetching website content: {e}")
            return ""