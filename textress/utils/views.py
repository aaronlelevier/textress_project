from rest_framework import viewsets
from rest_framework.response import Response


class BaseModelViewSet(viewsets.ModelViewSet):
    
    queryset = None
    serializer_class = None
    filter_fields = None

    def get_queryset(self):
        """
        Allow filterable by 'IN' keyword.

        ``filter_fields``: A list of filterable fields that uses the 
        Django ORM sytax. Must be defined on the ModelViewSet that is 
        implementing this feature.
        """
        queryset = super(BaseModelViewSet, self).get_queryset()

        if self.filter_fields:
            kwargs = {}

            for param in self.request.query_params:
                if param.split("__")[0] in self.filter_fields:
                    if param.split("__")[-1] == "in":
                        value = self.request.query_params.get(param).split(',')
                    else:
                        value = self.request.query_params.get(param)

                    kwargs.update({param: value})

            queryset = queryset.filter(**kwargs)

        return queryset

    def list(self, request):
        """
        Changes the structure of the List API data, so no more 'results', 'count', 
        'next', 'prev'.  Only An array of objects.
        """
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
