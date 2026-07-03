from enum import Enum

class TemplateType(str, Enum):
    RESEARCH = "research"
    LEGAL = "legal"
    FINANCIAL = "financial"
    TECHNICAL = "technical"
    GENERAL = "general"


TEMPLATES = {
    TemplateType.RESEARCH: {
        "name": "Research Paper Analysis",
        "description": "Best for academic papers, studies, and research documents",
        "question_starters": [
            "What is the main hypothesis of this paper?",
            "What methodology was used in this study?",
            "What are the key findings and conclusions?",
            "What are the limitations of this research?",
            "What datasets were used in this study?"
        ],
        "system_hint": "Focus on methodology, findings, and conclusions. Look for quantitative results.",
        "recommended_chunk_size": 400,
        "recommended_top_k": 4
    },
    TemplateType.LEGAL: {
        "name": "Legal Document QA",
        "description": "Best for contracts, agreements, and legal documents",
        "question_starters": [
            "What are the key obligations of each party?",
            "What are the termination clauses?",
            "What penalties are defined in this document?",
            "What are the payment terms?",
            "What jurisdiction governs this agreement?"
        ],
        "system_hint": "Focus on specific clauses, dates, obligations, and defined terms.",
        "recommended_chunk_size": 300,
        "recommended_top_k": 5
    },
    TemplateType.FINANCIAL: {
        "name": "Financial Report Analysis",
        "description": "Best for annual reports, earnings, and financial statements",
        "question_starters": [
            "What was the total revenue for this period?",
            "What are the key risk factors mentioned?",
            "What is the net profit margin?",
            "What are the major expenses?",
            "What is the company's growth strategy?"
        ],
        "system_hint": "Focus on numbers, percentages, and financial metrics.",
        "recommended_chunk_size": 350,
        "recommended_top_k": 4
    },
    TemplateType.TECHNICAL: {
        "name": "Technical Documentation",
        "description": "Best for API docs, system design docs, and technical specs",
        "question_starters": [
            "How does this system work?",
            "What are the API endpoints available?",
            "What are the system requirements?",
            "How do I configure this system?",
            "What are the known limitations?"
        ],
        "system_hint": "Focus on specifications, configurations, and technical details.",
        "recommended_chunk_size": 500,
        "recommended_top_k": 3
    },
    TemplateType.GENERAL: {
        "name": "General Document QA",
        "description": "Works for any document type",
        "question_starters": [
            "What is this document about?",
            "What are the key points?",
            "Can you summarize the main ideas?",
            "What are the most important details?",
            "What conclusions are drawn?"
        ],
        "system_hint": "General purpose retrieval and answering.",
        "recommended_chunk_size": 500,
        "recommended_top_k": 3
    }
}


def get_template(template_type: TemplateType) -> dict:
    return TEMPLATES.get(template_type, TEMPLATES[TemplateType.GENERAL])


def get_all_templates() -> list:
    return [
        {
            "type": t.value,
            "name": TEMPLATES[t]["name"],
            "description": TEMPLATES[t]["description"],
            "question_starters": TEMPLATES[t]["question_starters"],
            "recommended_chunk_size": TEMPLATES[t]["recommended_chunk_size"],
            "recommended_top_k": TEMPLATES[t]["recommended_top_k"]
        }
        for t in TemplateType
    ]


def get_recommended_settings(template_type: TemplateType) -> dict:
    template = get_template(template_type)
    return {
        "chunk_size": template["recommended_chunk_size"],
        "top_k": template["recommended_top_k"],
        "system_hint": template["system_hint"]
    }