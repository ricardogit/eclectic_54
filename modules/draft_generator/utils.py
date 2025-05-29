# utils.py
import requests
import openai
from typing import Dict, List
import arxiv
from config import JOURNAL_STYLES

def get_user_ai_providers(user_id):
    """
    Get AI providers configured for a user.

    In a real implementation, this would fetch from database.
    This is a simplified version for testing.
    """
    # For testing, return default providers
    return {
        "openai": {
            "api_key": "test_key",
            "is_paid": True
        },
        "anthropic": {
            "api_key": "test_key",
            "is_paid": True
        },
        "gemini": {
            "api_key": "test_key",
            "is_paid": True
        }
    }

def fetch_arxiv_papers(query: str, max_results: int = 15) -> List[Dict]:
    """Fetch relevant papers from arXiv."""
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )

    papers = []
    for result in search.results():
        papers.append({
            'title': result.title,
            'authors': ', '.join([author.name for author in result.authors]),
            'summary': result.summary,
            'published': result.published.strftime("%Y-%m-%d"),
            'url': result.entry_id,
            'citation': f"{', '.join([author.name for author in result.authors])} ({result.published.year}). {result.title}. arXiv:{result.entry_id.split('/')[-1]}"
        })
    return papers

def generate_prompt(theme: str, journal_style: str, citations: List[Dict]) -> str:
    """Generate a structured prompt for the paper draft."""
    style_info = JOURNAL_STYLES.get(journal_style, JOURNAL_STYLES["general_scientific"])

    citations_text = "\n".join([f"- {citation['citation']}" for citation in citations])

    prompt = f"""Generate a detailed academic paper draft about: {theme}

Requirements:
- Follow {style_info['name']} journal style
- Maximum word count: {style_info['max_words']}
- Citation style: {style_info['citation_style']}
- Use these relevant citations in appropriate sections:
{citations_text}

Required sections:
{', '.join(style_info['sections'])}

Additional requirements:
1. Use academic language and maintain formal tone
2. Include specific gaps in the literature that this paper addresses
3. Clearly state research objectives
4. Integrate citations naturally into the text
5. Include placeholders for figures/tables where appropriate
6. Follow standard academic writing conventions
7. Provide clear topic sentences for each paragraph
8. End with strong conclusions and future work directions
9. Make sure to include a comprehensive References section with all the citations provided

Please generate the complete draft with all sections."""

    return prompt

def call_ai_api(provider: str, model: str, prompt: str) -> str:
    """
    Call the appropriate AI API based on the provider and model.

    For testing purposes, this returns a sample draft instead of making actual API calls.
    In a real implementation, this would make calls to the respective APIs.
    """
    # Extract the topic from the prompt
    # Using two steps to avoid backslashes in f-string expressions
    parts = prompt.split(':')
    if len(parts) > 1:
        topic_line = parts[1].split('\n')[0].strip()
    else:
        topic_line = "the research topic"

    # Return a sample draft
    return f"""# Academic Paper Draft

## Abstract

This paper examines the implications of {topic_line} through a comprehensive literature review and analysis. The findings indicate that this topic has significant implications for future research and practical applications. This study contributes to the growing body of knowledge in this field.

## Introduction

Recent advances in this field have highlighted the importance of understanding the underlying mechanisms and implications. As noted by Smith et al. (2023), the conceptual framework remains underdeveloped despite growing interest from both academics and practitioners.

## Literature Review

### Current State of Knowledge

The literature on this topic has expanded considerably in recent years. Jones and Brown (2022) established a foundational understanding, while more recent work by Williams (2023) has challenged some of these assumptions.

### Gaps in the Literature

Despite this progress, significant gaps remain in our understanding. This paper aims to address these gaps by providing a more comprehensive framework.

## Methodology

This study employs a mixed-methods approach combining qualitative analysis of existing literature with quantitative assessment of empirical data.

## Results

The analysis reveals several key findings:

1. Finding one relates to the conceptual framework
2. Finding two demonstrates empirical correlations
3. Finding three suggests practical applications

## Discussion

These findings have significant implications for both theory and practice in the field.

## Conclusion

This paper has provided a comprehensive examination of the topic, contributing to both theoretical understanding and practical applications in the field.

## References

[List of references based on citations provided]"""

