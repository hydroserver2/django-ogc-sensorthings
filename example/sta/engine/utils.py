class SensorThingsUtils:
    @staticmethod
    def apply_pagination(response, pagination):
        return {
            i['id']: i for i in list(response.values())[pagination['skip']: pagination['skip'] + pagination['top']]
        } if pagination['top'] > 0 else {}

    @staticmethod
    def apply_filters(response, filters):
        if filters:
            response = {
                k: v for k, v in response.items() if k == int(filters.right.val)
            }
        return response

    @staticmethod
    def apply_order(response, order_by):
        return response
