import tempfile
import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from planetarium.models import ShowTheme, ShowSession, AstronomyShow, Reservation, PlanetariumDome, Ticket
from planetarium.serializers import AstronomyShowSerializer, AstronomyShowDetailSerializer

ASTRONOMY_SHOW_URL = reverse("planetarium:astronomyshow-list")
SHOW_SESSION_URL = reverse("planetarium:showsession-list")


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


# class AuthenticatedMovieApiTests(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = get_user_model().objects.create_user(
#             "test@test.com",
#             "testpass",
#         )
#         self.client.force_authenticate(self.user)
#
#     def test_list_movies(self):
#         sample_movie()
#         sample_movie()
#
#         res = self.client.get(MOVIE_URL)
#
#         movies = Movie.objects.order_by("id")
#         serializer = MovieListSerializer(movies, many=True)
#
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, serializer.data)
#
#     def test_filter_movies_by_genres(self):
#         genre1 = Genre.objects.create(name="Genre 1")
#         genre2 = Genre.objects.create(name="Genre 2")
#
#         movie1 = sample_movie(title="Movie 1")
#         movie2 = sample_movie(title="Movie 2")
#
#         movie1.genres.add(genre1)
#         movie2.genres.add(genre2)
#
#         movie3 = sample_movie(title="Movie without genres")
#
#         res = self.client.get(
#             MOVIE_URL, {"genres": f"{genre1.id},{genre2.id}"}
#         )
#
#         serializer1 = MovieListSerializer(movie1)
#         serializer2 = MovieListSerializer(movie2)
#         serializer3 = MovieListSerializer(movie3)
#
#         self.assertIn(serializer1.data, res.data)
#         self.assertIn(serializer2.data, res.data)
#         self.assertNotIn(serializer3.data, res.data)
#
#     def test_filter_movies_by_actors(self):
#         actor1 = Actor.objects.create(first_name="Actor 1", last_name="Last 1")
#         actor2 = Actor.objects.create(first_name="Actor 2", last_name="Last 2")
#
#         movie1 = sample_movie(title="Movie 1")
#         movie2 = sample_movie(title="Movie 2")
#
#         movie1.actors.add(actor1)
#         movie2.actors.add(actor2)
#
#         movie3 = sample_movie(title="Movie without actors")
#
#         res = self.client.get(
#             MOVIE_URL, {"actors": f"{actor1.id},{actor2.id}"}
#         )
#
#         serializer1 = MovieListSerializer(movie1)
#         serializer2 = MovieListSerializer(movie2)
#         serializer3 = MovieListSerializer(movie3)
#
#         self.assertIn(serializer1.data, res.data)
#         self.assertIn(serializer2.data, res.data)
#         self.assertNotIn(serializer3.data, res.data)
#
#     def test_filter_movies_by_title(self):
#         movie1 = sample_movie(title="Movie")
#         movie2 = sample_movie(title="Another Movie")
#         movie3 = sample_movie(title="No match")
#
#         res = self.client.get(MOVIE_URL, {"title": "movie"})
#
#         serializer1 = MovieListSerializer(movie1)
#         serializer2 = MovieListSerializer(movie2)
#         serializer3 = MovieListSerializer(movie3)
#
#         self.assertIn(serializer1.data, res.data)
#         self.assertIn(serializer2.data, res.data)
#         self.assertNotIn(serializer3.data, res.data)
#
#     def test_retrieve_movie_detail(self):
#         movie = sample_movie()
#         movie.genres.add(Genre.objects.create(name="Genre"))
#         movie.actors.add(
#             Actor.objects.create(first_name="Actor", last_name="Last")
#         )
#
#         url = detail_url(movie.id)
#         res = self.client.get(url)
#
#         serializer = MovieDetailSerializer(movie)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, serializer.data)
#
#     def test_create_movie_forbidden(self):
#         payload = {
#             "title": "Movie",
#             "description": "Description",
#             "duration": 90,
#         }
#         res = self.client.post(MOVIE_URL, payload)
#
#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#
#
# class AdminMovieApiTests(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = get_user_model().objects.create_user(
#             "admin@admin.com", "testpass", is_staff=True
#         )
#         self.client.force_authenticate(self.user)
#
#     def test_create_movie(self):
#         payload = {
#             "title": "Movie",
#             "description": "Description",
#             "duration": 90,
#         }
#         res = self.client.post(MOVIE_URL, payload)
#
#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         movie = Movie.objects.get(id=res.data["id"])
#         for key in payload.keys():
#             self.assertEqual(payload[key], getattr(movie, key))
#
#     def test_create_movie_with_genres(self):
#         genre1 = Genre.objects.create(name="Action")
#         genre2 = Genre.objects.create(name="Adventure")
#         payload = {
#             "title": "Spider Man",
#             "genres": [genre1.id, genre2.id],
#             "description": "With Spider-Man's identity now revealed, Peter asks Doctor Strange for help.",
#             "duration": 148,
#         }
#         res = self.client.post(MOVIE_URL, payload)
#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#
#         movie = Movie.objects.get(id=res.data["id"])
#         genres = movie.genres.all()
#         self.assertEqual(genres.count(), 2)
#         self.assertIn(genre1, genres)
#         self.assertIn(genre2, genres)
#
#     def test_create_movie_with_actors(self):
#         actor1 = Actor.objects.create(first_name="Tom", last_name="Holland")
#         actor2 = Actor.objects.create(first_name="Tobey", last_name="Maguire")
#         payload = {
#             "title": "Spider Man",
#             "actors": [actor1.id, actor2.id],
#             "description": "With Spider-Man's identity now revealed, Peter asks Doctor Strange for help.",
#             "duration": 148,
#         }
#         res = self.client.post(MOVIE_URL, payload)
#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#
#         movie = Movie.objects.get(id=res.data["id"])
#         actors = movie.actors.all()
#         self.assertEqual(actors.count(), 2)
#         self.assertIn(actor1, actors)
#         self.assertIn(actor2, actors)
#
