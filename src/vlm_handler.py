import base64
import requests
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class VLMHandler:
    """Handles Vision Language Model interactions using Groq API with Llama Scout"""

    def __init__(self, api_key: str, model: str):
        """
        Initialize Groq Llama Vision client
        
        Args:
            api_key: Groq API key
            model: Model name (meta-llama/llama-4-scout-17b-16e-instruct)
        """
        try:
            self.api_key = api_key
            self.model = model
            self.base_url = "https://api.groq.com/openai/v1"
            self.headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            logger.info("✅ Groq Llama Vision client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Groq Llama Vision client: {e}")
            raise

    # =========================
    # IMAGE ENCODING
    # =========================
    def _encode_image_to_base64(self, image_path: str) -> str:
        """Convert image file to base64 string"""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to encode image: {e}")
            raise

    def _encode_image_from_bytes(self, image_bytes: bytes) -> str:
        """Convert image bytes to base64 string"""
        try:
            return base64.b64encode(image_bytes).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to encode image from bytes: {e}")
            raise

    def _get_image_media_type(self, image_path: Optional[str] = None, 
                              image_bytes: Optional[bytes] = None) -> str:
        """Determine media type from image"""
        try:
            if image_path:
                ext = Path(image_path).suffix.lower()
                media_type_map = {
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp'
                }
                return media_type_map.get(ext, 'image/jpeg')
            else:
                # Basic detection from bytes signature
                if image_bytes and len(image_bytes) > 4:
                    if image_bytes.startswith(b'\xff\xd8\xff'):
                        return "image/jpeg"
                    elif image_bytes.startswith(b'\x89PNG'):
                        return "image/png"
                    elif image_bytes.startswith(b'GIF'):
                        return "image/gif"
                    elif image_bytes.startswith(b'WEBP'):
                        return "image/webp"
                return "image/jpeg"
        except Exception as e:
            logger.warning(f"Could not determine media type: {e}")
            return "image/jpeg"

    # =========================
    # PROMPTS
    # =========================
    def _create_extraction_prompt(self, user_prompt: str) -> str:
        """
        First stage: Extract all information from the image
        """
        return f"""You are Dnext Vision Assistant, an expert at analyzing images for customer support.

**User Request:**
{user_prompt}

**Your Task:**
Analyze this image thoroughly and extract ALL visible information:

1. **Text Content**: Extract any text, labels, buttons, menus, error messages
2. **UI Elements**: Describe interface components, layouts, forms
3. **Visual State**: Note colors, highlights, selections, active elements
4. **Error Indicators**: Identify warnings, errors, or unusual states
5. **Context Clues**: Platform name, page title, URL (if visible), timestamps
6. **Data/Values**: Numbers, codes, identifiers, dataset names

Be precise and comprehensive. List everything you see."""

    def _create_contextual_prompt(self, extracted_info: str, user_prompt: str, context: str = "") -> str:
        """
        Second stage: Provide contextualized answer using extracted info + documentation
        """
        return f"""You are Dnext Assistant, a technical support expert for DNEXT Intelligence SA - a Swiss company specializing in agriculture commodity data and analytics.

**Customer Request:**
{user_prompt}

**Image Analysis (what was detected):**
{extracted_info}

**Technical Documentation (reference only):**
{context if context else "No additional documentation available."}

---

**Response Guidelines:**

1. **CORE RULES**
- Answer confidently as a customer support expert
- NEVER mention "image analysis" or "documentation" explicitly
- Use ONLY information from above
- If critical information is missing, say: "For this specific request, please contact support@dnext.io with your screenshot"

2. **TROUBLESHOOTING PRIORITY**
- If image shows an ERROR: identify the issue and provide solution steps
- If image shows a WORKFLOW: guide user through the correct process
- If image shows DATA/UI: explain what user is seeing and next actions

3. **ACCOUNT / SUBSCRIPTION SAFETY**
- If question concerns accounts, billing, subscriptions, or access issues NOT clearly covered above, respond with: "For account or subscription-related issues, please contact support@dnext.io"

4. **STEP-BY-STEP GUIDES**
- Use numbered steps (1, 2, 3...)
- Mention prerequisites
- Highlight common pitfalls
- Reference specific UI elements seen in the image

5. **CODE RESPONSES** (if applicable)
- Provide COMPLETE, WORKING examples
- Use ```python``` blocks
- Include all imports
- Add brief inline comments

6. **FORMATTING**
- Use **bold** for key concepts and UI elements
- Bullet points for options/lists
- Clear sections
- Concise, scannable paragraphs

7. **TONE**
- Professional, helpful, and solution-focused
- Minimal emojis (✅ ❌ only for clarity)
- Acknowledge what user is experiencing

Now provide the best possible answer:"""

    # =========================
    # IMAGE ANALYSIS
    # =========================
    def _encode_image(
        self,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
    ) -> tuple[str, str]:
        """
        Internal helper to encode image and determine media type.

        Returns:
            Tuple of (base64_image_data, media_type)
        """
        if not image_path and not image_bytes:
            raise ValueError("Either image_path or image_bytes must be provided")

        if image_path:
            image_data = self._encode_image_to_base64(image_path)
            media_type = self._get_image_media_type(image_path=image_path)
        else:
            image_data = self._encode_image_from_bytes(image_bytes)
            media_type = self._get_image_media_type(image_bytes=image_bytes)

        return image_data, media_type

    def _run_extraction_stage(
        self,
        image_data: str,
        media_type: str,
        user_prompt: str,
    ) -> Dict[str, Any]:
        """
        Internal helper for Stage 1: vision extraction only.

        Returns:
            dict with keys: success, extracted_info, raw, usage, error
        """
        try:
            logger.info("Stage 1: Extracting information from image...")
            extraction_prompt = self._create_extraction_prompt(user_prompt)

            extraction_payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": extraction_prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{image_data}"
                                },
                            },
                        ],
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 800,
            }

            extraction_response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=extraction_payload,
                timeout=30,
            )

            if extraction_response.status_code != 200:
                error_msg = (
                    f"Groq API error (extraction): "
                    f"{extraction_response.status_code} - {extraction_response.text}"
                )
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "extracted_info": None,
                    "raw": None,
                    "usage": {},
                }

            extraction_result = extraction_response.json()
            extracted_info = extraction_result["choices"][0]["message"]["content"]

            logger.info(f"Extracted info preview: {extracted_info[:200]}...")

            return {
                "success": True,
                "error": None,
                "extracted_info": extracted_info,
                "raw": extraction_result,
                "usage": extraction_result.get("usage", {}),
            }
        except Exception as e:
            logger.error(f"Error during extraction stage: {e}")
            return {
                "success": False,
                "error": str(e),
                "extracted_info": None,
                "raw": None,
                "usage": {},
            }

    def _run_contextual_stage(
        self,
        extracted_info: str,
        user_prompt: str,
        context: str = "",
    ) -> Dict[str, Any]:
        """
        Internal helper for Stage 2: contextual answer only.

        Returns:
            dict with keys: success, response, raw, usage, error
        """
        try:
            logger.info("Stage 2: Generating contextual response...")
            contextual_prompt = self._create_contextual_prompt(
                extracted_info, user_prompt, context
            )

            # For stage 2, we only need text (no image)
            contextual_payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": contextual_prompt,
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 1200,
            }

            contextual_response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=contextual_payload,
                timeout=30,
            )

            if contextual_response.status_code != 200:
                error_msg = (
                    f"Groq API error (contextual): "
                    f"{contextual_response.status_code} - {contextual_response.text}"
                )
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "response": None,
                    "raw": None,
                    "usage": {},
                }

            final_result = contextual_response.json()
            response_text = final_result["choices"][0]["message"]["content"]

            return {
                "success": True,
                "error": None,
                "response": response_text,
                "raw": final_result,
                "usage": final_result.get("usage", {}),
            }
        except Exception as e:
            logger.error(f"Error during contextual stage: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": None,
                "raw": None,
                "usage": {},
            }

    def analyze_image(
        self,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        prompt: str = "Analyze this image and provide a detailed description.",
        context: str = "",
    ) -> Dict[str, Any]:
        """
        Process image with two-stage analysis:
        1. Extract all information from image
        2. Provide contextual answer using documentation

        Args:
            image_path: Path to image file
            image_bytes: Image bytes (alternative to path)
            prompt: User's question/request
            context: Technical documentation context

        Returns:
            Dictionary with response and metadata
        """
        try:
            # Encode image once
            image_data, media_type = self._encode_image(
                image_path=image_path,
                image_bytes=image_bytes,
            )

            # STAGE 1: Extract information from image
            extraction = self._run_extraction_stage(
                image_data=image_data,
                media_type=media_type,
                user_prompt=prompt,
            )
            if not extraction["success"]:
                return {
                    "success": False,
                    "error": extraction["error"],
                    "response": None,
                }

            extracted_info = extraction["extracted_info"]

            # STAGE 2: Generate contextual response
            contextual = self._run_contextual_stage(
                extracted_info=extracted_info,
                user_prompt=prompt,
                context=context,
            )
            if not contextual["success"]:
                return {
                    "success": False,
                    "error": contextual["error"],
                    "response": None,
                }

            return {
                "success": True,
                "response": contextual["response"],
                "extracted_info": extracted_info,  # For debugging
                "model": self.model,
                "usage": {
                    "extraction": extraction.get("usage", {}),
                    "contextual": contextual.get("usage", {}),
                },
                "error": None,
            }

        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": None,
            }

    def extract_image_info(
        self,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        user_prompt: str = "Extract all visible information from this image.",
    ) -> Dict[str, Any]:
        """
        Public helper to run ONLY the extraction stage and return
        a detailed textual description of the image.

        This is intended for:
        - Building a better retrieval query (RAG)
        - Handling image-only queries by turning them into text
        """
        try:
            image_data, media_type = self._encode_image(
                image_path=image_path,
                image_bytes=image_bytes,
            )

            extraction = self._run_extraction_stage(
                image_data=image_data,
                media_type=media_type,
                user_prompt=user_prompt,
            )

            if not extraction["success"]:
                return {
                    "success": False,
                    "error": extraction["error"],
                    "extracted_info": None,
                    "usage": extraction.get("usage", {}),
                }

            return {
                "success": True,
                "error": None,
                "extracted_info": extraction["extracted_info"],
                "usage": extraction.get("usage", {}),
            }

        except Exception as e:
            logger.error(f"Error extracting image info: {e}")
            return {
                "success": False,
                "error": str(e),
                "extracted_info": None,
                "usage": {},
            }

    # =========================
    # SPECIALIZED ANALYSIS
    # =========================
    def extract_text(self, image_path: Optional[str] = None,
                     image_bytes: Optional[bytes] = None,
                     context: str = "") -> str:
        """Extract text from image (OCR)"""
        prompt = "Extract all visible text from this image."
        
        result = self.analyze_image(
            image_path=image_path,
            image_bytes=image_bytes,
            prompt=prompt,
            context=context
        )

        return result["response"] if result["success"] else f"Error: {result['error']}"

    def analyze_document(self, image_path: Optional[str] = None,
                        image_bytes: Optional[bytes] = None,
                        doc_type: str = "document",
                        context: str = "") -> str:
        """Analyze document screenshot"""
        prompt = f"Analyze this {doc_type} screenshot and help me understand it."

        result = self.analyze_image(
            image_path=image_path,
            image_bytes=image_bytes,
            prompt=prompt,
            context=context
        )

        return result["response"] if result["success"] else f"Error: {result['error']}"