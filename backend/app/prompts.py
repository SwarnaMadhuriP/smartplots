import textwrap

ANALYZE_PROMPT = textwrap.dedent("""
You are a professional real estate investment analyst.

Analyze the following land plot STRICTLY based on the provided data.
Do NOT assume, invent, or use outside information.
If information is missing, mention it as a limitation.

User question:
{question}

Plot Data:
- Title: {title}
- City: {city}
- State: {state}
- Price: ${price}
- Size: {area} acres
- Price per acre: ${price_per_acre}
- Zoning: {zoning}
- Road access: {road}
- Water access: {water}
- Electricity: {electricity}
- Sewer: {sewer}
- Ideal for: {ideal_for}
- Risk notes: {risk_notes}

Return ONLY valid JSON with this exact shape:

{{
  "investment_score": number between 0 and 10,
  "risk_level": "Low" | "Medium" | "High",
  "growth_potential": "Low" | "Medium" | "High",
  "summary": "short 2-3 sentence summary",
  "reasons": ["short UI-friendly reason", "short UI-friendly reason", "short UI-friendly reason"],
  "pros": ["specific pro based on data", "specific pro based on data"],
  "cons": ["specific con or missing information", "specific con or missing information"]
}}

Rules:
- Return JSON only, no markdown
- Every claim must be tied to the provided plot data
- Reasons must explain why this plot matches the user question
- Do not include facts not present in the plot data
- If the user question cannot be answered from the data, say that in the summary
""")