# modules/draft_generator/callbacks.py
# Callbacks for the Academic Draft Generator

import dash
from dash import callback, Input, Output, State, ctx
from dash.dependencies import ALL
import dash_bootstrap_components as dbc
from dash import html
from flask_login import current_user
from modules.draft_generator.utils import (
    get_user_ai_providers,
    fetch_arxiv_papers,
    generate_prompt,
    call_ai_api
)

def register_draft_generator_callbacks(app):
    """Register all callbacks for the academic draft generator."""

    @app.callback(
        [Output("ai-provider-select", "options"),
         Output("ai-provider-select", "value"),
         Output("no-providers-alert", "is_open")],
        Input("draft-tab-container", "active_tab")
    )
    def update_provider_options(active_tab):
        """Update the AI provider options when the tab loads."""
        user_id = current_user.id if hasattr(current_user, 'id') and current_user.is_authenticated else None

        # For testing without authentication
        if not user_id:
            default_providers = [
                {"label": "OpenAI", "value": "openai"},
                {"label": "Anthropic", "value": "anthropic"},
                {"label": "Google Gemini", "value": "gemini"}
            ]
            return default_providers, "openai", False

        # Get the user's configured providers
        user_providers = get_user_ai_providers(user_id)

        if not user_providers:
            return [], None, True  # Show the no providers alert

        options = [
            {"label": provider.title(), "value": provider}
            for provider in user_providers.keys()
        ]

        default_value = options[0]["value"] if options else None

        return options, default_value, False

    @app.callback(
        [Output("model-select", "options"),
         Output("model-select", "value")],
        [Input("ai-provider-select", "value")]
    )
    def update_model_options(provider):
        """Update the model options based on the selected provider."""
        if not provider:
            return [], None

        # Maps of provider to available models
        provider_models = {
            "openai": [
                {"label": "GPT-3.5 Turbo", "value": "gpt-3.5-turbo"},
                {"label": "GPT-4", "value": "gpt-4"}
            ],
            "anthropic": [
                {"label": "Claude 3 Opus", "value": "claude-3-opus"},
                {"label": "Claude 3 Sonnet", "value": "claude-3-sonnet"}
            ],
            "gemini": [
                {"label": "Gemini Pro", "value": "gemini-pro"}
            ],
            "deepseek": [
                {"label": "DeepSeek Coder", "value": "deepseek-coder"}
            ],
            "huggingface": [
                {"label": "Mistral 7B", "value": "mistral-7b"},
                {"label": "Llama 2 70B", "value": "llama-2-70b"}
            ],
            "kimi": [
                {"label": "Kimi Large", "value": "kimi-large"}
            ]
        }

        options = provider_models.get(provider.lower(), [])
        default_value = options[0]["value"] if options else None

        return options, default_value

    @app.callback(
        Output("model-features", "children"),
        [Input("ai-provider-select", "value"),
         Input("model-select", "value")]
    )
    def update_model_features(provider, model):
        """Display features for the selected model."""
        if not provider or not model:
            return html.Div("Please select a provider and model", className="text-warning")

        # Model capabilities
        model_info = {
            "gpt-3.5-turbo": {
                "description": "Good balance of quality and speed",
                "capabilities": ["Academic writing", "Structured content", "Citations integration"]
            },
            "gpt-4": {
                "description": "Highest quality, more nuanced understanding",
                "capabilities": ["Complex reasoning", "Advanced academic writing", "Better literature review"]
            },
            "claude-3-opus": {
                "description": "Anthropic's flagship model for complex tasks",
                "capabilities": ["Academic writing", "Deep analysis", "Literature reviews"]
            },
            "claude-3-sonnet": {
                "description": "Balanced performance and speed",
                "capabilities": ["Academic writing", "Research summaries", "Citations"]
            },
            "gemini-pro": {
                "description": "Google's advanced language model",
                "capabilities": ["Academic writing", "Research analysis", "Citations"]
            },
            "deepseek-coder": {
                "description": "Specialized for technical content",
                "capabilities": ["Technical papers", "Code integration", "Mathematical content"]
            },
            "mistral-7b": {
                "description": "Open-source large language model",
                "capabilities": ["Academic writing", "Research summaries"]
            },
            "llama-2-70b": {
                "description": "High-performance open model",
                "capabilities": ["Academic writing", "Complex reasoning"]
            },
            "kimi-large": {
                "description": "Advanced language model with strong academic capabilities",
                "capabilities": ["Academic writing", "Research synthesis", "Citations"]
            }
        }

        if model not in model_info:
            return html.Div("Model information not available", className="text-warning")

        info = model_info[model]

        return dbc.Card([
            dbc.CardBody([
                html.H5(f"Model: {model}", className="card-title"),
                html.P(info["description"]),
                html.Ul([html.Li(capability) for capability in info["capabilities"]])
            ])
        ])

    @app.callback(
        Output("citations-container", "children"),
        Input("fetch-papers-btn", "n_clicks"),
        State("theme-input", "value"),
        prevent_initial_call=True
    )
    def update_citations(n_clicks, theme):
        """Fetch related papers from arXiv."""
        if not theme:
            return html.Div("Please enter a research topic first.", className="text-danger")

        try:
            papers = fetch_arxiv_papers(theme, max_results=15)  # Limit to 15 papers
            return dbc.Card([
                dbc.CardBody([
                    html.H5("Related Papers", className="mb-3"),
                    html.P(f"Found {len(papers)} relevant papers. Select the ones you want to include in your draft:"),
                    *[
                        dbc.Row([
                            dbc.Col([
                                html.Strong(paper['title']),
                                html.Br(),
                                html.Small(f"Authors: {paper['authors']}"),
                                html.Br(),
                                html.Small(f"Published: {paper['published']}")
                            ], width=10),
                            dbc.Col([
                                dbc.Checkbox(
                                    id={"type": "paper-checkbox", "index": i},
                                    value=True
                                )
                            ], width=2, className="d-flex align-items-center")
                        ], className="mb-3")
                        for i, paper in enumerate(papers[:15])
                    ]
                ])
            ])
        except Exception as e:
            return html.Div(f"Error fetching papers: {str(e)}", className="text-danger")

    @app.callback(
        Output({"type": "paper-checkbox", "index": ALL}, "value"),
        [Input("select-all-btn", "n_clicks"),
         Input("deselect-all-btn", "n_clicks")],
        prevent_initial_call=True
    )
    def toggle_all_citations(select_clicks, deselect_clicks):
        """Toggle all citation checkboxes."""
        triggered_id = ctx.triggered_id
        selected_value = triggered_id == "select-all-btn"

        # Return same value for all checkboxes
        return [selected_value] * 15  # Assuming max 15 papers

    @app.callback(
        [Output("draft-output", "children"),
         Output("send-to-editor-btn", "disabled")],
        Input("generate-btn", "n_clicks"),
        [State("theme-input", "value"),
         State("journal-select", "value"),
         State("ai-provider-select", "value"),
         State("model-select", "value"),
         State({"type": "paper-checkbox", "index": ALL}, "value"),
         State("citations-container", "children")],
        prevent_initial_call=True
    )
    def generate_draft(n_clicks, theme, journal_style, provider, model, checkbox_values, citations_div):
        """Generate the paper draft using the selected AI model."""
        if not theme:
            return "Please enter a research topic.", True

        if not provider or not model:
            return "Please select an AI provider and model.", True

        try:
            # Fetch papers again (in a real implementation, you'd store these in a session or state)
            papers = fetch_arxiv_papers(theme, max_results=15)

            # Filter based on checkbox values
            selected_papers = []
            for i, is_selected in enumerate(checkbox_values):
                if i < len(papers) and is_selected:
                    selected_papers.append(papers[i])

            # Generate prompt
            prompt = generate_prompt(theme, journal_style, selected_papers)

            # Call AI API to generate draft
            draft = call_ai_api(provider, model, prompt)

            # Return the draft and enable the send button
            return draft, False

        except Exception as e:
            return f"Error generating draft: {str(e)}", True
