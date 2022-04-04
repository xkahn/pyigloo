import datetime
import pyigloo
import pyigloo.iglootypes
import pyigloo.igloodates


class igtraffic:
    dates = {}
    date_list = []
    maxids = 30
    igloosession = None
    typelookuptable = None
    traffic_lookup = {}
    key_lookup = {}

    def __init__ (self, igloosession, igtype="Wiki", dates={"Week": 7, "Quarter": 90, "Year": 365}, timezone="us_eastern", ids = None):
        today = datetime.date.today()
        dl = []
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
            self.prep_ids(ids)

    def prep_ids(self, ids):
        self.listofids = [ids[i:i + self.maxids] for i in range(0, len(ids), self.maxids)]

    def uuid_to_odatakey(self):
        for ids in self.listofids:

            articlesinfo = self.igloosession.get_odata_url(self.typelookuptable["dtable"], 
                                                           [("$apply", "filter(" + " or ".join( ["source_system_id eq {0}".format(id) for id in ids]) + ")")]) 

            for ai in articlesinfo:
                self.traffic_lookup[ai["source_system_id"]] = {"key": ai[self.typelookuptable["dkey"]]}
                self.key_lookup[ai[self.typelookuptable["dkey"]]] = ai["source_system_id"]

    def get_traffic (self):
        if len(self.traffic_lookup) == 0:
            self.uuid_to_odatakey()

        for ids in self.listofids:
            list_of_eq = " or ".join(["{} eq {}".format(self.typelookuptable["dkey"], 
                                                        self.traffic_lookup[tl]["key"]) for tl in self.traffic_lookup if len(self.traffic_lookup[tl]) == 1])
            for tl in self.traffic_lookup:
                self.traffic_lookup[tl]['checked'] = 1

            for date in self.dates:
                d = self.dates[date]["halfhour"]
                for tl in self.traffic_lookup:
                    self.traffic_lookup[tl][date] = None
                filter = "filter((" + list_of_eq + ") and utc_half_hour_key ge " + str(d) + ")/groupby((" + self.typelookuptable["dkey"] + "), aggregate(" + self.typelookuptable["fkey"] + " with sum as " + self.typelookuptable["fkey"] + "))"
                traffic_stats = self.igloosession.get_odata_url(self.typelookuptable["ftable"], [("$apply", filter)])

                # traffic_stats should now contain an array of traffic results with no other information
                # it should be in the SAME order as traffic_lookup, so we need to iterate through 
                # traffic_lookup and assign the stats from traffic lookup

                for ts in traffic_stats:
                    self.traffic_lookup[self.key_lookup[ts[self.typelookuptable["dkey"]]]][date] = ts[self.typelookuptable["fkey"]]

        return self.traffic_lookup
