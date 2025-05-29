from dash import callback, Input, Output, State, html, dcc
import dash_bootstrap_components as dbc
from flask import jsonify, request
from flask_login import login_required, current_user

# Import your existing layout and callback functions
from layouts.fast_generator_layout import create_fast_draft_generatot_layout
from callbacks.fast_generator_callbacks import register_fast_draft_gen_callbacks

def init_academic_draft_generator(app, server):
    """
    Initialize the Academic Draft Generator module.

    Args:
        app: The main Dash app
        server: The Flask server
    """
    # Register the route for the module
    @server.route('/academic-draft-generator')
    @login_required
    def academic_draft_generator_route():
        return app.index()

    # Add a layout function for the module
    def academic_draft_layout():
        return html.Div([
            # Navigation bar with title and back button
            dbc.Navbar(
                dbc.Container([
                    dbc.Row([
                        dbc.Col([
                            html.H4("Academic Paper Draft Generator", className="mb-0 text-white"),
                        ]),
                        dbc.Col([
                            dbc.Button(
                                "Back to Editor",
                                id="back-to-editor-btn",
                                color="light",
                                className="ml-auto",
                                n_clicks=0
                            ),
                        ], width="auto"),
                    ], className="w-100"),
                ]),
                color="primary",
                dark=True,
                className="mb-4",
            ),

            # Main content - import your existing layout
            create_fast_draft_generatot_layout(),

            # Hidden div for storing state
            html.Div(id="page-state", style={"display": "none"}),

            # Add JavaScript for integration with the main editor
            html.Script("""
                // Send generated content to parent window when button is clicked
                const sendToEditorBtn = document.getElementById('send-to-quill-btn');
                if (sendToEditorBtn) {
                    sendToEditorBtn.addEventListener('click', function() {
                        const content = document.getElementById('draft-output').innerText;

                        // If we're in an iframe, send message to parent
                        if (window.parent !== window) {
                            window.parent.postMessage({
                                type: 'draftContent',
                                content: content
                            }, '*');
                        } else {
                            // If standalone, store in localStorage for retrieval
                            localStorage.setItem('generatedDraft', content);
                            alert('Draft saved. You can now return to the editor.');
                        }
                    });
                }

                // Handle back button
                const backBtn = document.getElementById('back-to-editor-btn');
                if (backBtn) {
                    backBtn.addEventListener('click', function() {
                        if (window.parent !== window) {
                            // In iframe - tell parent to close modal
                            window.parent.postMessage({
                                type: 'closeModal'
                            }, '*');
                        } else {
                            // Standalone - go back to main page
                            window.location.href = '/';
                        }
                    });
                }
            """)
        ])

    # Register the layout
    app.layout = academic_draft_layout

    # Register the callbacks
    register_fast_draft_gen_callbacks(app)

    # Add callback for handling the back button
    @callback(
        Output("page-state", "children"),
        Input("back-to-editor-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def handle_back_button(n_clicks):
        if n_clicks > 0:
            # This is just a placeholder - the actual navigation
            # is handled by the JavaScript
            return "navigating"
        return "staying"

    # Add API endpoint for retrieving generated content
    @server.route('/api/generated-draft', methods=['GET'])
    @login_required
    def get_generated_draft():
        user_id = current_user.id
        # In a real implementation, you would retrieve from a database
        # Here using a session-based approach for simplicity
        return jsonify({"content": request.session.get(f'user_{user_id}_draft', '')})

    @server.route('/api/generated-draft', methods=['POST'])
    @login_required
    def save_generated_draft():
        user_id = current_user.id
        content = request.json.get('content', '')
        # Store in session (in a real implementation, store in database)
        request.session[f'user_{user_id}_draft'] = content
        return jsonify({"success": True})

    # Return the module name for reference
    return "academic_draft_generator"
