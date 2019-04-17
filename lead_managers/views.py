from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from lead_managers.models import LeadManager
from lead_managers.utils import TENANT_LEAD, HOUSE_OWNER_LEAD
from leads.models import TenantLead, HouseOwnerLead, LeadStatusCategory, LeadSourceCategory, TenantLeadSource, \
    HouseOwnerLeadSource
from utility.form_field_utils import get_number, get_datetime

LOGIN_URL = '/login/'


def is_lead_manager(user):
    return LeadManager.objects.filter(user=user).count()


lead_manager_login_test = user_passes_test(is_lead_manager, login_url=LOGIN_URL)


def lead_manager_login_required(view):
    decorated_view = login_required(lead_manager_login_test(view), login_url=LOGIN_URL)
    return decorated_view


def logout_view(request):
    logout(request)
    request.session.flush()
    request.user = AnonymousUser
    return HttpResponseRedirect(reverse(home_page))


def login_view(request):
    error_msg = None
    logout(request)
    if request.POST:
        username, password = request.POST['username'], request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if is_lead_manager(user):
                if user.is_active:
                    login(request, user)
                    next_page = request.GET.get('next')
                    if next_page:
                        return HttpResponseRedirect(next_page)
                    else:
                        return HttpResponseRedirect(reverse(home_page))
            else:
                error_msg = 'You are not a Leads Manager.'
        else:
            error_msg = 'Username and Password do not match.'
    return render(request, 'login_page.html', {'error': error_msg})


@lead_manager_login_required
@require_http_methods(['GET'])
def home_page(request):
    return render(request, 'home_page.html')


@lead_manager_login_required
@require_http_methods(['GET', 'POST'])
def new_lead_form_view(request):
    if request.method == 'GET':
        lead_source_categories = LeadSourceCategory.objects.filter(active=True).values_list('name', flat=True)
        return render(request, 'new_lead_form.html', {'lead_source_categories': lead_source_categories})

    if request.method == 'POST':
        lead_manager = LeadManager.objects.get(user=request.user)
        data = request.POST
        name = data.get('name')
        gender = data.get('gender')
        phone_no = data.get('phone_no')
        email = data.get('email')
        permanent_address = data.get('permanent_address')
        source_category = LeadSourceCategory.objects.filter(name=data.get('source_category')).first()
        source_name = data.get('source_name')

        if data['lead_type'] == TENANT_LEAD:
            expected_rent_min = get_number(data.get('expected_rent_min'))
            expected_rent_max = get_number(data.get('expected_rent_max'))
            expected_movein_start = get_datetime(data.get('expected_movein_start'))
            expected_movein_end = get_datetime(data.get('expected_movein_end'))
            space_type = data.get('space_type')
            space_subtype = data.get('space_subtype')
            preferred_location = data.get('preferred_location')
            accomodation_for = data.getlist('accomodation_for')
            lead = TenantLead.objects.create(name=name, gender=gender, phone_no=phone_no, email=email,
                                             expected_rent_min=expected_rent_min, expected_rent_max=expected_rent_max,
                                             expected_movein_start=expected_movein_start,
                                             expected_movein_end=expected_movein_end, space_type=space_type,
                                             space_subtype=space_subtype, accomodation_for=accomodation_for,
                                             created_by=lead_manager)
            lead.preferred_location.street_address = preferred_location
            lead.preferred_location.save()

        elif data['lead_type'] == HOUSE_OWNER_LEAD:
            house_type = data.get('house_type')
            furnish_type = data.get('furnish_type')
            accomodation_allowed = data.getlist('accomodation_allowed')
            current_stay_status = data.get('current_stay_status')
            bhk_count = get_number(data.get('bhk_count'))
            current_rent = get_number(data.get('current_rent'))
            current_security_deposit = get_number(data.get('current_security_deposit'))
            expected_rent = get_number(data.get('expected_rent'))
            expected_security_deposit = get_number(data.get('expected_security_deposit'))
            shared_rooms_count = get_number(data.get('shared_rooms_count'))
            total_beds_count = get_number(data.get('total_beds_count'))
            private_rooms_count = get_number(data.get('private_rooms_count'))
            flats_count = get_number(data.get('flats_count'))
            house_address = data.get('house_address')
            lead = HouseOwnerLead.objects.create(name=name, gender=gender, phone_no=phone_no, email=email,
                                                 house_type=house_type, furnish_type=furnish_type,
                                                 accomodation_allowed=accomodation_allowed,
                                                 current_stay_status=current_stay_status, bhk_count=bhk_count,
                                                 current_rent=current_rent,
                                                 current_security_deposit=current_security_deposit,
                                                 expected_rent=expected_rent,
                                                 expected_security_deposit=expected_security_deposit,
                                                 shared_rooms_count=shared_rooms_count,
                                                 total_beds_count=total_beds_count,
                                                 private_rooms_count=private_rooms_count, flats_count=flats_count,
                                                 created_by=lead_manager)
            lead.house_address.street_address = house_address
            lead.house_address.save()
        else:
            return JsonResponse({'detail': 'Wrong lead type'})

        lead.managed_by.add(lead_manager)
        lead.permanent_address.street_address = permanent_address
        lead.permanent_address.save()
        lead.source.category = source_category
        lead.source.name = source_name
        lead.source.save()

        return JsonResponse({'detail': 'done'})


