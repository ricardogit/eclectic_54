# modules/draft_generator/layout.py
# Layout functions for the Academic Draft Generator

import dash_bootstrap_components as dbc
from dash import html, dcc
from modules.draft_generator.config import JOURNAL_STYLES

def create_draft_generator_layout():
    """
    Create the layout for the Academic Paper Draft Generator.
    """
    layout = html.Div([
        # Navigation bar with title and back button
        dbc.Row([
            dbc.Col([
                html.H2("Academic Paper Draft Generator", className="mb-4"),
            ], width=6),
            dbc.Col([
                dbc.Button(
                    [html.I(className="fas fa-arrow-left me-2"), "Back to Editor"],
                    id="back-to-editor-btn",
                    color="link",
                    className="me-3"
                ),
            ], width=4),
        ], className="mb-3"),

        # Tabs for navigation
        dbc.Tabs([
            # Tab 1: AI Provider & Model Selection
            dbc.Tab([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("AI Provider and Model Selection", className="card-title"),

                        html.Div(id="provider-status-message", className="mb-3"),

                        dbc.Row([
                            dbc.Col([
                                dbc.InputGroup([
                                    dbc.InputGroupText("AI Provider"),
                                    dbc.Select(
                                        id="ai-provider-select",
                                        options=[],  # Will be populated from database
                                        placeholder="Select provider"
                                    ),
                                ]),
                            ], width=6),

                            dbc.Col([
                                dbc.InputGroup([
                                    dbc.InputGroupText("Model"),
                                    dbc.Select(
                                        id="model-select",
                                        options=[],  # Will be populated based on provider
                                        placeholder="Select model"
                                    ),
                                ]),
                            ], width=6),
                        ], className="mb-3"),

                        # Model Features Display
                        html.Div(id="model-features", className="mb-3"),

                        # No providers configured message
                        dbc.Alert([
                            html.P("No AI providers configured. Please add API keys in the settings."),
                            dbc.Button("Go to AI Settings", href="/ai-settings", color="primary")
                        ], id="no-providers-alert", color="warning", className="mb-3", is_open=False)
                    ])
                ], className="mb-4"),
            ], label="Step 1: Select AI Provider & Model", tab_id="tab-1"),

            # Tab 2: Paper Parameters
            dbc.Tab([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Paper Parameters", className="card-title"),

                        dbc.InputGroup([
                            dbc.InputGroupText("Research Topic"),
                            dbc.Textarea(
                                id="theme-input",
                                placeholder="Enter your research topic and key concepts",
                                rows=2
                            ),
                        ], className="mb-3"),

                        dbc.Row([
                            dbc.Col([
                                dbc.InputGroup([
                                    dbc.InputGroupText("Journal Style"),
                                    dbc.Select(
                                        id="journal-select",
                                        options=[
                                            {"label": style["name"], "value": key}
                                            for key, style in JOURNAL_STYLES.items()
                                        ],
                                        value="general_scientific"
                                    ),
                                ]),
                            ], width=6),

                            dbc.Col([
                                dbc.Button(
                                    "Fetch Related Papers",
                                    id="fetch-papers-btn",
                                    color="secondary",
                                    className="w-100"
                                ),
                            ], width=6),
                        ], className="mb-3"),

                        # Citations Section
                        html.Div(id="citations-container", className="mb-3"),

                        # Select/Deselect All Citations
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "Select All Citations",
                                    id="select-all-btn",
                                    color="link",
                                    className="me-2"
                                ),
                                dbc.Button(
                                    "Deselect All Citations",
                                    id="deselect-all-btn",
                                    color="link"
                                ),
                            ], width=12, className="mb-3"),
                        ]),

                        dbc.Button(
                            "Generate Paper Draft",
                            id="generate-btn",
                            color="primary",
                            className="w-100"
                        ),
                    ])
                ], className="mb-4"),
            ], label="Step 2: Set Paper Parameters", tab_id="tab-2"),

            # Tab 3: Generated Draft
            dbc.Tab([
                dbc.Card([
                    dbc.CardBody([
                        html.H4("Generated Draft", className="card-title"),
                        dcc.Loading(
                            id="loading-draft",
                            children=[
                                html.Div(id="draft-output", className="border p-3")
                            ],
                            type="circle"
                        ),
                        dbc.Button(
                            "Send to Editor",
                            id="send-to-editor-btn",
                            color="success",
                            className="mt-3",
                            disabled=True
                        )
                    ])
                ]),
            ], label="Step 3: View Generated Draft", tab_id="tab-3"),
        ], id="draft-tab-container", active_tab="tab-1"),

        # JavaScript for integration with editor
        html.Script("""
            // Send generated content to parent window when button is clicked
            document.getElementById('send-to-editor-btn').addEventListener('click', function() {
                const content = document.getElementById('draft-output').innerText;

                // If we're in an iframe, send message to parent
                if (window.parent !== window) {
                    window.parent.postMessage({
                        type: 'draftContent',
                        content: content
                    }, '*');
                    alert('Draft sent to editor successfully!');
                } else {
                    // If standalone, store in localStorage
                    localStorage.setItem('generatedDraft', content);
                    alert('Draft saved. You can now return to the editor.');
                }
            });

            // Handle back button
            document.getElementById('back-to-editor-btn').addEventListener('click', function() {
                if (window.parent !== window) {
                    // In iframe - tell parent to close modal
                    window.parent.postMessage({
                        type: 'closeModal'
                    }, '*');
                } else {
                    // Go back to editor
                    window.location.href = '/editor/dashboard';
                }
            });
        """)
    ])

    return layout
