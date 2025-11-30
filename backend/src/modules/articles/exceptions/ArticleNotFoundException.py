class ArticleNotFoundException(Exception):
    def __init__(self, slug: str):
        self.slug = slug
        super().__init__(f"Article with slug '{slug}' not found")
