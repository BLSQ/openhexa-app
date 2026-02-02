SKILLS_REGISTRY = {}


def register_skill(name, description, content, sub_skills=None):
    SKILLS_REGISTRY[name] = {
        "description": description,
        "content": content,
        "sub_skills": sub_skills or {},
    }


def get_skill(name):
    return SKILLS_REGISTRY.get(name)


def get_available_skills():
    return {name: skill["description"] for name, skill in SKILLS_REGISTRY.items()}


def get_sub_skill_details(skill_name, sub_skill_name):
    skill = SKILLS_REGISTRY.get(skill_name)
    if not skill:
        return None
    return skill["sub_skills"].get(sub_skill_name)
