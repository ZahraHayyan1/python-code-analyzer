import os
import json
from jinja2 import Environment, FileSystemLoader

base_dir = os.path.dirname(__file__)
templates_dir = os.path.join(base_dir, "templates")

env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
env.filters["tojson"] = lambda v, indent=2: json.dumps(v, indent=indent)


def generate_report(results, output_path):
    template = env.get_template("report_template.html")
    html = template.render(**results)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path