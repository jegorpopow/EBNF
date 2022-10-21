import sublime
import sublime_plugin

class Completions(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if not view.match_selector(locations[0], "source.EBNF"):
            return []

        available_completions = [
            "start:",
            "names:",
            "rules:",
            "EPS"
        ]

        prefix = prefix.lower()

        out = []
        for comp in available_completions:
            if comp.lower().startswith(prefix):
                out.append(comp)

        return out