@lead_manager_login_required
@require_http_methods(['GET'])
def leads_list_view(request):
    lead_manager = LeadManager.objects.get(user=request.user)
    lead_source_categories = LeadSourceCategory.objects.filter(active=True).values_list('name', flat=True)
    lead_status_categories = LeadStatusCategory.objects.all().order_by('level').values_list('name', flat=True)

    lead_type = request.GET.get('type')
    if lead_type == TENANT_LEAD:
        leads = TenantLead.objects.select_related('source', 'status', 'permanent_address', 'preferred_location'
                                                  ).filter(managed_by=lead_manager).order_by('-updated_at')
    elif lead_type == HOUSE_OWNER_LEAD:
        leads = HouseOwnerLead.objects.select_related('source', 'status', 'permanent_address', 'house_address'
                                                      ).filter(managed_by=lead_manager).order_by('-updated_at')
    else:
        leads = None
    return render(request, 'leads_list_page.html', {'lead_type': lead_type,
                                                    'leads': leads,
                                                    'lead_source_categories': lead_source_categories,
                                                    'lead_status_categories': lead_status_categories})


@lead_manager_login_required
@require_http_methods(['GET'])
def lead_manage_view(request):
    lead_manager = LeadManager.objects.get(user=request.user)
    lead_source_categories = LeadSourceCategory.objects.filter(active=True).values_list('name', flat=True)

    lead_type = request.GET.get('type')
    lead_id = get_number(request.GET.get('id'))

    if lead_type == TENANT_LEAD and lead_id:
        try:
            lead = TenantLead.objects.get(id=lead_id, managed_by=lead_manager)
        except TenantLead.DoesNotExist:
            return render(request, 'lead_manage_page.html', {'msg': "No such lead found!"})
    elif lead_type == HOUSE_OWNER_LEAD and lead_id:
        try:
            lead = HouseOwnerLead.objects.get(id=lead_id, managed_by=lead_manager)
        except HouseOwnerLead.DoesNotExist:
            return render(request, 'lead_manage_page.html', {'msg': "No such lead found!"})
    else:
        return render(request, 'lead_manage_page.html', {'msg': "No such lead found!"})

    return render(request, 'lead_manage_page.html', {'lead_type': lead_type,
                                                     'lead': lead,
                                                     'lead_source_categories': lead_source_categories})


@lead_manager_login_required
@require_http_methods(['POST'])
def lead_edit_form_view(request):
    lead_manager = LeadManager.objects.get(user=request.user)
    data = dict(request.POST)

    # convert 'None' to None
    for key, val in data.items():
        if val == ['None']:
            data[key] = None
        else:
            data[key] = val[0]

    lead_type = data.get('lead_type')
    lead_id = get_number(data.get('lead_id'))

    if lead_type == TENANT_LEAD and lead_id:
        try:
            lead = TenantLead.objects.get(id=lead_id, managed_by=lead_manager)
        except TenantLead.DoesNotExist:
            return JsonResponse({'detail': 'Lead not found'})
    elif lead_type == HOUSE_OWNER_LEAD and lead_id:
        try:
            lead = HouseOwnerLead.objects.get(id=lead_id, managed_by=lead_manager)
        except HouseOwnerLead.DoesNotExist:
            return JsonResponse({'detail': 'Lead not found'})
    else:
        return JsonResponse({'detail': 'Lead not found'})

    lead.name = data.get('name')
    lead.phone_no = data.get('phone_no')
    lead.gender = data.get('gender')
    lead.email = data.get('email')
    lead.save()

    if not hasattr(lead, 'source'):
        if lead_type == TENANT_LEAD:
            TenantLeadSource(lead=lead).save()
        elif lead_type == HOUSE_OWNER_LEAD:
            HouseOwnerLeadSource(lead=lead).save()
    lead.source.category = LeadSourceCategory.objects.filter(name=data.get('source_category')).first()
    lead.source.name = data.get('source_name')
    lead.source.save()

    lead.permanent_address.street_address = data.get('permanent_street_address')
    lead.permanent_address.city = data.get('permanent_city')
    lead.permanent_address.state = data.get('permanent_state')
    lead.permanent_address.country = data.get('permanent_country')
    lead.permanent_address.save()

    if lead_type == TENANT_LEAD:
        lead.space_type = data.get('space_type')
        lead.space_subtype = data.get('space_subtype')
        lead.accomodation_for = request.POST.getlist('accomodation_for')
        lead.expected_rent_min = data.get('expected_rent_min')
        lead.expected_rent_max = data.get('expected_rent_max')
        lead.expected_movein_start = data.get('expected_movein_start')
        lead.expected_movein_end = data.get('expected_movein_end')
        lead.save()

        lead.preferred_location.street_address = data.get('preferred_location_street_address')
        lead.preferred_location.city = data.get('preferred_location_city')
        lead.preferred_location.state = data.get('preferred_location_state')
        lead.preferred_location.country = data.get('preferred_location_country')
        lead.preferred_location.save()

    elif lead_type == HOUSE_OWNER_LEAD:
        lead.house_type = data.get('house_type')
        lead.furnish_type = data.get('furnish_type')
        lead.accomodation_allowed = request.POST.getlist('accomodation_allowed')
        lead.current_stay_status = data.get('current_stay_status')
        lead.bhk_count = get_number(data.get('bhk_count'))
        lead.current_rent = get_number(data.get('current_rent'))
        lead.current_security_deposit = get_number(data.get('current_security_deposit'))
        lead.expected_rent = get_number(data.get('expected_rent'))
        lead.expected_security_deposit = get_number(data.get('expected_security_deposit'))
        lead.shared_rooms_count = get_number(data.get('shared_rooms_count'))
        lead.total_beds_count = get_number(data.get('total_beds_count'))
        lead.private_rooms_count = get_number(data.get('private_rooms_count'))
        lead.flats_count = get_number(data.get('flats_count'))
        lead.save()

        lead.house_address.street_address = data.get('house_street_address')
        lead.house_address.city = data.get('house_city')
        lead.house_address.state = data.get('house_state')
        lead.house_address.country = data.get('house_country')
        lead.house_address.save()

    return JsonResponse({'detail': 'done'})
