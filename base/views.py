from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect, render, reverse

from django.views.generic import View, FormView
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.core.mail import send_mail
import threading

from .forms import MyUserCreationForm, RoomForm, UserForm
from .models import Message, Relationship, Room, Topic, User


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        self.email.send(fail_silently=False)


def loginPage(request):
    
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'El usuario no existe')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido a ChatRoomStudy {request.user.username}')
            return redirect('home')
        else:
            messages.error(request, 'El email o password no existen')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    messages.success(request, 'Cerraste Sesion!')
    return redirect('login')


def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, 'Registro correcto, inicia sesion!')
            #login(request, user)
            return redirect('login')
        else:
            messages.error(request, 'Ocurrió un error durante el registro')

    return render(request, 'base/login_register.html', {'form': form})


@login_required(login_url='login')
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q))[0:3]

    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        messages.success(request, 'Sala creada correctamente')
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('No tienes permitida esta acción!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        messages.success(request, 'Sala Actualizada!')
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('No tienes permisos para esta acción!!')

    if request.method == 'POST':
        room.delete()
        room.topic.delete()
        messages.success(request, 'Sala Eliminada!')
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        messages.success(request, 'Se eliminó el mensaje!')
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Se actualizó el perfil correctamente!')
            return redirect('user-profile', pk=user.id)

    return render(request, 'base/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request, 'base/topics.html', {'topics': topics})


def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages': room_messages})


def passupdate(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Se actualizó tu password, inicia sesion!')
            return redirect('login')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'base/changepass.html', {'form': form})

    
    
def follow(request, pk):
    current_user = request.user
    to_user = User.objects.get(id=pk)
    to_user_id = to_user
    rel = Relationship(from_user=current_user, to_user=to_user_id)
    rel.save()
    messages.success(request, f'Comenzaste a seguir a {to_user.username}')
    return redirect('home')

def unfollow(request, pk):
    current_user = request.user
    to_user = User.objects.get(id=pk)
    to_user_id = to_user.id
    rel = Relationship.objects.get(from_user=current_user.id, to_user=to_user_id)
    rel.delete()
    messages.success(request, f'Haz dejado de seguir a {to_user.username}')
    return redirect('home')


class PassView(View):
    
    def get(self, request):
        return render(request, 'base/resetpassword.html')
    
    def post(self, request):
        email = request.POST['email']
        context = {'values': request.POST}
        data = User.objects.filter(email=email)
        if not data.exists():
            messages.error(request, 'Email invalido')
            return render(request, 'base/resetpassword.html', context)
        
        current_site = get_current_site(request)
        user = User.objects.filter(email=email)
        if user.exists():
            email_contents = {
                'user': user[0],
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                'token': PasswordResetTokenGenerator().make_token(user[0]),
            } 
            link = reverse('change-passw', kwargs = {
                'uidb64': email_contents['uid'], 'token': email_contents['token']
            })
            email_subject = 'Reset Password'
            reset_url = 'http://'+current_site.domain+link
            email = EmailMessage(
                email_subject,
                'Hola solicitaste restablecer tu contraseña, da click en el enlace y sigue los pasos \n'+reset_url,
                'noreply@marvel.com',
                [email],
            )
            EmailThread(email).start()
            messages.success(request, 'Te enviamos un mail, revisa tu casilla de correo')
        return render(request, 'base/resetpassword.html')


class ChangePasswordView(FormView):
    
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        return render(request, 'base/changepwd.html', context)
    
    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token
        }
        password = request.POST['password']
        password2 = request.POST['password2']
        
        if password != password2:
            return render(request, 'base/changepwd.html', context)
        if len(password) < 6:
            return render(request, 'base/changepwd.html', context)
        
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
        user.set_password(password)
        user.save()
        
        messages.success(request, 'Se restableció  tu contraseña!')
        
        return redirect('login')
    
class VerificationView(View):
    def get(self, request, uidb64, token):
        return redirect('login')