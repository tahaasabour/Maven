

from jinja2 import FileSystemLoader, Environment

class prompt_template_helper:
    @staticmethod
    def render_template(template_path: str, template_name: str, context: dict) -> str:
        try:
            loader = FileSystemLoader(template_path)
            env = Environment(loader=loader)
            template = env.get_template(template_name)
        except Exception as e:
            raise RuntimeError(f"Error loading or rendering template {template_name}: {e}")
        return template.render(context)