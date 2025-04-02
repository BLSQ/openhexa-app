def global_variables(request):
    menu_items = [
        {"title": "Catalog", "app": "catalog", "index_url": "catalog:index"},
        {"title": "Notebooks", "app": "notebooks", "index_url": "notebooks:index"},
        {"title": "Pipelines", "app": "pipelines", "index_url": "pipelines:index"},
    ]
    return {"main_menu_items": menu_items}
