from collections import defaultdict

__author__ = 'akamoroz'
from django import template

# http://softwaremaniacs.org/blog/2009/09/21/trees-in-django-templates/

register = template.Library()

class TreeNode(template.Node):
    def __init__(self, tree, node_list):
        self.tree = tree
        self.node_list = node_list

    def render(self, context):
        tree = self.tree.resolve(context)

        def pairs(items):
            def dirty(items):
                items = iter(items)
                head = None
                try:
                    while True:
                        item = items.next()
                        if isinstance(item, (list, tuple)):
                            yield head, item
                            head = None
                        else:
                            yield head, None
                            head = item
                except StopIteration:
                    yield head, None
            return ((h, t) for h, t in dirty(items) if h or t)

        def render_item(item, sub_items, level):
            return ''.join([
                '<li>',
                item and self.node_list.render(template.Context({'item': item, 'level': level})) or '',
                sub_items and '<ul>%s</ul>' % ''.join(render_items(sub_items, level + 1)) or '',
                '</li>'
            ])

        def render_items(items, level):
            return ''.join(render_item(h, t, level) for h, t in pairs(items))

        return render_items(tree, 0)

@register.tag
def tree(parser, token):
    bits = token.split_contents()
    if len(bits) != 2:
        raise template.TemplateSyntaxError('"%s" takes one argument: tree-structured list' % bits[0])
    node_list = parser.parse('end' + bits[0])
    parser.delete_first_token()
    return TreeNode(parser.compile_filter(bits[1]), node_list)


@register.filter
def astree(items, attribute):

    parent_map = defaultdict(list)
    for item in items:
        parent_map[getattr(item, attribute)].append(item)

    def tree_level(parent):
        for item in parent_map[parent]:
            yield item
            sub_items = list(tree_level(item))
            if sub_items:
                yield sub_items

    return list(tree_level(None))