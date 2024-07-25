# podcasts/management/commands/startjobs.py
# Standard Library
import logging

# Django
from django.conf import settings
from django.core.management.base import BaseCommand

# Third Party
import feedparser
from dateutil import parser
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

# Models
from podcasts.models import Episode

logger = logging.getLogger(__name__)

# podcasts/management/commands/startjobs.py

# ...

class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            fetch_realpython_episodes,
            trigger="interval",
            minutes=2,
            id="The Real Python Podcast",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: The Real Python Podcast.")

        scheduler.add_job(
            fetch_talkpython_episodes,
            trigger="interval",
            minutes=2,
            id="Talk Python Feed",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Talk Python Feed.")

        scheduler.add_job(
            fetch_codestory_episodes,
            triggers="interval",
            minutes=2,
            id="Code Story",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Code Story")

        scheduler.add_job(
            fetch_codeswitch_episodes,
            triggers="interval",
            minutes=2,
            id="Code Switch",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job: Code Switch")

        scheduler.add_job(
            fetch_topshelftech_episodes,
            triggers="interval",
            minutes=2,
            id="Top Shelf Tech",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: Delete Old Job Executions.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")

def save_new_episodes(feed):
    """Saves new episodes to the database.

    Checks the episode GUID against the episodes currently stored in the
    database. If not found, then a new `Episode` is added to the database.

    Args:
        feed: requires a feedparser object
    """
    podcast_title = feed.channel.title
    podcast_image = feed.channel.image["href"]

    for item in feed.entries:
        if not Episode.objects.filter(guid=item.guid).exists():
            episode = Episode(
                title=item.title,
                description=item.description,
                pub_date=parser.parse(item.published),
                link=item.link,
                image=podcast_image,
                podcast_name=podcast_title,
                guid=item.guid,
            )
            episode.save()

def fetch_codestory_episodes():
    _feed = feedparser.parse("https://feeds.redcircle.com/ac5e79a4-0405-49a3-af2c-02c37f0b3879")
    save_new_episodes(_feed)

def fetch_realpython_episodes():
    """Fetches new episodes from RSS for The Real Python Podcast."""
    _feed = feedparser.parse("https://realpython.com/podcasts/rpp/feed")
    save_new_episodes(_feed)

def fetch_talkpython_episodes():
    """Fetches new episodes from RSS for the Talk Python to Me Podcast."""
    _feed = feedparser.parse("https://talkpython.fm/episodes/rss")
    save_new_episodes(_feed)

def fetch_codeswitch_episodes():
    _feed = feedparser.parse("https://feeds.npr.org/510312/podcast.xml")
    save_new_episodes(_feed)
    
def delete_old_job_executions(max_age=604_800):
    """Deletes all apscheduler job execution logs older than `max_age`."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_codestory_episodes()
        fetch_realpython_episodes()
        fetch_talkpython_episodes()
        fetch_codeswitch_episodes()
        