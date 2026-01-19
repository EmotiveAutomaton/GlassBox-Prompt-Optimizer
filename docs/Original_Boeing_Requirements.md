

# Boeing Internal Technical Compliance Standard

**Version:** 1.0 (Derived from OPro Source Analysis)
**Scope:** API Interaction, Security Protocols, and Allowed Software Supply Chain

## 1. Network & API Interface Standards

Any application interacting with the Boeing AI Gateway (`bcai-public-api`) must adhere strictly to the following protocols. Failures here will result in immediate 401/403 errors or connection termination.

### 1.1 Endpoint Structure

* **Base URL Pattern:** `https://<internal-domain>` (e.g., `bcai-test.web.boeing.com`)
* **Target Resource:** `/bcai-public-api/conversation`
* **Method:** `POST` only.

### 1.2 Authentication & Headers

Authentication is handled via a **Personal Access Token (PAT)** encoded in Base64.

* **Header Key:** `Authorization`
* **Header Value Format:** `Basic <Base64_Token_String>`
* **CRITICAL CONSTRAINT:** The token string must be stripped of all whitespace. Do not include quotes.


* **Content-Type:** `application/json`
* **Accept:** `application/json`

### 1.3 Request Body Schema (Immutable)

The API rejects requests that do not strictly match this JSON schema. You cannot omit "optional" looking fields; the client hardcodes them for compliance.

| Field | Type | Value Constraint | Description |
| --- | --- | --- | --- |
| `model` | `string` | e.g., `"gpt-4o-mini"` | The internal model identifier. |
| `conversation_guid` | `string` | `UUIDv4` format | **Mandatory.** Must be generated client-side per session. |
| `stream` | `boolean` | `false` | Streaming is strictly disabled in this implementation. |
| `skip_db_save` | `boolean` | `true` | **Mandatory.** Prevents server-side persistence of conversation history. |
| `conversation_mode` | `list` | `["non-rag"]` | **Mandatory.** explicit mode declaration. |
| `temperature` | `float` | `0.0` - `1.0` | Default is usually 0.7; 0.3 for logic; 0.0 for eval. |
| `messages` | `list` | See Section 1.4 | Standard chat history format. |

### 1.4 Message Formatting

The API accepts standard role-based messaging but supports a specific "typed" content structure often required for internal parsing.

* **Simple Format:** `{"role": "user", "content": "Hello"}`
* **Typed Format (Preferred for Safety):**
```json
{
  "role": "user",
  "content": [
    { "type": "text", "text": "Your prompt here" }
  ]
}

```



### 1.5 Response Parsing Logic

The API response format requires specific traversal logic to handle variations in how the Assistant's reply is wrapped.

* **Primary Path:** `response.json()['choices'][0]['messages'][0]['content']` (Note: It may return a list of messages in choices, not just a message object).
* **Content Extraction Fallback:**
1. Check if `content` is a **List**: Iterate and join any items where `type == "text"`.
2. Check if `content` is a **String**: Use directly.
3. **Guard:** Ensure the body is valid JSON. If the API returns HTML (often a firewall or SSO redirect), raise a `RuntimeError`.



---

## 2. Security & Environment Constraints

### 2.1 SSL & Certificate Handling

The internal network uses a custom Certificate Authority (CA). Standard Python `requests` will fail with SSL errors unless configured correctly.

* **CA Bundle Path:** The application must allow pointing to a specific `.pem` or `.crt` file (Internal CA Bundle).
* **Implementation:** Pass the path to the `verify` parameter in `requests`.
* `requests.post(..., verify='/path/to/boeing-ca-bundle.crt')`



### 2.2 Credential Persistence

* **Storage Location:** Credentials (PATs) must be stored in User Environment Variables.
* **Read Key:** `BCAI_PAT_B64`
* **Write Mechanism:** Use OS-specific commands (e.g., `setx` on Windows) to persist tokens across sessions. Do *not* store plain-text tokens in local config files (JSON/YAML).

### 2.3 Threading Model

* **Main Thread:** strictly reserved for UI rendering.
* **API Calls:** Must occur in **Daemon Threads**.
* **Stop Signal:** Long-running loops (optimization/generation) must check a thread-safe `_stop_requested` flag between every API call to allow immediate user interruption.

---

## 3. Allowed Software Supply Chain (The "Green List")

The following packages are confirmed present and authorized in the current environment. Use these as your primary building blocks to avoid dependency hell.

### 3.1 Standard Library (Safe)

* `json`, `os`, `sys`, `threading`, `time`, `uuid`, `logging`
* `dataclasses` (for state management)
* `base64` (for auth encoding)
* `tkinter` (Standard GUI lib - *Note: You are moving to a web UI, but this confirms Python GUI libs are allowed*)

### 3.2 Third-Party "Green" Packages

These imports were explicitly found in the source code, meaning they are cleared for use.

| Package | Import Name | Usage Context |
| --- | --- | --- |
| **Requests** | `requests` | HTTP Client for API calls. |
| **PyMuPDF** | `fitz` | Parsing PDF files for context. |
| **python-pptx** | `pptx` | Parsing PowerPoint files. |
| **PyTest** | `pytest` | Testing framework (implied by `tests/`). |

### 3.3 inferred "Likely Safe" (Verify First)

* **Pandas:** Not explicitly seen, but standard for data science at Boeing.
* **Streamlit/NiceGUI:** Not seen, but commonly allowed for internal tooling. *Verify before committing.*

---

## 4. Error Handling Standards

Your application must catch and translate these specific HTTP status codes into user-guided actions:

* **401 (Unauthorized):** Trigger "Check PAT Format" dialog. Remind user of Base64 encoding.
* **403 (Forbidden):** Trigger "Access Denied" dialog. Remind user to check network access/VPN.
* **3xx (Redirects):** Likely an SSO interception. Fail hard and tell user to authenticate via browser or check VPN.
* **500+:** Implement exponential backoff (Start at 2s, double up to 32s).