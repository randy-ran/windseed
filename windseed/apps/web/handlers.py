import peewee

import tornado.web
import tornado.gen
import tornado.escape

from windseed.settings import env
from windseed.base import handler
from windseed.apps.web.models import Record


class Handler(handler.Handler):
    def write_error(self, status_code, **kwargs):
        self.render('web/error.html', status_code=status_code)


class ErrorHandler(tornado.web.ErrorHandler, Handler):
    pass


class RecordsHandler(Handler):
    """
    Records: /
    """
    def get_page_context(self):
        """
        Return current page context
        """
        try:
            page = int(self.get_argument('page', 1))
        except ValueError:
            page = 1

        records9 = Record\
            .select(
                Record,
                peewee.SQL('1 AS search_order'))\
            .where(
                Record.active == True,
                Record.name.contains('record 9'))
        records = Record\
            .select(
                Record,
                peewee.SQL('2 AS search_order'))\
            .where(Record.active == True)

        try:
            count = records.count()
        except peewee.IntegrityError:
            count = 0

        per_page = env.RECORDS_PER_PAGE
        page_count = int(count/per_page) + int(bool(count % per_page))

        prev_page, page, next_page = self.paging(page, page_count)

        try:
            records_ = (
                records9 | (records-records9))\
                .order_by(peewee.SQL('search_order, name'))\
                .paginate(page, paginate_by=per_page)

        except peewee.IntegrityError:
            records_ = []

        return dict(records=records_,
                    page_count=page_count,
                    prev_page=prev_page,
                    page=page,
                    next_page=next_page)

    @tornado.web.addslash
    @tornado.gen.coroutine
    def get(self):
        """
        Render records
        """
        self.render(
            'web/records.html',
            **self.get_page_context())


class SitemapHandler(Handler):
    """
    Sitemap: /sitemap/
    """
    def get_page_context(self):
        """
        Return current page context
        """
        try:
            records = Record\
                .select()\
                .where(Record.active == True)\
                .paginate(1, paginate_by=env.SITEMAP_PER_PAGE)
        except peewee.IntegrityError:
            records = []

        return dict(records=records)

    @tornado.gen.coroutine
    def get(self):
        """
        Render sitemap
        """
        self.set_header('Content-Type', 'text/xml')
        self.render(
            'web/sitemap.xml',
            **self.get_page_context())
