from ..models import Session,Attendance,Donation,Expense,Kid,Profile, Donor,Project
import math

def gallery(data,c,p=None,y=None,m=None):
    if p is None:
        if y is None and m is None:
            f = c.objects.all()
        elif y is not None and m is not None:
            f = c.objects.filter(date__year=y,date__month=m)
        elif y is not None:
            f = c.objects.filter(date__year=y)
        elif m is not None:
            f = c.objects.filter(date__month=m)
    else:
        if y is None and m is None:
            f = c.objects.filter(project__in=p)
        elif y is not None and m is not None:
            f = c.objects.filter(project__in=p,date__year=y,date__month=m)
        elif y is not None:
            f = c.objects.filter(project__in=p,date__year=y)
        elif m is not None:
            f = c.objects.filter(project__in=p,date__month=m)

    print(f)
    data['img_list'] = list(f.values_list('image',flat=True))
    data['length'] = list(range(1,int(math.ceil(len(data['img_list'])/3))+1))
    return data
