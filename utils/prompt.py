def generate_prompt(template_path, *args):
    template = open(template_path).read()
    prompt = template.format(*args)
    return prompt