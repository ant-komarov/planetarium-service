from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import (
    ShowTheme,
    ShowSession,
    AstronomyShow,
    PlanetariumDome
)
from planetarium.serializers import (
    AstronomyShowDetailSerializer,
    AstronomyShowListSerializer
)


ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")


def sample_astronomy_show(**params):
    defaults = {
        "title": "Test astronomy show",
        "description": "Test astronomy show description",
    }
    defaults.update(params)

    return AstronomyShow.objects.create(**defaults)


def sample_show_session(**params):
    planetarium_dome = PlanetariumDome.objects.create(
        name="Star", rows=15, seats_in_row=25
    )
    astronomy_show = AstronomyShow.objects.create(
        title="Star Show", description="Description"
    )

    defaults = {
        "show_time": "2023-08-02 15:00:00",
        "astronomy_show": astronomy_show,
        "planetarium_dome": planetarium_dome,
    }
    defaults.update(params)

    return ShowSession.objects.create(**defaults)


def detail_url(astronomy_show_id):
    return reverse("planetarium:astronomyshow-detail", args=[astronomy_show_id])


class UnauthenticatedAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ASTRONOMY_SHOW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAstronomyShowApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@ukr.net",
            "pwd12345pwd",
        )
        self.client.force_authenticate(self.user)

    def test_list_astronomy_shows(self):
        sample_astronomy_show()
        sample_astronomy_show()

        res = self.client.get(ASTRONOMY_SHOW_URL)

        astronomy_shows = AstronomyShow.objects.order_by("id")
        serializer = AstronomyShowListSerializer(astronomy_shows, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filter_astronomy_shows_by_show_themes(self):
        show_theme1 = ShowTheme.objects.create(name="Theme 1")
        show_theme2 = ShowTheme.objects.create(name="Theme 2")

        astronomy_show1 = sample_astronomy_show(title="Show 1", description="Description1")
        astronomy_show2 = sample_astronomy_show(title="Show 2", description="Description2")

        astronomy_show1.show_themes.add(show_theme1)
        astronomy_show2.show_themes.add(show_theme2)

        astronomy_show3 = sample_astronomy_show(title="Show without themes")

        res = self.client.get(
            ASTRONOMY_SHOW_URL, {"show_themes": f"{show_theme1.id},{show_theme2.id}"}
        )

        serializer1 = AstronomyShowListSerializer(astronomy_show1)
        serializer2 = AstronomyShowListSerializer(astronomy_show2)
        serializer3 = AstronomyShowListSerializer(astronomy_show3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_astronomy_shows_by_title(self):
        astronomy_show1 = sample_astronomy_show(title="Stars", description="Description1")
        astronomy_show2 = sample_astronomy_show(title="Sun is our star", description="Description2")
        astronomy_show3 = sample_astronomy_show(title="Mars", description="Description3")

        res = self.client.get(ASTRONOMY_SHOW_URL, {"title": "star"})

        serializer1 = AstronomyShowListSerializer(astronomy_show1)
        serializer2 = AstronomyShowListSerializer(astronomy_show2)
        serializer3 = AstronomyShowListSerializer(astronomy_show3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_retrieve_astronomy_show_detail(self):
        astronomy_show = sample_astronomy_show()
        show_theme = ShowTheme.objects.create(name="Star")
        astronomy_show.show_themes.add(show_theme)

        url = detail_url(astronomy_show.id)
        res = self.client.get(url)

        serializer = AstronomyShowDetailSerializer(astronomy_show)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_astronomy_show_forbidden(self):
        payload = {
            "title": "Stars",
            "description": "Description",
        }
        res = self.client.post(ASTRONOMY_SHOW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminMovieApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@ukr.net",
            "pwd12345pwd",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_astronomy_session(self):
        payload = {
            "title": "Stars",
            "description": "Description",
        }
        res = self.client.post(ASTRONOMY_SHOW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        astronomy_show = AstronomyShow.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(astronomy_show, key))

    def test_create_astronomy_shows_with_show_themes(self):
        show_theme1 = ShowTheme.objects.create(name="Planets")
        show_theme2 = ShowTheme.objects.create(name="Stars")
        payload = {
            "title": "Universe",
            "description": "Interesting journey throw the universe",
            "show_themes": [show_theme1.id, show_theme2.id],
        }
        res = self.client.post(ASTRONOMY_SHOW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        astronomy_show = AstronomyShow.objects.get(id=res.data["id"])
        show_themes = astronomy_show.show_themes.all()
        self.assertEqual(show_themes.count(), 2)
        self.assertIn(show_theme1, show_themes)
        self.assertIn(show_theme2, show_themes)
