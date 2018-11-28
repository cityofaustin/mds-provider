"""
MDS Provider API client implementation. 
"""

from datetime import datetime
import json

import requests
from requests import Session


class ProviderClient(object):
    """
    Client for MDS Provider APIs
    """

    def __init__(self, url, token, auth_type="Bearer", headers=None):
        """
        Initialize a new ProviderClient object.

        :url: The provider's base MDS endpoint url.
            
        :auth_type: The `Authorization` request header type. Default is `Bearer`.  
        
        :headers: Additional optional request headers
        
        :token: API access token which will be used to construct `Authorization` request header as `Authorization: <auth_type> <token>`
        """
        self.url = url
        self.token = token

        self.auth_type = auth_type
        self.headers = headers if headers else {}

        self.session = self._auth_session()

    def _auth_session(self):
        """
        Internal helper to establish an authenticated session with the
        `Authorization: :auth_type: :token:` header.
        """
        self.headers.update({"Authorization": f"{self.auth_type} {self.token}"})
        session = Session()
        session.headers.update(self.headers)

        return session

    def _build_url(self, endpoint):
        """
        Internal helper for building API urls.
        """
        return self.url.rstrip("/") + "/" + endpoint

    def _request(self, endpoint, params, paging):
        """
        Internal helper for sending requests.

        Returns a list of trip records.
        """

        def __describe(res):
            """
            Prints details about the given response.
            """
            print(f"Requested {res.url}, Response Code: {res.status_code}")
            print("Response Headers:")
            for k, v in res.headers.items():
                print(f"{k}: {v}")

            if r.status_code is not 200:
                print(r.text)

        def __has_data(page):
            """
            Checks if this :page: has a "data" property with a non-empty payload
            """
            data = page["data"] if "data" in page else {"__payload__": []}
            payload = data[endpoint] if endpoint in data else []
            print(f"Got payload with {len(payload)} {endpoint}")
            return len(payload) > 0

        def __next_url(page):
            """
            Gets the next URL or None from :page:
            """
            return page["links"].get("next") if "links" in page else None

        # create a request url for each provider
        url = self._build_url(endpoint)

        # get the initial page of data
        r = self.session.get(url, params=params)

        if r.status_code is not 200:
            __describe(r)
            # TODO: implement re-try and log failures
            # TODO: break request.get and response check into separate function
            r.raise_for_status()

        this_page = r.json()

        self.data = this_page["data"]["trips"] if __has_data(this_page) else []

        # get subsequent pages of data
        next_url = __next_url(this_page)

        while paging and next_url:
            r = self.session.get(next_url)

            if r.status_code is not 200:
                __describe(r)
                break

            this_page = r.json()

            if __has_data(this_page):
                self.data += this_page["data"]["trips"]
                next_url = __next_url(this_page)
            else:
                break

        return self.data

    def _date_format(self, dt):
        """
        Internal helper to format datetimes for querystrings.
        """
        return int(dt.timestamp()) if isinstance(dt, datetime) else int(dt)

    def get_status_changes(
        self,
        start_time=None,
        end_time=None,
        bbox=None,
        paging=True,
        **kwargs,
    ):
        """
        Request Status Changes data. Returns a dict of provider => list of status_changes payload(s)

        Supported keyword args:

            - `start_time`: Filters for status changes where `event_time` occurs at or after the given time
                            Should be a datetime object or numeric representation of UNIX seconds

            - `end_time`: Filters for status changes where `event_time` occurs at or before the given time
                          Should be a datetime object or numeric representation of UNIX seconds

            - `bbox`: Filters for status changes where `event_location` is within defined bounding-box.
                      The order is defined as: southwest longitude, southwest latitude, 
                      northeast longitude, northeast latitude (separated by commas).

                      e.g.

                      bbox=-122.4183,37.7758,-122.4120,37.7858

            - `paging`: True (default) to follow paging and request all available data.
                        False to request only the first page.
        """
        if providers is None:
            providers = self.providers

        # convert datetimes to querystring friendly format
        if start_time is not None:
            start_time = self._date_format(start_time)
        if end_time is not None:
            end_time = self._date_format(end_time)

        # gather all the params together
        params = {**dict(start_time=start_time, end_time=end_time, bbox=bbox), **kwargs}

        # make the request(s)
        status_changes = self._request(providers, mds.STATUS_CHANGES, params, paging)

        return status_changes

    def get_trips(
        self,
        providers=None,
        device_id=None,
        vehicle_id=None,
        start_time=None,
        end_time=None,
        bbox=None,
        paging=True,
        **kwargs,
    ):
        """
        Request Trips data. Returns a dict of provider => list of trips payload(s).

        Supported keyword args:

            - `providers`: One or more Providers to issue this request to.
                           The default is to issue the request to all Providers.

            - `device_id`: Filters for trips taken by the given device.

            - `vehicle_id`: Filters for trips taken by the given vehicle.

            - `start_time`: Filters for trips where `start_time` occurs at or after the given time
                            Should be a datetime object or numeric representation of UNIX seconds

            - `end_time`: Filters for trips where `end_time` occurs at or before the given time
                          Should be a datetime object or numeric representation of UNIX seconds

            - `bbox`: Filters for trips where and point within `route` is within defined bounding-box.
                      The order is defined as: southwest longitude, southwest latitude, 
                      northeast longitude, northeast latitude (separated by commas).

                      e.g.

                      bbox=-122.4183,37.7758,-122.4120,37.7858

            - `paging`: True (default) to follow paging and request all available data.
                        False to request only the first page.
        """
        # convert datetimes to querystring friendly format
        if start_time is not None:
            start_time = self._date_format(start_time)
        if end_time is not None:
            end_time = self._date_format(end_time)

        # gather all the params togethers
        params = {
            **dict(
                device_id=device_id,
                vehicle_id=vehicle_id,
                start_time=start_time,
                end_time=end_time,
                bbox=bbox,
            ),
            **kwargs,
        }

        # make the request(s)
        trips = self._request("trips", params, paging)

        return trips
