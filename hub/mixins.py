from django.http import HttpResponseNotFound


class HTMXMixin():
    """
    A mixin to add proper HTMX handling to class-based views.
    
    It requires a list of partials, which are the template parts that can be renderer in this view, along with their respective rendering functions.
    The partials should be defined in the `partials` attribute of the class.

    Optionally an action can be added by setting the partial to a touple of functtions (render_function, action_function).
    """

    partials = {}
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not hasattr(self, 'partials'):
            self.partials = {}
        if not isinstance(self.partials, dict):
            raise ValueError("Partials must be a dictionary mapping partial names to rendering functions.")
            
    def dispatch(self, request, *args, **kwargs):
        if request.htmx:
            # Grab the partial name based on the URL, with the arg hx
            partial_name = request.GET.get("hxp", "")
            if partial_name != "":
                if partial_name in self.partials:
                    # If the partial is found, check if it has an action function
                    if isinstance(self.partials[partial_name], tuple):
                        # If the partial is a tuple, it contains both a render function and an action function
                        render_function, action_function = self.partials[partial_name]
                        # Call the action function first
                        _ = action_function(request, *args, **kwargs)
                        return render_function(request, *args, **kwargs)
                    else:
                        # Call the rendering function for the partial
                        return self.partials[partial_name](request, *args, **kwargs)
                # If the partial is not found, return a 404 response
                return HttpResponseNotFound("Partial not found: {}".format(partial_name))
        return super().dispatch(request, *args, **kwargs)