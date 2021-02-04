def global_variables(request):
    return {
        "main_menu_items": [
            {"title": "Dashboard", "app": "dashboard", "index_url": "dashboard:index"},
            {"title": "Catalog", "app": "catalog", "index_url": "catalog:index"},
            {"title": "Notebooks", "app": "notebooks", "index_url": "notebooks:index"},
            {"title": "Pipelines", "app": None, "index_url": "dashboard:index"},
        ]
    }
