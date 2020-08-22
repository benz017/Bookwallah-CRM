import requests
import json
MAILCHIMP_API_KEY = "e878009d8adeeb7bb38d7ec78f8d6595-us3"
MAILCHIMP_LIST_ID = "4184463c28"

Base_URL = "https://us3.api.mailchimp.com/3.0/"

User = "benz017"


def get_lists():
    params = {"fields":"lists.id,lists.name"}
    req = requests.get('https://us3.api.mailchimp.com/3.0/lists',params=params, auth=('user', MAILCHIMP_API_KEY),
                       headers={"content-type": "application/json"})
    #print(req.json())
    return req.json()

def get_members():
    req ={}
    for i in get_lists()['lists']:
        params = {"fields": "members.list_id,members.id,members.email_address,members.merge_fields.FNAME,members.merge_fields.LNAME,members.merge_fields.ADDRESS,members.merge_fields.PHONE"}
        req = requests.get('https://us3.api.mailchimp.com/3.0/lists/'+i['id']+'/members',params=params, auth=('user', MAILCHIMP_API_KEY),
                       headers={"content-type": "application/json"})
        req = req.json()
        req.update({'members':{i["name"]:req["members"]}})
    #print(req)
    return req
#get_members()

def get_campaigns(count=50,off=0):
    endpoint_URL= "/campaigns"
    params = {"count":count,"offset":off}
    req = requests.get('https://us3.api.mailchimp.com/3.0/campaigns/',auth=('user', MAILCHIMP_API_KEY),params=params,headers={"content-type": "application/json"})
    #print(req.json())
    return req.json()


def get_campaign(id):
    params = {"fields":"type,recipients.list_name,settings.from_name,settings.reply_to,settings.title,"
                       "settings.subject_line,settings.preview_text,settings.template_id,"
                       "social_card.image_url,social_card.title,social_card.description"}
    req = requests.get('https://us3.api.mailchimp.com/3.0/campaigns/'+id, auth=('user', MAILCHIMP_API_KEY),params=params,headers={"content-type": "application/json"})
    content = requests.get('https://us3.api.mailchimp.com/3.0/campaigns/' + id+'/content', auth=('user', MAILCHIMP_API_KEY),
                       headers={"content-type": "application/json"})
    #f = open("test.html", "w+")
    #f.write(content.json()["html"])
    #f.close()
    #print(content.json())
    print(req.json()["type"])
    if req.json()["type"] == "plaintext":
        return req.json(),content.json()['plain_text']
    else:
        return req.json(), content.json()['html']
#get_campaign('23f929fb52')


def edit_campaign(cid,type,recipients,title,from_name,reply_to,url,s_title,desc,subject,
                          preview,temp_id,content):
    if type == "Plain Text":
        body1 = {
            "recipients": {"list_id": recipients},
            "settings": {"subject_line": subject,
                         "preview_text":preview,
                         "title": title,
                         "from_name": from_name,
                         "reply_to":reply_to,},
            "social_card":{"image_url":url,
                           "title":s_title,
                           "description":desc,}
        }
        body2 = {"plain_text":content,}
    else:
        body1 = {
            "recipients": {"list_id": recipients},
            "settings": {"subject_line": subject,
                         "preview_text": preview,
                         "title": title,
                         "from_name": from_name,
                         "reply_to": reply_to,
                         "template_id": int(temp_id)},
            "social_card": {"image_url": url,
                            "title": s_title,
                            "description": desc, }
        }
        body2 = {"html": content,
                 "template": get_templates(temp_id)}
    endpoint_URL = "/campaigns/"+cid
    req = requests.patch('https://us3.api.mailchimp.com/3.0'+endpoint_URL,data=json.dumps(body1), auth=('user', MAILCHIMP_API_KEY),
                       headers={"content-type": "application/json"})
    req2 = requests.put('https://us3.api.mailchimp.com/3.0' + endpoint_URL+'/content', data=json.dumps(body2),
                         auth=('user', MAILCHIMP_API_KEY),
                         headers={"content-type": "application/json"})
    print(3,req2.text)
    #send_campaign(req.json()['campaigns'][0])


def delete_campaign(cid):
    endpoint_URL = "/campaigns/"+cid
    req = requests.delete('https://us3.api.mailchimp.com/3.0'+endpoint_URL, auth=('user', MAILCHIMP_API_KEY),
                       headers={"content-type": "application/json"})
    print(req)


def send_campaign(cid):
    endpoint_URL = "/campaigns/"+cid+"/actions/send"
    req = requests.patch('https://us3.api.mailchimp.com/3.0' + endpoint_URL,
                         auth=('user', MAILCHIMP_API_KEY),
                         headers={"content-type": "application/json"})
    return req

#get_campaigns()
#edit_campaign('23f929fb52')


def get_templates(id=""):
    if id == "":
        params = {"fields": "templates.id,templates.name,templates.thumbnail"}
        req = requests.get('https://us3.api.mailchimp.com/3.0/templates',params=params,
                             auth=('user', MAILCHIMP_API_KEY),
                             headers={"content-type": "application/json"})
    else:
        req = requests.get('https://us3.api.mailchimp.com/3.0/templates/'+id,
                           auth=('user', MAILCHIMP_API_KEY),
                           headers={"content-type": "application/json"})
    return req.json()





get_templates('1010')