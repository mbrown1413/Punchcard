"""
The block between "neststart" and "nestend" template tags define nested
content. Any "nest" template tag within "nestntart" and "nestend" will render
this nested contents recursively. Any arguments to "nest" will be passed to
"neststart" as the variable names used in "neststart".

For example, to nest categories in an unordered list:

    {% neststart categories %}
        <ul>
            {% for category in categories %}
                <li><a href="{{ category.get_absolute_url }}">{{ category.name }}</a>
                    {% if category.children %}
                        {{ nest category.children }}
                    {% endif %}
                </li>
            {% endfor %}
        </ul>
    {% nestend %}

"""

from django import template
register = template.Library()


class NestStartNode(template.Node):

    def __init__(self, nodelist, nest_var_name):
        self.nodelist = nodelist
        self.nest_var_name = nest_var_name

    def render(self, context):
        context.render_context['nest_start_node'] = self
        context['nestlevel'] = context.get('nestlevel', -1) + 1
        ret = self.nodelist.render(context)
        context['nestlevel'] = context.get('nestlevel', -1) - 1
        return ret


class NestEndNode(template.Node):

    def render(self, context):
        if 'nest_start_node' in context.render_context:
            del context.render_context['nest_start_node']
        else:
            raise template.TemplateSyntaxError("nestend tag encountered without neststart tag")
        return ''


class NestNode(template.Node):

    def __init__(self, nest_var):
        self.nest_var = template.Variable(nest_var)

    def render(self, context):
        nest_start_node = context.render_context.get('nest_start_node', None)
        if not nest_start_node:
            raise template.TemplateSyntaxError("nest tag must be between neststart and nestend tags")

        # Record nest var's value, and replace it with nest tag's argument
        var_name = nest_start_node.nest_var_name
        var_was_set = var_name in context
        if var_was_set:
            original_value = context[var_name]
        context[var_name] = self.nest_var.resolve(context)

        ret = nest_start_node.render(context)

        # Reset nest var to original value
        if var_was_set:
            context[var_name] = original_value
        else:
            del context[var_name]

        return ret


@register.tag(name='neststart')
def do_neststart(parser, token):
    nodelist = parser.parse(('nestend',))
    args = token.split_contents()[1:]
    if len(args) != 1:
        raise template.TemplateSyntaxError("neststart tag expects one argument")
    return NestStartNode(nodelist, args[0])

@register.tag(name='nestend')
def do_nestend(parser, token):
    if len(token.split_contents()) != 1:
        raise template.TemplateSyntaxError("nestend tag expects no arguments")
    return NestEndNode()

@register.tag(name='nest')
def do_nest(parser, token):
    args = token.split_contents()[1:]
    if len(args) != 1:
        raise template.TemplateSyntaxError("nest tag expects one argument")
    return NestNode(args[0])
