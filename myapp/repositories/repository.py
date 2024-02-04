class Repository:    
    def __init__(self, model):
        self.model = model

    def create(self, validated_data):
        return self.model.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def filter_objects(self, **filters):
        return self.model.objects.filter(**filters)

    def get_object(self, **filters):
        return self.model.objects.get(**filters)
    
    def get_object_or_fail(self, **filters):
        try:
            return  self.model.objects.get(**filters)
        except self.model.DoesNotExist:
            return None

    def get_object_or_none(self, model, **filters):
        try:
            return model.objects.get(**filters)
        except model.DoesNotExist:
            return None
