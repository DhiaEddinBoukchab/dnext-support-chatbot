"""OpenAI chat helper for classification and answer generation."""

import logging
from typing import Dict, List, Optional

from openai import OpenAI


logger = logging.getLogger(__name__)


class LLMHandler:
    """Handle OpenAI chat completions for the FastAPI service."""

    def __init__(self, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info("OpenAI client initialized")

    def classify_conversation(self, query: str) -> str:
        """Classify a message as CASUAL or TECHNICAL."""
        prompt = f"""
DNEXT Intelligence SA is a dynamic and privately-owned Swiss-based company specializing in agriculture commodity expertise.
Classify the following user message into exactly ONE category.

CATEGORIES:

CASUAL:
- Greetings, thanks, small talk
- Jokes, chitchat
- "hello", "thanks", "how are you?"

TECHNICAL:
- Platform usage or troubleshooting
- Market data, analysis, forecasts
- API, code, technical questions
- Subscription, access, account questions
- Any query where the word "Dnext" exists

User message:
"{query}"

Respond with ONLY ONE WORD:
CASUAL or TECHNICAL
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10,
            )
            classification = (response.choices[0].message.content or "").strip().upper()
            logger.info(f"Conversation classified as: {classification}")
            return classification if classification in {"CASUAL", "TECHNICAL"} else "TECHNICAL"
        except Exception as exc:
            logger.error(f"Classification error: {exc}")
            return "TECHNICAL"

    @staticmethod
    def _build_history_messages(
        conversation_history: Optional[List[Dict]],
        max_turns: int = 10,
    ) -> List[Dict]:
        """Convert recent session history into OpenAI message format."""
        if not conversation_history:
            return []

        recent = conversation_history[-max_turns:] if len(conversation_history) > max_turns else conversation_history
        messages: List[Dict] = []
        for message in recent:
            role = message.get("role")
            content = message.get("content", "")
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})
        return messages

    def generate_response(
        self,
        context: str,
        query: str,
        conversation_history: Optional[List[Dict]] = None,
        conversation_type: Optional[str] = None,
    ) -> str:
        """Generate one chat response from context and recent history."""
        conversation_type = conversation_type or self.classify_conversation(query)
        prompt = (
            self._create_casual_prompt(query)
            if conversation_type == "CASUAL"
            else self._create_technical_prompt(context, query)
        )

        messages = self._build_history_messages(conversation_history)
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3 if conversation_type == "CASUAL" else 0.2,
                max_tokens=800 if conversation_type == "CASUAL" else 1500,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error(f"LLM generation error: {exc}")
            return f"Error generating response: {exc}"

    @staticmethod
    def _create_casual_prompt(query: str) -> str:
        return f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are Dnext Assistant, a professional and helpful AI assistant for the Dnext platform.

<|start_header_id|>user<|end_header_id|>
{query}

<|start_header_id|>assistant<|end_header_id|>
**Instructions:**
- Respond naturally and warmly like a human support agent
- Be formal, short, and engaging
- If asked what you can help with, mention:
  Market data and analysis
  Forecasts
  API usage
  Dataset access
  Platform troubleshooting

Now respond naturally:"""

    @staticmethod
    def _create_technical_prompt(context: str, query: str) -> str:
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
- Never mention documentation or sources
- Use only information present above
- If information is missing, say:
  "For this request, please contact support@dnext.io"

2. **ACCOUNT / SUBSCRIPTION SAFETY**
- If the question concerns accounts, billing, subscriptions, or access and is not clearly covered above, respond with:
  "For account or subscription-related issues, please contact support@dnext.io"

3. **STRICT CODE RESPONSES**
- If the information is insufficient, respond: "For this request, please contact support@dnext.io".
- When providing code, use the exact code from the documentation above.
- Do not rename variables, restructure functions, or remove any code lines.
- You may add very brief inline comments only to clarify non-obvious lines, but do not modify logic or structure.
- Ensure code is wrapped in ```python``` blocks and is copy-paste ready.

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

Now provide the best possible answer:"""
