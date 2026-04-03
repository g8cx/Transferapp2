import csv

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render

from cargo.models import Cargo
from companies.models import Company
from drivers.models import Driver
from vehicles.models import Vehicle
from waybills.models import Waybill, WaybillItem

from .forms import LoginForm, RegisterForm


VIEWER_GROUP_NAME = "waybill_viewers"


def can_view_saved_waybills(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name=VIEWER_GROUP_NAME).exists()
    )


def get_post_login_redirect(user):
    if can_view_saved_waybills(user) and not user.is_superuser:
        return "waybill_list"
    return "home"


def auth_page(request):
    if request.user.is_authenticated:
        return redirect(get_post_login_redirect(request.user))

    login_form = LoginForm(request, data=request.POST or None, prefix="login")
    register_form = RegisterForm(request.POST or None, prefix="register")

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "login" and login_form.is_valid():
            auth_login(request, login_form.get_user())
            messages.success(request, "Вы успешно вошли в систему.")
            return redirect(get_post_login_redirect(login_form.get_user()))
        if form_type == "login" and not login_form.is_valid():
            messages.error(request, "Неверное имя пользователя или пароль.")

        if form_type == "register" and register_form.is_valid():
            user = register_form.save()
            auth_login(request, user)
            messages.success(request, "Регистрация завершена. Добро пожаловать.")
            return redirect(get_post_login_redirect(user))

    return render(
        request,
        "auth.html",
        {
            "login_form": login_form,
            "register_form": register_form,
        },
    )


def login_page(request):
    if request.user.is_authenticated:
        return redirect(get_post_login_redirect(request.user))

    form = LoginForm(request, data=request.POST or None)
    next_url = request.POST.get("next") or request.GET.get("next") or "/home/"

    if request.method == "POST" and form.is_valid():
        auth_login(request, form.get_user())
        messages.success(request, "Вы успешно вошли в систему.")
        return redirect(next_url if next_url != "/home/" else get_post_login_redirect(form.get_user()))
    if request.method == "POST" and not form.is_valid():
        messages.error(request, "Неверное имя пользователя или пароль.")

    return render(request, "registration/login.html", {"form": form, "next": next_url})


def existing_users_login(request):
    if request.user.is_authenticated:
        return redirect(get_post_login_redirect(request.user))

    form = LoginForm(request, data=request.POST or None)
    next_url = request.POST.get("next") or request.GET.get("next") or "/home/"

    if request.method == "POST" and form.is_valid():
        auth_login(request, form.get_user())
        messages.success(request, "Вы успешно вошли в систему.")
        return redirect(next_url if next_url != "/home/" else get_post_login_redirect(form.get_user()))
    if request.method == "POST" and not form.is_valid():
        messages.error(request, "Неверное имя пользователя или пароль.")

    return render(request, "login_existing.html", {"form": form, "next": next_url})


def _clean_rows(values):
    return [value.strip() for value in values]


def _parse_int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 0


def _parse_float(value):
    normalized = str(value).strip().replace(",", ".")
    try:
        return float(normalized)
    except (TypeError, ValueError):
        return 0


def _build_waybill_queryset():
    return (
        Waybill.objects.select_related("sender", "receiver", "driver", "vehicle")
        .prefetch_related("waybillitem_set__cargo")
        .order_by("-date", "-id")
    )


def _write_waybill_rows(writer, waybills):
    writer.writerow(
        [
            "Номер накладной",
            "Дата составления",
            "Дата погрузки",
            "Дата доставки",
            "Грузоотправитель",
            "Адрес отправителя",
            "Телефон отправителя",
            "ИНН/КПП отправителя",
            "Грузополучатель",
            "Адрес получателя",
            "Телефон получателя",
            "ИНН/КПП получателя",
            "Транспорт",
            "Водитель",
            "Груз",
            "Вес",
            "Количество",
            "Примечание",
        ]
    )

    for waybill in waybills:
        items = list(waybill.waybillitem_set.all())
        if not items:
            writer.writerow(
                [
                    waybill.number,
                    waybill.date,
                    waybill.loading_date or "",
                    waybill.delivery_date or "",
                    waybill.sender.name,
                    waybill.sender.address,
                    waybill.sender.phone,
                    waybill.sender.tax_id,
                    waybill.receiver.name,
                    waybill.receiver.address,
                    waybill.receiver.phone,
                    waybill.receiver.tax_id,
                    str(waybill.vehicle),
                    waybill.driver.name,
                    "",
                    "",
                    "",
                    waybill.additional_info,
                ]
            )
            continue

        for item in items:
            writer.writerow(
                [
                    waybill.number,
                    waybill.date,
                    waybill.loading_date or "",
                    waybill.delivery_date or "",
                    waybill.sender.name,
                    waybill.sender.address,
                    waybill.sender.phone,
                    waybill.sender.tax_id,
                    waybill.receiver.name,
                    waybill.receiver.address,
                    waybill.receiver.phone,
                    waybill.receiver.tax_id,
                    str(waybill.vehicle),
                    waybill.driver.name,
                    item.cargo.name,
                    item.weight,
                    item.quantity,
                    waybill.additional_info,
                ]
            )


