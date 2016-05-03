import abc
import datetime
import smappdragon

class SmappCollection(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, data_source_type, **kwargs):
            # non mongo collection
            if 'filepath' in kwargs:
                if data_source_type == 'bson':
                    self.collection = smappdragon.BsonCollection(kwargs['filepath'])
                elif data_source_type == 'json':
                    self.collection = smappdragon.JsonCollection(kwargs['filepath'])
                elif data_source_type == 'csv':
                    self.collection = smappdragon.CsvCollection(kwargs['filepath'])
            # mongo collection
            elif data_source_type == 'mongo':
                self.collection = smappdragon.MongoCollection(
                    kwargs['host'],
                    kwargs['port'],
                    kwargs['user'],
                    kwargs['password'],
                    kwargs['database'],
                    kwargs['collection']
                )
            # some kinda error
            else:
                raise IOError('Could not find your input, it\'s mispelled or doesn\'t exist.')

    def get_tweets_containing(self, term):
        def tweet_contains_term(tweet):
            return term in tweet['text']
        self.collection.set_custom_filter(tweet_contains_term)
        return self

    def count_tweet_terms(self, term):
        def tweet_contains_term(tweet):
            return term in tweet['text']
        return sum(1 for tweet in self.collection.set_custom_filter(tweet_contains_term).get_iterator())

    def get_tweet_texts(self, term):
        self.collection.strip_tweets(['text'])
        return self

    def get_date_range(self, start, end):
        if type(start) is not datetime.date or type(end) is not datetime.date:
            raise ValueError('inputs to date_range must be python datetime.date objects')
        def tweet_is_in_date_range(tweet):
            return tweet['timestamp'] >= start and tweet['timestamp'] < end
        self.collection.set_custom_filter(tweet_is_in_date_range)
        return self

    def tweet_language_is(self, language_code):
        def language_in_tweet(tweet):
            return language_code in tweet['lang']
        return self

    def user_language_is(self, language_code):
        def language_in_tweet(tweet):
            return language_code in tweet['user']['lang']
        return self

    def exclude_retweets(self):
        def tweet_is_not_retweet(tweet):
            return 'retweeted_status' in tweet
        self.collection.set_custom_filter(tweet_is_not_retweet)
        return self

    def tweets_with_user_location(self, place_term):
        def user_has_location(tweet):
            return place_term in tweet['user']['location']
        self.collection.set_custom_filter(user_has_location)
        return self

    def get_geo_enabled(self):
        def geo_enabled_filter(tweet):
            return ("coordinates" in tweet 
                and tweet["coordinates"] is not None 
                and "coordinates" in tweet["coordinates"])
        self.collection.set_custom_filter(geo_enabled_filter)
        return self

    def get_non_geo_enabled(self):
        def non_geo_enabled_filter(tweet):
            return 'coordinates' not in tweet or \
                tweet['coordinates'] is None or \
                'coordinates' not in tweet['coordinates']
        self.collection.set_custom_filter(non_geo_enabled_filter)
        return self

    def limit_number_of_tweets(self, limit):
        self.collection.set_limit(limit)
        return self

    def get_top_hashtags(self, num_top):
        return self.collection.top_entities({'hashtags':num_top})

    def get_top_urls(self, num_top):
        return self.collection.top_entities({'urls':num_top})

    def get_top_mentions(self, num_top):
        return self.collection.top_entities({'user_mentions':num_top})

    def get_top_media(self, num_top):
        return self.collection.top_entities({'media':num_top})

    def get_top_symbols(self, num_top):
        return self.collection.top_entities({'symbols':num_top})
'''
author @yvan
for a lower level set of tools see: https://github.com/SMAPPNYU/smappdragon
'''