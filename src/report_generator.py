from jinja2 import Environment, FileSystemLoader
import json

def generate_report(results, output="Report_Generator.html"):
    env = Environment(loader=FileSystemLoader("."), autoescape=True)
    env.filters["tojson"] = lambda v, indent=2: json.dumps(v, indent=indent)

    template = env.get_template("report_template.html")
    html = template.render(
        metrics=results["metrics"],
        syntax=results["syntax"],
        nodes=results["nodes"]
    )

    with open(output, "w", encoding="utf-8") as f:
        f.write(html)

    return output
