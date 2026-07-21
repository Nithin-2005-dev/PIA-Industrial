from typing import Protocol, Sequence
import urllib.error
from app.kernel.models import CapabilityCard, AgentAction


class LLMResponse:
    """Wrapper for LLM responses, optionally containing tool calls."""
    def __init__(self, content: str, actions: list[AgentAction] = None):
        self.content = content
        self.actions = actions or []


class LLMProvider(Protocol):
    """Abstract interface for all LLM providers."""
    
    def generate(
        self,
        prompt: str,
        tools: Sequence[ToolSpecification] = (),
    ) -> LLMResponse:
        ...


class MockLLMProvider:
    def __init__(self, latency_ms: int = 10, token_rate: int = 100):
        self.latency_ms = latency_ms
        self.token_rate = token_rate

    def generate(self, prompt: str, tools: Sequence = ()) -> LLMResponse:
        import time
        time.sleep(self.latency_ms / 1000.0)
        return LLMResponse("Mock response from MockLLMProvider")


class OpenAIProvider:
    """Real OpenAI API integration."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model
        
    def generate(self, prompt: str, tools: Sequence[CapabilityCard] = ()) -> LLMResponse:
        import json
        import urllib.request
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # Format tools for OpenAI if provided
        openai_tools = []
        for tool in tools:
            # Simplistic mapping of CapabilityCard to OpenAI Tool format
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": {inp: {"type": "string"} for inp in tool.inputs},
                        "required": tool.inputs
                    } if getattr(tool, "inputs", None) else {"type": "object", "properties": {}}
                }
            })
            
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are the PIA AI Engineering Advisor."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.0
        }
        
        if openai_tools:
            data["tools"] = openai_tools
            data["tool_choice"] = "auto"
            
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode("utf-8"), 
            headers=headers, 
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                message = result["choices"][0]["message"]
                if "tool_calls" in message and message["tool_calls"]:
                    # If it's a tool call, we return the arguments of the first tool for now
                    # (CognitiveRuntime expects the PLAN to be returned as text, e.g., "PLAN: [tool_name]")
                    # For simplicity, if the LLM calls a tool, we can extract the name.
                    tool_calls = []
                    for t in message["tool_calls"]:
                        tool_calls.append(t["function"]["name"])
                    return LLMResponse(content=f"PLAN: {json.dumps(tool_calls)}")
                    
                return LLMResponse(content=message.get("content", ""))
        except Exception as e:
            return LLMResponse(content=f"Error connecting to OpenAI: {e}")

class OllamaProvider:
    """Local Ollama integration."""
    
    def __init__(self, model: str = "llama3"):
        self.model = model
        self.host = "http://127.0.0.1:11434"
        
    def generate(self, prompt: str, tools: Sequence[CapabilityCard] = ()) -> LLMResponse:
        import json
        import urllib.request
        
        url = f"{self.host}/api/chat"
        headers = {
            "Content-Type": "application/json"
        }
        
        # Format tools (Ollama supports OpenAI-style tools in recent versions)
        ollama_tools = []
        for tool in tools:
            ollama_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": {inp: {"type": "string"} for inp in getattr(tool, "inputs", [])},
                        "required": getattr(tool, "required", [])
                    } if getattr(tool, "inputs", None) else {"type": "object", "properties": {}}
                }
            })
            
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are the PIA AI Engineering Advisor."},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "options": {"temperature": 0.0, "num_predict": 4096}
        }
        
        if ollama_tools:
            data["tools"] = ollama_tools
            
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode("utf-8"), 
            headers=headers, 
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                
                message = result.get("message", {})
                if "tool_calls" in message and message["tool_calls"]:
                    tool_calls = []
                    for t in message["tool_calls"]:
                        tool_calls.append(t["function"]["name"])
                    return LLMResponse(content=f"PLAN: {json.dumps(tool_calls)}")
                    
                return LLMResponse(content=message.get("content", ""))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            return LLMResponse(content=f"Ollama HTTP Error {e.code}: {e.reason}\nBody: {body}\nIs the model '{self.model}' installed? Try running 'ollama run {self.model}'")
        except Exception as e:
            return LLMResponse(content=f"Error connecting to Ollama: {e}. Is Ollama running on {self.host}?")

class GeminiProvider:
    """Real Google Gemini API integration with production hardening."""

    def __init__(self, api_key: str, models: list[str] = None, debug: bool = False, allow_model_fallback: bool = False):
        self.api_key = api_key
        # Explicit resolution policy
        self.policy = models or ["gemini-2.5-flash", "gemini-2.5-pro"]
        self.debug = debug
        self.allow_model_fallback = allow_model_fallback
        
        # Resolve active model at startup
        self.active_model = self.policy[0]
        self._prompt_cache = {}
        
        if self.debug:
            print("\n=========================================")
            print("Provider Policy")
            print("=========================================")
            print(f"Requested: Auto")
            print(f"Resolved Policy:\n" + "\n".join(f"{i+1}. {m}" for i, m in enumerate(self.policy)))
            print(f"Current Model: {self.active_model}")
            print(f"Fallback Allowed: {self.allow_model_fallback}")
            print("=========================================\n")

    def _format_error(self, model: str, e: 'urllib.error.HTTPError', body: str) -> str:
        import json
        error_type = e.reason
        reason = "Unknown"
        retry_after = "N/A"
        
        try:
            data = json.loads(body)
            err = data.get("error", {})
            error_type = err.get("status", error_type)
            reason = err.get("message", "No message provided.")
            
            for detail in err.get("details", []):
                if detail.get("@type") == "type.googleapis.com/google.rpc.RetryInfo":
                    retry_after = detail.get("retryDelay", retry_after)
                if detail.get("@type") == "type.googleapis.com/google.rpc.QuotaFailure":
                    reason = "Quota limit exhausted."
                    violations = detail.get("violations", [])
                    if violations:
                        reason = f"Quota metric '{violations[0].get('quotaMetric')}' exceeded."
        except Exception:
            pass

        return (
            f"Provider      : Gemini\n"
            f"Model         : {model}\n\n"
            f"Error Type    : {error_type}\n"
            f"Reason        : {reason}\n"
            f"Retry After   : {retry_after}\n"
        )

    def generate(self, prompt: str, tools: Sequence[CapabilityCard] = ()) -> LLMResponse:
        import json
        import urllib.request
        import urllib.error
        import time
        import hashlib
        
        # ─── Prompt Cache ───
        prompt_hash = hashlib.sha256((prompt + str([t.name for t in tools])).encode()).hexdigest()
        if prompt_hash in self._prompt_cache:
            if self.debug:
                print(f"[DEBUG] Cache Hit: {prompt_hash[:8]}")
            return self._prompt_cache[prompt_hash]
            
        if self.debug:
            print(f"[DEBUG] Cache Miss: {prompt_hash[:8]}")

        headers = {
            "Content-Type": "application/json",
        }

        # Convert tools into Gemini function declarations
        gemini_tools = []
        if tools:
            function_declarations = []
            for tool in tools:
                function_declarations.append(
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                k: {
                                    "type": str(v.get("type", "string")).upper(),
                                    "description": v.get("description", "")
                                }
                                for k, v in getattr(tool, "inputs", {}).items()
                            },
                            "required": getattr(tool, "required", []),
                        } if getattr(tool, "inputs", {}) else {
                            "type": "OBJECT",
                            "properties": {}
                        },
                    }
                )
            gemini_tools = [{"functionDeclarations": function_declarations}]

        data = {
            "systemInstruction": {
                "parts": [{"text": "You are the PIA AI Engineering Advisor."}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.0
            }
        }

        if gemini_tools:
            data["tools"] = gemini_tools

        payload_bytes = json.dumps(data).encode("utf-8")
        
        max_retries = 3
        base_delay = 1.0
        
        while True:
            model = self.active_model
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            
            for attempt in range(max_retries):
                try:
                    req = urllib.request.Request(url=url, headers=headers, data=payload_bytes, method="POST")
                    with urllib.request.urlopen(req, timeout=60) as response:
                        result = json.loads(response.read().decode("utf-8"))

                    candidate = result.get("candidates", [{}])[0]
                    content = candidate.get("content", {})

                    for part in content.get("parts", []):
                        if "functionCall" in part:
                            tool_name = part["functionCall"]["name"]
                            args = part["functionCall"].get("args", {})
                            action = AgentAction(tool=tool_name, arguments=args)
                            resp = LLMResponse(content="", actions=[action])
                            self._prompt_cache[prompt_hash] = resp
                            return resp

                    text = "".join(part.get("text", "") for part in content.get("parts", []))
                    resp = LLMResponse(content=text)
                    self._prompt_cache[prompt_hash] = resp
                    return resp

                except urllib.error.HTTPError as e:
                    body = e.read().decode("utf-8", errors="replace")
                    if e.code == 429:
                        if "limit: 0" in body.lower():
                            last_error_response = self._format_error(model, e, body)
                            break # Break retry loop, check fallback
                        if attempt < max_retries - 1:
                            delay = base_delay * (2 ** attempt)
                            print(f"\n[Warning] Rate limit exceeded (429) on {model}. Retrying in {delay} seconds...")
                            time.sleep(delay)
                            continue
                            
                    last_error_response = self._format_error(model, e, body)
                    break # Break retry loop, check fallback

                except Exception as e:
                    import traceback
                    last_error_response = f"Unexpected Error on {model}:\n{traceback.format_exc()}"
                    break

            # If we exhausted retries or hit a hard error, check fallback policy
            if self.allow_model_fallback:
                current_idx = self.policy.index(self.active_model)
                if current_idx + 1 < len(self.policy):
                    next_model = self.policy[current_idx + 1]
                    print(f"\nFallback Allowed:\nTrue\n\nReason:\nQuota exhausted / Provider error\nSwitching:\n{self.active_model}\n→\n{next_model}\n")
                    self.active_model = next_model
                    continue # Try the entire flow again with the new model
            
            # If no fallback or we ran out of models
            return LLMResponse(content=f"[PROVIDER_ERROR]\n{last_error_response}")