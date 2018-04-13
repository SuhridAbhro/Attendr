from django.shortcuts import render, render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from .forms import RegistrationForm, FilterAttendance, VerifyForm
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Student_Details, Student_Attendance, Token
from .serializers import StudentDetailsSerializer, TokenSerializer, StudentAttendanceSerializer
from rest_framework import status
from django.contrib.auth import get_user_model
from time import gmtime, strftime
import requests
from django.utils.html import escape
from datetime import date
from io import BytesIO
from .pdf_utils import PdfPrint

import itertools
import functools


from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
#from Project.settings import DEFAULT_FROM_EMAIL
from django.views.generic import *
from .forms import PasswordResetRequestForm,SetPasswordForm,ContactUsForm



@login_required(login_url='/login/')
def successful_login(request):
    ntime = strftime("%H", gmtime())
    ##    if int(ntime) > 8:
    ##        d=Student_Attendance.objects.all()
    ##        f=Student_Details.objects.filter(~Q(st_id__in=d.values_list('st_id',flat=True)))
    ##        for data in f:
    ##            ntime=strftime("%d/%m/%y", gmtime())
    ##            r=requests.post('https://attendanceproject.herokuapp.com/dashboard/apia/',data={'st_id':data.st_id,'date':ntime,'status':'0'})
    # http_date=''
    print(request.POST)

    form = VerifyForm(request.POST or None)
    http_data = request.POST.get('data')
    print(http_data)
    if http_data:
        http_status, http_sid, http_vdate = http_data.split(",")
    else:
        http_sid = None
        http_status = None
        http_vdate = None
    ##    http_sid=request.POST.get('id')
    ##    http_status=request.POST.get('status')
    ##    http_vdate = request.POST.get('date')
    print(http_sid)
    print(http_status)
    print(http_vdate)
    if http_sid and http_status and http_vdate:
        r = requests.post('http://127.0.0.1:8000/home/apia/',
                          data={'st_id': http_sid, 'date': http_vdate, 'status': http_status})
        print(r.content)

    form = FilterAttendance(request.POST or None)
    http_uid = request.session['username']
    user = get_user_model()
    uid = user.objects.get(sid=http_uid)
    staff_value = uid.is_staff
    request.session['staff_value']=staff_value
    print(staff_value)
    http_date = request.POST.get('date_id')
    http_class = request.POST.get('class_id')
    http_sec = request.POST.get('sec_id')

    if staff_value:
        date_item = Student_Attendance.objects.values('date').distinct()
        class_item = Student_Details.objects.values('s_class').distinct()
        section_item = Student_Details.objects.values('sec').distinct()
    else:
        date_item = Student_Attendance.objects.values('date').distinct()
        class_item = Student_Details.objects.filter(st_id=user.objects.get(sid=http_uid)).values('s_class')
        section_item = Student_Details.objects.filter(st_id=user.objects.get(sid=http_uid)).values('sec')

    if http_date and http_class and http_sec and staff_value:
        stu_count = Student_Details.objects.filter(s_class=http_class, sec=http_sec).count()
        stu_det = Student_Details.objects.filter(s_class=http_class, sec=http_sec)
        stu_att = Student_Attendance.objects.filter(date=http_date, st_id__in=stu_det.values_list('st_id', flat=True))
        att_count = Student_Attendance.objects.filter(date=http_date,
                                                      st_id__in=stu_det.values_list('st_id', flat=True)).count()
    elif http_date and http_class and http_sec and not staff_value:
        stu_count = Student_Details.objects.filter(s_class=http_class, sec=http_sec).count()
        stu_det = Student_Details.objects.filter(st_id=uid, s_class=http_class, sec=http_sec)
        stu_att = Student_Attendance.objects.filter(date=http_date, st_id__in=stu_det.values_list('st_id', flat=True))
        att_count = Student_Attendance.objects.filter(date=http_date,
                                                      st_id__in=stu_det.values_list('st_id', flat=True)).count()
    else:
        stu_count = 0
        stu_att = ''
        stu_det = ''
        att_count = 0

    return render(request, 'dashboard.html',
                  {"counter": functools.partial(next, itertools.count()), 'stu_count': stu_count, 'stu_att': stu_att,
                   'stu_det': stu_det, 'date_item': date_item, 'class_item': class_item, 'section_item': section_item,
                   'att_count': att_count, 'staff_value': staff_value, })


def site_history(request):
    class_item = Student_Details.objects.values('s_class').distinct()
    section_item = Student_Details.objects.values('sec').distinct()
    staff_value=request.session['staff_value']
    return render(request,'history.html',{'class_item':class_item,'section_item':section_item,'staff_value':staff_value})


