import dash
from dash import html, dcc, dash_table, no_update, Output, Input, State
import dash_bootstrap_components as dbc
from flask_login import current_user
from flask import has_request_context


def create_settings_layout():
    """
    Create the user settings page layout with integrated AI configuration

    Returns:
        Settings layout component
    """

    # Return a function instead of direct layout
    # This makes the layout dynamic and only executes when a request is active
    def serve_layout():
        # Safer check for authentication
        if not has_request_context() or not hasattr(current_user,
                                                    'is_authenticated') or not current_user.is_authenticated:
            return html.Div([
                html.H3("Authentication Required"),
                html.P("Please log in to access the settings dashboard."),
                html.A("Go to Login", href="/auth/login", className="btn btn-primary")
            ], className="p-4 text-center")

        # Get user data - only executed when authenticated
        try:
            name = current_user.full_name if hasattr(current_user, 'full_name') else ""
            email = current_user.email if hasattr(current_user, 'email') else ""
        except Exception:
            # Fallback in case of any attribute errors
            name = ""
            email = ""

        layout = html.Div([
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("Settings", className="mb-4"),
                    html.P("Manage your account, preferences, AI providers, and scientific database access.")
                ])
            ], className="mb-4"),

            # Settings tabs
            dbc.Tabs([
                # Profile settings tab
                dbc.Tab([
                    html.Div([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Full Name"),
                                    dbc.Input(
                                        type="text",
                                        id="settings-name",
                                        value=name,
                                        placeholder="Your full name"
                                    )
                                ], width=12, md=6)
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Email Address"),
                                    dbc.InputGroup([
                                        dbc.Input(
                                            type="email",
                                            id="settings-email",
                                            value=email,
                                            placeholder="Your email address"
                                        ),
                                        dbc.InputGroupText("@")
                                    ])
                                ], width=12, md=6)
                            ], className="mb-3"),

                            dbc.Button(
                                "Update Profile",
                                id="update-profile",
                                color="primary",
                                className="mt-3"
                            )
                        ])
                    ], className="p-3")
                ], label="Profile", tab_id="profile"),

                # Password change tab
                dbc.Tab([
                    html.Div([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Current Password"),
                                    dbc.Input(
                                        type="password",
                                        id="current-password",
                                        placeholder="Enter your current password"
                                    )
                                ], width=12, md=6)
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("New Password"),
                                    dbc.Input(
                                        type="password",
                                        id="new-password",
                                        placeholder="Enter new password"
                                    )
                                ], width=12, md=6)
                            ], className="mb-3"),

                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Confirm New Password"),
                                    dbc.Input(
                                        type="password",
                                        id="confirm-password",
                                        placeholder="Confirm new password"
                                    )
                                ], width=12, md=6)
                            ], className="mb-3"),

                            dbc.Button(
                                "Change Password",
                                id="change-password",
                                color="primary",
                                className="mt-3"
                            )
                        ])
                    ], className="p-3")
                ], label="Password", tab_id="password"),

                # Preferences tab
                dbc.Tab([
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                html.H5("Appearance"),
                                dbc.RadioItems(
                                    id="theme-preference",
                                    options=[
                                        {"label": "Light Theme", "value": "light"},
                                        {"label": "Dark Theme", "value": "dark"},
                                        {"label": "System Default", "value": "system"}
                                    ],
                                    value="light",
                                    inline=True
                                )
                            ], width=12)
                        ], className="mb-4"),

                        dbc.Row([
                            dbc.Col([
                                html.H5("Editor Preferences"),
                                dbc.Checklist(
                                    id="editor-preferences",
                                    options=[
                                        {"label": "Auto-save (every 2 minutes)", "value": "autosave"},
                                        {"label": "Spell check", "value": "spellcheck"},
                                        {"label": "Grammar check", "value": "grammarcheck"},
                                        {"label": "Word count", "value": "wordcount"}
                                    ],
                                    value=["autosave", "spellcheck", "wordcount"],
                                    inline=True
                                )
                            ], width=12)
                        ], className="mb-4"),

                        dbc.Row([
                            dbc.Col([
                                html.H5("Citation Style"),
                                dbc.Select(
                                    id="citation-style",
                                    options=[
                                        {"label": "APA", "value": "apa"},
                                        {"label": "MLA", "value": "mla"},
                                        {"label": "Chicago", "value": "chicago"},
                                        {"label": "IEEE", "value": "ieee"},
                                        {"label": "Harvard", "value": "harvard"}
                                    ],
                                    value="apa"
                                )
                            ], width=6)
                        ], className="mb-4"),

                        dbc.Button(
                            "Save Preferences",
                            id="save-preferences",
                            color="primary",
                            className="mt-3"
                        )
                    ], className="p-3")
                ], label="Preferences", tab_id="preferences"),

                # AI Providers tab
                dbc.Tab([
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader(html.H4("AI Provider Configuration", className="mb-0")),
                                    dbc.CardBody([
                                        # Configuration Form
                                        dbc.Row([
                                            dbc.Col([
                                                html.H5("Add New Provider", className="mb-3")
                                            ], width=12)
                                        ]),

                                        dbc.Row([
                                            dbc.Col([
                                                dcc.Dropdown(
                                                    id='provider-dropdown',
                                                    options=[
                                                        {'label': 'OpenAI', 'value': 'openai'},
                                                        {'label': 'Anthropic', 'value': 'anthropic'},
                                                        {'label': 'Gemini', 'value': 'gemini'},
                                                        {'label': 'Deepseek', 'value': 'deepseek'},
                                                        {'label': 'HuggingFace', 'value': 'huggingface'},
                                                        {'label': 'Kimi', 'value': 'kimi'}
                                                    ],
                                                    placeholder="Select AI Provider",
                                                    className="mb-3"
                                                )
                                            ], width=12, md=6)
                                        ]),

                                        dbc.Row([
                                            dbc.Col([
                                                dbc.InputGroup([
                                                    dbc.InputGroupText("🔑"),
                                                    dbc.Input(id='api-key-input', type='password',
                                                              placeholder="Enter API Key")
                                                ], className="mb-3"),
                                            ], width=12, md=6)
                                        ]),

                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Checkbox(
                                                    id="is-paid-checkbox",
                                                    label="Paid API Key",
                                                    className="mb-3"
                                                )
                                            ], width=12, md=6)
                                        ]),

                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Button("Save Configuration", id='save-button',
                                                           color="primary", className="mb-4")
                                            ], width=12, md=6)
                                        ]),

                                        html.Div(id='api-message', className="mb-4"),

                                        # API Keys Table
                                        html.Hr(),
                                        html.H5("Your API Keys", className="mb-3"),
                                        html.Div(id='api-keys-table-container')
                                    ])
                                ])
                            ], width=12)
                        ])
                    ], className="p-3")
                ], label="AI Providers", tab_id="ai_providers"),

                # Scientific Databases tab
                dbc.Tab([
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardHeader(html.H4("Scientific Database Configuration", className="mb-0")),
                                    dbc.CardBody([
                                        # Configuration Form
                                        dbc.Row([
                                            dbc.Col([
                                                html.H5("Add New Database Access", className="mb-3")
                                            ], width=12)
                                        ]),

                                        dbc.Row([
                                            dbc.Col([
                                                dcc.Dropdown(
                                                    id='sci-db-dropdown',
                                                    options=[
                                                        {'label': 'IEEE Xplore', 'value': 'ieee'},
                                                        {'label': 'Scopus', 'value': 'scopus'},
                                                        {'label': 'Web of Science', 'value': 'wos'},
                                                        {'label': 'ScienceDirect', 'value': 'sciencedirect'},
                                                        {'label': 'SpringerLink', 'value': 'springer'},
                                                        {'label': 'PubMed', 'value': 'pubmed'},
                                                        {'label': 'JSTOR', 'value': 'jstor'},
                                                        {'label': 'ACM Digital Library', 'value': 'acm'},
                                                        {'label': 'Dimensions', 'value': 'dimensions'},
                                                        {'label': 'arXiv', 'value': 'arxiv'}
                                                    ],
                                                    placeholder="Select Scientific Database",
                                                    className="mb-3"
                                                )
                                            ], width=12, md=6)
                                        ]),

                                        dbc.Row([
                                            dbc.Col([
                                                dbc.InputGroup([
                                                    dbc.InputGroupText("🔑"),
                                                    dbc.Input(id='sci-db-key-input', type='password',
                                                              placeholder="Enter API Key or Access Token")
                                                ], className="mb-3"),
                                            ], width=12, md=6)
                                        ]),

                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Checkbox(
                                                    id="sci-db-institutional-checkbox",
                                                    label="Institutional Access",
                                                    className="mb-3"
                                                )
                                            ], width=12, md=6)
                                        ]),

                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Input(id='sci-db-institution-input', type='text',
                                                          placeholder="Institution Name (if applicable)",
                                                          className="mb-3")
                                            ], width=12, md=6)
                                        ]),

                                        dbc.Row([
                                            dbc.Col([
                                                dbc.Button("Save Database Access", id='save-sci-db-button',
                                                           color="primary", className="mb-4")
                                            ], width=12, md=6)
                                        ]),

                                        html.Div(id='sci-db-message', className="mb-4"),

                                        # Scientific Database Keys Table
                                        html.Hr(),
                                        html.H5("Your Database Access Keys", className="mb-3"),
                                        html.Div(id='sci-db-keys-table-container')
                                    ])
                                ])
                            ], width=12)
                        ])
                    ], className="p-3")
                ], label="Scientific Databases", tab_id="sci_databases"),

                # Account tab
                dbc.Tab([
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                html.H5("Account Status"),
                                html.P("Current Plan: Free"),
                                html.P("Storage Used: 15MB / 100MB"),
                                dbc.Progress(value=15, max=100, striped=True, className="mb-3"),
                                dbc.Button("Upgrade Plan", color="success", className="me-2"),
                                dbc.Button("Manage Storage", color="info")
                            ], width=12)
                        ], className="mb-4"),

                        dbc.Row([
                            dbc.Col([
                                html.H5("Data Management"),
                                dbc.Button("Export All Data", color="primary", className="me-2"),
                                dbc.Button("Delete All Documents", color="warning", className="me-2"),
                                dbc.Button("Delete Account", color="danger")
                            ], width=12)
                        ], className="mb-4")
                    ], className="p-3")
                ], label="Account", tab_id="account")
            ], id="settings-tabs", active_tab="profile")
        ])

        return layout

    # Return the function that creates the layout
    return serve_layout


