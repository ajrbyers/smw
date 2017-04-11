from django.core.cache import cache
from django.db.models import Model
from hashlib import sha1
from random import randint
import math


def cache_result(seconds=3600, expiry_variance=0.2, override_key=None):
    def doCache(f):
        def x(*args, **kwargs):

            # Don't bother if seconds is set to 0
            if not seconds:
                return f(*args, **kwargs)

            # Generate the key from the function name and given arguments
            key = sha1(override_key or u"//".join((
                unicode(f),
                u"//".join(objectToString(a) for a in args),
                u"//".join(unicode(a.updated) for a in args if hasattr(a, "updated")),
                u"//".join(unicode(k) + objectToString(v) for k, v in kwargs.iteritems()),
                u"//".join(unicode(v.updated) for k, v in kwargs.iteritems() if hasattr(v, "updated")),
            )).encode("utf-8")).hexdigest()
            flag = key + "flag"

            # If a cached result exists, return it.
            skip_cache_read = kwargs.pop("skip_cache_read", False)
            result = cache.get(key) if not skip_cache_read and cache.get(flag) else None
            if result:
                return result[0]

            # If no result exists, generate one and return it. While generating a result,
            # postpone further regenerations to prevent cache stampeding.
            cache.set(flag, True, int(math.log(seconds)))
            result = f(*args, **kwargs)
            cache.set(flag, True, seconds + randint(-int(seconds * expiry_variance), int(seconds * expiry_variance)))
            cache.set(key, (result, ), max(seconds * 10, 86400 * 7))
            return result
        return x

    def objectToString(obj):
        if isinstance(obj, Model):
            object_class = type(obj)
            return ".".join((
                object_class.__module__,
                object_class.__name__,
                unicode(obj.pk),
            ))
        else:
            return unicode(obj)
    return doCache
