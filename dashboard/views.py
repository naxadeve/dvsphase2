from django.shortcuts import render, redirect
import pandas as pd
from django.http import HttpResponse, HttpResponseRedirect
import requests
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .forms import UserForm, ProgramCreateForm, PartnerCreateForm, SectorCreateForm, SubSectorCreateForm, \
    MarkerCategoryCreateForm, MarkerValueCreateForm, GisLayerCreateForm, ProvinceCreateForm, DistrictCreateForm, \
    PalikaCreateForm, IndicatorCreateForm, ProjectCreateForm, PermissionForm, FiveCreateForm, OutputCreateForm, \
    GroupForm, BudgetCreateForm, PartnerContactForm, CmpForm, GisStyleForm, UserProfileForm, FeedbackDataForm, FAQForm, \
    TACForm, NSForm, ManualForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes, renderer_classes, authentication_classes
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from core.models import Manual, Province, Program, FiveW, District, GapaNapa, Partner, Sector, SubSector, MarkerCategory, \
    MarkerValues, Indicator, IndicatorValue, GisLayer, Project, PartnerContact, Output, Notification, \
    BudgetToSecondTier, BudgetToFirstTier, Cmp, GisStyle, FeedbackForm, FAQ, TermsAndCondition, NationalStatistic
from .models import UserProfile, Log
from django.contrib.auth.models import User, Group, Permission
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from zipfile import ZipFile
import os
from django.contrib import messages
from random import randint
from django.contrib.admin.models import LogEntry
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.shortcuts import (get_object_or_404,
                              render,
                              HttpResponseRedirect)
import datetime
from django.db.models import Q
from .filters import fivew, export, cleardata
from django.http import FileResponse
from django.http import JsonResponse
from django.db.models import Sum

from about_us.models import AboutUs, ContactUs
from about_us.forms import AboutUsForm, ContactUsForm

# Create your views here.


@login_required()
def login_test(request, **kwargs):
    # user = authenticate(username='sumit', password='sumit1234')
    group = Group.objects.get(user=request.user)

    return HttpResponse(group.name)
    # return HttpResponse(kwargs['group'] + kwargs['partner'])
    # return render(request, 'dashboard.html')
    # return HttpResponse(request.user.has_perm('core.add_program'))


# def deleteallfivewdata(request):
#     if "GET" == request.method:
#         messages.error(request, 'Alert:You may Loose All Your Data,Please Backup First')
#         return render(request, 'confirm.html')
#     else:
#         FiveW.objects.all().delete()
#         return JsonResponse({'result': 'success'}, status=HTTP_200_OK)


def project(value1, value2):
    try:
        data = Project.objects.get(code=value1)
    except:
        data = Project.objects.get(code=value1, partner_id__code=value2)

    return data


def clear_data(request):
    partnerdata = request.GET.getlist('partner', None)
    programdata = request.GET.getlist('program', None)
    print(programdata)
    projectdata = request.GET.getlist('project', None)
    provincedata = request.GET.getlist('province', None)
    districtdata = request.GET.getlist('district', None)
    municipalitydata = request.GET.getlist('gapanapa', None)
    user = request.user
    user_data = UserProfile.objects.get(user=user)
    group = Group.objects.get(user=user)
    data = cleardata(partnerdata, programdata, projectdata, provincedata, districtdata, municipalitydata, group,
                     user_data)
    data.delete()
    messages.success(request, 'Success!' + ':' + "Successfully Deleted ")
    return redirect('/dashboard/five-list')


# def unique(list1):
#     unique_list = []
#     finaldata = []
#     for x in list1:
#         if x not in unique_list:
#             unique_list.append(x)
#     for x in unique_list:
#         finaldata.append(x)
#     if None in finaldata:
#         finaldata.remove(None)
#     return finaldata

@login_required()
def bulkCreate(request):
    if "GET" == request.method:
        return render(request, 'bulk_upload.html')
    else:
        csv = request.FILES["shapefile"]
        uploaded_file = request.FILES['shapefile']
        if request.POST.get('clear_data', None) is not None:
            FiveW.objects.all().delete()

        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file).fillna('')
        elif uploaded_file.name.endswith(('.xls', 'xlsx')):
            df = pd.read_excel(uploaded_file).fillna('')
        else:
            messages.error(request, "Please upload a .csv or .xls file")
        upper_range = len(df)
        fivew_correct = []
        fivew_incorrect = []
        error_log = []
        error = []
        success_count = 0
        update_count = 0
        user = request.user
        user_data = UserProfile.objects.get(user=user)
        group = Group.objects.get(user=user)
        if group.name == 'admin':
            for row in range(0, upper_range):
                try:
                    try:
                        test = FiveW.objects.get(supplier_id__code=int(df['1st TIER PARTNER CODE'][row]),
                                                 component_id__code=str(
                                                     df['Project/Component Code'][row]),
                                                 program_id__code=str(
                                                     int(df['Programme Code'][row])),
                                                 province_id__code=str(
                                                     int(df['PROVINCE.CODE'][row])),
                                                 district_id__code=str(
                                                     df['D.CODE'][row]),
                                                 municipality_id__hlcit_code=str(df['PALIKA.Code'][row]))
                        test.status = 'Ongoing' if df['PROJECT STATUS'][row][0].lower(
                        ) == 'o' else "Completed"
                        test.second_tier_partner_name = df['2nd TIER PARTNER'][row]
                        test.reporting_line_ministry = df['REPORTING LINE MINISTRY'][row]
                        test.contact_name = df['CONTACT NAME'][row]
                        test.designation = df['DESIGNATION'][row]
                        test.contact_number = df['CONTACT NUMBER'][row]
                        test.email = df['EMAIL'][row]
                        test.remarks = df['REMARKS'][row]
                        test.allocated_budget = float(df['BUDGET (£)'][row])
                        test.save()

                        update_count += 1

                    except ObjectDoesNotExist:
                        fivew_correct.append(FiveW(
                            supplier_id=Partner.objects.get(
                                code=int(df['1st TIER PARTNER CODE'][row])),
                            second_tier_partner_name=df['2nd TIER PARTNER'][row],
                            component_id=project(df['Project/Component Code'][row],
                                                 int(df['1st TIER PARTNER CODE'][row])),
                            program_id=Program.objects.get(
                                code=str(int(df['Programme Code'][row]))),
                            province_id=Province.objects.get(
                                code=str(int(df['PROVINCE.CODE'][row]))),
                            district_id=District.objects.get(
                                code=str(df['D.CODE'][row])),
                            municipality_id=GapaNapa.objects.get(
                                hlcit_code=str(df['PALIKA.Code'][row])),
                            status='Ongoing' if df['PROJECT STATUS'][row][0].lower(
                            ) == 'o' else "Completed",
                            reporting_line_ministry=df['REPORTING LINE MINISTRY'][row],
                            contact_name=df['CONTACT NAME'][row],
                            designation=df['DESIGNATION'][row],
                            contact_number=df['CONTACT NUMBER'][row],
                            email=df['EMAIL'][row],
                            remarks=df['REMARKS'][row],
                            allocated_budget=float(df['BUDGET (£)'][row])
                        ))
                        success_count += 1

                except Exception as e:
                    fivew_incorrect.append(row)
                    error_log.append(e)
                    error.append(str(row + 2))
            if fivew_incorrect:
                test = df.loc[fivew_incorrect, :]
                test['Errors'] = error_log
                test.to_csv('media/errordata.csv')
            if len(error) > 0:
                messages.error(request, 'Error in row(s)' +
                               str(' '.join([str(elem) for elem in error])))
            if success_count > 0:
                messages.success(
                    request, 'Success! : ' + str(success_count) + ' ' + "row(s) Of Five-w Data Added ")
            if update_count > 0:
                messages.info(
                    request, 'Updated! : ' + str(update_count) + " row(s) Of Five-w Data Updated ")

            FiveW.objects.bulk_create(fivew_correct)

        else:
            for row in range(0, upper_range):
                try:
                    try:
                        test = FiveW.objects.get(supplier_id__id=user_data.partner.id,
                                                 supplier_id__code=int(
                                                     df['1st TIER PARTNER CODE'][row]),
                                                 component_id__id=user_data.project.id,
                                                 component_id__code=str(
                                                     df['Project/Component Code'][row]),
                                                 program_id__id=user_data.program.id,
                                                 program_id__code=str(
                                                     int(df['Programme Code'][row])),
                                                 province_id__code=str(
                                                     int(df['PROVINCE.CODE'][row])),
                                                 district_id__code=str(
                                                     df['D.CODE'][row]),
                                                 municipality_id__hlcit_code=str(df['PALIKA.Code'][row]))
                        test.status = 'Ongoing' if df['PROJECT STATUS'][row][0].lower(
                        ) == 'o' else "Completed"
                        test.second_tier_partner_name = df['2nd TIER PARTNER'][row]
                        test.reporting_line_ministry = df['REPORTING LINE MINISTRY'][row]
                        test.contact_name = df['CONTACT NAME'][row]
                        test.designation = df['DESIGNATION'][row]
                        test.contact_number = df['CONTACT NUMBER'][row]
                        test.email = df['EMAIL'][row]
                        test.remarks = df['REMARKS'][row]
                        test.allocated_budget = float(df['BUDGET (£)'][row])
                        test.save()

                        update_count += 1
                    except ObjectDoesNotExist:
                        fivew_correct.append(FiveW(
                            supplier_id=Partner.objects.get(id=user_data.partner.id,
                                                            code=int(df['1st TIER PARTNER CODE'][row])),
                            second_tier_partner_name=df['2nd TIER PARTNER'][row],
                            component_id=Project.objects.get(id=user_data.project.id,
                                                             code=df['Project/Component Code'][row]),
                            program_id=Program.objects.get(id=user_data.program.id,
                                                           code=str(int(df['Programme Code'][row]))),
                            province_id=Province.objects.get(
                                code=df['PROVINCE.CODE'][row]),
                            district_id=District.objects.get(
                                code=df['D.CODE'][row]),
                            municipality_id=GapaNapa.objects.get(
                                hlcit_code=df['PALIKA.Code'][row]),
                            status='Ongoing' if df['PROJECT STATUS'][row][0].lower(
                            ) == 'o' else "Completed",
                            reporting_line_ministry=df['REPORTING LINE MINISTRY'][row],
                            contact_name=df['CONTACT NAME'][row],
                            designation=df['DESIGNATION'][row],
                            contact_number=df['CONTACT NUMBER'][row],
                            email=df['EMAIL'][row],
                            remarks=df['REMARKS'][row],
                            allocated_budget=float(df['BUDGET (£)'][row])
                        ))
                        success_count += 1

                except Exception as e:
                    fivew_incorrect.append(row)
                    error_log.append(e)
                    error.append(str(row + 2))
            if fivew_incorrect:
                test = df.loc[fivew_incorrect, :]
                test['Errors'] = error_log
                test.to_csv('media/errordata.csv')

            if len(error) > 0:
                messages.error(request, 'Error in row(s)' +
                               str(' '.join([str(elem) for elem in error])))
            if success_count > 0:
                messages.success(
                    request, 'Success! : ' + str(success_count) + ' ' + "row(s) Of Five-w Data Added ")
            if update_count > 0:
                messages.info(
                    request, 'Updated! : ' + str(update_count) + " row(s) Of Five-w Data Updated ")
            FiveW.objects.bulk_create(fivew_correct)

    return redirect('/dashboard/five-list', messages)


