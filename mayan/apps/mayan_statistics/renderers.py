import json


class ChartRenderer:
    def __init__(self, data):
        self.data = data

    def _get_chart_data(self):
        raise NotImplementedError

    def get_chart_data(self):
        return json.dumps(obj=self._get_chart_data())


class RendererChartJSLine(ChartRenderer):
    template_name = 'statistics/renderers/chartjs/line.html'

    dataset_palette = (
        {
            'backgroundColor': 'rgba(24, 188, 156, 0.1)',
            'borderColor': '#18bc9c',
            'pointBorderWidth': 3,
            'pointHitRadius': 6,
            'pointHoverRadius': 7,
            'pointRadius': 6,
        },
    )

    def _get_chart_data(self):
        labels = []
        datasets = []

        for count, serie in enumerate(iterable=self.data['series'].items()):
            series_name, series_data = serie
            dataset_labels = []
            dataset_values = []

            for data_point in series_data:
                dataset_labels.extend(data_point.keys())
                dataset_values.extend(data_point.values())

            labels = dataset_labels
            dataset = {
                'cubicInterpolationMode': 'monotone',
                'data': dataset_values,
                'fill': True,
                'label': series_name
            }
            dataset.update(
                RendererChartJSLine.dataset_palette[
                    count % len(RendererChartJSLine.dataset_palette)
                ]
            )

            datasets.append(dataset)

        data = {
            'datasets': datasets,
            'labels': labels
        }

        return data


class RendererChartJSDoughnut(ChartRenderer):
    dataset_palette = (
        {
            'backgroundColor': (
                'red', 'orange', 'yellow', 'green', 'blue', 'violet'
            )
        },
    )
    template_name = 'statistics/renderers/chartjs/doughnut.html'

    def _get_chart_data(self):
        labels = []
        datasets = []

        for count, serie in enumerate(iterable=self.data['series'].items()):
            dataset = {
                'data': []
            }

            series_name, series_data = serie

            for entry in series_data:
                labels.append(entry['label'])
                dataset['data'].append(entry['value'])

            dataset.update(
                self.dataset_palette[
                    count % len(self.dataset_palette)
                ]
            )

            datasets.append(dataset)

        data = {
            'datasets': datasets,
            'labels': labels
        }

        return data


class RendererChartJSPie(RendererChartJSDoughnut):
    template_name = 'statistics/renderers/chartjs/pie.html'
