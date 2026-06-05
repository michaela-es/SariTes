from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

PAGE_SIZE = 10

def paginate(queryset, request, page_size=PAGE_SIZE, param_name='page'):
    page_number = request.GET.get(param_name, 1)
    paginator = Paginator(queryset, page_size)
    try:
        page = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page = paginator.page(1)
    return page
