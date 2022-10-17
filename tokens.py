def fill_regex_pattern(start: str, sym: str):
    return fr"{start}.+?(?<!(?<!\\)\\){sym}"


NON_TERMINAL_REGEX = fill_regex_pattern("<", ">")
TERMINAL_REGEX = fill_regex_pattern("\"", "\"")
NAME_REGEX = r"\$[A-Za-z_`]+"
KEYWORD_REGEX = r"[a-zA-Z]+:?"

LKLEENE_REGEX = r"\{"
RKLEENE_REGEX = r"\}"

LOPT_REGEX = r"\["
ROPT_REGEX = r"\]"

LGROUP_REGEX = r"\("
RGROUP_REGEX = r"\)"

ALT_SEP_REGEX = r"\|"
BIND_REGEX = r":="
BIND_END_REGEX = r";"