def register_settings_callbacks(app):
    """
    Register callbacks for the settings page

    Args:
        app: The Dash app instance
    """
    from dash import Input, Output, State, callback_context
    from models import db, User, AIProvider, ScientificDatabase
    from datetime import datetime
    import json

    # Initialize tables when tabs are selected
    @app.callback(
        [Output('api-keys-table-container', 'children'),
         Output('sci-db-keys-table-container', 'children')],
        [Input('settings-tabs', 'active_tab')]
    )
    def initialize_tables(active_tab):
        # Create empty divs by default
        api_table = []
        sci_db_table = []

        # Only populate the relevant table based on the active tab
        if active_tab == 'ai_providers':
            api_table = [create_api_keys_table()]
        elif active_tab == 'sci_databases':
            sci_db_table = [create_sci_db_keys_table()]

        return api_table, sci_db_table

    # Create table components
    def create_api_keys_table():
        return dash_table.DataTable(
            id='api-keys-table',
            columns=[
                {'name': 'Provider', 'id': 'provider'},
                {'name': 'API Key', 'id': 'api_key', 'presentation': 'markdown'},
                {'name': 'Paid', 'id': 'is_paid'},
                {'name': 'Last Updated', 'id': 'updated_at'},
                {'name': '', 'id': 'actions', 'presentation': 'markdown'}
            ],
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'minWidth': '100px',
                'maxWidth': '180px',
                'whiteSpace': 'normal'
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'column_id': 'is_paid'},
                    'textAlign': 'center'
                }
            ],
            data=get_api_configs_for_table()
        )

    def create_sci_db_keys_table():
        return dash_table.DataTable(
            id='sci-db-keys-table',
            columns=[
                {'name': 'Database', 'id': 'database'},
                {'name': 'API Key/Token', 'id': 'api_key', 'presentation': 'markdown'},
                {'name': 'Institutional', 'id': 'is_institutional'},
                {'name': 'Institution', 'id': 'institution'},
                {'name': 'Last Updated', 'id': 'updated_at'},
                {'name': '', 'id': 'actions', 'presentation': 'markdown'}
            ],
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'minWidth': '100px',
                'maxWidth': '180px',
                'whiteSpace': 'normal'
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'column_id': 'is_institutional'},
                    'textAlign': 'center'
                }
            ],
            data=get_sci_db_configs_for_table()
        )

    # Add more callbacks for saving AI providers and scientific databases
    @app.callback(
        [Output('api-message', 'children'),
         Output('provider-dropdown', 'value'),
         Output('api-key-input', 'value'),
         Output('is-paid-checkbox', 'checked'),
         Output('api-keys-table-container', 'children', allow_duplicate=True)],
        [Input('save-button', 'n_clicks')],
        [State('provider-dropdown', 'value'),
         State('api-key-input', 'value'),
         State('is-paid-checkbox', 'checked')],
        prevent_initial_call=True
    )
    def save_api_configuration(n_clicks, provider, api_key, is_paid):
        if not n_clicks or not provider or not api_key:
            return no_update, no_update, no_update, no_update, no_update

        # Check if the configuration already exists
        existing_config = AIProvider.query.filter_by(
            user_id=current_user.id,
            provider=provider
        ).first()

        if existing_config:
            # Update existing configuration
            existing_config.api_key = api_key
            existing_config.is_paid = is_paid if is_paid is not None else False
            existing_config.updated_at = datetime.utcnow()
            message = html.Div(f"Updated {provider.capitalize()} API configuration", className="text-success")
        else:
            # Create new configuration
            new_config = AIProvider(
                user_id=current_user.id,
                provider=provider,
                api_key=api_key,
                is_paid=is_paid if is_paid is not None else False
            )
            db.session.add(new_config)
            message = html.Div(f"Added {provider.capitalize()} API configuration", className="text-success")

        # Commit changes
        db.session.commit()

        # Reset form and update table
        return message, None, None, False, [create_api_keys_table()]

    # Scientific Database Configuration Callback
    @app.callback(
        [Output('sci-db-message', 'children'),
         Output('sci-db-dropdown', 'value'),
         Output('sci-db-key-input', 'value'),
         Output('sci-db-institutional-checkbox', 'checked'),
         Output('sci-db-institution-input', 'value'),
         Output('sci-db-keys-table-container', 'children', allow_duplicate=True)],
        [Input('save-sci-db-button', 'n_clicks')],
        [State('sci-db-dropdown', 'value'),
         State('sci-db-key-input', 'value'),
         State('sci-db-institutional-checkbox', 'checked'),
         State('sci-db-institution-input', 'value')],
        prevent_initial_call=True
    )
    def save_sci_db_configuration(n_clicks, database, api_key, is_institutional, institution):
        if not n_clicks or not database or not api_key:
            return no_update, no_update, no_update, no_update, no_update, no_update

        # Check if the configuration already exists
        existing_config = ScientificDatabase.query.filter_by(
            user_id=current_user.id,
            database_name=database
        ).first()

        if existing_config:
            # Update existing configuration
            existing_config.api_key = api_key
            existing_config.is_institutional = is_institutional if is_institutional is not None else False
            existing_config.institution = institution
            existing_config.updated_at = datetime.utcnow()
            message = html.Div(f"Updated {database.capitalize()} database configuration", className="text-success")
        else:
            # Create new configuration
            new_config = ScientificDatabase(
                user_id=current_user.id,
                database_name=database,
                api_key=api_key,
                is_institutional=is_institutional if is_institutional is not None else False,
                institution=institution
            )
            db.session.add(new_config)
            message = html.Div(f"Added {database.capitalize()} database configuration", className="text-success")

        # Commit changes
        db.session.commit()

        # Reset form and update table
        return message, None, None, False, "", [create_sci_db_keys_table()]


