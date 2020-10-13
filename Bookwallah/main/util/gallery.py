from ..models import Session,Attendance,Donation,Expense,Kid,Profile, Donor,Project
import math
import numpy as np
from django.conf import settings
month_dict = {1:'JAN',2: 'FEB',3: 'MAR', 4:'APR', 5:'MAY', 6:'JUN', 7:'JUL',8: 'AUG', 9:'SEP', 10:'OCT', 11:'NOV', 12:'DEC'}

def gallery(data,c,p=None,y=None,m=None):
    for k,v in month_dict.items():
        if m==v:
            m=k
    if p is None:
        if y is None and m is None:
            f = c.objects.all()
        elif y is not None and m is not None:
            f  = c.objects.filter(date__year=y,date__month=m)
        elif y is not None:
            f = c.objects.filter(date__year=y)
        elif m is not None:
            f = c.objects.filter(date__month=m)
    else:
        if c == Project:
            if y is None and m is None:
                f = c.objects.filter(project_name=p)
            elif y is not None and m is not None:
                f = c.objects.filter(project_name=p, date__year=y, date__month=m)
                print(123, f)
            elif y is not None:
                f = c.objects.filter(project_name=p, date__year=y)
            elif m is not None:
                f = c.objects.filter(project_name=p, date__month=m)
        else:
            if y is None and m is None:
                f = c.objects.filter(project__in=p)
            elif y is not None and m is not None:
                f = c.objects.filter(project__in=p,date__year=y,date__month=m)
                print(123,f)
            elif y is not None:
                f = c.objects.filter(project__in=p,date__year=y)
            elif m is not None:
                f = c.objects.filter(project__in=p,date__month=m)

    print(c,p,y,m)
    data['img_list'] = [settings.MEDIA_URL+av for av in list(f.values_list('image',flat=True))]
    length = list(range(1,int(math.ceil(len(data['img_list'])/3))+1))
    row_list = []
    for i in length:
        l = len(data['img_list'])
        le = math.ceil(l / 3)
        # print(ilist,l,math.ceil(le),type(len(ilist)))

        if i == le:
            ar = np.arange((i - 1) * 3, l).tolist()
        else:
            ar = np.arange((i - 1) * 3, i * 3).tolist()
        row_list.append(ar)
    data['row_list']=row_list
    print(data,row_list)
    return data
