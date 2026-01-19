---
description: Given a website, scrapes for hypnotic inductions and deepeners
---

---
name: "Librarian: Hypnosis Script Ingestion"
description: "Robustly scrapes a target URL, analyzes content for hypnotic structures (Induction, Deepener, Safety), classifies intensity, and exports a strict Grimoire YAML to staging."
author: "HMP System"
version: "2.0.0"

inputs:
  - name: url
    type: string
    description: "The full URL to the target script."
  - name: slug
    type: string
    description: "A unique identifier for this content (e.g., 'deep_trance_v1')."
  - name: tags
    type: string
    description: "Comma-separated tags (optional). Defaults to 'induction'."
    default: "induction, generic"

steps:
  # ---------------------------------------------------------
  # PHASE 1: TOOLING INTEGRITY CHECK
  # ---------------------------------------------------------
  - id: check_scraper_tool
    name: "Verify Scraper Utility"
    uses: script
    run: |
      import os
      if not os.path.exists('tools/scraper.py'):
          print("MISSING")
      else:
          print("EXISTS")

  - id: generate_scraper_if_missing
    name: "Self-Heal: Generate Scraper"
    if: "{{check_scraper_tool.output}} == MISSING"
    uses: file_write
    path: "tools/scraper.py"
    content: |
      import requests
      from bs4 import BeautifulSoup
      import sys
      import os
      import re

      def clean_text(text):
          # Remove multiple newlines and excessive whitespace
          text = re.sub(r'\n\s*\n', '\n\n', text)
          text = re.sub(r' +', ' ', text)
          return text.strip()

      def fetch(url, output_path):
          headers = {
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
          }
          try:
              print(f"Fetching {url}...")
              response = requests.get(url, headers=headers, timeout=15)
              response.raise_for_status()
              
              soup = BeautifulSoup(response.text, 'html.parser')
              
              # Remove junk
              for tag in soup(['script', 'style', 'nav', 'footer', 'iframe', 'header', 'aside']):
                  tag.decompose()
              
              # Extract Title
              title = soup.title.string if soup.title else "Unknown Title"
              
              # Extract Body Text (preserving paragraph structure)
              text_content = ""
              for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'li']):
                  text_content += f"{p.get_text()}\n"
              
              final_text = f"TITLE: {title}\nURL: {url}\n\n{clean_text(text_content)}"
              
              os.makedirs(os.path.dirname(output_path), exist_ok=True)
              with open(output_path, 'w', encoding='utf-8') as f:
                  f.write(final_text)
              print(f"SUCCESS: Saved to {output_path}")
              
          except Exception as e:
              print(f"ERROR: {str(e)}")
              sys.exit(1)

      if __name__ == "__main__":
          if len(sys.argv) < 3:
              print("Usage: scraper.py <url> <output_path>")
              sys.exit(1)
          fetch(sys.argv[1], sys.argv[2])

  # ---------------------------------------------------------
  # PHASE 2: EXECUTION
  # ---------------------------------------------------------
  - id: run_scrape
    name: "Execute Scrape"
    uses: script
    run: "python tools/scraper.py \"{{inputs.url}}\" \"_agent_network/staging/raw/temp_{{inputs.slug}}.txt\""

  # ---------------------------------------------------------
  # PHASE 3: INTELLIGENCE & ANALYSIS
  # ---------------------------------------------------------
  - id: analyze_structure
    name: "Semantic Analysis"
    uses: llm
    prompt: |
      You are an expert Hypnotic Content Analyzer.
      Read the raw text content below from the file `_agent_network/staging/raw/temp_{{inputs.slug}}.txt`.
      
      **Goal:** Deconstruct this text into the HMP Grimoire Structure.
      
      **Analysis Rules:**
      1. **Mechanic:** Extract the psychological logic (looping, confusion, fractionation).
      2. **Somatic:** Extract physical instructions (deep breath, heavy eyes, muscle relaxation).
      3. **Identity:** Extract role-play or internal state shifts.
      4. **Safety:** Identify any triggers or warnings.
      5. **Intensity:** Rate from 1 (Relaxation) to 5 (Deep Trance/Control).
      
      **RAW TEXT:**
      {{run_scrape.output}} (or read from file if context allows)
      
      **OUTPUT JSON ONLY:**
      {
        "title": "Extracted Title",
        "author": "Inferred Author",
        "mechanic_text": "...",
        "somatic_text": "...",
        "identity_text": "...",
        "intensity": "integer",
        "is_nsfw": boolean
      }

  # ---------------------------------------------------------
  # PHASE 4: SCHEMA GENERATION
  # ---------------------------------------------------------
  - id: format_grimoire_yaml
    name: "Format to Grimoire Schema"
    uses: llm
    prompt: |
      Take the JSON analysis from the previous step and format it into the STRICT Grimoire YAML Schema.
      
      **Context:**
      - Slug: {{inputs.slug}}
      - Tags: {{inputs.tags}}
      - NSFW: {{analyze_structure.is_nsfw}}
      
      **YAML Rules:**
      1. Root node ID must be `node_{{inputs.slug}}`.
      2. Item ID must be `item_{{inputs.slug}}_01`.
      3. `visible_to_partner`: Set to true.
      4. `scripts` block must contain `mechanic`, `somatic`, `identity` keys using Block Scalars (|).
      
      **Expected Output Format:**
      ```yaml
      - id: node_{{inputs.slug}}
        title: "{{analyze_structure.title}}"
        type: "Quest"
        tags: [{{inputs.tags}}]
        intensity: {{analyze_structure.intensity}}
        items:
          - id: item_{{inputs.slug}}_01
            title: "Induction Phase"
            type: Suggestion
            visible_to_partner: true
            scripts:
              mechanic: |
                {{analyze_structure.mechanic_text}}
              somatic: |
                {{analyze_structure.somatic_text}}
              identity: |
                {{analyze_structure.identity_text}}
      ```
      
      Return ONLY the YAML block.

  # ---------------------------------------------------------
  # PHASE 5: EXPORT & LOGGING
  # ---------------------------------------------------------
  - id: save_yaml
    name: "Export to Staging"
    uses: file_write
    path: "_agent_network/staging/{{inputs.slug}}.yaml"
    content: "{{format_grimoire_yaml.output}}"

  - id: log_success
    name: "Log Operation"
    uses: file_write
    path: "_agent_network/log/librarian_history.md"
    mode: "append"
    content: |
      - **{{inputs.slug}}**: Scraped from {{inputs.url}}. (Intensity: {{analyze_structure.intensity}}, NSFW: {{analyze_structure.is_nsfw}})