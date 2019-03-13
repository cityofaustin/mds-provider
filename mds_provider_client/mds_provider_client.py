"""
MDS Provider API client implementation. 
"""
from datetime import datetime
import json
import logging
import time

import requests
from requests import Session


class ProviderClient(object):
    """
    Client for MDS Provider APIs
    """

    def __init__(
        self,
        url,
        auth_type="Bearer",
        token=None,
        user=None,
        password=None,
        headers=None,
        timeout=10,
        max_attempts=5,
        delay=1
    ):
        """
        Initialize a new ProviderClient object.

        :url: The provider's base MDS endpoint url.
        
        :token: API access token which will be used to construct `Authorization` request
            header as `Authorization: <auth_type> <token>`

        :auth_type: The `Authorization` request header type. Default is `Bearer`.  
        
        :headers: Additional optional request headers
        
        :timeout: Number of seconds before request timeout (default 10)

        :max_attempts: The maximum number times to attempt to send a request, in the event
            of timeout (default 5). 
        
        :delay: Number of seconds to wait between requests (default 1).

        """
        self.delay = delay
        self.url = url
        self.token = token
        self.user = user
        self.password = password

        if not token and not user:
            raise Exception("Username or token is required")

        self.auth_type = auth_type
        self.headers = headers if headers else {}
        self.timeout = timeout
        self.max_attempts = max_attempts

        self.session = self._auth_session()

    def _auth_session(self):
        """
        Internal helper to establish an authenticated session with the
        `Authorization: :auth_type: :token:` header.
        """
        session = Session()

        if self.auth_type.lower() == "httpbasicauth":
            session.auth = (self.user, self.password)

        else:
            self.headers.update({"Authorization": f"{self.auth_type} {self.token}"})
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

        Returns list of records and stores them at `self.<endpoint>`. 
        """

        def __has_data(page):
            """
            Checks if this :page: has a "data" property with a non-empty payload
            """
            data = page["data"] if "data" in page else {"__payload__": []}
            payload = data[endpoint] if endpoint in data else []
            print(f"Got payload with {len(payload)} {endpoint}")
            return len(payload) > 0

        def __next_url(self):
            """
            Gets the next URL or None from :page:
            """
            return self.links.get("next")

        url = self._build_url(endpoint)

        setattr(self, endpoint, [])

        while True:
            #  logic to retry request on timeout
            attempts = 0
            while attempts < self.max_attempts:

                attempts += 1

                time.sleep(self.delay)

                try:
                    # get the data
                    logging.debug(params)

                    self.res = self.session.get(
                        url, params=params, timeout=self.timeout
                    )

                    self.res.raise_for_status()

                    break

                except requests.exceptions.Timeout as e:
                    if attempts < self.max_attempts:
                        print("Request timeout. Trying again...")
                        continue
                    else:
                        raise e

            this_page = self.res.json()

            if __has_data(this_page):
                # append retrieved data
                getattr(self, endpoint).extend(this_page["data"][endpoint])
            else:
                # assume subsequent pages are empty
                break

            # get subsequent pages of data
            self.links = this_page.get("links")

            if not self.links:
                break

            # after the initial request, remove start/end time from request params
            # because these are included in the pagination `links`
            params = None

            url = self.links.get("next")

            if not paging or not url:
                break

        return getattr(self, endpoint)

    def _date_format(self, dt):
        """
        Internal helper to format datetimes for querystrings.
        """
        return int(dt.timestamp()) if isinstance(dt, datetime) else int(dt)

    def get_status_changes(
        self, start_time=None, end_time=None, bbox=None, paging=True, **kwargs
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

        # convert datetimes to querystring friendly format
        if start_time is not None:
            start_time = self._date_format(start_time)
        if end_time is not None:
            end_time = self._date_format(end_time)

        # gather all the params together
        params = {**dict(start_time=start_time, end_time=end_time, bbox=bbox), **kwargs}

        # make the request(s)
        status_changes = self._request("status_changes", params, paging)

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


if __name__ == "__main__":
    import logging

    logging.getLogger(__name__)