@login_required()
def uploadData(request):
    if "GET" == request.method:
        return render(request, 'shapefile.html')
    else:
        csv = request.FILES["shapefile"]
        df = pd.read_csv(csv)
        upper_range = len(df)

        try:
            # fiveData = [
            #     FiveW(
            #         program_name=Program.objects.get(program_name='Naxa'),
            #         partner_name=Partner.objects.get(partner_name='Naxa')
            #     ) for row in range(0, 2)
            # ]

            # five = FiveW.objects.bulk_create(fiveData)
            # list = []
            for row in range(0, upper_range):
                print(row)
                print(df['New Local Unit'][row])

                supplier_id = Partner.objects.get(
                    code=str(int(df['Tier 1_Partner'][row])))
                second_tier_partner = Partner.objects.get(
                    code=str(int(df['Tier 2_Partner_code'][row])))
                component_id = Project.objects.get(
                    code=str(df['Component'][row]))
                program_id = Program.objects.get(
                    code=str(int(df['Programme'][row])))
                province_id = Province.objects.get(
                    code=str(int(df['State'][row])))
                district_id = District.objects.get(
                    name=df['Project District'][row])
                municipality_id = GapaNapa.objects.get(
                    hlcit_code=df['hlcit_code'][row])
                ward = None
                local_partner = None
                project_title = df['Name of the Project'][row]
                status = df['Status'][row]
                start_date = datetime.strptime(
                    df['Start date'][row], "%m/%d/%Y").strftime('%Y-%m-%d')
                end_date = datetime.strptime(
                    df['End Date'][row], "%m/%d/%Y").strftime('%Y-%m-%d')
                allocated_budget = float(
                    df['Allocated Funds to Local Units'][row])
                male_beneficiary = (
                    int(df['Total Beneficiaries'][row]) - int(df['Female Beneficiaries'][row]))
                female_beneficiary = int(df['Female Beneficiaries'][row])
                total_beneficiary = int(df['Total Beneficiaries'][row])

                # try:
                #     supplier_id = Partner.objects.get(code=int(df['Tier 1_Partner'][row]))
                #
                # except:
                #     supplier_id = None
                #
                # try:
                #     second_tier_partner = Partner.objects.get(code=int(df['Tier 2_Partner_code'][row]))
                #
                # except:
                #     second_tier_partner = None
                #
                # try:
                #     component_id = Partner.objects.get(code=int(df['Component'][row]))
                #
                # except:
                #     component_id = None
                #
                # try:
                #     program_id = Program.objects.get(code=int(df['Programme'][row]))
                #
                # except:
                #     program_id = None
                #
                # try:
                #     province_id = Province.objects.get(code=int(df['State'][row]))
                #
                # except:
                #     province_id = None
                #
                # try:
                #     district_id = District.objects.get(name=df['Project District'][row])
                #
                # except:
                #     district_id = None
                #
                # try:
                #     municipality_id = GapaNapa.objects.get(name=df['New Local Unit'][row])
                #
                # except:
                #     municipality_id = None
                #
                # try:
                #     ward = None
                #
                # except:
                #     ward = None
                #
                # try:
                #     local_partner = None
                #
                # except:
                #     local_partner = None
                #
                # try:
                #     project_title = df['Name of the Project'][row]
                #
                # except:
                #     project_title = None
                #
                # try:
                #     status = df['Status'][row]
                #
                # except:
                #     status = 'Ongoing'
                #
                # try:
                #     start_date = df['Start date'][row]
                #
                # except:
                #     start_date = None
                #
                # try:
                #     end_date = df['End Date'][row]
                #
                # except:
                #     end_date = None
                #
                # try:
                #     allocated_budget = float(df['Allocated Funds to Local Units'][row])
                #
                # except:
                #     allocated_budget = 0
                #
                # try:
                #     male_beneficiary = (int(df['Total Beneficiaries'][row]) - int(df['Female Beneficiaries'][row]))
                #
                # except:
                #     male_beneficiary = 0
                #
                # try:
                #     female_beneficiary = int(df['Female Beneficiaries'][row])
                #
                # except:
                #     female_beneficiary = 0
                #
                # try:
                #     total_beneficiary = int(df['Total Beneficiaries'][row])
                #
                # except:
                #     total_beneficiary = 0

                # print(datetime.datetime.strptime(df['Start date'][row], '%Y-%m-%d'))
                # print(start_date)
                # print(df['New Local Unit'][row])
                # print(GapaNapa.objects.get(name=df['New Local Unit'][row]))

                five = FiveW.objects.create(supplier_id=supplier_id, second_tier_partner=second_tier_partner,
                                            program_id=program_id,
                                            component_id=component_id, province_id=province_id, district_id=district_id,
                                            municipality_id=municipality_id,
                                            ward=ward,
                                            local_partner=local_partner,
                                            project_title=project_title,
                                            status=status,
                                            start_date=start_date,
                                            end_date=end_date,
                                            allocated_budget=allocated_budget,
                                            male_beneficiary=male_beneficiary, female_beneficiary=female_beneficiary,
                                            total_beneficiary=total_beneficiary,
                                            )

            print(supplier_id)
            print('success')
            # FiveW.objects.create(fiveData)
            # data_list = [1, 2]
            # a = PartnerContact.objects.get(partner_id=58, name='sumit')
            # prog = Partner.objects.get(id='2')
            # progg = Program.objects.get(id='31')
            # progg.partner.add(prog)

            return HttpResponse('five')
        except Exception as e:
            return HttpResponse(e)


# def ShapefileUpload(request):
#     if "GET" == request.method:
#
#         return render(request, 'shapefile.html')
#     else:
#         shapefile = request.FILES["shapefile"]
#         layer_name = 'sumit' + str(randint(0, 9999))
#         # return HttpResponse(layer_name)
#         url = 'http://139.59.67.104:8080/geoserver/rest/workspaces/Naxa/datastores/' + layer_name + '/file.shp'
#         # return HttpResponse(url)
#
#         headers = {
#             'Content-type': 'application/zip',
#         }
#         response = requests.put(url, headers=headers, data=shapefile, auth=('admin', 'geoserver'))
#         # print(response)
#         return HttpResponse(response.status_code)


def ShapefileUpload(request):
    if "GET" == request.method:

        return render(request, 'shapefile.html')
    else:
        # shapefile = request.FILES["shapefile"]
        get_store_name = GisLayer.objects.filter(
            id=19).values_list('store_name', flat=True)

        url = 'http://139.59.67.104:8080/geoserver/rest/workspaces/Naxa/datastores/' + get_store_name[
            0] + '?recurse=true'
        headers = {
            'Content-type': '',
        }
        response = requests.delete(
            url, headers=headers, auth=('admin', 'geoserver'))
        # print(response)
        return HttpResponse(response.status_code)


@login_required()
def create_role(request):
    if "GET" == request.method:
        permissions = Permission.objects.all()
        return render(request, 'create_role.html', {'permissions': permissions})

    else:
        role = request.POST['role']
        permission_list = request.POST.getlist('permission')
        group = Group.objects.create(name=role)
        for permissions in permission_list:
            permission_check = Permission.objects.get(id=permissions)
            group.permissions.add(permission_check)

        return redirect('role-list')


@login_required()
def edit_role(request):
    if "GET" == request.method:
        permissions_e = Permission.objects.filter(group__id=9)
        permissions = Permission.objects.all()
        return render(request, 'edit_role.html', {'permissions': permissions, 'permission_e': permissions_e})

    else:
        role = request.POST['role']
        permission_list = request.POST.getlist('permission')
        group = Group.objects.create(name=role)
        for permissions in permission_list:
            permission_check = Permission.objects.get(id=permissions)
            group.permissions.add(permission_check)

        return redirect('role-list')


@login_required()
def assign_role(request, **kwargs):
    if "GET" == request.method:
        groups = Group.objects.all()
        user = request.user
        user_data = UserProfile.objects.get(user=user)
        return render(request, 'assign_role.html', {'user': user_data, 'groups': groups, 'user_id': kwargs['id']})
    else:
        user_id = request.POST['user']
        group_id = request.POST['group_id']
        user = User.objects.get(id=user_id)
        group = Group.objects.get(id=group_id)
        user.groups.add(group)
        notify_message = user.username + ' was assigned ' + \
            group.name + ' role by ' + request.user.username
        notify = Notification.objects.create(user=user, message=notify_message, type='role',
                                             link='/dashboard/user-list')
        return redirect('user-list')


'''@login_required()
def Invitation(request):
    if "GET" == request.method:
        group = Group.objects.all()
        partner = Partner.objects.all()
        # program = Program.objects.all()
        # project = Project.objects.all()
        return render(request, 'invitation_form.html', {'group': group, 'partners': partner, })

    else:
        user = request.user
        user_data = UserProfile.objects.get(user=user)
        url = settings.SITE_URL
        group = request.POST["group"]
        emails = request.POST["email"]
        partnered = request.POST["partner"]
        # programed = request.POST["program"]
        # projected = request.POST["project"]
        subject = 'User Invitation'
        message = render_to_string('mail.html', {'group': group, 'url': url, 'partner': partnered, 'user': user_data, })

        recipient_list = [emails]
        email = EmailMessage(
            subject, message, 'from@example.com', recipient_list
        )
        email.content_subtype = "html"
        mail = email.send()
        if mail == 1:
            msg = emails + " was successfully invited"
            messages.success(request, msg)
            notify_message = emails + ' was invited to create account by ' + user_data.name
            notify = Notification.objects.create(user=user, message=notify_message, type='invitation',
                                                 link='/dashboard/user-list')
            return redirect('user-list')
        else:
            msg = emails + " could not be invited "
            messages.success(request, msg)
            return redirect('user-list')'''


def signup(request, **kwargs):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            if kwargs['group'] != 0:
                group = Group.objects.get(pk=kwargs['group'])
                user.groups.add(group)

            UserProfile.objects.create(user=user, name=request.POST['name'], email=request.POST['email'],
                                       partner_id=int(request.POST['partner']), image=request.FILES['image'])

            notify_message = request.POST['email'] + \
                ' has created account by username ' + request.POST['username']

            notify_messages = 'Activate account for user ' + \
                request.POST['username']

            notify = Notification.objects.create(user=user, message=notify_message, type='signup',
                                                 link='/dashboard/user-list')
            notified = Notification.objects.create(user=user, message=notify_messages, type='signup',
                                                   link='/dashboard/user-list')
            return render(request, 'registered_message.html', {'user': request.POST['name']})
        else:
            if kwargs['group'] == 0:
                partner = Partner.objects.all()
                # program = Program.objects.all()
                # project = Project.objects.all()
            else:
                partner = Partner.objects.filter(id=kwargs['partner'])
                # program = Program.objects.filter(id=kwargs['program'])
                # project = Project.objects.filter(id=kwargs['project'])

            return render(request, 'signups.html',
                          {'form': form, 'partners': partner, })

    else:
        form = UserCreationForm()
        if kwargs['group'] == 0:
            partner = Partner.objects.all()
            # program = Program.objects.all()
            # project = Project.objects.all()
        else:
            partner = Partner.objects.filter(id=kwargs['partner'])
            # program = Program.objects.filter(id=kwargs['program'])
            # project = Project.objects.filter(id=kwargs['project'])

        return render(request, 'signups.html',
                      {'form': form, 'partners': partner, })


def createuser(request, **kwargs):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            group = Group.objects.get(pk=request.POST['group'])
            user.groups.add(group)
            '''
            if kwargs['group'] != 0:
                group = Group.objects.get(pk=kwargs['group'])
                user.groups.add(group)
            '''
            try:
                UserProfile.objects.create(user=user, name=request.POST['name'], email=request.POST['email'],
                                           partner_id=int(request.POST['partner']), image=request.FILES['image'],
                                           program_id=int(
                                               request.POST['program']),
                                           project_id=int(request.POST['project']))
            except:
                UserProfile.objects.create(user=user, name=request.POST['name'], email=request.POST['email'],
                                           partner_id=int(
                                               request.POST['partner']),
                                           program_id=int(
                                               request.POST['program']),
                                           project_id=int(request.POST['project']))

            notify_message = request.POST['email'] + \
                ' has created account by username ' + request.POST['username']

            notify_messages = 'Activate account for user ' + \
                request.POST['username']

            notify = Notification.objects.create(user=user, message=notify_message, type='signup',
                                                 link='/dashboard/user-list')
            notified = Notification.objects.create(user=user, message=notify_messages, type='signup',
                                                   link='/dashboard/user-list')
            return render(request, 'registered_message.html', {'user': request.POST['name']})
        else:
            partner = Partner.objects.all()
            group = Group.objects.all()
            programs = Program.objects.values(
                'id', 'name', 'partner_id__id').order_by('name')
            projects = Project.objects.values(
                'id', 'name', 'program_id__id', 'code', 'partner_id__id').order_by('name')

            return render(request, 'createuser.html',
                          {'form': form, 'partners': partner, 'group': group, 'programs': programs,
                           'projects': projects})

    else:
        form = UserCreationForm()
        partner = Partner.objects.order_by('name')
        group = Group.objects.all()
        programs = Program.objects.values(
            'id', 'name', 'partner_id__id').order_by('name')
        projects = Project.objects.values(
            'id', 'name', 'program_id__id', 'code', 'partner_id__id').order_by('name')
        return render(request, 'createuser.html',
                      {'form': form, 'partners': partner, 'group': group, 'programs': programs,
                       'projects': projects})


