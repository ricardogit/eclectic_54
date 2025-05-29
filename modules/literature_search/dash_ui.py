import dash
from dash import html, dcc, Input, Output, State, callback_context, ALL, MATCH
import dash_bootstrap_components as dbc
import requests
import json
from datetime import datetime

# Flag to determine if we're running standalone or in Flask
STANDALONE_MODE = __name__ == "__main__"

# Define layout
literature_layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Literature Search", className="mb-4"),

                # Search form
                dbc.Card([
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Search Query"),
                                dbc.Input(
                                    id="literature-search-query",
                                    type="text",
                                    placeholder="Enter search terms...",
                                ),
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Source"),
                                dbc.Select(
                                    id="literature-search-source",
                                    options=[
                                        {"label": "All Sources", "value": "all"},
                                        {"label": "arXiv", "value": "arxiv"},
                                        {"label": "PubMed", "value": "pubmed"},
                                    ],
                                    value="all",
                                ),
                            ], width=3),
                            dbc.Col([
                                dbc.Label("Max Results"),
                                dbc.Input(
                                    id="literature-search-max-results",
                                    type="number",
                                    value=25,
                                    min=5,
                                    max=100,
                                    step=5,
                                ),
                            ], width=3),
                        ]),
                        html.Div(className="mt-3", children=[
                            dbc.Button(
                                "Search",
                                id="literature-search-button",
                                color="primary",
                                n_clicks=0,
                            ),
                            # Explicit loading div
                            html.Div(id="literature-search-loading", className="d-inline-block ml-2"),
                        ]),
                    ]),
                ], className="mb-4"),

                # Recent searches
                dbc.Card([
                    dbc.CardHeader("Recent Searches"),
                    dbc.CardBody([
                        html.Div(id="literature-recent-searches"),
                    ]),
                ], className="mb-4"),

                # Search results
                dbc.Card([
                    dbc.CardHeader("Search Results"),
                    dbc.CardBody([
                        html.Div(id="literature-search-results", style={"minHeight": "200px"}),
                    ]),
                ], className="mb-4"),
            ], width=8),

            # Right sidebar for collections
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("My Collections"),
                    dbc.CardBody([
                        html.Div(id="literature-collections"),
                        html.Hr(),
                        html.H5("Create New Collection"),
                        dbc.Input(
                            id="literature-new-collection-name",
                            type="text",
                            placeholder="Collection name...",
                            className="mb-2",
                        ),
                        dbc.Textarea(
                            id="literature-new-collection-description",
                            placeholder="Description...",
                            className="mb-2",
                        ),
                        dbc.Button(
                            "Create Collection",
                            id="literature-create-collection-button",
                            color="primary",
                            size="sm",
                            n_clicks=0,
                        ),
                        html.Div(id="literature-collection-create-result", className="mt-2"),
                    ]),
                ], className="mb-4"),

                # Selected collection
                dbc.Card([
                    dbc.CardHeader(
                        html.Div(id="literature-selected-collection-header", children="Selected Collection")),
                    dbc.CardBody([
                        html.Div(id="literature-collection-papers", style={"minHeight": "200px"}),
                    ]),
                ]),
            ], width=4),
        ]),

        # Paper detail modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle(html.Div(id="literature-paper-modal-title"))),
            dbc.ModalBody([
                html.Div(id="literature-paper-modal-content"),
                html.Div(id="literature-save-paper-result", className="mt-2"),
                html.Div(id="literature-add-to-collection-result", className="mt-2"),
            ]),
            dbc.ModalFooter([
                html.Div(id="literature-paper-add-to-collection-dropdown", className="mr-auto"),
                dbc.Button(
                    "Close",
                    id="literature-close-paper-modal",
                    className="ml-auto",
                    n_clicks=0,
                ),
                html.Div(style={"display": "none"}, children=[
                    dbc.Button(
                        "Save Paper",
                        id="literature-save-paper-button",
                        color="success",
                        className="mt-3",
                        n_clicks=0,
                    ),
                    dbc.Button(
                        "Add",
                        id="literature-add-to-collection-button",
                        color="secondary",
                        size="sm",
                        className="ml-2",
                    ),
                    dbc.Select(
                        id="literature-add-to-collection-select",
                        options=[],
                        value=None,
                    ),
                ]),
            ]),
        ], id="literature-paper-modal", size="xl"),

        # Confirmation modal
        dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Confirmation")),
            dbc.ModalBody(html.Div(id="literature-confirm-modal-body")),
            dbc.ModalFooter([
                dbc.Button(
                    "Cancel",
                    id="literature-confirm-cancel",
                    color="secondary",
                    n_clicks=0,
                ),
                dbc.Button(
                    "Confirm",
                    id="literature-confirm-ok",
                    color="danger",
                    n_clicks=0,
                ),
            ]),
        ], id="literature-confirm-modal"),
    ]),

    # Store components for state
    dcc.Store(id="literature-search-results-store"),
    dcc.Store(id="literature-collections-store"),
    dcc.Store(id="literature-selected-paper-store"),
    dcc.Store(id="literature-selected-collection-store"),
    dcc.Store(id="literature-confirm-action-store"),
])

