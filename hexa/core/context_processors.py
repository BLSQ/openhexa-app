def global_variables(request):
    menu_items = [
        {"title": "Dashboard", "app": "dashboard", "index_url": "core:dashboard"},
        {"title": "Catalog", "app": "catalog", "index_url": "catalog:index"},
        {"title": "Notebooks", "app": "notebooks", "index_url": "notebooks:index"},
        {"title": "Pipelines", "app": "pipelines", "index_url": "pipelines:index"},
        {
            "title": "Visualizations",
            "app": "visualizations",
            "index_url": "visualizations:visualization_index",
        },
    ]
    if request.user.is_authenticated and request.user.has_feature_flag("new_frontend"):
        menu_items.insert(1, {"title": "Collections", "index_url": "core:collections"})

    return {"main_menu_items": menu_items}
