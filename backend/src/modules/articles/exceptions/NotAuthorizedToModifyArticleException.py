class NotAuthorizedToModifyArticleException(Exception):
    def __init__(self):
        super().__init__("Not authorized to modify this article")
