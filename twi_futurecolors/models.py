from django.db import models
from django.db.models.signals import pre_save, pre_init
from django.dispatch.dispatcher import receiver
import twitter


class Tweet(models.Model):
    tweet = models.TextField()
    parent = models.ForeignKey('self', blank=True, null=True, related_name="child_tweet_set")
    retweet = models.BooleanField(default=False)
    created_at = models.DateTimeField(blank=True, null=True)
    user = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return self.tweet

    class Meta:
        pass

class TwMention(models.Model):
    user = models.CharField(max_length=100)
    tweets = models.ManyToManyField('Tweet', blank=True)

    def check_updates(self):
        user_last_tweets = twitter.Api().GetSearch(term=u'%%40%s' % self.user, lang='ru',query_users=True)
        #new_tweets =[]
        for last_tweet in user_last_tweets:
            tweet, created = Tweet.objects.get_or_create(
                id=last_tweet.id,
                #tweet=last_tweet.text,
                #parent=last_tweet.in_reply_to_status_id if last_tweet.in_reply_to_status_id else None,
                #created_at=last_tweet.created_at,
                #user=last_tweet.user,
                )
            if created:
                #new_tweets.append(tweet)
                self.tweets.add(tweet)
        self.save()

    def __unicode__(self):
        return self.user

    class Meta:
        pass


#Signals
@receiver(pre_save, sender=Tweet)
def tweet_pre_save(sender,instance,**kwargs):
    new_tweet = twitter.Api().GetStatus(instance.id)
    instance.tweet = new_tweet.text
    if new_tweet.in_reply_to_status_id:
        tweet, created = Tweet.objects.get_or_create(
            id=new_tweet.in_reply_to_status_id,
            )
        instance.parent = tweet



