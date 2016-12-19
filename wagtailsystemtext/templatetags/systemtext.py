from django import template
from django.conf import settings
from django.template import Library, Node, TemplateSyntaxError, Variable
from django.template.base import TOKEN_TEXT, TOKEN_VAR, render_value_in_context
from django.utils import six, translation
from django.utils.safestring import SafeData, mark_safe

from wagtailsystemtext.utils import gettext
from wagtailsystemtext.models import SystemString


register = template.Library()


class TranslateNode(Node):
    def __init__(self, filter_expression, group, asvar=None,
                 message_context=None):
        self.noop = True
        self.asvar = asvar
        self.group = group
        self.message_context = message_context
        self.filter_expression = filter_expression
        if isinstance(self.filter_expression.var, six.string_types):
            self.filter_expression.var = Variable("'%s'" %
                                                  self.filter_expression.var)

    def render(self, context):
        self.filter_expression.var.translate = not self.noop
        if self.message_context:
            self.filter_expression.var.message_context = (
                self.message_context.resolve(context))
        output = self.filter_expression.resolve(context)

        value = render_value_in_context(output, context)

        # Restore percent signs. Percent signs in template text are doubled
        # so they are not interpreted as string format flags.
        is_safe = isinstance(value, SafeData)
        value = value.replace('%%', '%')
        value = gettext(value, group=self.group)
        value = mark_safe(value) if is_safe else value
        if self.asvar:
            context[self.asvar] = value
            return ''
        else:
            return value


@register.tag("st_trans")
def do_trans(parser, token):
    bits = token.split_contents()
    message_string = parser.compile_filter(bits[1])
    remaining = bits[2:]

    asvar = None
    message_context = None
    seen = set()
    group = SystemString.DEFAULT_GROUP

    while remaining:
        option = remaining.pop(0)

        if option == 'group':
            value = remaining.pop(0)[1:-1]
            group = value

    return TranslateNode(message_string, group, asvar, message_context)