class types:
    iglootypes = {
        # Containers
        "Community":
            {"children": True,
            "content": False,
            "type": "container"},
        "Space":
            {"children": True,
            "content": False,
            "type": "container"},
        "Page":
            {"children": True,
            "content": False,
            "type": "container"},

        # Content Channels
        "Wiki":
            {"children": True,
            "content": True,
            "type": "channel"},
        "BlogChannel":
            {"children": True,
            "content": True,
            "type": "channel"},
        "FolderChannel":
            {"children": True,
            "content": True,
            "type": "channel"},
        "ForumChannel":
            {"children": True,
            "content": True,
            "type": "channel"},
        "Calendar":
            {"children": True,
            "content": True,
            "type": "channel"},
        "MicroBlogChannel":
            {"children": True,
            "content": True,
            "type": "channel"},
            
        # Content
        "WikiArticle":
            {"children": False,
            "content": True,
            "type": "article"},
        "BlogArticle":
            {"children": False,
            "content": True,
            "type": "article"},
        "ForumTopic":
            {"children": False,
            "content": True,
            "type": "article"},
        "Folder":
            {"Children": True,
            "content": False,
            "type": "channel"},
        "Document":
            {"children": False,
            "content": False,
            "type": "article"},
        "CalendarEvent":
            {"children": False,
            "content": True,
            "type": "article"},

        # Sub-content
        "ForumPost":
            {"children": False,
            "content": True,
            "type": "article"},
        "Comment":
            {"children": False,
            "content": True,
            "type": "comment"},
        "relatedObject":
            {"children": False,
            "content": True,
            "type": "attachment"},

        # Search Results
        "IglooList":
            {"children": True,
            "content": False,
            "type": "list"}
    }

    def __init__ (self, mytype):
        if (type(mytype) == "<class 'str'>"):
            self.mytype = mytype
        else:
            self.mytype = mytype["__type"]
        self.info = self.iglootypes[self.mytype.split(":")[0]]

    def __str__(self):
        return self.mytype.split(":")[0]

    def get_info (self):
        return self.info