import datetime
import pyigloo
import pyigloo.iglootypes
import pyigloo.igloodates


class igtraffic:
    """
    Get article view data for a list of IDs of the same type (wiki, blog, etc.)

    By default, return week, quarter, and year values
    """
    # Igloo's odata source has views over time information, but pulling
    # it is tricky over odata calls since we can't easily join 
    # tables and intermediate queries may create HUGE URLs.

    dates = {}
    date_list = []
    maxids = 30
    igloosession = None
    typelookuptable = None
    traffic_lookup = {}
    key_lookup = {}
    listofids = []

    def __init__ (self, igloosession, igtype="Wiki", dates={"Week": 7, "Quarter": 90, "Year": 365}, timezone="us_eastern", ids = None):
        today = datetime.date.today()
        dl = []
        self.traffic_lookup = {}
        self.key_lookup = {}
        self.listofids = []
        self.igloosession = igloosession
        self.typelookuptable = pyigloo.iglootypes.types.odataChildTypes[igtype]

        for date in dates.keys():
            dt = today - datetime.timedelta(days=dates[date])
            parsed =  dt.strftime("%Y-%m-%dT00:00:00Z")
            dl.append("{}_dt eq {}".format(timezone, parsed))
            self.dates[date] = {"offset": dates[date], "dt": dt, "parsed": parsed}

        query = [("$filter"," or ".join(dl))]
        result = igloosession.get_odata_url('dUtcHalfHour', query)

        for d in self.dates:
            halfhour = next((item[timezone + "_half_hour_key"] for item in result if item[timezone + "_dt"] == self.dates[d]["parsed"]), None)
            self.dates[d]["halfhour"] = halfhour
            self.date_list.append(halfhour)

        if ids is not None:
            self.listofids = ids

    def uuid_to_odatakey(self):
        listofids = [self.listofids[i:i + self.maxids] for i in range(0, len(self.listofids), self.maxids)]

        for ids in listofids:

            articlesinfo = self.igloosession.get_odata_url(self.typelookuptable["dtable"], 
                                                           [("$apply", "filter(" + " or ".join( ["source_system_id eq {0}".format(id) for id in ids]) + ")")]) 

            for ai in articlesinfo:
                self.traffic_lookup[ai["source_system_id"]] = {"key": ai[self.typelookuptable["dkey"]]}
                self.key_lookup[ai[self.typelookuptable["dkey"]]] = ai["source_system_id"]

    def get_traffic (self):
        if len(self.traffic_lookup) == 0:
            self.uuid_to_odatakey()

        listofids = [self.listofids[i:i + self.maxids] for i in range(0, len(self.listofids), self.maxids)]

        for ids in listofids:

            ids = [id for id in ids if id in self.traffic_lookup]

            list_of_eq = " or ".join(["{} eq {}".format(self.typelookuptable["dkey"], 
                                                        self.traffic_lookup[id]["key"]) for id in ids if 'checked' not in self.traffic_lookup[id]])
            
            for id in ids:
                if id in self.traffic_lookup:
                    self.traffic_lookup[id]['checked'] = 1
                else:
                    self.traffic_lookup[id] = {'chcked': 1}

            for date in self.dates:
                d = self.dates[date]["halfhour"]
                for id in ids:
                    self.traffic_lookup[id][date] = 0
                filter = "filter((" + list_of_eq + ") and utc_half_hour_key ge " + str(d) + ")/groupby((" + self.typelookuptable["dkey"] + "), aggregate(" + self.typelookuptable["fkey"] + " with sum as " + self.typelookuptable["fkey"] + "))"
                traffic_stats = self.igloosession.get_odata_url(self.typelookuptable["ftable"], [("$apply", filter)])

                # traffic_stats should now contain an array of traffic results with no other information
                # it should be in the SAME order as traffic_lookup, so we need to iterate through 
                # traffic_lookup and assign the stats from traffic lookup

                for ts in traffic_stats:
                    self.traffic_lookup[self.key_lookup[ts[self.typelookuptable["dkey"]]]][date] = ts[self.typelookuptable["fkey"]]

        return self.traffic_lookup

    def get_latest_views (self):
        # fContentBlog $apply=filter(blog_key eq 33831 or blog_key eq 51303 or blog_key eq 583189 or blog_key eq 40806)/groupby((blog_key), aggregate(blog_views with sum as blog_views))	

        if len(self.traffic_lookup) == 0:
            self.uuid_to_odatakey()

        listofids = [self.listofids[i:i + self.maxids] for i in range(0, len(self.listofids), self.maxids)]

        for ids in listofids:

            ids = [id for id in ids if id in self.traffic_lookup]

            list_of_eq = " or ".join(["{} eq {}".format(self.typelookuptable["dkey"], 
                                                        self.traffic_lookup[id]["key"]) for id in ids if 'utcchecked' not in self.traffic_lookup[id]])
            
            for id in ids:
                if id in self.traffic_lookup:
                    self.traffic_lookup[id]['utcchecked'] = 1
                else:
                    self.traffic_lookup[id] = {'utcchcked': 1}


            filter = "filter(" + list_of_eq + ")/groupby((" + self.typelookuptable["dkey"] + "), aggregate(utc_half_hour_key with max as utc_half_hour_key))"
            traffic_stats = self.igloosession.get_odata_url(self.typelookuptable["ftable"], [("$apply", filter)])

            # traffic_stats should now contain an array of traffic results with no other information
            # it should be in the SAME order as traffic_lookup, so we need to iterate through 
            # traffic_lookup and assign the stats from traffic lookup

            for ts in traffic_stats:
                self.traffic_lookup[self.key_lookup[ts[self.typelookuptable["dkey"]]]]["utc_half_hour_key"] = ts["utc_half_hour_key"]

        return self.traffic_lookup

    def half_hour_to_date (self, timezone="us_eastern"):
        listofids = [self.listofids[i:i + 10] for i in range(0, len(self.listofids), 10)]

        for ids in listofids:

            ids = [id for id in ids if id in self.traffic_lookup]

            finddates = ["utc_half_hour_key eq {}".format(self.traffic_lookup[id]["utc_half_hour_key"]) for id in ids]

            query = [("$filter"," or ".join(finddates))]
            result = self.igloosession.get_odata_url('dUtcHalfHour', query)

            for id in ids:
                self.traffic_lookup[id]["last_view"] = next((" ".join(item[timezone + "_dt"][:-1].split("T")) for item in result if item["utc_half_hour_key"] == self.traffic_lookup[id]["utc_half_hour_key"]), None)

        return self.traffic_lookup