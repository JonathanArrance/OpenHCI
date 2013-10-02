    
from django.template import Library, , resolve_variable, TemplateSyntaxError, Variable
register = Library()


@register.filter
def node_list():
    return Node.objects.all()

@register.filter(is_safe=True)
def colgroup_list(self, col_group_info):
    colheader ="" 
    for cg in col_group_info:
        colheader += "<colgroup char='.' align='char' span='%i'  ></colgroup>" % (cg[0])
    return colheader
register.tag('colgroup_list', colgroup_list)
    
@register.filter(is_safe=True)    
def colgroup_headers(self, col_group_info):
    colheader ="" 
    colheader += "<tr>"
    for cg in col_group_info:
        colheader += "<th colspan='%i'>%s</th>" % (cg[0], cg[1])
    colheader += "</tr>"
    return colheader
    
register.tag('colgroup_headers', colgroup_headers)
