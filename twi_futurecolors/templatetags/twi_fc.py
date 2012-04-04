__author__ = 'akamoroz'
import logging
from urllib2 import URLError

from django import template
from django.core.cache import cache
from templatetag_sugar.parser import Optional, Constant, Name, Variable
from templatetag_sugar.register import tag
import ttp
import twitter


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


def get_cache_key(*args):
    return 'get_tweets_%s' % ('_'.join([str(arg) for arg in args if arg]))

@tag(register, [Constant("for"), Variable(), Constant("as"), Name(),])
def get_mentions(context, username, asvar):
    cache_key = get_cache_key(username)
    try:
        user_last_tweets = twitter.Api().GetSearch(term=u'%%40%s' % username, lang='ru',query_users=True)
    except (twitter.TwitterError, URLError), e:
        logging.getLogger(__name__).error(str(e))
        context[asvar] = cache.get(cache_key, [])
        return ""


    tweets = []

    def check_tweet_in_tree(tweet, tree):
        for tw in tree:
            if isinstance(tw,list):
                check_tweet_in_tree(tweet, tw)
            elif tweet.id == tw.id:
                return True
            else:
                return False

    for tweet in user_last_tweets:
        if tweet.in_reply_to_status_id:
            tree = None
            while tweet.in_reply_to_status_id:
                tree = [ tweet, tree ] if tree else [tweet]
                tweet = twitter.Api().GetStatus(tweet.in_reply_to_status_id)

            used = False

            for use_tweet in tweets:
                if not isinstance(use_tweet,list) and tweet.id == use_tweet.id:
                    used = True

            if not used:
                tweets.extend([tweet,tree])
        elif not tweet.retweeted_status:
            tweets.append(tweet)

    context[asvar] = tweets
    cache.set(cache_key, tweets)
    return ''
