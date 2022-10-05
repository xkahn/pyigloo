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
        "Model.DashboardPage":
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
        "Folder":
            {"Children": True,
            "content": False,
            "type": "channel"},
        "TaskChannel":
            {"Children": True,
            "content": False,
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
        "CalendarEventInstance":
            {"children": False,
            "content": True,
            "type": "article"
            },
        "CalendarEventException":
            {"children": False,
            "content": True,
            "type": "article"
            },

        # Search Results
        "IglooList":
            {"children": True,
            "content": False,
            "type": "list"}
    }

    odataChildTypes = {
        "Wiki":
            {"dtable": "dContentWiki",
            "dkey": "wiki_key",
            "ftable": "fContentWiki",
            "fkey": "wiki_content_views"},
        "BlogChannel":
            {"dtable": "dContentBlog",
            "dkey": "blog_key",
            "ftable": "fContentBlog",
            "fkey": "blog_views"},
        "ForumTopic":
            {"dtable": "dContentForumTopic",
            "dkey": "forum_key",
            "ftable": "fContentForumTopic",
            "fkey": "forum_topic_views"},
        "Folder":
            {"dtable": "dContentDocument",
            "dkey": "content_document_key",
            "ftable": "fContentDocument",
            "fkey": "document_views"},
        "FolderChannel":
            {"dtable": "dContentDocument",
            "dkey": "content_document_key",
            "ftable": "fContentDocument",
            "fkey": "document_views"},
       "Calendar":
            {"dtable": "dContentCalendar",
            "dkey": "calendar_content_key",
            "ftable": "fContentCalendar",
            "fkey": "calendar_views"},
        "ForumChannel":
            {"dtable": "dContentForumTopic",
            "dkey": "forum_key",
            "ftable": "fContentForumTopic",
            "fkey": "forum_topic_views"},
        "MicroBlogChannel":
            {"dtable": "dContentMicroblog",
            "dkey": "microblog_key",
            "ftable": "fContentMicroblog",
            "fkey": "microblog_content_views"},
        "TaskChannel":
            {"dtable": None,
            "dkey": None,
            "ftable": None,
            "fkey": None}
    }

    odatatypes = {
        # Content
        "WikiArticle":
            {"dtable": "dContentWiki",
            "dkey": "wiki_key",
            "ftable": "fContentWiki",
            "fkey": "wiki_content_views"},
        "BlogArticle":
            {"dtable": "dContentBlog",
            "dkey": "blog_key",
            "ftable": "fContentBlog",
            "fkey": "blog_views"},
        "ForumTopic":
            {"dtable": "dContentForumTopic",
            "dkey": "forum_key",
            "ftable": "fContentForumTopic",
            "fkey": "forum_topic_views"},
        "Document":
            {"dtable": "dContentDocument",
            "dkey": "content_document_key",
            "ftable": "fContentDocument",
            "fkey": "document_views"},
        "CalendarEvent":
            {"dtable": "dContentCalendar",
            "dkey": "calendar_content_key",
            "ftable": "fContentCalendar",
            "fkey": "calendar_views"},
    }

    v2tov1 = {
        "wiki": "Wiki",
        "wikiArticle": "WikiArticle",
        "blogChannel": "BlogChannel",
        "blogArticle": "BlogArticle",
        "calendar": "Calendar",
        "calendarEvent": "CalendarEvent",
        "calendarEventException": "CalendarEventException",
        "calendarEventInstance": "CalendarEventInstance",
        "document": "Document",
        "folder": "Folder",
        "folderChannel": "FolderChannel",
        "forumTopic": "ForumTopic",
        "page": "Page",
        "space": "Space",
    }

    def __init__ (self, mytype):
        if type(mytype) == "<class 'str'>":
            self.mytype = mytype
        elif "__type" in mytype:
            self.mytype = mytype["__type"]
        else:
            self.info = self.v2tov1[mytype["objectType"]]
            self.mytype = self.info + ":v2"
            return
            
        self.info = self.iglootypes[self.mytype.split(":")[0]]

    def __str__(self):
        return self.mytype.split(":")[0]

    def get_info (self):
        return self.info