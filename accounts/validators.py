from django.core.exceptions import ValidationError
import os

def allow_only_images_validator(value):
    # below takes the extension portion of the file
    ext = os.path.splitext(value.name)[1]
    valid_extensions = [
        'png','jpg','jpeg'
        ]
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.  Allowed extensions are:' + str(valid_extensions))
    else:
        # valid extension
        pass


