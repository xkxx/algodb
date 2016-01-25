from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import RawTokenFormatter
from pygments.token import Token, string_to_tokentype

formatter = RawTokenFormatter()

def extract_keywords(snippet, lang):
    tokens_str = code_to_raw_tokens(snippet, "python")
    return extract_keywords_tokens(tokens_str)

# TODO: redis lang mapping
def lang_mapping(raw_lang):
    mapping = {}
    return mapping[raw_lang]

def code_to_raw_tokens(snippet, lang):
    # e.g. lang = python
    lexer = get_lexer_by_name(lang, stripall=True)
    return highlight(snippet, lexer, formatter)

def extract_keywords_tokens(tokens_str):
    keywords = []
    for token in tokens_str.strip().split("\n"):
        (tokentype, tokenvalue) = tuple(token.split("\t"))
        tokenvalue = tokenvalue[2:-1].replace("\\t", "").replace("\\n", "").strip()
        tokentype = string_to_tokentype(tokentype)

        if (tokentype is Token.Name.Function \
            or tokentype in Token.Text \
            or tokentype in Token.Comment) \
            and tokentype not in Token.Name.Builtin \
            and tokentype not in Token.Variable \
            and len(tokenvalue) > 1:
            keywords.append( (tokentype_to_string(tokentype), tokenvalue) )
    return keywords

def tokentype_to_string(tokentype):
    if tokentype is Token.Name.Function:
        return 'function_name'
    if tokentype in Token.Text:
        return 'text'
    if tokentype in Token.Comment:
        return 'comment'

def sample_output(name):
    snippet = open(name + ".txt").read()
    tokens_str = code_to_raw_tokens(snippet, "python")  # TODO change the language
    output = open(name, 'w+')
    output.write(tokens_str)

def main():
    import sys
    input = sys.argv[1]
    lang = sys.argv[2]
    snippet = open(input).read()
    tokens_str = code_to_raw_tokens(snippet, lang)
    keywords = extract_keywords_tokens(tokens_str)
    for (type, token) in keywords:
        print '%s:\n\t%s' % (type, token)

if __name__ == '__main__':
    print extract_keywords(open('./examples/heapsort_python.txt').read(), 'python')
