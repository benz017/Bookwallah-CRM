from linkedin_v2.linkedin import (LinkedInAuthentication, LinkedInApplication,
                               PERMISSIONS)

if __name__ == '__main__':
    API_KEY = '86jm210h5i5hd7'
    API_SECRET = 'J8AXYsRzMoGygeUu'
    RETURN_URL = 'http://127.0.0.1:8000/accounts/profile'
    authentication = LinkedInAuthentication(API_KEY, API_SECRET, RETURN_URL,
                                            PERMISSIONS.enums.values())
    print(authentication.authorization_url)
    application = LinkedInApplication(authentication)