def updateuser(request, id):
    context = {}
    obj = get_object_or_404(UserProfile, id=id)
    form = UserProfileForm(request.POST or None, instance=obj)
    if form.is_valid():
        ho = form.save()
        try:
            ho.image = request.FILES['image']
        except:
            pass
        ho.save()
        test = User.objects.filter(id=obj.user.id)
        test2 = User.objects.get(id=obj.user.id)
        test.update(username=request.POST['username'])
        old_group = Group.objects.get(user=test2)
        group = Group.objects.get(pk=request.POST['group'])
        old_group.user_set.remove(test2)
        group.user_set.add(test2)
        return HttpResponseRedirect("/dashboard/user-list")
    partner = Partner.objects.order_by('name')
    programs = Program.objects.values(
        'id', 'name', 'partner_id__id').order_by('name')
    projects = Project.objects.values(
        'id', 'name', 'program_id__id', 'partner_id__id').order_by('name')
    group = Group.objects.all()
    user = User.objects.all()
    context["form"] = form
    context["partner"] = partner
    context['user'] = user
    context['programs'] = programs
    context['projects'] = projects
    context['groups'] = group

    return render(request, "updateuser.html", context)


def feedback_status(request, **kwargs):
    feedback = FeedbackForm.objects.get(id=kwargs['id'])
    if feedback.status == 'Old':
        feedback.status = "New"
        feedback.save()
        if feedback.name:
            msg = str(feedback.name) + " " + \
                "Feedback Successfully changed From Old To New"
        else:
            msg = "Feedback Successfully changed From Old To New"
        messages.success(request, msg)
    else:
        feedback.status = 'Old'
        feedback.save()
        if feedback.name:
            msg = str(feedback.name) + " " + \
                "Feedback Successfully changed From New to Old"
        else:
            msg = "Feedback Successfully changed From New to Old"
        messages.success(request, msg)
    return redirect('feedback-list')


def activate_user(request, **kwargs):
    user = User.objects.get(id=kwargs['id'])
    if user.is_active == False:
        user_data = UserProfile.objects.get(user=user)
        emails = user_data.email
        url = settings.SITE_URL
        user.is_active = True
        user.save()
        subject = 'Login'
        message = render_to_string('confirmation_mail.html', {
                                   'url': url, 'user': user_data})

        recipient_list = [emails]
        email = EmailMessage(
            subject, message, 'noreply.dfid@gmail.com', recipient_list
        )
        email.content_subtype = "html"
        mail = email.send()
        if mail == 1:
            msg = emails + " was successfully activated"
            messages.success(request, msg)

            notify_message = 'Account for username ' + user.username + \
                ' was activated by ' + request.user.username

            notify = Notification.objects.create(user=request.user, message=notify_message, type='activation',
                                                 link='/dashboard/user-list')

        else:
            msg = emails + " could not be activated "
            messages.success(request, msg)

        return redirect('user-list')
    else:
        user.is_active = False
        user.save()
        msg = "Successfully Deactivated"
        messages.success(request, msg)
        return redirect('user-list')


@authentication_classes([SessionAuthentication, ])
@api_view()
@permission_classes([IsAuthenticated, ])
def auth(request):
    user = request.user
    # return HttpResponse(user)

    if user is None:
        return Response({'error': 'Please authorize first'},
                        status=HTTP_400_BAD_REQUEST)
    if not user:
        return Response({'error': 'Invalid Credentials'},
                        status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key},
                    status=HTTP_200_OK)


def check_login(request):
    if "GET" == request.method:
        form = UserForm()
        return render(request, 'sign_in.html', {'form': form})
    else:
        username = request.POST["username"]
        password = request.POST["password"]
        users = authenticate(request, username=username, password=password)
        if users is not None:
            login(request, users)
            return HttpResponse(request.user)
        else:
            return HttpResponse("login failed")


def province_list(request):
    template_name = 'province_list.html'
    province = Program.objects.filter(id=5).order_by('id')
    data_list = Program.objects.filter(id=5).values_list('sector', flat=True)
    user = request.user
    # LogEntry.objects.all().delete()

    if (data_list):
        filter_sector = Sector.objects.order_by('id')

    else:
        filter_sector = Sector.objects.exclude(id__in=data_list)

    data = {}
    data['object_list'] = province
    data['log'] = LogEntry.objects.filter(user_id=user).order_by('-id')[:5]
    data['sector'] = Sector.objects.all(
    ).prefetch_related('Sector').order_by('id')
    data['filtered'] = filter_sector
    return render(request, template_name, data)


