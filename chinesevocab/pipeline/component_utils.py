import pymongo


# the problem that this is supposed to solve is
# that  topic can come either from the command line and
# magically be assigned to the class, or it can be defined
# in the settings
from scrapy.exceptions import CloseSpider


def set_topic(cls):
	topic = cls.settings.get("TOPIC", None)
	if topic:
		setattr(cls, 'topic', topic)
	else:
		topic = getattr(cls, 'topic', None)
	if not topic:
		topic = "genome"
		setattr(cls, 'topic', topic)
	return topic


def topic_translation(cls):
	topic = getattr(cls, 'topic', None)
	# we should have the translation at this point
	client     = pymongo.MongoClient(cls.settings['MONGODB_URI'])
	db         = client[cls.settings['MONGODB_DB']]
	collection = cls.settings['TRANSLATION_COLLECTION']
	# the second argument is projection, it specifies which arguments to return (1=return, 0=do not)
	ret = db[collection].find_one({'english': {'$eq': topic.replace("_", " ")}}, {'chinese': 1})
	client.close()
	if not ret or 'chinese' not in ret or not ret['chinese']:
		raise CloseSpider(f"Chinese translation for the topic '{topic}' not found in the local DB")
	return ret['chinese']


