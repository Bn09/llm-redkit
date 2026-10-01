OWASP_LLM_TOP10 = {
    "prompt_injection":      ["LLM01:2025 Prompt Injection"],
    "jailbreak":             ["LLM01:2025 Prompt Injection"],
    "encoding":              ["LLM01:2025 Prompt Injection"],
    "data_leak":             ["LLM02:2025 Sensitive Information Disclosure",
                              "LLM06:2025 Excessive Agency"],
    "system_extract":        ["LLM07:2025 System Prompt Leakage"],
    "agentic.confused_deputy":   ["LLM01", "LLM08:2025 Excessive Agency"],
    "agentic.exfil_chain":       ["LLM02", "LLM06"],
    "agentic.memory_poison":     ["LLM01", "LLM08"],
    "agentic.indirect_injection":["LLM01", "LLM08"],
    "agentic.delegation_hijack": ["LLM08"],
    "agentic.tool_output_injection": ["LLM01", "LLM08"],
    "rag.poison":            ["LLM03:2025 Supply Chain", "LLM08"],
    "rag.extract":           ["LLM02", "LLM08"],
    "multiturn.crescendo":   ["LLM01", "LLM07"],
    "multiturn.tap":         ["LLM01"],
}

MITRE_ATLAS = {
    "prompt_injection":      ["AML.T0051 LLM Prompt Injection"],
    "jailbreak":             ["AML.T0054 LLM Jailbreak"],
    "data_leak":             ["AML.T0057 LLM Data Leakage"],
    "encoding":              ["AML.T0054"],
    "system_extract":        ["AML.T0056 LLM Meta Prompt Extraction"],
    "agentic.confused_deputy":   ["AML.T0053 AI Agent Tool Invocation"],
    "agentic.exfil_chain":       ["AML.T0057", "AML.T0012"],
    "agentic.memory_poison":     ["AML.T0050"],
    "agentic.indirect_injection":["AML.T0051"],
    "rag.poison":            ["AML.T0056"],
    "multiturn.crescendo":   ["AML.T0054", "AML.T0056"],
    "multiturn.tap":         ["AML.T0054"],
}

def map_frameworks(category):
    out = []
    for c in OWASP_LLM_TOP10.get(category, []):
        out.append("OWASP " + c)
    for c in MITRE_ATLAS.get(category, []):
        out.append("MITRE " + c)
    return out