# Mock data for standalone testing
# Base URL for literature API endpoints
API_BASE_URL = "/literature/api"

# Mock data for standalone testing
MOCK_DATA = {
    "collections": [
        {
            "id": 1,
            "name": "Machine Learning",
            "description": "Papers about machine learning and AI",
            "created_at": "2025-05-01T00:00:00Z"
        },
        {
            "id": 2,
            "name": "Natural Language Processing",
            "description": "NLP research",
            "created_at": "2025-05-02T00:00:00Z"
        }
    ],
    "search_results": {
        "query": "machine learning",
        "source": "all",
        "results": [
            {
                "id": 1,
                "title": "Deep Learning Advances",
                "authors": "Smith, J., Johnson, R.",
                "abstract": "This paper discusses recent advances in deep learning techniques...",
                "doi": "10.1234/dl.2025.001",
                "url": "https://example.com/papers/dl-001",
                "journal": "Journal of AI Research",
                "year": 2025,
                "source_db": "arxiv",
                "paper_id": "arxiv:2025.12345"
            },
            {
                "id": 2,
                "title": "Transformer Models for Medical Imaging",
                "authors": "Brown, A., Davis, M.",
                "abstract": "We present a novel approach to medical image analysis using transformer models...",
                "doi": "10.1234/med.2025.002",
                "url": "https://example.com/papers/med-002",
                "journal": "Medical AI Journal",
                "year": 2025,
                "source_db": "pubmed",
                "paper_id": "pubmed:987654321"
            }
        ],
        "count": 2
    },
    "search_history": [
        {
            "id": 1,
            "query": "machine learning",
            "source_db": "all",
            "results_count": 120,
            "created_at": "2025-05-01T10:00:00Z"
        },
        {
            "id": 2,
            "query": "natural language processing",
            "source_db": "arxiv",
            "results_count": 85,
            "created_at": "2025-05-02T14:30:00Z"
        }
    ],
    "collection_papers": [
        {
            "id": 1,
            "title": "Deep Learning Advances",
            "authors": "Smith, J., Johnson, R.",
            "journal": "Journal of AI Research",
            "year": 2025
        }
    ],
    "paper_details": {
        "id": 1,
        "title": "Deep Learning Advances",
        "authors": "Smith, J., Johnson, R.",
        "abstract": "This paper discusses recent advances in deep learning techniques...",
        "doi": "10.1234/dl.2025.001",
        "url": "https://example.com/papers/dl-001",
        "journal": "Journal of AI Research",
        "year": 2025,
        "source_db": "arxiv",
        "paper_id": "arxiv:2025.12345"
    },
    "paper_saved": {
        "message": "Paper saved successfully",
        "paper": {
            "id": 1,
            "title": "Deep Learning Advances"
        }
    },
    "collection_created": {
        "message": "Collection created successfully",
        "collection": {
            "id": 3,
            "name": "New Collection",
            "description": "A collection of papers"
        }
    },
    "paper_added": {
        "message": "Paper added to collection successfully"
    },
    "paper_removed": {
        "message": "Paper removed from collection successfully"
    }
}