@login_required
def home(request):
    if can_view_saved_waybills(request.user) and not request.user.is_superuser:
        return redirect("waybill_list")

    if request.method == "POST":
        sender, _ = Company.objects.get_or_create(
            name=request.POST.get("shipper_name", "").strip(),
            address=request.POST.get("shipper_address", "").strip(),
            defaults={
                "phone": request.POST.get("shipper_phone", "").strip(),
                "tax_id": request.POST.get("shipper_tax_id", "").strip(),
            },
        )

        receiver, _ = Company.objects.get_or_create(
            name=request.POST.get("consignee_name", "").strip(),
            address=request.POST.get("consignee_address", "").strip(),
            defaults={
                "phone": request.POST.get("consignee_phone", "").strip(),
                "tax_id": request.POST.get("consignee_tax_id", "").strip(),
            },
        )

        if sender.phone != request.POST.get("shipper_phone", "").strip() or sender.tax_id != request.POST.get("shipper_tax_id", "").strip():
            sender.phone = request.POST.get("shipper_phone", "").strip()
            sender.tax_id = request.POST.get("shipper_tax_id", "").strip()
            sender.save(update_fields=["phone", "tax_id"])

        if receiver.phone != request.POST.get("consignee_phone", "").strip() or receiver.tax_id != request.POST.get("consignee_tax_id", "").strip():
            receiver.phone = request.POST.get("consignee_phone", "").strip()
            receiver.tax_id = request.POST.get("consignee_tax_id", "").strip()
            receiver.save(update_fields=["phone", "tax_id"])

        driver_name = request.POST.get("driver_name", "").strip() or "Не указан"
        driver, _ = Driver.objects.get_or_create(
            name=driver_name,
            defaults={"phone": ""},
        )

        vehicle_description = request.POST.get("vehicle_description", "").strip()
        vehicle, _ = Vehicle.objects.get_or_create(
            description=vehicle_description,
            defaults={"plate_number": "", "model": vehicle_description, "capacity": 0},
        )

        waybill = Waybill.objects.create(
            number=request.POST.get("waybill_number", "").strip(),
            date=request.POST.get("waybill_date"),
            loading_date=request.POST.get("loading_date"),
            delivery_date=request.POST.get("delivery_date") or None,
            additional_info=request.POST.get("additional_info", "").strip(),
            sender=sender,
            receiver=receiver,
            driver=driver,
            vehicle=vehicle,
        )

        cargo_names = _clean_rows(request.POST.getlist("cargo_name[]"))
        cargo_weights = _clean_rows(request.POST.getlist("cargo_weight[]"))
        cargo_quantities = _clean_rows(request.POST.getlist("cargo_quantity[]"))

        for name, weight, quantity in zip(cargo_names, cargo_weights, cargo_quantities):
            if not name:
                continue

            cargo, _ = Cargo.objects.get_or_create(name=name)
            WaybillItem.objects.create(
                waybill=waybill,
                cargo=cargo,
                quantity=_parse_int(quantity),
                weight=_parse_float(weight),
            )

        messages.success(request, f"Накладная {waybill.number} сохранена в базе данных.")
        return redirect("home")

    return render(request, "home.html")


@login_required
def waybill_list(request):
    waybills = _build_waybill_queryset()
    return render(request, "waybill_list.html", {"waybills": waybills})


@login_required
def export_waybills_csv(request):
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="waybills.csv"'
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")
    _write_waybill_rows(writer, _build_waybill_queryset())
    return response


@login_required
def export_waybill_csv(request, waybill_id):
    waybill = get_object_or_404(
        _build_waybill_queryset(),
        pk=waybill_id,
    )

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="waybill_{waybill.number}.csv"'
    response.write("\ufeff")

    writer = csv.writer(response, delimiter=";")
    _write_waybill_rows(writer, [waybill])
    return response


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Регистрация завершена. Добро пожаловать.")
            return redirect(get_post_login_redirect(user))
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})
