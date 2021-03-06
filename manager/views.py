from django.contrib.auth import login, logout
from django.db.models import Count, Prefetch, Avg
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from manager.forms import BookForm, CustomAuthenticationForm, CommentForm
from manager.models import Book, Comment, LikeCommentUser
from manager.models import LikeBookUser as RateBookUser


def hello(request, name="filipp", digit=None):
    if digit is not None:
        return HttpResponse(f"digit is {digit}")
    return HttpResponse(f"hello {name}")


class MyPage(View):
    def get(self, request):
        context = {}
        comment_query = Comment.objects.annotate(count_like=Count("users_like")).select_related("author")
        comments = Prefetch("comments", comment_query)
        context['books'] = Book.objects.prefetch_related("authors", comments)
        context['range'] = range(1, 6)
        context['form'] = BookForm()
        return render(request, "index.html", context)


class LoginView(View):
    def get(self, request):
        return render(request, "login.html", {'form': CustomAuthenticationForm()})

    def post(self, request):
        user = CustomAuthenticationForm(data=request.POST)
        if user.is_valid():
            login(request, user.get_user())
        return redirect("the-main-page")


def logout_user(request):
    logout(request)
    return redirect("the-main-page")


class AddLike2Comment(View):
    def get(self, request, id):
        if request.user.is_authenticated:
            LikeCommentUser.objects.create(user=request.user, comment_id=id)
        return redirect("the-main-page")


class AddRate2Book(View):
    def get(self, request, slug, rate, location=None):
        if request.user.is_authenticated:
            book_id = Book.objects.get(slug=slug).id
            RateBookUser.objects.create(user=request.user, book_id=book_id, rate=rate)
        if location is None:
            return redirect("the-main-page")
        return redirect("book-detail", slug=slug)


class BookDetail(View):
    def get(self, request, slug):
        comment_query = Comment.objects.annotate(count_like=Count("users_like")).select_related("author")
        comments = Prefetch("comments", comment_query)
        book = Book.objects.prefetch_related("authors", comments).get(slug=slug)
        return render(request, "book_detail.html", {"book": book, "rate": 2, 'form': CommentForm()})


class AddBook(View):
    def post(self, request):
        if request.user.is_authenticated:
            bf = BookForm(data=request.POST)
            book = bf.save(commit=True)
            book.authors.add(request.user)
            book.save()
        return redirect("the-main-page")

class AddCommentToBook(View):
    def post(self, request, book_id):
        if request.user.is_authenticated:
            cf = CommentForm(request.POST)
            comment = cf.save(commit=False)
            comment.book_id = book_id
            comment.save()
        return redirect('book-detail', slug=Book.objects.get(id=book_id).slug)
