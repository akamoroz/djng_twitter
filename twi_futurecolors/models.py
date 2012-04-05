import logging
import re
from django.db import models
from django.db.models.signals import pre_save, pre_init
from django.dispatch.dispatcher import receiver
import twitter


class Tweet(models.Model):
    #TODO: add other fields (created_at, retweet, bla-bla-bla)
    tweet = models.TextField()
    parent = models.ForeignKey('self', blank=True, null=True, related_name="child_tweet_set")
    retweet = models.BooleanField(default=False)
    created_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('TwUser', related_name='user_set')
    mentions = models.ManyToManyField('TwUser',related_name='mention_set')

    def __unicode__(self):
        return self.tweet

    class Meta:
        pass

class TwUser(models.Model):
    user = models.CharField(max_length=100)
    #tweets = models.ManyToManyField('Tweet', blank=True)

    def check_updates(self):
        user_last_tweets = twitter.Api().GetSearch(term=u'%%40%s' % self.user, lang='ru',query_users=True)
        #new_tweets =[]
        for last_tweet in user_last_tweets:
            tweet, created = Tweet.objects.get_or_create(
                    id=last_tweet.id,
                )
            tweet.mentions.add(self)

    def __unicode__(self):
        return self.user

    class Meta:
        pass


#Signals
@receiver(pre_save, sender=Tweet)
def tweet_pre_save(sender,instance,**kwargs):
    #TODO: celery?
    new_tweet = twitter.Api().GetStatus(instance.id)
    instance.tweet = new_tweet.text
    instance.user,created = TwUser.objects.get_or_create(user=new_tweet.user.screen_name)
    mentions = re.match(r"@(\w+) ", instance.tweet)
    if mentions:
        for mention in mentions.groups():
            user,created = TwUser.objects.get_or_create(user=mention)
            instance.mentions.add(user)
    if new_tweet.in_reply_to_status_id:
        tweet, created = Tweet.objects.get_or_create(
            id=new_tweet.in_reply_to_status_id,
            )
        #TODO: rewrite_code
        for ment in instance.mentions.all():
            tweet.mentions.add(ment)
        tweet.mentions.add(instance.user)
        #tweet.mentions=[instance.mentions]+ [instance.user]
        instance.parent = tweet




