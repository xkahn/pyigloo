# -*- coding: utf-8 -*-
"""
pyigloo is a small wrapper for Igloo API calls in Python


.. codeauthor:: Benjamin Kahn <xkahn@redhat.com>

Usage example:
>>>

"""

class igloo:

    import requests

    IGLOO_API_ROOT_V1 = ".api/api.svc/"
    IGLOO_API_ROOT_V2 = ".api2/api/"

    ticket = None
    igloo = None
    endpoint = None

    def __init__(self, info, session=None):
        self.endpoint = info["API_ENDPOINT"]
        self.igloo = self.requests.session()
        if session == None:
            self.connect(info)
        else:
            self.adopt(session)

    def __repr__(self):
        return '<{} @ {}>'.format(self.ticket, self.endpoint)

    def connect (self, info):
        v2 = {
            "AppId":        info["ACCESS_KEY"],
            "AppPassword":  info["API_KEY"],
            "UserName":     info["API_USER"],
            "UserPassword": info["API_PASSWORD"],
            "instance":     0, # FIXME: Allow this to be set
            "version":      1  # FIXME: Allow this to be set
        }
        result = self.get_session_v2(v2)
        cookie = self.requests.cookies.create_cookie ("iglooauth", result.json()['TokenId'])
        self.igloo.cookies.set_cookie(cookie)
        self.ticket = cookie

    def adopt (self, session):
        cookie = self.requests.cookies.create_cookie ("iglooauth", session)
        self.igloo.cookies.set_cookie(cookie)
        self.ticket = cookie

    def get_session_v1 (self, params):
        """
        APIv1 session/create

        https://customercare.igloosoftware.com/cmedia/api-docs/#/Session/post__api_api_svc_session_create
        """
        url = '{0}{1}session/create'.format(self.endpoint, self.IGLOO_API_ROOT_V1)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.post(url, data=params, headers=headers)
        return result

    def get_session_v2 (self, params):
        """
        APIv2 Session/Create

        https://customercare.igloosoftware.com/cmedia/api-docs/?api=api2#/Session/Session_CreateV1
        """
        url = '{0}{1}Session/Create'.format(self.endpoint, self.IGLOO_API_ROOT_V2)
        result = self.igloo.post(url, json=params)
        return result

    def get_web_uri (self, url):
        """
        Using the login key, pull and return a full igloo web page instead of an API call

        url: The URL fragment (not including ENDPOINT) to retrieve
        returns: The full requests response object
        """
        url = '{0}{1}'.format(self.endpoint, url)
        result = self.igloo.get(url)
        return result

    def get_odata_url (self, table, action):
        """
        Using the login key, pull and return an oData table instead of an Igloo API call

        table: the table name
        action: fully specified query in a tuple or None
        """
        url = '{0}odata/{1}'.format(self.endpoint, table)
        result = self.igloo.get(url, params=action)
        return result.json()['value']

    def get_paged_odata_url (self, table, action, skip=0):
        """
        Using the login key, pull and return an oData table instead of an Igloo API call

        oData URLs are limited to 10000 rows, this funtion has a skip parameter for
        starting at a particular row

        table: the table name
        action: fully specified query in a tuple or None
        skip: number of rows to start from

        This version returns the FULL json response to include the @odata.nextLink value
        """
        url = '{0}odata/{1}'.format(self.endpoint, table)
        result = self.igloo.get(url, params=action + [("$skip", skip)])
        return result.json()

    def get_all_odata_url (self, table, action):
        """
        oData URLs are limited to 10000 rows, this funtion will return a generator
        that will keep returning rows until the total space is exhausted

        table: the table name
        action: fully specified query in a tuple or None
        """
        items = self.get_paged_odata_url (table, action)
        total = len(items["value"])
        returned = 0
        while True:
            for item in items["value"]:
                returned += 1
                yield item

            if "@odata.nextLink" not in items:
                break

            items = self.get_paged_odata_url (table, action, returned+1)

    def community_view (self):
        """ 
        APIv1 community/view call

        https://customercare.igloosoftware.com/cmedia/api-docs/#/Community/get__api_api_svc_community_view
        """
        url = '{0}{1}community/view'.format(self.endpoint, self.IGLOO_API_ROOT_V1)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers)
        return result.json()['response']

    def community_info (self):
        """
        APIv2 community/info call

        https://customercare.igloosoftware.com/cmedia/api-docs/?api=api2#/Community/Community_GetCommunityInfoByDomain
        """
        url = '{0}{1}/community/info'.format(self.endpoint, self.IGLOO_API_ROOT_V2)
        result = self.igloo.post(url)
        return result

    def objects_bypath (self, path, domain = None):
        """
        APIv1 objects/byPath call

        https://customercare.igloosoftware.com/cmedia/api-docs/#/Objects/get__api_api_svc_objects_byPath
        Given a URI fragment, return information about the object

        This is the most common API call, allowing you to dereference a URL to an ID
        """
        url = '{0}{1}/objects/byPath'.format(self.endpoint, self.IGLOO_API_ROOT_V1)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers, params={'path': path, 'domain': domain})
        return result.json()['response']

    def objects_view (self, objectid):
        """
        APIv1 objects/{objectId}/view call

        https://customercare.igloosoftware.com/cmedia/api-docs/#/Objects/get__api_api_svc_objects__objectId__view
        Given am object id, return information about the object
        """
        url = '{0}{1}/objects/{2}/view'.format(self.endpoint, self.IGLOO_API_ROOT_V1, objectid)
        headers =  {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers)
        return result.json()['response']

    def objects_children_view (self, objectid, max=10, start=0, orderby="None", future=True):
        """
        APIv1 objects/{objectId}/children/view call
        
        https://customercare.igloosoftware.com/cmedia/api-docs/#/Objects/get__api_api_svc_objects__objectId__children_view
        Given an object id, return a list of the children contained in the object
        """
        url = '{0}{1}/objects/{2}/children/view'.format(self.endpoint, self.IGLOO_API_ROOT_V1, objectid)
        headers =  {b'Accept': 'application/json'}
        params = {'maxcount': max, 'startindex': start, 'orderby': orderby, 'includefuturepublished': future}
        result = self.igloo.get(url, headers=headers, params=params)
        return result.json()['response']

    def get_all_children_from_object (self, objectid, orderby="None", future=True, pagesize=100, current_page=0):
        """ 
        Return a generator object that handles pagination for us
        for objects/{objectId}/children/view
        """
        items = self.objects_children_view(objectid, pagesize, pagesize * current_page, orderby, future)
        total = int(items['totalCount'])
        returned = 0
        while True:
            for item in items["items"]:
                returned += 1
                yield item

            if returned >= total:
                break

            current_page += 1
            items = self.objects_children_view(objectid, pagesize, current_page * pagesize, orderby, future)

    def objects_comments_view (self, objectid, max=10, start=0, getdrafts=False):
        """
        APIv1 objects/{objectId}/comments/view call

        https://source.redhat.com/cmedia/api-docs/#/Objects/get__api_api_svc_objects__objectId__comments_view
        Gets Comments (if any) associated with the specified Object
        """
        url = '{0}{1}/objects/{2}/comments/view'.format(self.endpoint, self.IGLOO_API_ROOT_V1, objectid)
        headers =  {b'Accept': 'application/json'}
        params = {'maxcount': max, 'startindex': start, 'getdrafts': getdrafts}
        result = self.igloo.get(url, headers=headers, params=params)
        return result.json()['response']

    def get_all_comments_from_object (self, objectid, getdrafts=False, pagesize=100, current_page=0):
        """ 
        Return a generator object that handles pagination for us
        for objects/{objectId}/comments/view
        """
        items = self.objects_comments_view(objectid, pagesize, pagesize * current_page, getdrafts)
        total = int(items['totalCount'])
        returned = 0
        while True:
            for item in items["items"]:
                returned += 1
                yield item

            if returned >= total:
                break

            current_page += 1
            items = self.objects_comments_view(objectid, pagesize, current_page * pagesize, getdrafts)

    def attachments_view (self, objectid):
        """
        APIv1 attachments/{objectId}/view call

        https://customercare.igloosoftware.com/cmedia/cmedia/api-docs/#/Attachments/get__api_api_svc_attachments__objectId__view
        Given an object, return the list of attachments
        """
        url = '{0}{1}/attachments/{2}/view'.format(self.endpoint, self.IGLOO_API_ROOT_V1, objectid)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers)
        return result.json()['response']

    def apisync_view_usergroups (self, userIds = []):
        """
        APIv1 apisync/view_usergroups call
        
        https://customercare.igloosoftware.com/cmedia/api-docs/#/APISync/post__api_api_svc_apisync_view_usergroups
        Return a list of group IDs a user belongs to
        """
        url = '{0}{1}/apisync/view_usergroups'.format(self.endpoint, self.IGLOO_API_ROOT_V1)
        payload = {"userIds": userIds}
        headers =  {b'Accept': 'application/json'}
        result = self.igloo.post(url, headers=headers, params=payload)
        return result.json()['dictionary']

    def apisync_view_profile (self, userIds = []):
        """
        APIv1 /.api/api.svc/apisync/view_profile call
        
        https://source.redhat.com/cmedia/api-docs/#/APISync/post__api_api_svc_apisync_view_profile
        Return a FULL list of user profile settings
        """
        url = '{0}{1}/apisync/view_profile'.format(self.endpoint, self.IGLOO_API_ROOT_V1)
        payload = {"userIds": userIds}
        headers =  {b'Accept': 'application/json'}
        result = self.igloo.post(url, headers=headers, params=payload)
        return result.json()['dictionary']
    
    def community_usergroups_view (self, usergroupId):
        """
        APIv1 /community/usergroups/{usergroupId}/view call

        https://customercare.igloosoftware.com/cmedia/api-docs/#/CommunityUserGroups/get__api_api_svc_community_usergroups__usergroupId__view
        """
        url = '{0}{1}/community/usergroups/{2}/view'.format(self.endpoint, self.IGLOO_API_ROOT_V1, usergroupId)
        headers =  {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers)
        return result.json()['response']

    def usergroups_members_view (self, usergroupId, maxcount=10000, startindex=None, orderby=None):
        """
        APIv1 /usergroups/{usergroupId}/members/view calls

        ***undocumented*** but may be similar to
        https://source.redhat.com/cmedia/api-docs/#/Usergroups/get__api_api_svc_usergroups_members_view

        Return a list of members of the specified group
        """
        url = '{0}{1}/usergroups/{2}/members/view'.format(self.endpoint, self.IGLOO_API_ROOT_V1, usergroupId)
        headers = {b'Accept': 'application/json'}
        params = {"maxcount": maxcount, "startindex": startindex}
        result = self.igloo.get(url, headers=headers, params=params)
        return result.json()['response']

    def get_all_usergroups_members_view (self, usergroupId, maxcount=10000, page=0, orderby=None):
        """
        Return a generator object that handles pagination for us
        for usergroups/members/view
        """
        items = self.usergroups_members_view (usergroupId, maxcount=maxcount, startindex=page*maxcount, orderby=orderby)
        total = int(items['totalCount'])
        returned = 0
        while True:
            for item in items["items"]:
                returned += 1
                yield item

            if returned >= total:
                break

            page += 1
            items = self.usergroups_members_view (usergroupId, maxcount=maxcount, startindex=page*maxcount, orderby=orderby)

    def spaces_groups (self, spaceId):
        """
        APIv1 /.api/api.svc/spaces/{spaceId}/groups call

        https://customercare.igloosoftware.com/cmedia/api-docs/#/Spaces/get__api_api_svc_spaces__spaceId__groups
        Gets a list of all the groups within a given space.
        """
        url = '{0}{1}/spaces/{2}/groups'.format(self.endpoint, self.IGLOO_API_ROOT_V1, spaceId)
        headers = {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers)
        return result.json()['response']

    def search_members (self, query, rows=None, page=None, qType=None, hl=None, groupId=None, groupIds=None, parent=None):
        """
        APIv1 /.api/api.svc/search/members call

        Searches for users by search engine
        https://customercare.igloosoftware.com/cmedia/api-docs/#/Search/get__api_api_svc_search_members
        """
        url = '{0}{1}/search/members'.format(self.endpoint, self.IGLOO_API_ROOT_V1)
        params = {"q": query, "qType": qType, "rows": rows, "page": page, "hl": hl, "groupId": groupId, "groupIds": groupIds, "parent": parent}
        headers =  {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers, params=params)
        return result.json()['response']

    def get_all_search_members (self, query, rows=100, page=0, qType=None, hl=None, groupId=None, groupIds=None, parent=None):
        """ 
        Return a generator object that handles pagination for us
        for search/members
        """
        items = self.search_members(query, rows, rows * page, qType, hl, groupId, groupIds, parent)
        total = int(items['totalCount'])
        returned = 0
        while True:
            for item in items["items"]:
                returned += 1
                yield item

            if returned >= total:
                break

            page += 1
            items = self.search_members(query, rows, rows * page, qType, hl, groupId, groupIds, parent)


    def users_searchbyname (self, name):
        """
        APIv1 /.api/api.svc/users/searchByName call

        Searches for users by name (does partial matching).
        https://customercare.igloosoftware.com/cmedia/api-docs/#/Users/get__api_api_svc_users_searchByName
        """
        url = '{0}{1}/users/searchByName'.format(self.endpoint, self.IGLOO_API_ROOT_V1)
        payload = {"criteria": name}
        headers =  {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers, params=payload)
        return result.json()['response']

    def forumchannels_forumtopics_view (self, forumChannelId):
        """
        APIv1 /forumchannels/{forumChannelId}/forumtopics/view call

        """
        url = '{0}{1}/forumchannels/{2}/forumtopics/view'.format(self.endpoint, self.IGLOO_API_ROOT_V1, forumChannelId)
        headers =  {b'Accept': 'application/json'}
        result = self.igloo.get(url, headers=headers)
        return result.json()['response']

    def user_get (self, userId):
        """
        APIv2 /.api2/api/User/{userId}/Get
        
        Returns user status information including email and last login date
        undocumented
        """
        url = '{0}{1}/User/{2}/Get'.format(self.endpoint, self.IGLOO_API_ROOT_V2, userId)
        result = self.igloo.get(url)
        return result.json()
