---
description: Uses low-restriction llms to make any specified input text much more explicitly and graphically sexual in specified manners
---

---
name: "Shadow Writer: Content Transmutation"
description: "Takes a draft file (YAML/JSON/Text) and rewrites the prose to be explicitly erotic and hypnotic while strictly preserving the original data structure."
author: "HMP System"
version: "3.0.0"

inputs:
  - name: draft_file
    type: string
    description: "Filename in '_agent_network/inbox/' (e.g., 'draft_submission.yaml')."
  - name: slug
    type: string
    description: "Unique identifier for the output."
  - name: intensity
    type: string
    default: "Extreme"
    description: "Target tone (e.g., 'Extreme', 'Predatory', 'Sensory Overload')."
  - name: model
    type: string
    default: "dolphin-mistral"
    description: "Local Ollama model ID."

steps:
  # ---------------------------------------------------------
  # PHASE 1: INFRASTRUCTURE (Bridge Check)
  # ---------------------------------------------------------
  - id: check_bridge_tool
    name: "Verify Local Bridge"
    uses: script
    run: |
      import os
      if not os.path.exists('tools/local_llm_bridge.py'):
          print("MISSING")
      else:
          print("EXISTS")

  - id: generate_bridge_if_missing
    name: "Self-Heal: Generate Bridge Script"
    if: "{{check_bridge_tool.output}} == MISSING"
    uses: file_write
    path: "tools/local_llm_bridge.py"
    content: |
      import requests
      import sys
      import os

      # CONFIG
      OLLAMA_URL = "http://localhost:11434/api/generate"

      def invoke_local_model(input_path, output_path, model, intensity):
          try:
              with open(input_path, 'r', encoding='utf-8') as f:
                  content = f.read()
          except FileNotFoundError:
              print(f"ERROR: File {input_path} not found.")
              sys.exit(1)

          # THE SHADOW DIRECTIVE
          # We instruct the model to act as a Text Processing Engine, not a Chatbot.
          system_prompt = (
              f"You are the Shadow Engine. Your task is to rewrite the content provided below.\n"
              f"TARGET TONE: {intensity}. Extremely Explicit. Graphic. Erotic Hypnosis Best Practices.\n"
              f"CONSTRAINT: You must preserve the data structure (YAML/JSON keys) exactly.\n"
              f"ACTION: Replace the value text with high-intensity, kink-aligned hypnotic prose.\n"
              f"Use fractionation, sensory words, and deepener loops.\n"
              f"Do not output conversational filler. Output the rewritten file content ONLY."
          )

          payload = {
              "model": model,
              "prompt": f"{system_prompt}\n\nINPUT CONTENT:\n{content}",
              "stream": False,
              "options": {
                  "temperature": 0.8, # Slightly lower to preserve structure
                  "num_ctx": 8192     # Larger context for file structure
              }
          }

          print(f"Shadow Writer transmuting {input_path}...")
          
          try:
              response = requests.post(OLLAMA_URL, json=payload, timeout=300)
              response.raise_for_status()
              result_text = response.json().get("response", "")

              os.makedirs(os.path.dirname(output_path), exist_ok=True)
              with open(output_path, 'w', encoding='utf-8') as f:
                  f.write(result_text)
              print(f"SUCCESS: Wrote to {output_path}")

          except Exception as e:
              print(f"ERROR: {str(e)}")
              sys.exit(1)

      if __name__ == "__main__":
          if len(sys.argv) < 5:
              print("Usage: bridge.py <in> <out> <model> <intensity>")
              sys.exit(1)
          invoke_local_model(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

  # ---------------------------------------------------------
  # PHASE 2: TRANSMUTATION (Local Execution)
  # ---------------------------------------------------------
  - id: execute_shadow_pass
    name: "Run Local Transmutation"
    uses: script
    # Input: Inbox Draft -> Output: Staging Raw
run: "python tools/local_llm_bridge.py ... _agent_network/staging/shadow_{{inputs.slug}}.txt ..."
\"_agent_network/staging/raw/shadow_{{inputs.slug}}.txt\" \"{{inputs.model}}\" \"{{inputs.intensity}}\""

  # ---------------------------------------------------------
  # PHASE 3: STRUCTURE RECOVERY (Cloud Validation)
  # ---------------------------------------------------------
  - id: validate_structure
    name: "Validate & Repair Schema"
    uses: llm
    prompt: |
      You are the Quality Assurance Safety Valve.
      The Local LLM has rewritten the text of a file to be NSFW/Explicit.
      
      **YOUR JOB:**
      1. Read '_agent_network/staging/shadow_{{inputs.slug}}.txt'
      2. **IGNORE THE CONTENT.** Do not censor it. The user explicitly requested high-entropy erotic content.
      3. **CHECK THE SYNTAX.**
         - If the Local LLM broke the YAML indentation or JSON brackets, fix the syntax.
         - Ensure `id`, `type`, and `visible_to_partner` fields remain intact.
      4. Output the strictly valid YAML/JSON.

  # ---------------------------------------------------------
  # PHASE 4: EXPORT & LOGGING
  # ---------------------------------------------------------
  - id: export_final
    name: "Export to Staging"
    uses: file_write
    path: "_agent_network/staging/{{inputs.slug}}.yaml"
    content: "{{validate_structure.output}}"

  - id: log_success
    name: "Log Transmutation"
    uses: file_write
    path: "_agent_network/log/shadow_history.md"
    mode: "append"
    content: |
      - **{{inputs.slug}}**: Transmuted {{inputs.draft_file}} at intensity '{{inputs.intensity}}'. Model: {{inputs.model}}.