class ProgramList(LoginRequiredMixin, ListView):
    template_name = 'program_list.html'
    model = Program

    def get_context_data(self, **kwargs):
        data = super(ProgramList, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        group = Group.objects.get(user=user)
        if group.name == 'admin':
            program_list = Program.objects.order_by('id')
        else:
            program_list = Program.objects.order_by('id')
        data['list'] = program_list
        data['user'] = user_data
        data['active'] = 'program'
        return data


class OutputList(LoginRequiredMixin, ListView):
    template_name = 'output_list.html'
    model = Program

    def get_context_data(self, **kwargs):
        data = super(OutputList, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        output_list = Output.objects.all()
        data['list'] = output_list
        data['user'] = user_data
        data['active'] = 'output'
        return data


class CmpList(LoginRequiredMixin, ListView):
    template_name = 'cmp_list.html'
    model = Program

    def get_context_data(self, **kwargs):
        data = super(CmpList, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        cmp_list = Cmp.objects.values('project_code', 'project_name', 'total_project_budget', 'percentage_in_country',
                                      'budget_country_fy', 'sro_name', 'category', 'poc', 'poc_email', 'remarks',
                                      'province_id__name', 'district_id__name', 'municipality_id__name', 'id').order_by(
            'id')
        data['list'] = cmp_list
        data['user'] = user_data
        data['active'] = 'cmp'
        return data


class PermissionList(LoginRequiredMixin, ListView):
    template_name = 'permission_list.html'
    model = Program

    def get_context_data(self, **kwargs):
        data = super(PermissionList, self).get_context_data(**kwargs)
        permission_list = Permission.objects.order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = permission_list
        data['user'] = user_data
        data['active'] = 'permission'
        return data


class RoleList(LoginRequiredMixin, ListView):
    template_name = 'role_list.html'
    model = Group

    def get_context_data(self, **kwargs):
        data = super(RoleList, self).get_context_data(**kwargs)
        role_list = Group.objects.order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = role_list
        data['user'] = user_data
        data['active'] = 'permission'
        return data


def ExportData(request):
    partnerdata = request.GET.getlist('partner', None)
    programdata = request.GET.getlist('program', None)
    projectdata = request.GET.getlist('project', None)
    provincedata = request.GET.getlist('province', None)
    districtdata = request.GET.getlist('district', None)
    municipalitydata = request.GET.getlist('gapanapa', None)
    user = request.user
    user_data = UserProfile.objects.get(user=user)
    group = Group.objects.get(user=user)
    data = export(partnerdata, programdata, projectdata, provincedata,
                  districtdata, municipalitydata, group, user_data)
    newdata = []
    for d in data:
        d['1st TIER PARTNER'] = d.pop('supplier_id__name')
        d['1st TIER PARTNER CODE'] = d.pop('supplier_id__code')
        d['2nd TIER PARTNER'] = d.pop('second_tier_partner_name')
        d['PROGRAMME NAME'] = d.pop('program_id__name')
        d['Programme Code'] = d.pop('program_id__code')
        d['PROJECT/COMPONENT NAME'] = d.pop('component_id__name')
        d['Project/Component Code'] = d.pop('component_id__code')
        d['PROJECT STATUS'] = d.pop('status')
        d['PROVINCE'] = d.pop('province_id__name')
        d['PROVINCE.CODE'] = d.pop('province_id__code')
        d['DISTRICT'] = d.pop('district_id__name')
        d['D.CODE'] = d.pop('district_id__code')
        d['PALIKA'] = d.pop('municipality_id__name')
        d['PALIKA.Code'] = d.pop('municipality_id__hlcit_code')
        d['BUDGET (£)'] = d.pop('allocated_budget')
        d['REMARKS'] = d.pop('remarks')
        d['EMAIL'] = d.pop('email')
        d['CONTACT NAME'] = d.pop('contact_name')
        d['CONTACT NUMBER'] = d.pop('contact_number')
        d['DESIGNATION'] = d.pop('designation')
        d['REPORTING LINE MINISTRY'] = d.pop('reporting_line_ministry')
        newdata.append(d)
    df = pd.DataFrame(newdata)
    df.to_csv('media/exportdata.csv')
    return JsonResponse({'resp': 'success'})


class FiveList(LoginRequiredMixin, ListView):
    template_name = 'five_list.html'
    paginate_by = 2
    model = FiveW

    def get_context_data(self, **kwargs):
        partnerdata = self.request.GET.getlist('partner', None)
        programdata = self.request.GET.getlist('program', None)
        projectdata = self.request.GET.getlist('project', None)
        provincedata = self.request.GET.getlist('province', None)
        districtdata = self.request.GET.getlist('district', None)
        municipalitydata = self.request.GET.getlist('gapanapa', None)

        if partnerdata or projectdata or programdata or provincedata or districtdata or municipalitydata:
            user = self.request.user
            user_data = UserProfile.objects.get(user=user)
            group = Group.objects.get(user=user)
            if group.name == 'admin':
                dat_values = fivew(partnerdata, programdata, projectdata, provincedata, districtdata, municipalitydata,
                                   group, user_data)
                partner = Partner.objects.values('id', 'name').order_by('name')
                project = Project.objects.values(
                    'id', 'program_id__id', 'name', 'partner_id__id').order_by('name')
                program = Program.objects.values(
                    'id', 'name', 'partner_id__id').order_by('name')
                province = Province.objects.exclude(
                    code=-1).values('id', 'name').order_by('name')
                district = District.objects.exclude(
                    code=-1).values('id', 'province_id__id', 'name').order_by('name')
                gapanapa = GapaNapa.objects.exclude(code=-1).values('id', 'province_id__id', 'district_id__id',
                                                                    'name').order_by('name')

            else:
                dat_values = fivew(partnerdata, programdata, projectdata, provincedata, districtdata, municipalitydata,
                                   group, user_data)
                partner = Partner.objects.filter(id=user_data.partner.id).values(
                    'id', 'name').order_by('name')
                program = Program.objects.filter(id=user_data.program.id).values('id', 'name',
                                                                                 'partner_id__id').order_by('name')
                project = Project.objects.filter(id=user_data.project.id).values('id', 'program_id__id',
                                                                                 'name', 'partner_id__id').order_by(
                    'name')
                province = Province.objects.exclude(
                    code=-1).values('id', 'name').order_by('name')
                district = District.objects.exclude(
                    code=-1).values('id', 'province_id__id', 'name').order_by('name')
                gapanapa = GapaNapa.objects.exclude(code=-1).values('id', 'province_id__id', 'district_id__id',
                                                                    'name').order_by('name')

            paginator = Paginator(dat_values, 500)
            page_numbers_range = 500
            max_index = len(paginator.page_range)
            print(paginator)
            page_number = self.request.GET.get('page')
            current_page = int(page_number) if page_number else 1
            page_obj = paginator.get_page(page_number)
            start_index = int((current_page - 1) /
                              page_numbers_range) * page_numbers_range
            end_index = start_index + page_numbers_range
            if end_index >= max_index:
                end_index = max_index

            page_range = paginator.page_range[start_index:end_index]
            province_minus_id = Province.objects.get(code=-1)
            district_minus_id = District.objects.get(code=-1)
            municipality_minus_id = GapaNapa.objects.get(code=-1)

            data = {
                'page_range': page_range,
                'list': page_obj,
                'active': 'five',
                'user': user_data,
                'partner': partner,
                'program': program,
                'project': project,
                'province': province,
                'district': district,
                'pr': province_minus_id.id,
                'dr': district_minus_id.id,
                'mr': municipality_minus_id.id,
                'gapanapa': gapanapa,
                'partnerdata': partnerdata,
                'programdata': programdata,
                'projectdata': projectdata,
                'provincedata': provincedata,
                'municipalitydata': municipalitydata,
                'districtdata': districtdata,
                'domain': settings.SITE_URL,
                'total_objects': dat_values.count()

            }
            return data
        else:
            data = super(FiveList, self).get_context_data(**kwargs)
            user = self.request.user
            user_data = UserProfile.objects.get(user=user)
            group = Group.objects.get(user=user)
            if group.name == 'admin':
                five = FiveW.objects.values('id', 'supplier_id__name', 'second_tier_partner_name', 'program_id__name',
                                            'component_id__name', 'status', 'province_id__name', 'district_id__name',
                                            'municipality_id__name', 'allocated_budget').order_by('id')
                partner = Partner.objects.values('id', 'name').order_by('name')
                project = Project.objects.values(
                    'id', 'program_id__id', 'name', 'partner_id__id').order_by('name')
                program = Program.objects.values(
                    'id', 'name', 'partner_id__id').order_by('name')
                province = Province.objects.exclude(
                    code=-1).values('id', 'name').order_by('name')
                district = District.objects.exclude(
                    code=-1).values('id', 'province_id__id', 'name').order_by('name')
                gapanapa = GapaNapa.objects.exclude(code=-1).values('id', 'province_id__id', 'district_id__id',
                                                                    'name').order_by('name')

            else:
                five = FiveW.objects.filter(supplier_id=user_data.partner.id, program_id=user_data.program.id,
                                            component_id=user_data.project.id).values('id', 'supplier_id__name',
                                                                                      'second_tier_partner_name',
                                                                                      'program_id__name',
                                                                                      'component_id__name', 'status',
                                                                                      'province_id__name',
                                                                                      'district_id__name',
                                                                                      'municipality_id__name',
                                                                                      'allocated_budget').order_by('id')
                partner = Partner.objects.filter(id=user_data.partner.id).values(
                    'id', 'name').order_by('name')
                program = Program.objects.filter(id=user_data.program.id).values('id', 'name',
                                                                                 'partner_id__id').order_by('name')
                project = Project.objects.filter(id=user_data.project.id).values('id', 'program_id__id',
                                                                                 'name', 'partner_id__id').order_by(
                    'name')
                province = Province.objects.exclude(
                    code=-1).values('id', 'name').order_by('name')
                district = District.objects.exclude(
                    code=-1).values('id', 'province_id__id', 'name').order_by('name')
                gapanapa = GapaNapa.objects.exclude(code=-1).values('id', 'province_id__id', 'district_id__id',
                                                                    'name').order_by('name')

            paginator = Paginator(five, 500)
            page_numbers_range = 500
            max_index = len(paginator.page_range)
            print(paginator)
            page_number = self.request.GET.get('page')
            current_page = int(page_number) if page_number else 1
            page_obj = paginator.get_page(page_number)
            start_index = int((current_page - 1) /
                              page_numbers_range) * page_numbers_range
            end_index = start_index + page_numbers_range
            if end_index >= max_index:
                end_index = max_index

            page_range = paginator.page_range[start_index:end_index]
            province_minus_id = Province.objects.get(code=-1)
            district_minus_id = District.objects.get(code=-1)
            municipality_minus_id = GapaNapa.objects.get(code=-1)
            data['pr'] = province_minus_id.id
            data['dr'] = district_minus_id.id
            data['mr'] = municipality_minus_id.id
            data['page_range'] = page_range
            data['list'] = page_obj
            data['user'] = user_data
            data['partner'] = partner
            data['program'] = program
            data['project'] = project
            data['province'] = province
            data['district'] = district
            data['gapanapa'] = gapanapa
            data['active'] = 'five'
            data['five'] = five
            data['domain'] = settings.SITE_URL
            data['total_objects'] = five.count()
            return data


class UserList(LoginRequiredMixin, ListView):
    template_name = 'user_list.html'
    model = Program

    def get_context_data(self, **kwargs):
        data = super(UserList, self).get_context_data(**kwargs)
        user_list = UserProfile.objects.order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = user_list
        data['user'] = user_data
        data['active'] = 'user'
        return data


class PartnerList(LoginRequiredMixin, ListView):
    template_name = 'partner_list.html'
    model = Partner

    def get_context_data(self, **kwargs):
        data = super(PartnerList, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        group = Group.objects.get(user=user)
        if group.name == 'admin':
            partner_list = Partner.objects.order_by('id')
        else:
            partner_list = Partner.objects.filter(id=user_data.partner.id)

        data['list'] = partner_list
        data['user'] = user_data
        data['active'] = 'partner'
        return data


class PartnerContactList(LoginRequiredMixin, ListView):
    template_name = 'partnerContact_list.html'
    model = PartnerContact

    def get_context_data(self, **kwargs):
        data = super(PartnerContactList, self).get_context_data(**kwargs)
        partner = self.request.GET['id']
        partner_contact = PartnerContact.objects.filter(
            partner_id__id=partner).order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = partner_contact
        data['count'] = partner_contact.count()
        data['user'] = user_data
        data['active'] = 'partner'
        return data


class SectorList(LoginRequiredMixin, ListView):
    template_name = 'sector_list.html'
    model = Sector

    def get_context_data(self, **kwargs):
        data = super(SectorList, self).get_context_data(**kwargs)
        sector_list = Sector.objects.order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = sector_list
        data['user'] = user_data
        data['active'] = 'sector'
        return data


class ProjectList(LoginRequiredMixin, ListView):
    template_name = 'project_list.html'
    model = Project

    def get_context_data(self, **kwargs):
        program_ids = self.request.GET.getlist('program', None)
        data = super(ProjectList, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        group = Group.objects.get(user=user)
        program = Program.objects.order_by('name')
        if program_ids:
            project_list = Project.objects.filter(
                program_id__in=program_ids).order_by('id')
        else:
            if group.name == 'admin':
                project_list = Project.objects.order_by('id')
            else:
                project_list = Project.objects.order_by('id')

        data['list'] = project_list
        data['program'] = program
        data['user'] = user_data
        data['selected'] = program_ids
        data['active'] = 'project'
        return data


class SubSectorList(LoginRequiredMixin, ListView):
    template_name = 'sub_sector_list.html'
    model = SubSector

    def get_context_data(self, **kwargs):
        data = super(SubSectorList, self).get_context_data(**kwargs)
        sub_sector_list = SubSector.objects.order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = sub_sector_list
        data['user'] = user_data
        data['active'] = 'sector'
        return data


class BudgetList(LoginRequiredMixin, ListView):
    template_name = 'budget_list.html'
    model = BudgetToFirstTier

    def get_context_data(self, **kwargs):
        data = super(BudgetList, self).get_context_data(**kwargs)
        budget_list = BudgetToFirstTier.objects.order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = budget_list
        data['user'] = user_data
        data['active'] = 'budget'
        return data


class MarkerList(LoginRequiredMixin, ListView):
    template_name = 'marker_list.html'
    model = MarkerCategory

    def get_context_data(self, **kwargs):
        data = super(MarkerList, self).get_context_data(**kwargs)
        marker_list = MarkerCategory.objects.order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = marker_list
        data['user'] = user_data
        data['active'] = 'marker'
        return data


class MarkerValueList(LoginRequiredMixin, ListView):
    template_name = 'marker_value_list.html'
    model = MarkerValues

    def get_context_data(self, **kwargs):
        data = super(MarkerValueList, self).get_context_data(**kwargs)
        markervalue_list = MarkerValues.objects.order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = markervalue_list
        data['user'] = user_data
        data['active'] = 'marker'
        return data


class IndicatorList(LoginRequiredMixin, ListView):
    template_name = 'indicator_list.html'
    model = Indicator

    def get_context_data(self, **kwargs):
        data = super(IndicatorList, self).get_context_data(**kwargs)
        indicator_list = Indicator.objects.filter(show_flag=1).order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = indicator_list
        data['user'] = user_data
        data['active'] = 'indicator'
        return data


class FeedbackList(LoginRequiredMixin, ListView):
    template_name = 'feedback_list.html'
    model = FeedbackForm

    def get_context_data(self, **kwargs):
        data = super(FeedbackList, self).get_context_data(**kwargs)
        feedbacklist = FeedbackForm.objects.order_by('-id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = feedbacklist
        data['user'] = user_data
        data['active'] = 'feedback'
        return data


class FAQList(LoginRequiredMixin, ListView):
    template_name = 'faq_list.html'
    model = FAQ

    def get_context_data(self, **kwargs):
        data = super(FAQList, self).get_context_data(**kwargs)
        faqlist = FAQ.objects.order_by('order')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = faqlist
        data['user'] = user_data
        data['active'] = 'faq'
        return data


class NSList(LoginRequiredMixin, ListView):
    template_name = 'ns_list.html'
    model = NationalStatistic

    def get_context_data(self, **kwargs):
        data = super(NSList, self).get_context_data(**kwargs)
        nslist = NationalStatistic.objects.order_by('-id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = nslist
        data['user'] = user_data
        data['active'] = 'ns'
        return data


class ManualList(LoginRequiredMixin, ListView):
    template_name = 'manual_list.html'
    model = Manual

    def get_context_data(self, **kwargs):
        data = super(ManualList, self).get_context_data(**kwargs)
        manualList = Manual.objects.order_by('-id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = manualList
        data['user'] = user_data
        data['active'] = 'man'
        return data


class TACList(LoginRequiredMixin, ListView):
    template_name = 'tac_list.html'
    model = TermsAndCondition

    def get_context_data(self, **kwargs):
        data = super(TACList, self).get_context_data(**kwargs)
        taclist = TermsAndCondition.objects.order_by('order')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = taclist
        data['user'] = user_data
        data['active'] = 'tac'
        return data


class IndicatorValueList(LoginRequiredMixin, ListView):
    template_name = 'indicator_value_list.html'
    model = Indicator

    def get_context_data(self, **kwargs):
        indicator = self.request.GET['id']
        data = super(IndicatorValueList, self).get_context_data(**kwargs)
        indicator_value_list = IndicatorValue.objects.filter(
            indicator_id=indicator).order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = indicator_value_list
        data['user'] = user_data
        data['active'] = 'indicator'
        return data


class GisLayerList(LoginRequiredMixin, ListView):
    template_name = 'gis_layer_list.html'
    model = GisLayer

    def get_context_data(self, **kwargs):
        data = super(GisLayerList, self).get_context_data(**kwargs)
        gis_layer_list = GisLayer.objects.order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = gis_layer_list
        data['user'] = user_data
        data['active'] = 'gis'
        return data


class ProvinceList(LoginRequiredMixin, ListView):
    template_name = 'provinces_list.html'
    model = Province

    def get_context_data(self, **kwargs):
        data = super(ProvinceList, self).get_context_data(**kwargs)
        province = Province.objects.values('id', 'name', 'code').order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = province
        data['user'] = user_data
        data['active'] = 'location'
        return data


class DistrictList(LoginRequiredMixin, ListView):
    template_name = 'district_list.html'
    model = District

    def get_context_data(self, **kwargs):
        data = super(DistrictList, self).get_context_data(**kwargs)

        district = District.objects.values(
            'id', 'name', 'code', 'province_id').order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = district
        data['user'] = user_data
        data['active'] = 'location'
        return data


class PalikaList(LoginRequiredMixin, ListView):
    template_name = 'palika_list.html'
    model = GapaNapa

    def get_context_data(self, **kwargs):
        data = super(PalikaList, self).get_context_data(**kwargs)
        palika = GapaNapa.objects.values('id', 'name', 'province_id', 'district_id', 'gn_type_en', 'gn_type_np',
                                         'population', 'geography', 'cbs_code', 'hlcit_code', 'p_code').order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['list'] = palika
        data['active'] = 'location'
        return data


class Dashboard(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        group = Group.objects.get(user=user)
        log = Log.objects.all().order_by('-id')
        total_budget_spend = 0
        if group.name == 'admin':
            five = FiveW.objects.order_by('id')
        else:
            five = FiveW.objects.select_related('supplier_id').filter(supplier_id=user_data.partner.id,
                                                                      program_id=user_data.program.id,
                                                                      component_id=user_data.project.id)
            total_budget = five.aggregate(Sum('allocated_budget'))
            total_budget_spend = total_budget['allocated_budget__sum']

        return render(request, 'dashboard.html',
                      {'user': user_data, 'active': 'dash', 'fives': five, 'logs': log, 'group': group,
                       'total_budget_spend': total_budget_spend})


class ProgramAdd(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        return render(request, 'program_add.html', {'user': user_data, 'active': 'program'})


class VectorMap(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        return render(request, 'vector_map.html')


class ProgramCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Program
    template_name = 'program_add.html'
    form_class = ProgramCreateForm
    success_message = 'Program successfully Created'

    def get_context_data(self, **kwargs):
        data = super(ProgramCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        markers = MarkerCategory.objects.all().prefetch_related(
            'MarkerCategory').order_by('id')
        partners = Partner.objects.order_by('name')
        sectors = Sector.objects.all().prefetch_related('Sector').order_by('id')
        data['sectors'] = sectors
        data['partners'] = partners
        data['markers'] = markers
        data['user'] = user_data
        data['active'] = 'program'
        return data

    def get_success_url(self):
        return reverse_lazy('program-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "New program " + self.object.name + \
            "  has been added by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class PartnerCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Partner
    template_name = 'partner_add.html'
    form_class = PartnerCreateForm
    success_message = 'Partner successfully Created'

    def get_context_data(self, **kwargs):
        data = super(PartnerCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'partner'
        return data

    def get_success_url(self):
        return reverse_lazy('partner-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        contact_names = self.request.POST.getlist('contact_person_name')
        emails = self.request.POST.getlist('contact_person_email')
        numbers = self.request.POST.getlist('contact_person_ph')
        upper_range = len(contact_names)
        print(upper_range)
        print(contact_names[0])
        if contact_names[0]:
            for row in range(0, upper_range):
                PartnerContact.objects.create(partner_id=self.object, name=contact_names[row], email=emails[row],
                                              phone_number=numbers[row])

        message = "New partner " + self.object.name + \
            "  has been added by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


def AddPartnerContact(request, **kwargs):
    if "GET" == request.method:
        user = request.user
        user_data = UserProfile.objects.get(user=user)
        return render(request, 'partnerContact_add.html', {'user': user_data, 'user_id': kwargs['id']})
    else:
        contact_names = request.POST.getlist('contact_person_name')
        emails = request.POST.getlist('contact_person_email')
        numbers = request.POST.getlist('contact_person_ph')
        upper_range = len(contact_names)
        for row in range(0, upper_range):
            PartnerContact.objects.create(partner_id_id=int(kwargs['id']), name=contact_names[row], email=emails[row],
                                          phone_number=numbers[row])
        return redirect('partner-list')


class RoleCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Group
    template_name = 'create_role.html'
    form_class = GroupForm
    success_message = 'Role successfully added'

    def get_context_data(self, **kwargs):
        data = super(RoleCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'role'
        data['permissions'] = Permission.objects.all()
        return data

    def get_success_url(self):
        return reverse_lazy('role-list')


class FAQCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = FAQ
    template_name = 'faq_add.html'
    form_class = FAQForm
    success_message = 'FAQ successfully added'

    def get_context_data(self, **kwargs):
        data = super(FAQCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'faq'
        data['permissions'] = Permission.objects.all()
        return data

    def get_success_url(self):
        return reverse_lazy('faq-list')

    # def form_valid(self, form):
    #     self.object = form.save()
    #     message = "Partner " + self.object.name + "  has been edited by " + self.request.user.username
    #     log = Log.objects.create(user=self.request.user, message=message, type="update")
    #     return HttpResponseRedirect(self.get_success_url())


class TACCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = TermsAndCondition
    template_name = 'tac_add.html'
    form_class = TACForm
    success_message = 'Terms and condition successfully added'

    def get_context_data(self, **kwargs):
        data = super(TACCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'tac'
        data['permissions'] = Permission.objects.all()
        return data

    def get_success_url(self):
        return reverse_lazy('tac-list')


class SectorCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Sector
    template_name = 'sector_add.html'
    form_class = SectorCreateForm
    success_message = 'Sector successfully Created'

    def get_context_data(self, **kwargs):
        data = super(SectorCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'sector'
        return data

    def get_success_url(self):
        return reverse_lazy('sector-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "New sector " + self.object.name + \
            "  has been added by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class OutputCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Output
    template_name = 'output_add.html'
    form_class = OutputCreateForm
    success_message = 'Sector successfully Created'

    def get_context_data(self, **kwargs):
        data = super(OutputCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'output'
        return data

    def get_success_url(self):
        return reverse_lazy('output-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "New ouput " + self.object.indicator + \
            "  has been added by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class FiveCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = FiveW
    template_name = 'five_adds.html'
    form_class = FiveCreateForm
    success_message = 'Five W successfully Created'

    def get_context_data(self, **kwargs):
        data = super(FiveCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        group = Group.objects.get(user=user)
        if group.name == 'admin':
            partner = Partner.objects.order_by('id')
            program = Program.objects.values(
                'id', 'name', 'partner_id__id').order_by('id')
            project = Project.objects.values(
                'id', 'name', 'program_id__id', 'partner_id__id').order_by('id')
        else:
            partner = Partner.objects.filter(
                id=user_data.partner.id).order_by('id')
            program = Program.objects.filter(id=user_data.program.id).values('id', 'name', 'partner_id__id').order_by(
                'id')
            project = Project.objects.filter(id=user_data.project.id).values('id', 'name', 'program_id__id',
                                                                             'partner_id__id').order_by('id')

        all_partner = Partner.objects.order_by('id')
        province = Province.objects.values(
            'id', 'name', 'code').exclude(code=-1).order_by('id')
        district = District.objects.values(
            'id', 'name', 'province_id__id', 'code').exclude(code=-1).order_by('id')
        municipality = GapaNapa.objects.values(
            'id', 'name', 'district_id__id', 'code').exclude(code=-1).order_by('id')
        province_minus_id = Province.objects.get(code=-1)
        district_minus_id = District.objects.get(code=-1)
        municipality_minus_id = GapaNapa.objects.get(code=-1)
        contact = PartnerContact.objects.values('id', 'name').order_by('id')
        data['user'] = user_data
        data['partners'] = partner
        data['programs'] = program
        data['projects'] = project
        data['all_partner'] = all_partner
        data['provinces'] = province
        data['districts'] = district
        data['pr'] = province_minus_id.id
        data['dr'] = district_minus_id.id
        data['mr'] = municipality_minus_id.id
        data['municipalities'] = municipality
        data['contacts'] = contact
        return data

    def get_success_url(self):
        return reverse_lazy('five-list')

    def form_valid(self, form):
        # contract_id = self.request.POST['contract_value_id']
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        # if contract_id == '0':
        #     data_filter = budget_to_second_tier = BudgetToSecondTier.objects.filter(
        #         supplier_id_id=self.request.POST['supplier_id'],
        #         second_tier_partner_id=self.request.POST['second_tier_partner'],
        #         program_id_id=self.request.POST['program_id'],
        #         component_id_id=self.request.POST['component_id'], )
        #
        #     print(data_filter.count())
        #     if data_filter.count() == 0:
        #         budget_to_second_tier = BudgetToSecondTier.objects.create(
        #             supplier_id_id=self.request.POST['supplier_id'],
        #             second_tier_partner_id=self.request.POST['second_tier_partner'],
        #             program_id_id=self.request.POST['program_id'],
        #             component_id_id=self.request.POST['component_id'],
        #             contract_value=self.request.POST['contract_value'])
        #
        #
        #
        # else:
        #     budget_to_second_tier = BudgetToSecondTier.objects.filter(id=contract_id).update(
        #         contract_value=self.request.POST['contract_value'])

        message = "New Five W " + \
            str(self.object.supplier_id) + \
            "  has been added by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class ProjectCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'project_add.html'
    form_class = ProjectCreateForm
    success_message = 'Project successfully Created'

    def get_context_data(self, **kwargs):
        data = super(ProjectCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['programs'] = Program.objects.order_by('name')
        data['partners'] = Partner.objects.order_by('name')
        sectors = Sector.objects.all().prefetch_related('Sector').order_by('id')
        data['sectors'] = sectors
        data['user'] = user_data
        data['active'] = 'project'
        for test in Program.objects.all():
            for test2 in test.partner_id.all():
                print(test2.id)
        return data

    def get_success_url(self):
        return reverse_lazy('project-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "New project " + self.object.name + \
            "  has been added by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class CmpCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'cmp_add.html'
    form_class = CmpForm
    success_message = 'Cmp successfully Created'

    def get_context_data(self, **kwargs):
        data = super(CmpCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        province = Province.objects.values('id', 'name').order_by('id')
        data['provinces'] = province
        data['user'] = user_data
        data['active'] = 'cmp'
        return data

    def get_success_url(self):
        return reverse_lazy('cmp-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "New cmp " + self.object.project_name + \
            "  has been added by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class PermissionCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Permission
    template_name = 'permission_add.html'
    form_class = PermissionForm
    success_message = 'Permission successfully Created'

    def get_context_data(self, **kwargs):
        data = super(PermissionCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'permission'
        return data

    def get_success_url(self):
        return reverse_lazy('permission-list')

    # def form_valid(self, form):
    #     self.object = form.save()
    #     message = "New project " + self.object.name + "  has been added by " + self.request.user.username
    #     log = Log.objects.create(user=self.request.user, message=message, type="create")
    #     return HttpResponseRedirect(self.get_success_url())


class SubSectorCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = SubSector
    template_name = 'sub_sector_add.html'
    form_class = SubSectorCreateForm
    success_message = 'Sub Sector successfully Created'

    def get_context_data(self, **kwargs):
        data = super(SubSectorCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['sectors'] = Sector.objects.order_by('id')
        data['active'] = 'sector'
        return data

    def get_success_url(self):
        return reverse_lazy('subsector-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "New Sub Sector " + self.object.name + \
            "  has been added by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class ProvinceCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Province
    template_name = 'province_add.html'
    form_class = ProvinceCreateForm
    success_message = 'Province successfully Created'

    def get_context_data(self, **kwargs):
        data = super(ProvinceCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'location'
        return data

    def get_success_url(self):
        return reverse_lazy('province-list')

    def form_valid(self, form):
        self.object = form.save()
        message = "New province " + self.object.name + \
            "  has been added by " + self.request.user.username
        log = Log.objects.create(
            user=self.request.user, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class DistrictCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = District
    template_name = 'district_add.html'
    form_class = DistrictCreateForm
    success_message = 'District successfully Created'

    def get_context_data(self, **kwargs):
        data = super(DistrictCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['province'] = Province.objects.values('id', 'name').order_by('id')
        data['active'] = 'location'
        return data

    def get_success_url(self):
        return reverse_lazy('district-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "New District " + self.object.name + \
            "  has been added by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class PalilkaCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = GapaNapa
    template_name = 'palika_add.html'
    form_class = PalikaCreateForm
    success_message = 'Palika successfully Created'

    def get_context_data(self, **kwargs):
        data = super(PalilkaCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['province'] = Province.objects.values('id', 'name').order_by('id')
        data['district'] = District.objects.values(
            'id', 'name', 'province_id__id').order_by('id')
        data['active'] = 'location'
        return data

    def get_success_url(self):
        return reverse_lazy('palika-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "New Municipality " + self.object.name + \
            "  has been added by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class MarkerValueCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = MarkerValues
    template_name = 'marker_value_add.html'
    form_class = MarkerValueCreateForm
    success_message = 'Marker Value successfully Created'

    def get_context_data(self, **kwargs):
        data = super(MarkerValueCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['sectors'] = MarkerCategory.objects.order_by('id')
        data['active'] = 'marker'
        return data

    def get_success_url(self):
        return reverse_lazy('markervalue-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "New Marker Value " + self.object.value + \
            "  has been added by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class MarkerCategoryCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = MarkerCategory
    template_name = 'marker_cat_add.html'
    form_class = MarkerCategoryCreateForm
    success_message = 'Marker successfully Created'

    def get_context_data(self, **kwargs):
        data = super(MarkerCategoryCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'marker'
        return data

    def get_success_url(self):
        return reverse_lazy('marker-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "New Marker Category " + self.object.name + \
            "  has been added by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class IndicatorCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Indicator
    template_name = 'indicator_add.html'
    form_class = IndicatorCreateForm
    success_message = 'Indicator successfully Created'

    def get_context_data(self, **kwargs):
        data = super(IndicatorCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'indicator'
        return data

    def get_success_url(self):
        return reverse_lazy('indicator-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "New Indicator " + self.object.name + \
            "  has been added by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class BudgetCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = Program
    template_name = 'budget_add.html'
    form_class = BudgetCreateForm
    success_message = 'Budget successfully Created'

    def get_context_data(self, **kwargs):
        data = super(BudgetCreate, self).get_context_data(**kwargs)
        program = Program.objects.all().order_by('id')
        project = Project.objects.all().order_by('id')
        partners = Partner.objects.all().order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['programs'] = program
        data['projects'] = project
        data['partners'] = partners
        data['active'] = 'budget'
        return data

    def get_success_url(self):
        return reverse_lazy('budget-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "New Budget For " + self.object.supplier_id.name + \
            "  has been added by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class ProgramUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Program
    template_name = 'program_edit.html'
    form_class = ProgramCreateForm
    success_message = 'Program successfully updated'

    def get_context_data(self, **kwargs):
        data = super(ProgramUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        marker_list = Program.objects.filter(
            id=self.kwargs['pk']).values_list('marker_category', flat=True)
        if (marker_list[0] == None):
            filter_marker = MarkerCategory.objects.order_by('id')
        else:
            filter_marker = MarkerCategory.objects.exclude(id__in=marker_list)
        sector_list = Program.objects.filter(
            id=self.kwargs['pk']).values_list('sector', flat=True)

        if (sector_list[0] == None):
            filter_sector = Sector.objects.order_by('id')

        else:
            filter_sector = Sector.objects.exclude(id__in=sector_list)

        data['sectors'] = filter_sector
        data['markers'] = filter_marker
        data['user'] = user_data
        data['active'] = 'program'

        # program = Program.objects.get(id=self.kwargs['pk'])
        partners = Partner.objects.order_by('name')
        # datatoselect = []
        # datanottoselect = []
        # for data in partners:
        #     for data1 in program.partner_id.all():
        #         if data.id == data1.id:
        #             datatoselect.append(data1)
        # # # datatoselect = set(datatoselect)
        # # for test in partners:
        # #     if test.name not in datatoselect:
        # #         datanottoselect.append(test)
        # # # datanottoselect = set(datanottoselect)
        # # print("datatoselect")
        # # print(datatoselect)
        # # print("datanottoselect")
        # # print(datanottoselect)
        # #
        # # # data['datatoselect'] = datatoselect
        # # # data['datanottoselect'] = datanottoselect
        data['partners'] = partners
        # data['programs'] = program
        return data

    def get_success_url(self):
        return reverse_lazy('program-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "Program " + self.object.name + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="update")
        return HttpResponseRedirect(self.get_success_url())


class PartnerUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Partner
    template_name = 'partner_edit.html'
    form_class = PartnerCreateForm
    success_message = 'Partner successfully updated'

    def get_context_data(self, **kwargs):
        data = super(PartnerUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        partner = Partner.objects.order_by('id')
        data['user'] = user_data
        data['active'] = 'partner'
        data['partner'] = partner
        return data

    def get_success_url(self):
        return reverse_lazy('partner-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "Partner " + self.object.name + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="update")
        return HttpResponseRedirect(self.get_success_url())


class CmpUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Cmp
    template_name = 'cmp_edit.html'
    form_class = CmpForm
    success_message = 'Cmp successfully Created'

    def get_context_data(self, **kwargs):
        data = super(CmpUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        province = Province.objects.values('id', 'name').order_by('id')
        district = District.objects.values('id', 'name').order_by('id')
        municipality = GapaNapa.objects.values('id', 'name').order_by('id')
        data['provinces'] = province
        data['districts'] = district
        data['municipalities'] = municipality
        data['user'] = user_data
        data['active'] = 'cmp'
        return data

    def get_success_url(self):
        return reverse_lazy('cmp-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "In cmp " + self.object.project_name + \
            "  has been edit by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="update")
        return HttpResponseRedirect(self.get_success_url())


class PartnerContactUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = PartnerContact
    template_name = 'partnerContact_edit.html'
    form_class = PartnerContactForm
    success_message = 'Partner Contact successfully updated'

    def get_context_data(self, **kwargs):
        data = super(PartnerContactUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'partner'
        return data

    def get_success_url(self):
        return reverse_lazy('partner-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "Partner contact" + self.object.name + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="update")
        return HttpResponseRedirect(self.get_success_url())


class FAQUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = FAQ
    template_name = 'faq_edit.html'
    form_class = FAQForm
    success_message = 'FAQ successfully updated'

    def get_context_data(self, **kwargs):
        data = super(FAQUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'faq'
        data['permissions'] = Permission.objects.all()
        return data

    def get_success_url(self):
        return reverse_lazy('faq-list')


class NSUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = NationalStatistic
    template_name = 'ns_edit.html'
    form_class = NSForm
    success_message = 'National Statistic successfully updated'

    def get_context_data(self, **kwargs):
        data = super(NSUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'ns'
        data['permissions'] = Permission.objects.all()
        return data

    def get_success_url(self):
        return reverse_lazy('ns-list')


class ManualUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Manual
    template_name = 'manual_edit.html'
    form_class = ManualForm
    success_message = 'Manuals successfully updated'

    def get_context_data(self, **kwargs):
        data = super(ManualUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'man'
        data['permissions'] = Permission.objects.all()
        return data

    def get_success_url(self):
        return reverse_lazy('manual-list')


class TACUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = TermsAndCondition
    template_name = 'tac_edit.html'
    form_class = TACForm
    success_message = 'Terms and condition successfully updated'

    def get_context_data(self, **kwargs):
        data = super(TACUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'tac'
        data['permissions'] = Permission.objects.all()
        return data

    def get_success_url(self):
        return reverse_lazy('tac-list')


class RoleUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Group
    template_name = 'edit_role.html'
    form_class = GroupForm
    success_message = 'Role successfully updated'

    def get_context_data(self, **kwargs):
        data = super(RoleUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'role'
        data['permissions'] = Permission.objects.all()
        return data

    def get_success_url(self):
        return reverse_lazy('role-list')

    # def form_valid(self, form):
    #     self.object = form.save()
    #     message = "Partner " + self.object.name + "  has been edited by " + self.request.user.username
    #     log = Log.objects.create(user=self.request.user, message=message, type="update")
    #     return HttpResponseRedirect(self.get_success_url())


class OutputUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Output
    template_name = 'output_edit.html'
    form_class = OutputCreateForm
    success_message = 'Sector successfully Created'

    def get_context_data(self, **kwargs):
        data = super(OutputUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'output'
        return data

    def get_success_url(self):
        return reverse_lazy('output-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "Output " + self.object.indicator + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="update")
        return HttpResponseRedirect(self.get_success_url())


class FiveUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = FiveW
    template_name = 'five_edits.html'
    form_class = FiveCreateForm
    success_message = 'Five W successfully Created'

    def get_context_data(self, **kwargs):
        data = super(FiveUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        group = Group.objects.get(user=user)
        if group.name == 'admin':
            partner = Partner.objects.order_by('id')
            program = Program.objects.values(
                'id', 'name', 'partner_id__id').order_by('id')
            project = Project.objects.values(
                'id', 'name', 'program_id__id', 'partner_id__id').order_by('id')
        else:
            partner = Partner.objects.filter(
                id=user_data.partner.id).order_by('id')
            program = Program.objects.filter(id=user_data.program.id).values('id', 'name', 'partner_id__id').order_by(
                'id')
            project = Project.objects.filter(id=user_data.project.id).values('id', 'name', 'program_id__id',
                                                                             'partner_id__id').order_by('id')
        province = Province.objects.values('id', 'name', 'code').order_by('id')
        district = District.objects.values(
            'id', 'name', 'province_id__id', 'code').order_by('id')
        municipality = GapaNapa.objects.values(
            'id', 'name', 'district_id__id', 'code').order_by('id')
        province_minus_id = Province.objects.get(code=-1)
        district_minus_id = District.objects.get(code=-1)
        municipality_minus_id = GapaNapa.objects.get(code=-1)
        contact = PartnerContact.objects.all().order_by('id')
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['partners'] = partner
        data['programs'] = program
        data['projects'] = project
        data['pr'] = province_minus_id.id
        data['dr'] = district_minus_id.id
        data['mr'] = municipality_minus_id.id
        data['provinces'] = province
        data['districts'] = district
        data['municipalities'] = municipality
        data['contacts'] = contact
        return data

    def get_success_url(self):
        return reverse_lazy('five-list')

    def form_valid(self, form):
        # contract_id = self.request.POST['contract_value_id']
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        # if contract_id == '0':
        #     data_filter = budget_to_second_tier = BudgetToSecondTier.objects.filter(
        #         supplier_id_id=self.request.POST['supplier_id'],
        #         second_tier_partner_id=self.request.POST['second_tier_partner'],
        #         program_id_id=self.request.POST['program_id'],
        #         component_id_id=self.request.POST['component_id'], )
        #
        #     print(data_filter.count())
        #     if data_filter.count() == 0:
        #         budget_to_second_tier = BudgetToSecondTier.objects.create(
        #             supplier_id_id=self.request.POST['supplier_id'],
        #             second_tier_partner_id=self.request.POST['second_tier_partner'],
        #             program_id_id=self.request.POST['program_id'],
        #             component_id_id=self.request.POST['component_id'],
        #             contract_value=self.request.POST['contract_value'])
        #
        #
        #
        # else:
        #     budget_to_second_tier = BudgetToSecondTier.objects.filter(id=contract_id).update(
        #         contract_value=self.request.POST['contract_value'])
        message = "New Five W " + \
            str(self.object.supplier_id) + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class PermissionUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Permission
    template_name = 'permission_add.html'
    form_class = PermissionForm
    success_message = 'Permission successfully edited'

    def get_context_data(self, **kwargs):
        data = super(PermissionUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'permission'
        return data

    def get_success_url(self):
        return reverse_lazy('permission-list')


class SectorUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Sector
    template_name = 'sector_edit.html'
    form_class = SectorCreateForm
    success_message = 'Sector successfully Updated'

    def get_context_data(self, **kwargs):
        data = super(SectorUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'sector'
        return data

    def get_success_url(self):
        return reverse_lazy('sector-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "Sector " + self.object.name + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="update")
        return HttpResponseRedirect(self.get_success_url())


class ProjectUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'project_edit.html'
    form_class = ProjectCreateForm
    success_message = 'Project successfully Created'

    def get_context_data(self, **kwargs):
        data = super(ProjectUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['programs'] = Program.objects.order_by('name')
        sector_list = Project.objects.filter(
            id=self.kwargs['pk']).values_list('sector', flat=True)

        if (sector_list[0] == None):
            filter_sector = Sector.objects.order_by('id')

        else:
            filter_sector = Sector.objects.exclude(id__in=sector_list)

        data['sectors'] = filter_sector
        data['partners'] = Partner.objects.order_by('name')
        data['test'] = sector_list
        data['user'] = user_data
        data['active'] = 'project'
        data['selectpartner'] = Project.objects.filter(id=self.kwargs['pk'])
        return data

    def get_success_url(self):
        return reverse_lazy('project-list')

    def form_valid(self, form):
        self.object = form.save()
        user_data = UserProfile.objects.get(user=self.request.user)
        message = "Project " + self.object.name + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="update")
        return HttpResponseRedirect(self.get_success_url())


class SubSectorUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = SubSector
    template_name = 'sub_sector_edit.html'
    form_class = SubSectorCreateForm
    success_message = 'Sub Sector successfully Updated'

    def get_context_data(self, **kwargs):
        data = super(SubSectorUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['sectors'] = Sector.objects.order_by('id')
        data['active'] = 'sector'
        return data

    def get_success_url(self):
        return reverse_lazy('subsector-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "Sub sector " + self.object.name + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="update")
        return HttpResponseRedirect(self.get_success_url())


class MarkerCategoryUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = MarkerCategory
    template_name = 'marker_cat_edit.html'
    form_class = MarkerCategoryCreateForm
    success_message = 'Marker Category successfully Updated'

    def get_context_data(self, **kwargs):
        data = super(MarkerCategoryUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'marker'
        return data

    def get_success_url(self):
        return reverse_lazy('marker-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "Marker Category " + self.object.name + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="update")
        return HttpResponseRedirect(self.get_success_url())


class MarkerValueUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = MarkerValues
    template_name = 'marker_value_edit.html'
    form_class = MarkerValueCreateForm
    success_message = 'Marker Value successfully Updated'

    def get_context_data(self, **kwargs):
        data = super(MarkerValueUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['sectors'] = MarkerCategory.objects.order_by('id')
        data['active'] = 'marker'
        return data

    def get_success_url(self):
        return reverse_lazy('markervalue-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "Marker Value " + self.object.value + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="update")
        return HttpResponseRedirect(self.get_success_url())


class ProvinceUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Province
    template_name = 'province_edit.html'
    form_class = ProvinceCreateForm
    success_message = 'Province successfully Updated'

    def get_context_data(self, **kwargs):
        data = super(ProvinceUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'location'
        return data

    def get_success_url(self):
        return reverse_lazy('province-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "Province" + self.object.name + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="update")
        return HttpResponseRedirect(self.get_success_url())


class PalikaUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = GapaNapa
    template_name = 'palika_edit.html'
    form_class = PalikaCreateForm
    success_message = 'Palika successfully Updated'

    def get_context_data(self, **kwargs):
        data = super(PalilkaUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['province'] = Province.objects.order_by('id')
        data['active'] = 'location'
        return data

    def get_success_url(self):
        return reverse_lazy('palika-list')


class DistrictUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = District
    template_name = 'district_edit.html'
    form_class = DistrictCreateForm
    success_message = 'District successfully Updated'

    def get_context_data(self, **kwargs):
        data = super(DistrictUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['province'] = Province.objects.order_by('id')
        data['active'] = 'location'
        return data

    def get_success_url(self):
        return reverse_lazy('district-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "District " + self.object.name + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="update")
        return HttpResponseRedirect(self.get_success_url())


class PalilkaUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = GapaNapa
    template_name = 'palika_edit.html'
    form_class = PalikaCreateForm
    success_message = 'Palika successfully Updated'

    def get_context_data(self, **kwargs):
        data = super(PalilkaUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['province'] = Province.objects.values('id', 'name').order_by('id')
        data['district'] = District.objects.values('id', 'name').order_by('id')
        data['active'] = 'location'
        return data

    def get_success_url(self):
        return reverse_lazy('palika-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "Municipality " + self.object.name + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="update")
        return HttpResponseRedirect(self.get_success_url())


class IndicatorUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = Indicator
    template_name = 'indicator_edit.html'
    form_class = IndicatorCreateForm
    success_message = 'Indicator successfully Edited'

    def get_context_data(self, **kwargs):
        data = super(IndicatorUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'indicator'
        return data

    def get_success_url(self):
        return reverse_lazy('indicator-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "Indicator " + self.object.indicator + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="update")
        return HttpResponseRedirect(self.get_success_url())


class GisLayerUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = GisLayer
    template_name = 'gis_layer_edit.html'
    form_class = GisLayerCreateForm
    success_message = 'Map Layer successfully Edited'

    def get_context_data(self, **kwargs):
        data = super(GisLayerUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['active'] = 'gis'
        return data

    def get_success_url(self):
        return reverse_lazy('gis-layer-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = "Map Layer " + self.object.name + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="update")
        return HttpResponseRedirect(self.get_success_url())


class BudgetUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = BudgetToFirstTier
    template_name = 'budget_edit.html'
    form_class = BudgetCreateForm
    success_message = 'Budget edited Created'

    def get_context_data(self, **kwargs):
        data = super(BudgetUpdate, self).get_context_data(**kwargs)
        program = Program.objects.all().order_by('id')
        project = Project.objects.all().order_by('id')
        partners = Partner.objects.all().order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['programs'] = program
        data['projects'] = project
        data['partners'] = partners
        data['active'] = 'budget'
        return data

    def get_success_url(self):
        return reverse_lazy('budget-list')

    def form_valid(self, form):
        user_data = UserProfile.objects.get(user=self.request.user)
        self.object = form.save()
        message = " Budget For " + self.object.supplier_id.name + \
            "  has been edited by " + self.request.user.username
        log = Log.objects.create(
            user=user_data, message=message, type="create")
        return HttpResponseRedirect(self.get_success_url())


class ProgramDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Program
    template_name = 'program_confirm_delete.html'
    success_message = 'Program successfully deleted'

    # success_url = reverse_lazy('program-list')

    def get_context_data(self, **kwargs):
        data = super(ProgramDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data

    def get_success_url(self):
        return reverse_lazy('program-list')


class UserDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'user_delete.html'
    success_message = 'User successfully deleted'
    success_url = reverse_lazy('user-list')

    # success_url = reverse_lazy('program-list')

    def get_context_data(self, **kwargs):
        data = super(UserDelete, self).get_context_data(**kwargs)
        user_list = UserProfile.objects.order_by('id')
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = user_list
        data['user'] = user_data
        data['active'] = 'user'
        return data

    def delete(self, request, *args, **kwargs):
        messages.info(self.request, self.success_message)
        return super(UserDelete, self).delete(request, *args, **kwargs)


class FiveDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = FiveW
    template_name = 'five_delete.html'
    success_message = 'Row successfully deleted'
    success_url = reverse_lazy('five-list')

    def delete(self, request, *args, **kwargs):
        messages.info(self.request, self.success_message)
        return super(FiveDelete, self).delete(request, *args, **kwargs)


class PartnerDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Partner
    template_name = 'partner_confirm_delete.html'
    success_message = 'Partner successfully deleted'
    success_url = reverse_lazy('partner-list')

    def get_context_data(self, **kwargs):
        data = super(PartnerDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data


class PartnerContactDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = PartnerContact
    template_name = 'partnerContact_confirm_delete.html'
    success_message = 'Partner successfully deleted'
    success_url = reverse_lazy('partner-list')

    def get_context_data(self, **kwargs):
        data = super(PartnerContactDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data


class SectorDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Sector
    template_name = 'sector_confirm_delete.html'
    success_message = 'Sector successfully deleted'
    success_url = reverse_lazy('sector-list')

    def get_context_data(self, **kwargs):
        data = super(SectorDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data


class SubSectorDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = SubSector
    template_name = 'sub_sector_confirm_delete.html'
    success_message = 'Sub Sector successfully deleted'
    success_url = reverse_lazy('subsector-list')

    def get_context_data(self, **kwargs):
        data = super(SubSectorDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data


class ProjectDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'project_confirm_delete.html'
    success_message = 'Project successfully deleted'
    success_url = reverse_lazy('project-list')

    def get_context_data(self, **kwargs):
        data = super(ProjectDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data

    # def delete(self, request, *args, **kwargs):
    #     delete_data = Project.objects.filter(id=kwargs['pk']).delete()
    #     message = "Project  has been deleted by " + self.request.user.username
    #     log = Log.objects.create(user=self.request.user, message=message, type="delete")
    #     return redirect('project-list')


class MarkerCategoryDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = MarkerCategory
    template_name = 'marker_cat_confirm_delete.html'
    success_message = 'Marker category successfully deleted'
    success_url = reverse_lazy('marker-list')

    def get_context_data(self, **kwargs):
        data = super(MarkerCategoryDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data


class MarkerValueDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = MarkerValues
    template_name = 'marker_value_confirm_delete.html'
    success_message = 'Marker category successfully deleted'
    success_url = reverse_lazy('markervalue-list')

    def get_context_data(self, **kwargs):
        data = super(MarkerValueDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data


class PermissionDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Permission
    template_name = 'permission_confirm_delete.html'
    success_message = 'Permission successfully deleted'
    success_url = reverse_lazy('permission-list')

    def get_context_data(self, **kwargs):
        data = super(PermissionDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data


class RoleDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Group
    template_name = 'role_confirm_delete.html'
    success_message = 'Permission successfully deleted'
    success_url = reverse_lazy('role-list')

    def get_context_data(self, **kwargs):
        data = super(RoleDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data


class FAQDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = FAQ
    template_name = 'faq_confirm_delete.html'
    success_message = 'FAQ successfully deleted'
    success_url = reverse_lazy('faq-list')

    def get_context_data(self, **kwargs):
        data = super(FAQDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data

    def delete(self, request, *args, **kwargs):
        messages.info(self.request, self.success_message)
        return super(FAQDelete, self).delete(request, *args, **kwargs)


class TACDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = TermsAndCondition
    template_name = 'tac_confirm_delete.html'
    success_message = 'Terms and condition successfully deleted'
    success_url = reverse_lazy('tac-list')

    def get_context_data(self, **kwargs):
        data = super(TACDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data

    def delete(self, request, *args, **kwargs):
        messages.info(self.request, self.success_message)
        return super(TACDelete, self).delete(request, *args, **kwargs)


class ProvinceDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Province
    template_name = 'province_confirm_delete.html'
    success_message = 'Province successfully deleted'
    success_url = reverse_lazy('province-list')

    def get_context_data(self, **kwargs):
        data = super(ProvinceDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data


class DistrictDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = District
    template_name = 'district_confirm_delete.html'
    success_message = 'District successfully deleted'
    success_url = reverse_lazy('district-list')

    def get_context_data(self, **kwargs):
        data = super(DistrictDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data


class PalikaDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = GapaNapa
    template_name = 'palika_confirm_delete.html'
    success_message = 'Plaika successfully deleted'
    success_url = reverse_lazy('palika-list')

    def get_context_data(self, **kwargs):
        data = super(PalikaDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data


class IndicatorDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Indicator
    template_name = 'indicator_confirm_delete.html'
    success_message = 'Indicator successfully deleted'
    success_url = reverse_lazy('indicator-list')

    def get_context_data(self, **kwargs):
        data = super(IndicatorDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data


class BudgetDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = BudgetToFirstTier
    template_name = 'budget_confirm_delete.html'
    success_message = 'Budget successfully deleted'
    success_url = reverse_lazy('budget-list')

    def get_context_data(self, **kwargs):
        data = super(BudgetDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data


class CmpDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = Cmp
    template_name = 'cmp_confirm_delete.html'
    success_message = 'Cmp successfully deleted'
    success_url = reverse_lazy('cmp-list')

    def get_context_data(self, **kwargs):
        data = super(CmpDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data


def gisLayer_create(request):
    template_name = 'gis_add.html'
    form = GisLayerCreateForm(request.POST or None)
    user_data = UserProfile.objects.get(user=request.user)
    if form.is_valid():

        shapefile = request.FILES["shapefile"]
        named = request.POST["name"]
        store_named = request.POST["filename"]
        store_name = store_named.replace(
            " ", "_").lower() + str(randint(0, 99999))

        # return HttpResponse(layer_name)

        if request.POST['type'] == 'vector':

            url = 'http://139.59.67.104:8080/geoserver/rest/workspaces/Naxa/datastores/' + \
                store_name + '/file.shp'
            headers = {
                'Content-type': 'application/zip',
            }
            response = requests.put(
                url, headers=headers, data=shapefile, auth=('admin', 'geoserver'))

        else:

            url = 'http://139.59.67.104:8080/geoserver/rest/workspaces/Naxa/coveragestores/' + \
                store_name + '/file.geotiff'
            headers = {
                'Content-type': 'application/zip',
            }
            response = requests.put(
                url, headers=headers, data=shapefile, auth=('admin', 'geoserver'))
            # return HttpResponse(response)

        if response.status_code == 201:
            zipfile = ZipFile(shapefile)
            names = zipfile.namelist()
            layer_name = os.path.splitext(names[0])[0]
            obj = form.save(commit=False)
            obj.workspace = 'Naxa'
            obj.layer_name = layer_name
            obj.store_name = store_name
            obj.geoserver_url = 'http://139.59.67.104:8080/geoserver/gwc/service/tms/1.0.0/Naxa:' + \
                layer_name + '@EPSG%3A900913@pbf/{z}/{x}/{-y}.pbf'

            obj.save()
            messaged = "Map Layer " + named + "  has been added by " + request.user.username
            log = Log.objects.create(
                user=user_data, message=messaged, type="create")
            messages.success(request, "Layer successfully uploaded")

        else:
            messages.error(
                request, "Layer could not be  uploaded !! Please Try again")

        return redirect('gis-layer-list')
    return render(request, template_name, {'form': form, 'user': user_data})


def gisLayer_replace(request, **kwargs):
    template_name = 'gis_replace.html'
    user_data = UserProfile.objects.get(user=request.user)
    instance = GisLayer.objects.get(id=kwargs['pk'])
    get_store_name = GisLayer.objects.filter(
        id=kwargs['pk']).values_list('store_name', flat=True)
    form = GisLayerCreateForm(request.POST or None, instance=instance)
    # return HttpResponse(instance.store_name)

    if form.is_valid():

        shapefile = request.FILES["shapefile"]
        named = request.POST["name"]
        store_named = request.POST["filename"]
        store_names = store_named.replace(
            " ", "_").lower() + str(randint(0, 99999999))

        # return HttpResponse(instance.layer_name)

        if request.POST['type'] == 'vector':

            store_check_url = 'http://139.59.67.104:8080/geoserver/rest/workspaces/Naxa/datastores/' + get_store_name[
                0] + '?recurse=true'

            headers = {
                'Content-type': '',
            }
            response = requests.delete(
                store_check_url, headers=headers, auth=('admin', 'geoserver'))
            # return HttpResponse(response.status_code)

            url = 'http://139.59.67.104:8080/geoserver/rest/workspaces/Naxa/datastores/' + \
                store_names + '/file.shp'
            headers = {
                'Content-type': 'application/zip',
            }
            response = requests.put(
                url, headers=headers, data=shapefile, auth=('admin', 'geoserver'))

        else:

            store_check_url = 'http://139.59.67.104:8080/geoserver/rest/workspaces/Naxa/coveragestores/' + \
                              get_store_name[0] + '?recurse=true'
            headers = {
                'Content-type': '',
            }
            requests.delete(store_check_url, headers=headers,
                            auth=('admin', 'geoserver'))

            url = 'http://139.59.67.104:8080/geoserver/rest/workspaces/Naxa/coveragestores/' + \
                store_names + '/file.geotiff'
            headers = {
                'Content-type': 'application/zip',
            }
            response = requests.put(
                url, headers=headers, data=shapefile, auth=('admin', 'geoserver'))
            # return HttpResponse(response)

        if response.status_code == 201:
            zipfile = ZipFile(shapefile)
            names = zipfile.namelist()
            layer_name = os.path.splitext(names[0])[0]
            obj = form.save(commit=False)
            obj.workspace = 'Naxa'
            obj.store_name = store_names
            obj.layer_name = layer_name
            obj.geoserver_url = 'http://139.59.67.104:8080/geoserver/gwc/service/tms/1.0.0/Naxa:' + \
                layer_name + '@EPSG%3A900913@pbf/{z}/{x}/{-y}.pbf'

            obj.save()
            messaged = "Map Layer " + named + "  has been edited by " + request.user.username
            log = Log.objects.create(
                user=user_data, message=messaged, type="edited")
            messages.success(request, "Layer successfully replaced")

        else:
            messages.error(
                request, "Layer could not be  replaced !! Please Try again")

        return redirect('gis-layer-list')
    return render(request, template_name, {'form': form, 'user': user_data})


def gisLayer_delete(request, **kwargs):
    get_store_name = GisLayer.objects.filter(
        id=kwargs['pk']).values_list('store_name', flat=True)
    type = GisLayer.objects.filter(
        id=kwargs['pk']).values_list('type', flat=True)

    if type[0] == 'vector':
        store = 'datastores'
    else:
        store = 'coveragestores'

    store_check_url = 'http://139.59.67.104:8080/geoserver/rest/workspaces/Naxa/' + store + '/' + get_store_name[
        0] + '?recurse=true'

    headers = {
        'Content-type': '',
    }
    response = requests.get(
        store_check_url, headers=headers, auth=('admin', 'geoserver'))

    if response.status_code == 200:

        delete_url = 'http://139.59.67.104:8080/geoserver/rest/workspaces/Naxa/' + store + '/' + get_store_name[
            0] + '?recurse=true'

        headers = {
            'Content-type': '',
        }
        delete_response = requests.delete(
            delete_url, headers=headers, auth=('admin', 'geoserver'))

        if delete_response.status_code == 200:
            delete = GisLayer.objects.filter(id=kwargs['pk']).delete()

        else:
            messages.success(request, "Layer could not be deleted")
            return redirect('gis-layer-list')
    else:

        delete = GisLayer.objects.filter(id=kwargs['pk']).delete()

    if delete:
        messages.success(request, "Layer successfully deleted")
        return redirect('gis-layer-list')
    else:
        messages.success(request, "Layer could not be Deleted")
        return redirect('gis-layer-list')


class StyleList(LoginRequiredMixin, ListView):
    template_name = 'gis_layer_style_list.html'
    model = GisStyle

    def get_context_data(self, **kwargs):
        data = super(StyleList, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        style = GisStyle.objects.filter(layer__id=self.kwargs['pk'])
        data['id'] = self.kwargs['pk']
        data['list'] = style
        data['user'] = user_data
        data['active'] = 'style'
        return data


class StyleCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = GisStyle
    template_name = 'gis_layer_style_add.html'
    form_class = GisStyleForm
    success_message = 'Style successfully Created'

    def get_context_data(self, **kwargs):
        data = super(StyleCreate, self).get_context_data(**kwargs)
        layer = GisLayer.objects.get(id=self.kwargs['pk'])
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['layer'] = layer
        data['active'] = 'style'
        return data

    def get_success_url(self):
        return "/dashboard/gis_style_layer_list/" + str(self.kwargs['pk'])


class StyleUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = GisStyle
    template_name = 'gis_layer_style_update.html'
    form_class = GisStyleForm
    success_message = 'Style successfully updated'

    def get_context_data(self, **kwargs):
        data = super(StyleUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        id_gis = GisStyle.objects.get(id=self.kwargs['pk'])
        print(id_gis.layer.id)
        layers = GisLayer.objects.all()
        data['layers'] = layers
        data['user'] = user_data
        data['active'] = 'style'
        return data

    def get_success_url(self):
        id_gis = GisStyle.objects.get(id=self.kwargs['pk'])
        return "/dashboard/gis_style_layer_list/" + str(id_gis.layer.id)


class AboutUsList(LoginRequiredMixin, ListView):
    template_name = 'about_us_list.html'
    model = AboutUs

    def get_context_data(self, **kwargs):
        data = super(AboutUsList, self).get_context_data(**kwargs)
        about_us_list = AboutUs.objects.all()
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = about_us_list
        data['user'] = user_data
        return data


class ContactUsList(LoginRequiredMixin, ListView):
    template_name = 'contact_us_list.html'
    model = ContactUs

    def get_context_data(self, **kwargs):
        data = super(ContactUsList, self).get_context_data(**kwargs)
        contact_us_list = ContactUs.objects.all()
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['list'] = contact_us_list
        data['user'] = user_data
        return data


class AboutUsCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = AboutUs
    template_name = 'about_us_add.html'
    form_class = AboutUsForm
    success_message = 'About Us Successfully Added'

    def get_context_data(self, **kwargs):
        data = super(AboutUsCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['permissions'] = Permission.objects.all()
        return data

    def get_success_url(self):
        return reverse_lazy('about-us-list')


class ContactUsCreate(SuccessMessageMixin, LoginRequiredMixin, CreateView):
    model = ContactUs
    template_name = 'contact_us_add.html'
    form_class = ContactUsForm
    success_message = 'Contact Us Successfully Added'

    def get_context_data(self, **kwargs):
        data = super(ContactUsCreate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['permissions'] = Permission.objects.all()
        return data

    def get_success_url(self):
        return reverse_lazy('contact-us-list')


class AboutUsUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = AboutUs
    template_name = 'about_us_update.html'
    form_class = AboutUsForm
    success_message = 'About Us  Successfully Updated'

    def get_context_data(self, **kwargs):
        data = super(AboutUsUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['permissions'] = Permission.objects.all()
        return data

    def get_success_url(self):
        return reverse_lazy('about-us-list')


class ContactUsUpdate(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = ContactUs
    template_name = 'contact_us_update.html'
    form_class = ContactUsForm
    success_message = 'Contact Us  Successfully Updated'

    def get_context_data(self, **kwargs):
        data = super(ContactUsUpdate, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        data['permissions'] = Permission.objects.all()
        return data

    def get_success_url(self):
        return reverse_lazy('contact-us-list')


class AboutUsDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = AboutUs
    template_name = 'about_us_confirm_delete.html'
    success_message = 'About us successfully deleted'
    success_url = reverse_lazy('about-us-list')

    def get_context_data(self, **kwargs):
        data = super(AboutUsDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data

    def delete(self, request, *args, **kwargs):
        messages.info(self.request, self.success_message)
        return super(AboutUsDelete, self).delete(request, *args, **kwargs)


class ContactUsDelete(SuccessMessageMixin, LoginRequiredMixin, DeleteView):
    model = AboutUs
    template_name = 'contact_us_confirm_delete.html'
    success_message = 'Contact Us successfully deleted'
    success_url = reverse_lazy('contact-us-list')

    def get_context_data(self, **kwargs):
        data = super(ContactUsDelete, self).get_context_data(**kwargs)
        user = self.request.user
        user_data = UserProfile.objects.get(user=user)
        data['user'] = user_data
        return data

    def delete(self, request, *args, **kwargs):
        messages.info(self.request, self.success_message)
        return super(ContactUsDelete, self).delete(request, *args, **kwargs)