def pdf_test(request):
    print(request.POST)
    http_date=request.POST.get('date')
    http_class = request.POST.get('class_id')
    http_sec = request.POST.get('sec_id')
    print(http_class)
    print(http_sec)
    print(http_date)
    if request.POST.get('stu_id'):
        http_stid=request.POST.get('stu_id')
    else:
        http_stid = request.session['username']
    d,m,y=http_date.split("/")
    user = get_user_model()
    uid = user.objects.filter(sid=http_stid)
    if http_class and http_sec:
        details = Student_Details.objects.filter(s_class=http_class, sec=http_sec)
        attendance = Student_Attendance.objects.filter(date__contains=('/'+m+'/'), st_id__in=details.values_list('st_id', flat=True))
        pie=0
    else:
        attendance = Student_Attendance.objects.filter(st_id=uid[0],date__contains=('/'+m+'/'))
        details = Student_Details.objects.filter(st_id=uid[0])
        pie=1
    print(attendance)
    print(details)
    response = HttpResponse(content_type='application/pdf')
    today = date.today()
    filename = 'pdf_attendance' + today.strftime('%Y-%m-%d')
    response['Content-Disposition'] = \
        'attachement; filename={0}.pdf'.format(filename)
    buffer = BytesIO()
    report = PdfPrint(buffer, 'A4')
    pdf = report.report(attendance, details,http_date,pie, 'Student Attendance data')
    response.write(pdf)
    return response



class ContactUsView(FormView):
        template_name = "contact_form/contact_form.html"    #code for template is given below the view's code
        success_url = '/home/contact/'
        form_class = ContactUsForm
        def post(self, request, *args, **kwargs):
            '''
            A normal post request which takes input from field "name" and "subject" (in ContactUsForm). 
            '''
            form = self.form_class(request.POST)
            if form.is_valid():
                name= form.cleaned_data["name"]
                subject=form.cleaned_data["subject"]
            user = get_user_model()
            http_stid = request.session['username']
            uid = user.objects.filter(sid=http_stid)
            stu_det=Student_Details.objects.filter(st_id=uid[0].sid)
            if stu_det[0].email:
                c = {
                    'email': 'attendrteam@gmail.com',
                    'name': name,
                    'content':subject,
                    'user':uid[0],
                    'u_mail':stu_det[0].email
                    }
                subject_template_name='contact_form/contact_form_subject.txt' 
                # copied from django/contrib/admin/templates/registration/password_reset_subject.txt to templates directory
                email_template_name='contact_form/contact_form_email.html'    
                # copied from django/contrib/admin/templates/registration/password_reset_email.html to templates directory
                subject = loader.render_to_string(subject_template_name, c)
                # Email subject *must not* contain newlines
                subject = ''.join(subject.splitlines())
                email = loader.render_to_string(email_template_name, c)
                send_mail(subject, email, stu_det[0].email , ['attendrteam@gmail.com'], fail_silently=False)
                result = self.form_valid(form)
                messages.success(request, 'An email has been sent to the administration. We will get back to you soon.')
                return result
                result = self.form_invalid(form)
                messages.error(request, 'No email id associated with this user')
                return result




class ResetPasswordRequestView(FormView):
        template_name = "account/test_template.html"    #code for template is given below the view's code
        success_url = '/login/'
        form_class = PasswordResetRequestForm

        @staticmethod
        def validate_email_address(email):
            '''
            This method here validates the if the input is an email address or not. Its return type is boolean, True if the input is a email address or False if its not.
            '''
            try:
                validate_email(email)
                return True
            except ValidationError:
                return False

        def post(self, request, *args, **kwargs):
            '''
            A normal post request which takes input from field "email_or_username" (in ResetPasswordRequestForm). 
            '''
            form = self.form_class(request.POST)
            if form.is_valid():
                data= form.cleaned_data["email_or_username"]
            if self.validate_email_address(data) is True:                 #uses the method written above
                '''
                If the input is an valid email address, then the following code will lookup for users associated with that email address. If found then an email will be sent to the address, else an error message will be printed on the screen.
                '''
                User = get_user_model()
                stu_det=Student_Details.objects.filter(email=data)
                if stu_det:
                    associated_users=User.objects.filter(sid=stu_det[0])
                else:
                    associated_users=None
                if associated_users:
                    c = {
                        'email': stu_det[0].email,
                        'domain': request.META['HTTP_HOST'],
                        'site_name': 'Attendr',
                        'uid': urlsafe_base64_encode(force_bytes(associated_users[0].pk)).decode(),
                        'user': associated_users[0],
                        'token': default_token_generator.make_token(associated_users[0]),
                        'protocol': 'http',
                        }
                    subject_template_name='registration/password_reset_subject.txt' 
                    # copied from django/contrib/admin/templates/registration/password_reset_subject.txt to templates directory
                    email_template_name='registration/password_reset_email.html'    
                    # copied from django/contrib/admin/templates/registration/password_reset_email.html to templates directory
                    subject = loader.render_to_string(subject_template_name, c)
                    # Email subject *must not* contain newlines
                    subject = ''.join(subject.splitlines())
                    email = loader.render_to_string(email_template_name, c)
                    send_mail(subject, email, DEFAULT_FROM_EMAIL , [stu_det[0].email], fail_silently=False)
                    result = self.form_valid(form)
                    messages.success(request, 'An email has been sent to ' + data +". Please check its inbox to continue reseting password.")
                    return result
                result = self.form_invalid(form)
                messages.error(request, 'No user is associated with this email address')
                return result
            else:
                '''
                If the input is an username, then the following code will lookup for users associated with that user. If found then an email will be sent to the user's address, else an error message will be printed on the screen.
                '''
                User = get_user_model()
                associated_users= User.objects.filter(sid=data)
                if associated_users:
                    stu_det=Student_Details.objects.filter(st_id=associated_users[0].sid)
                if associated_users:
                    c = {
                        'email': stu_det[0].email,
                        'domain': request.META['HTTP_HOST'], #or your domain
                        'site_name': 'Attendr',
                        'uid': urlsafe_base64_encode(force_bytes(associated_users[0].sid)).decode(),
                        'user': associated_users[0],
                        'token': default_token_generator.make_token(associated_users[0]),
                        'protocol': 'http',
                        }
                    subject_template_name='registration/password_reset_subject.txt'
                    email_template_name='registration/password_reset_email.html'
                    subject = loader.render_to_string(subject_template_name, c)
                    # Email subject *must not* contain newlines
                    subject = ''.join(subject.splitlines())
                    email = loader.render_to_string(email_template_name, c)
                    send_mail(subject, email, DEFAULT_FROM_EMAIL , [stu_det[0].email], fail_silently=False)
                    result = self.form_valid(form)
                    messages.success(request, 'Email has been sent to ' + data +"'s email address. Please check its inbox to continue reseting password.")
                    return result
                result = self.form_invalid(form)
                messages.error(request, 'This username does not exist in the system.')
                return result
            messages.error(request, 'Invalid Input')
            return self.form_invalid(form)