def get_api_configs_for_table():
    """
    Get AI configurations formatted for the DataTable
    Returns:
        List of dictionaries with API configurations
    """
    from models import AIProvider

    try:
        # Only query if we're in a request context with an authenticated user
        if has_request_context() and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            configs = AIProvider.query.filter_by(user_id=current_user.id).all()

            table_data = []
            for config in configs:
                # Mask API key
                masked_key = f"{'*' * 20}{config.api_key[-5:]}" if config.api_key else ""

                table_data.append({
                    'provider': config.provider.capitalize(),
                    'api_key': masked_key,
                    'is_paid': "✓" if config.is_paid else "✗",
                    'updated_at': config.updated_at.strftime("%Y-%m-%d") if config.updated_at else "",
                    'actions': "**[Edit](edit)** | **[Delete](delete)**"
                })

            return table_data
        else:
            return []
    except Exception:
        # Return empty list in case of any errors
        return []


def get_sci_db_configs_for_table():
    """
    Get Scientific Database configurations formatted for the DataTable

    Returns:
        List of dictionaries with Scientific Database configurations
    """
    from models import ScientificDatabase

    try:
        # Only query if we're in a request context with an authenticated user
        if has_request_context() and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            configs = ScientificDatabase.query.filter_by(user_id=current_user.id).all()

            table_data = []
            for config in configs:
                # Mask API key
                masked_key = f"{'*' * 20}{config.api_key[-5:]}" if config.api_key else ""

                table_data.append({
                    'database': config.database_name.capitalize(),
                    'api_key': masked_key,
                    'is_institutional': "✓" if config.is_institutional else "✗",
                    'institution': config.institution or "-",
                    'updated_at': config.updated_at.strftime("%Y-%m-%d") if config.updated_at else "",
                    'actions': "**[Edit](edit)** | **[Delete](delete)**"
                })

            return table_data
        else:
            return []
    except Exception:
        # Return empty list in case of any errors
        return []