# Helper function to handle API calls - uses mock data in standalone mode
def api_call(endpoint, method="get", params=None, json_data=None):
    """
    Makes API calls with proper error handling.

    Args:
        endpoint: API endpoint path (e.g., '/search', '/collections')
        method: HTTP method ('get', 'post', 'delete', etc.)
        params: Query parameters for GET requests
        json_data: JSON data for POST requests

    Returns:
        Response data as a dictionary or error information
    """
    if STANDALONE_MODE:
        # In standalone mode, return mock data based on the endpoint
        print(f"[Standalone Mode] API Call: {method.upper()} {endpoint}")

        # Return mock data based on the endpoint and method
        if endpoint == "/collections" and method.lower() == "get":
            return MOCK_DATA["collections"]
        elif endpoint.startswith("/collections") and method.lower() == "post":
            return MOCK_DATA["collection_created"]
        elif "/collections/" in endpoint and endpoint.endswith("/papers") and method.lower() == "get":
            return MOCK_DATA["collection_papers"]
        elif "/collections/" in endpoint and "/papers/" in endpoint and method.lower() == "post":
            return MOCK_DATA["paper_added"]
        elif "/collections/" in endpoint and "/papers/" in endpoint and method.lower() == "delete":
            return MOCK_DATA["paper_removed"]
        elif endpoint == "/search" and method.lower() == "get":
            return MOCK_DATA["search_results"]
        elif endpoint == "/search-history" and method.lower() == "get":
            return MOCK_DATA["search_history"]
        elif endpoint == "/papers" and method.lower() == "post":
            return MOCK_DATA["paper_saved"]
        elif endpoint.startswith("/papers/") and method.lower() == "get":
            return MOCK_DATA["paper_details"]
        else:
            print(f"[Warning] No mock data available for: {method.upper()} {endpoint}")
            return {"error": "No mock data available for this endpoint"}

    # In integrated mode, make real API calls
    try:
        # Construct the full URL path using the API_BASE_URL
        full_url = f"{API_BASE_URL}{endpoint}"
        print(f"[API Call] {method.upper()} {full_url}")

        # Make the appropriate HTTP request based on the method
        if method.lower() == "get":
            response = requests.get(full_url, params=params)
        elif method.lower() == "post":
            response = requests.post(full_url, json=json_data, params=params)
        elif method.lower() == "put":
            response = requests.put(full_url, json=json_data, params=params)
        elif method.lower() == "delete":
            response = requests.delete(full_url, params=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # Check for HTTP errors
        response.raise_for_status()

        # Parse JSON response
        try:
            return response.json()
        except ValueError:
            # Return empty object if response is not JSON
            return {}

    except requests.RequestException as e:
        print(f"[API Error] {e}")
        # Extract status code if available
        status_code = e.response.status_code if hasattr(e, 'response') and hasattr(e.response, 'status_code') else None
        error_message = str(e)

        # For specific status codes, provide more helpful messages
        if status_code == 404:
            error_message = f"Resource not found: {full_url}"
        elif status_code == 401:
            error_message = "Authentication required. Please log in."
        elif status_code == 403:
            error_message = "You don't have permission to access this resource."
        elif status_code == 500:
            error_message = "Server error. Please try again or contact support."

        return {"error": error_message, "status_code": status_code}
    except ValueError as e:
        print(f"[API Error] Invalid method: {e}")
        return {"error": str(e)}
    except Exception as e:
        print(f"[API Error] Unexpected error: {e}")
        return {"error": f"Unexpected error: {str(e)}"}


def register_callbacks(dash_app):
    """Register all callbacks for the Dash app"""

    # Initialize page
    @dash_app.callback(
        Output("literature-collections-store", "data"),
        Input("literature-collections-store", "id"),
        prevent_initial_call=False
    )
    def initialize_page(_):
        return api_call("/api/literature/collections")

    # Search papers
    @dash_app.callback(
        [
            Output("literature-search-results-store", "data"),
            Output("literature-search-loading", "children"),
        ],
        [
            Input("literature-search-button", "n_clicks"),
        ],
        [
            State("literature-search-query", "value"),
            State("literature-search-source", "value"),
            State("literature-search-max-results", "value"),
        ],
        prevent_initial_call=True,
    )
    def search_papers(n_clicks, query, source, max_results):
        if not n_clicks or not query:
            return None, ""

        params = {
            "query": query,
            "source": source,
            "max_results": max_results
        }

        results = api_call("/api/literature/search", params=params)
        return results, ""

    # Display search results
    @dash_app.callback(
        Output("literature-search-results", "children"),
        [Input("literature-search-results-store", "data")],
        prevent_initial_call=True,
    )
    def display_search_results(data):
        if not data:
            return html.Div("No search results to display.")

        if "error" in data:
            return html.Div(f"Error: {data['error']}", className="text-danger")

        results = data.get("results", [])
        count = data.get("count", 0)

        if count == 0:
            return html.Div("No results found for your query.")

        result_cards = []
        for i, paper in enumerate(results):
            result_cards.append(
                dbc.Card([
                    dbc.CardHeader(html.H5(paper["title"])),
                    dbc.CardBody([
                        html.P(f"Authors: {paper.get('authors', 'Unknown')}"),
                        html.P(f"Source: {paper.get('journal', 'Unknown')}, {paper.get('year', '')}"),
                        html.P(paper.get("abstract", "")[:200] + "..." if paper.get("abstract") and len(
                            paper.get("abstract")) > 200 else paper.get("abstract") or "No abstract available"),
                        dbc.Button(
                            "View Details",
                            id={"type": "literature-view-paper-button", "index": i},
                            color="primary",
                            size="sm",
                            className="mt-2",
                        ),
                    ]),
                ], className="mb-3")
            )

        return html.Div([
            html.H4(f"Found {count} results"),
            html.Div(result_cards),
        ])

    # Display collections
    @dash_app.callback(
        Output("literature-collections", "children"),
        [Input("literature-collections-store", "data")],
        prevent_initial_call=True,
    )
    def display_collections(data):
        if not data:
            return html.Div("No collections to display.")

        if "error" in data:
            return html.Div(f"Error: {data['error']}", className="text-danger")

        if not isinstance(data, list):
            return html.Div("No collections found.")

        collection_items = []
        for i, collection in enumerate(data):
            collection_items.append(
                dbc.Button(
                    collection["name"],
                    id={"type": "literature-select-collection-button", "index": i},
                    color="link",
                    className="d-block text-left mb-2",
                )
            )

        return html.Div(collection_items) if collection_items else html.Div("No collections yet. Create one below.")

    # Add all your other callbacks here, updating them to use the api_call helper
    # For example:

    @dash_app.callback(
        Output("literature-recent-searches", "children"),
        [Input("literature-search-results-store", "data")],
        prevent_initial_call=True,
    )
    def display_recent_searches(_):
        searches = api_call("/api/literature/search-history")

        if "error" in searches:
            return html.Div(f"Error loading recent searches: {searches['error']}", className="text-danger")

        if not searches:
            return html.Div("No recent searches.")

        search_items = []
        for search in searches:
            search_items.append(
                html.Div([
                    html.A(
                        search["query"],
                        href="#",
                        id={"type": "literature-recent-search-link", "index": search["id"]},
                        className="mr-2",
                    ),
                    html.Small(
                        f"({search['source_db']}, {search['results_count']} results)",
                        className="text-muted",
                    ),
                ], className="mb-2")
            )

        return html.Div(search_items)

    # Create new collection
    @dash_app.callback(
        [
            Output("literature-collections-store", "data", allow_duplicate=True),
            Output("literature-collection-create-result", "children"),
            Output("literature-new-collection-name", "value"),
            Output("literature-new-collection-description", "value"),
        ],
        [Input("literature-create-collection-button", "n_clicks")],
        [
            State("literature-new-collection-name", "value"),
            State("literature-new-collection-description", "value"),
        ],
        prevent_initial_call=True,
    )
    def create_collection(n_clicks, name, description):
        if not n_clicks or not name:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update

        try:
            # Call API
            response = requests.post(
                "/api/literature/collections",
                json={
                    "name": name,
                    "description": description or "",
                },
            )

            # Check for errors
            response.raise_for_status()

            # Get updated collections
            collections_response = requests.get("/api/literature/collections")
            collections_response.raise_for_status()

            # Return success message
            return collections_response.json(), html.Div("Collection created successfully",
                                                         className="text-success"), "", ""
        except Exception as e:
            return dash.no_update, html.Div(f"Error: {str(e)}", className="text-danger"), dash.no_update, dash.no_update


    # Handle clicking on a recent search
    @dash_app.callback(
        [
            Output("literature-search-query", "value"),
            Output("literature-search-source", "value"),
            Output("literature-search-button", "n_clicks"),
        ],
        [Input({"type": "literature-recent-search-link", "index": ALL}, "n_clicks")],
        [State({"type": "literature-recent-search-link", "index": ALL}, "children")],
        prevent_initial_call=True,
    )
    def handle_recent_search_click(n_clicks, queries):
        if not any(n_clicks):
            return dash.no_update, dash.no_update, dash.no_update

        # Find clicked item
        clicked_index = next((i for i, n in enumerate(n_clicks) if n), None)
        if clicked_index is None:
            return dash.no_update, dash.no_update, dash.no_update

        # Get query text
        query = queries[clicked_index]

        # Set form values and trigger search
        return query, "all", 1

    # View paper details
    @dash_app.callback(
        Output("literature-selected-paper-store", "data"),
        [Input({"type": "literature-view-paper-button", "index": ALL}, "n_clicks")],
        [State("literature-search-results-store", "data")],
        prevent_initial_call=True,
    )
    def select_paper(n_clicks_list, search_results):
        if not n_clicks_list or not any(n_clicks_list) or not search_results or "results" not in search_results:
            return dash.no_update

        # Find which button was clicked
        ctx = callback_context
        if not ctx.triggered:
            return dash.no_update

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        try:
            button_index = json.loads(button_id)["index"]
        except:
            return dash.no_update

        # Get paper data from search results
        if button_index >= len(search_results["results"]):
            return dash.no_update

        paper = search_results["results"][button_index]

        return paper

    # Handle paper selection and display modal
    @dash_app.callback(
        [
            Output("literature-paper-modal", "is_open"),
            Output("literature-paper-modal-title", "children"),
            Output("literature-paper-modal-content", "children"),
            Output("literature-paper-add-to-collection-dropdown", "children"),
        ],
        [
            Input("literature-selected-paper-store", "data"),
            Input("literature-close-paper-modal", "n_clicks"),
        ],
        [
            State("literature-collections-store", "data"),
            State("literature-paper-modal", "is_open"),
        ],
    )
    def handle_paper_selection(paper_data, close_clicks, collections, is_open):
        ctx = callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if trigger_id == "literature-close-paper-modal" and close_clicks:
            return False, "", "", ""

        if not paper_data:
            return is_open, "", "", ""

        # Create collection dropdown for adding paper
        collection_options = []
        if collections and isinstance(collections, list):
            for collection in collections:
                collection_options.append(
                    {"label": collection["name"], "value": collection["id"]}
                )

        add_to_collection_dropdown = html.Div([
            dbc.Label("Add to Collection", className="mr-2"),
            dbc.Select(
                id="literature-add-to-collection-select",
                options=collection_options,
                value=None,
                placeholder="Select collection...",
                className="d-inline-block" if collection_options else "d-none",
                style={"width": "200px"},
            ),
            dbc.Button(
                "Add",
                id="literature-add-to-collection-button",
                color="secondary",
                size="sm",
                className="ml-2",
                disabled=len(collection_options) == 0,
            ),
        ])

        # Format authors nicely
        authors = paper_data.get("authors", "Unknown")
        if isinstance(authors, list):
            authors = ", ".join(authors)

        # Create modal content
        content = html.Div([
            html.H6("Authors"),
            html.P(authors),

            html.H6("Abstract"),
            html.P(paper_data.get("abstract", "No abstract available")),

            html.H6("Source"),
            html.P([
                html.Span(f"{paper_data.get('journal', 'Unknown')}, {paper_data.get('year', '')}"),
                html.Br(),
                html.A(
                    "View Original",
                    href=paper_data.get("url", "#"),
                    target="_blank",
                    className="mt-2",
                ) if paper_data.get("url") else "",
            ]),

            html.H6("DOI"),
            html.P(paper_data.get("doi", "Not available")),

            dbc.Button(
                "Save Paper",
                id="literature-save-paper-button",
                color="success",
                className="mt-3",
                n_clicks=0,
            ),
        ])

        return True, paper_data.get("title", "Paper Details"), content, add_to_collection_dropdown

    # Save paper
    @dash_app.callback(
        Output("literature-save-paper-result", "children"),
        [Input("literature-save-paper-button", "n_clicks")],
        [State("literature-selected-paper-store", "data")],
        prevent_initial_call=True,
    )
    def save_paper(n_clicks, paper_data):
        if not n_clicks or not paper_data:
            return dash.no_update

        try:
            # Call API
            response = requests.post(
                "/api/literature/papers",
                json=paper_data,
            )

            # Check for errors
            response.raise_for_status()

            # Show success message
            result = response.json()
            return html.Div([
                html.I(className="fa fa-check mr-1"),
                f"Paper saved successfully (ID: {result['paper']['id']})"
            ], className="text-success")
        except Exception as e:
            return html.Div([
                html.I(className="fa fa-times mr-1"),
                f"Error: {str(e)}"
            ], className="text-danger")

    # Add paper to collection
    @dash_app.callback(
        Output("literature-add-to-collection-result", "children"),
        [Input("literature-add-to-collection-button", "n_clicks")],
        [
            State("literature-selected-paper-store", "data"),
            State("literature-add-to-collection-select", "value"),
        ],
        prevent_initial_call=True,
    )
    def add_paper_to_collection(n_clicks, paper_data, collection_id):
        if not n_clicks or not paper_data or not collection_id:
            return dash.no_update

        try:
            # First save the paper if needed
            save_response = requests.post(
                "/api/literature/papers",
                json=paper_data,
            )
            save_response.raise_for_status()
            paper_result = save_response.json()
            paper_id = paper_result["paper"]["id"]

            # Then add to collection
            add_response = requests.post(
                f"/api/literature/collections/{collection_id}/papers/{paper_id}",
            )
            add_response.raise_for_status()

            # Show success message
            return html.Div([
                html.I(className="fa fa-check mr-1"),
                "Added to collection successfully"
            ], className="text-success")
        except Exception as e:
            return html.Div([
                html.I(className="fa fa-times mr-1"),
                f"Error: {str(e)}"
            ], className="text-danger")

    # Select collection
    @dash_app.callback(
        [
            Output("literature-selected-collection-store", "data"),
            Output("literature-selected-collection-header", "children"),
        ],
        [Input({"type": "literature-select-collection-button", "index": ALL}, "n_clicks")],
        [
            State({"type": "literature-select-collection-button", "index": ALL}, "children"),
            State("literature-collections-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def select_collection(n_clicks_list, collection_names, collections):
        if not n_clicks_list or not any(n_clicks_list) or not collections:
            return dash.no_update, dash.no_update

        # Find which button was clicked
        ctx = callback_context
        if not ctx.triggered:
            return dash.no_update, dash.no_update

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        try:
            button_index = json.loads(button_id)["index"]
        except:
            return dash.no_update, dash.no_update

        # Get collection
        if button_index >= len(collections):
            return dash.no_update, dash.no_update

        collection = collections[button_index]

        # Set header
        header = html.Div([
            collection["name"],
            html.Small(f" ({collection.get('description', '')})", className="text-muted ml-2")
        ])

        return collection, header

    # Display collection papers
    @dash_app.callback(
        Output("literature-collection-papers", "children"),
        [Input("literature-selected-collection-store", "data")],
        prevent_initial_call=True,
    )
    def display_collection_papers(collection):
        if not collection:
            return html.Div("Select a collection to view its papers.")

        try:
            # Call API
            response = requests.get(f"/api/literature/collections/{collection['id']}/papers")

            # Check for errors
            response.raise_for_status()

            # Parse data
            papers = response.json()

            if not papers:
                return html.Div("No papers in this collection.")

            paper_items = []
            for i, paper in enumerate(papers):
                paper_items.append(
                    dbc.Card([
                        dbc.CardBody([
                            html.H6(paper["title"], className="mb-1"),
                            html.P(f"Authors: {paper.get('authors', 'Unknown')}", className="small mb-1"),
                            html.P(f"Source: {paper.get('journal', 'Unknown')}", className="small mb-1"),
                            dbc.Button(
                                "Remove",
                                id={"type": "literature-remove-paper-button", "index": i},
                                color="danger",
                                size="sm",
                                className="mt-1",
                                outline=True,
                            ),
                        ]),
                    ], className="mb-2")
                )

            return html.Div(paper_items)
        except Exception as e:
            return html.Div(f"Error loading collection papers: {str(e)}", className="text-danger")

    # Remove paper from collection (confirmation)
    @dash_app.callback(
        [
            Output("literature-confirm-modal", "is_open"),
            Output("literature-confirm-modal-body", "children"),
            Output("literature-confirm-action-store", "data"),
        ],
        [Input({"type": "literature-remove-paper-button", "index": ALL}, "n_clicks")],
        [
            State("literature-selected-collection-store", "data"),
            State("literature-collection-papers", "children"),
        ],
        prevent_initial_call=True,
    )
    def confirm_remove_paper(n_clicks_list, collection, paper_cards):
        if not n_clicks_list or not any(n_clicks_list) or not collection:
            return False, "", {}

        # Find which button was clicked
        ctx = callback_context
        if not ctx.triggered:
            return False, "", {}

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        try:
            button_index = json.loads(button_id)["index"]
        except:
            return False, "", {}

        # Get corresponding paper info
        try:
            # Call API to get papers
            response = requests.get(f"/api/literature/collections/{collection['id']}/papers")
            response.raise_for_status()
            papers = response.json()

            if button_index >= len(papers):
                return False, "", {}

            paper = papers[button_index]

            # Prepare confirm message
            confirm_message = html.Div([
                "Are you sure you want to remove ",
                html.Strong(paper["title"]),
                " from the collection ",
                html.Strong(collection["name"]),
                "?"
            ])

            # Store action data
            action_data = {
                "action": "remove_paper",
                "paper_id": paper["id"],
                "collection_id": collection["id"]
            }

            return True, confirm_message, action_data
        except:
            return False, "", {}

    # Handle confirmation dialog
    @dash_app.callback(
        [
            Output("literature-confirm-modal", "is_open", allow_duplicate=True),
            Output("literature-collection-papers", "children", allow_duplicate=True),
        ],
        [
            Input("literature-confirm-cancel", "n_clicks"),
            Input("literature-confirm-ok", "n_clicks"),
        ],
        [
            State("literature-confirm-action-store", "data"),
            State("literature-confirm-modal", "is_open"),
            State("literature-selected-collection-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def handle_confirmation(cancel_clicks, ok_clicks, action_data, is_open, collection):
        ctx = callback_context
        if not ctx.triggered:
            return is_open, dash.no_update

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if trigger_id == "literature-confirm-cancel":
            return False, dash.no_update

        if trigger_id == "literature-confirm-ok" and action_data and action_data.get("action") == "remove_paper":
            try:
                # Call API to remove paper
                paper_id = action_data["paper_id"]
                collection_id = action_data["collection_id"]

                response = requests.delete(
                    f"/api/literature/collections/{collection_id}/papers/{paper_id}"
                )
                response.raise_for_status()

                # Refresh papers list
                papers_response = requests.get(f"/api/literature/collections/{collection_id}/papers")
                papers_response.raise_for_status()
                papers = papers_response.json()

                # Create updated paper items list
                if not papers:
                    return False, html.Div("No papers in this collection.")

                paper_items = []
                for i, paper in enumerate(papers):
                    paper_items.append(
                        dbc.Card([
                            dbc.CardBody([
                                html.H6(paper["title"], className="mb-1"),
                                html.P(f"Authors: {paper.get('authors', 'Unknown')}", className="small mb-1"),
                                html.P(f"Source: {paper.get('journal', 'Unknown')}", className="small mb-1"),
                                dbc.Button(
                                    "Remove",
                                    id={"type": "literature-remove-paper-button", "index": i},
                                    color="danger",
                                    size="sm",
                                    className="mt-1",
                                    outline=True,
                                ),
                            ]),
                        ], className="mb-2")
                    )

                return False, html.Div(paper_items)
            except Exception as e:
                # Return to closed state with unchanged papers list
                return False, dash.no_update

        return is_open, dash.no_update


# For standalone testing
if __name__ == "__main__":
    from dash import Dash

    app = Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True  # IMPORTANT: Add this flag
    )
    app.layout = literature_layout
    register_callbacks(app)
    app.run(debug=True)