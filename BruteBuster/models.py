from django.utils import timezone

# default values that can be overriden in settings.py
BB_MAX_FAILURES = int(getattr(settings, 'BB_MAX_FAILURES', 5)) 
BB_BLOCK_INTERVAL = int(getattr(settings, 'BB_BLOCK_INTERVAL', 3)) 


class FailedAttempt (models.Model):
    username = models.CharField('Username', max_length=255)
    IP = models.IPAddressField('IP Address', null=True)
    failures = models.PositiveIntegerField('Failures', default=0)
    timestamp = models.DateTimeField('Last failed attempt', auto_now=True)

    def save(self, *args, **kwargs):
        self.timestamp = timezone.now()
        super(FailedAttempt, self).save(*args, **kwargs)

    def too_many_failures(self):
        """Check if the minumum number of failures needed for a block
        is reached"""
        return self.failures >= BB_MAX_FAILURES

    def recent_failure(self):
        """Checks if the timestamp one the FailedAttempt object is
                recent enough to result in an increase in failures"""
        if settings.USE_TZ:
            now = datetime.utcnow().replace(tzinfo=utc)
        else:
            now = datetime.now()
        return now < self.timestamp + timedelta(minutes=BB_BLOCK_INTERVAL)

    def blocked(self):
        """Shortcut function for checking both too_many_failures and recent_failure """
        return self.too_many_failures() and self.recent_failure()
    blocked.boolean = True

    def __unicode__(self):
        return u'%s (%d failures until %s): ' % (self.username, self.failures, self.timestamp)

    class Meta:
        ordering = ['-timestamp']
        unique_together = (("username", "IP"),)