class PasswordResetConfirmView(FormView):
    template_name = "account/test_template.html"
    success_url = '/login/'
    form_class = SetPasswordForm

    def post(self, request, uidb64=None, token=None, *arg, **kwargs):
        """
        View that checks the hash in a password reset link and presents a
        form for entering a new password.
        """
        UserModel = get_user_model()
        form = self.form_class(request.POST)
        assert uidb64 is not None and token is not None  # checked by URLconf
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = UserModel._default_manager.get(sid=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None
        if user is not None and default_token_generator.check_token(user, token):
            if form.is_valid():
                new_password = form.cleaned_data['new_password2']
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password has been reset.')
                return self.form_valid(form)
            else:
                messages.error(
                    request, 'Password reset has not been unsuccessful.')
                return self.form_invalid(form)
        else:
            messages.error(
                request, 'The reset password link is no longer valid.')
            return self.form_invalid(form)







class ApiDetails(APIView):
    def get(self, request, std_id, format=None):
        try:
            http_stdid = Student_Details.objects.filter(st_id=std_id)
        except Student_Details.DoesNotExist:
            return Response("Student ID error", status=status.HTTP_404_NOT_FOUND)
        serializer = StudentDetailsSerializer(http_stdid, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        pstd_id = request.POST.get('st_id')
        User = get_user_model()
        if User.objects.filter(sid=pstd_id).exists():
            serializer = StudentDetailsSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Student ID error", status=status.HTTP_404_NOT_FOUND)


class ApiAttendance(APIView):
    def get(self, request, std_id, format=None):
        try:
            http_stdid = Student_Attendance.objects.filter(st_id=std_id)
        except Student_Attendance.DoesNotExist:
            return Response("Student ID error", status=status.HTTP_404_NOT_FOUND)
        serializer = StudentAttendanceSerializer(http_stdid, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        pstd_id = request.POST.get('st_id')
        p_date = request.POST.get('date')
        User = get_user_model()
        if User.objects.filter(sid=pstd_id).exists():
            uid = User.objects.filter(sid=pstd_id)
            http_date = Student_Attendance.objects.get(st_id=uid[0], date=p_date)
            print(http_date)
            serializer = StudentAttendanceSerializer(http_date, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Student ID error", status=status.HTTP_404_NOT_FOUND)


class ApiLogin(APIView):
    def get(self, request, format=None):
        u_id = request.GET.get('uid')
        password = request.GET.get('password')
        user = authenticate(sid=u_id, password=password)
        if user is None:
            return Response("Login error", status=status.HTTP_404_NOT_FOUND)
        else:
            return Response("Login successfull", status=status.HTTP_201_CREATED)

    def post(self, request, format=None):
        u_id = request.POST.get('uid')
        password = request.POST.get('password')
        token = request.POST.get('token')
        try:
            http_token = Token.objects.get(uid=u_id)
        except Token.DoesNotExist:
            http_token = ''
        user = authenticate(sid=u_id, password=password)
        if user is None:
            return Response("Login error", status=status.HTTP_404_NOT_FOUND)
        else:
            if token:
                if http_token:
                    serializer = TokenSerializer(http_token, data=request.data)
                else:
                    serializer = TokenSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response("Login successfull token not supplied", status=status.HTTP_201_CREATED)

