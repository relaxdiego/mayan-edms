import base64
import io

from django import forms


class Base64ImageWidget(forms.widgets.Widget):
    template_name = 'converter/forms/widgets/base64_image.html'

    def format_value(self, value):
        if value == '' or value is None:
            return None
        else:
            with io.BytesIO() as output:
                value.save(output, format='PNG')
                image = output.getvalue()
                url = 'data:image/png;charset=utf-8;base64,{}'.format(
                    str(
                        base64.b64encode(s=image)
                    )
                )

                return url


class ImageWidget(forms.widgets.Widget):
    template_name = 'converter/forms/widgets/widget_image.html'

    def format_value(self, value):
        if value == '' or value is None:
            return None
        return value
