from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.db import connection
from django.utils.html import format_html

from .models import Choice, Question
from django.contrib.auth.models import User


def error_view(request):
    raise Exception("Simulated error")
    # Problem: This view simulates an error, which might give an attacker sensitive information about the application.
    # Fix: Remove this view in a production environment or handle errors properly by, for example, showing a generic error page.


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = User.objects.filter(username=username, password=password).first()
        # Problem: Storing password as text, enabling broken authentication attacks.
        # Fix: Use Django's built-in authentication system which handles password hashing automatically.

        if user:
            request.session['user_id'] = user.id
            return redirect('polls:index')
        else:
            return render(request, 'polls/login.html', {'error': 'Invalid username or password'})
    
    return render(request, 'polls/login.html')


def xss_vulnerable_view(request):
    user_input = request.GET.get('user_input', '')
    # Problem: User input is allowed directly into the HTML page, enabling XSS attacks.
    # Fix: Prevent XSS attacks by using Django's escape function to prevent HTML code execution.
    return HttpResponse(format_html('<html><body>{}<br><form method="get"><input type="text" name="user_input"><input type="submit" value="Submit"></form></body></html>', user_input))


def vulnerable_view(request):
    param = request.GET.get('param')
    if param:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM polls_question WHERE question_text LIKE '%%{param}%%'")
            # A fix for the problem is to pass the parameters in a separate list after the query:
            # cursor.execute("SELECT * FROM polls_question WHERE question_text LIKE %s", [f"%{param}%"])
            result = cursor.fetchall()
        return HttpResponse(result)
    return HttpResponse("Please provide a parameter.")


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        # Problem: Reveals unpublished questions to all users.
        # Fix: Uncomment the following line to only show published questions.
        # return Question.objects.filter(pub_date__lte=timezone.now())
        return Question.objects.all()


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))
    

def get_queryset(self):
    """
    Return the last five published questions (not including those set to be
    published in the future).
    """
    return Question.objects.filter(pub_date__lte=timezone.now()).order_by("-pub_date")[
        :5
    ]