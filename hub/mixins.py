from django.http import HttpResponseNotFound


class HTMXMixin():
    """
    A mixin to add proper HTMX handling to class-based views.
    
    It requires a list of partials, which are the template parts that can be renderer in this view, along with their respective rendering functions.
    The partials should be defined in the `partials` attribute of the class.
    """

    partials = {}
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'partials'):
            self.partials = {}
        if not isinstance(self.partials, dict):
            raise ValueError("Partials must be a dictionary mapping partial names to rendering functions.")
        for name, func in self.partials.items():
            if not callable(func):
                raise ValueError("Each partial must be a callable function that takes a request and returns an HttpResponse.")
            
    def dispatch(self, request, *args, **kwargs):
        if request.htmx:
            # Grab the partial name based on the URL, with the prefix ##
            partial_name = request.path.split("##")[-1]
            if partial_name in self.partials:
                # Call the rendering function for the partial
                return self.partials[partial_name](request, *args, **kwargs)
            else:
                # If the partial is not found, return a 404 response
                return HttpResponseNotFound("Partial not found: {}".format(partial_name))
        return super().dispatch(request, *args, **kwargs)