import re 

from django import template
register = template.Library()

@register.filter
def replace (string, args):
    result = re.findall(args, string)

    return ', '.join(result)

@register.filter
def truncatetw (string):
    new_string = string
    string_split = string.split('\n')
    
    if len(string_split) > 5:
        new_string = '\n'.join(string_split[:5]) + '......'
    elif len(string) > 200:
        new_string = string[:200] + '......'

    return new_string

# @register.filter
# def _uniq(seq):
#     seen = dict()
#     dep = seq[::2]
#     limit = seq[1::2]
#     for index, i in enumerate(dep):
#         if not i in seen:
#             seen[i] = limit[index]
#     return seen