from django.test import TestCase

from wagtailsystemtext.utils import (
    gettext, set_site, fill_cache, preload, _cleanup,
)
from tests.factories import SiteFactory, PageFactory, SystemStringFactory


class ReplaceTestCase(TestCase):
    def tearDown(self):
        _cleanup()

    def test_replace(self):
        site = SiteFactory.create(
            root_page=PageFactory.create(title='mypage', path='00010002')
        )

        SystemStringFactory.create(
            identifier='headline',
            string='Headline!',
            site=site,
        )

        set_site(site)
        fill_cache(site)
        preload(site)

        self.assertEquals(gettext('headline'), 'Headline!')

    def test_group_replace(self):
        site = SiteFactory.create(
            root_page=PageFactory.create(title='mypage', path='00010002')
        )

        SystemStringFactory.create(
            identifier='sub_headline',
            string='My subheadline',
            group='sub',
            site=site,
        )

        set_site(site)
        fill_cache(site)
        preload(site)

        self.assertEquals(gettext('sub_headline', 'sub'), 'My subheadline')

    def test_two_sites(self):
        site = SiteFactory.create(
            root_page=PageFactory.create(title='mypage', path='00010002')
        )

        site_b = SiteFactory.create(
            root_page=PageFactory.create(title='mypage', path='00010003')
        )

        SystemStringFactory.create(
            identifier='headline',
            string='headline a',
            site=site,
        )

        SystemStringFactory.create(
            identifier='headline',
            string='headline b',
            site=site_b,
        )

        fill_cache(site)
        fill_cache(site_b)

        preload(site)
        preload(site_b)

        set_site(site)
        self.assertEquals(gettext('headline'), 'headline a')

        set_site(site_b)
        self.assertEquals(gettext('headline'), 'headline b')
